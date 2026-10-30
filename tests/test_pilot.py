"""Offline runner checks; all inference responses are explicit test doubles."""

import hashlib
import io
import json

import pytest
from fastapi.testclient import TestClient

from meta_vibe_coding import pilot
from meta_vibe_coding.core import FlowError


def seed(tmp_path):
    event = {"type": "error", "timestamp": 1000,
             "error": {"type": "provider.free-limit", "retryAfterMs": 2000}}
    record = {"kind": "fictional-development-pilot", "source_commit": "design-baseline",
        "authority": {"additional_spend_cap_usd": 0, "native_invocation_limit": 7},
        "agent": {"name": "opencode", "requested_model": "opencode/fictional-free"},
        "attempts": [{"native_stdout": None, "request": {"request_id": "seed-1"}},
                     {"native_stdout": json.dumps(event), "request": {"request_id": "seed-2"}}],
        "resume_gate": {"retry_not_before_utc": "1970-01-01T00:00:00Z"}}
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(record))
    return path, record


def test_cooldown_uses_native_evidence_and_preserves_remaining_allowance(tmp_path):
    _, record = seed(tmp_path)
    assert pilot.pilot_plan(record, now=2.999)["status"] == "cooldown"
    plan = pilot.pilot_plan(record, now=3)
    assert plan["status"] == "pricing_check_required"
    assert plan["retry_not_before_utc"] == "1970-01-01T00:00:03+00:00"
    assert plan["remaining_invocations"] == 5
    record["attempts"] = [{"native_stdout": None, "request": {"request_id": f"seed-{i}"}} for i in range(8)]
    assert pilot.pilot_plan(record, now=4)["status"] == "allowance_exhausted"


@pytest.mark.parametrize("change", ["scope", "spend", "model", "allowance", "timestamp", "duplicate_request"])
def test_invalid_pilot_authority_or_cooldown_fails_closed(tmp_path, change):
    _, record = seed(tmp_path)
    if change == "scope": record["kind"] = "private-owner-session"
    if change == "spend": record["authority"]["additional_spend_cap_usd"] = 1
    if change == "model": record["agent"]["requested_model"] = "opencode/paid-model"
    if change == "allowance": record["authority"]["native_invocation_limit"] = 99
    if change == "duplicate_request": record["attempts"][1]["request"]["request_id"] = "seed-1"
    if change == "timestamp":
        event = json.loads(record["attempts"][1]["native_stdout"])
        event["error"]["retryAfterMs"] = True
        record["attempts"][1]["native_stdout"] = json.dumps(event)
    with pytest.raises(ValueError): pilot.pilot_plan(record, now=4)


def test_default_and_cooldown_checks_never_enable_or_start_the_agent(tmp_path, monkeypatch):
    path, _ = seed(tmp_path)
    monkeypatch.setattr(pilot.time, "time", lambda: 2)
    def forbidden(*args): raise AssertionError("Must not configure or start the agent")
    monkeypatch.setattr(pilot, "configure_pilot", forbidden)
    monkeypatch.setattr(pilot, "record_app", forbidden)
    assert pilot.main(["--record", str(path)]) == 0
    output = tmp_path / "must-not-exist.jsonl"
    assert pilot.main(["--record", str(path), "--serve", "--free-pricing-checked", "--output", str(output)]) == 2
    assert not output.exists()


def test_serving_requires_explicit_current_free_pricing_confirmation(tmp_path, monkeypatch):
    path, _ = seed(tmp_path)
    monkeypatch.setattr(pilot.time, "time", lambda: 4)
    with pytest.raises(SystemExit) as error: pilot.main(["--record", str(path), "--serve"])
    assert error.value.code == 2


def test_changed_login_retry_preserves_cooldown_evidence_allowance_and_claim(tmp_path, monkeypatch):
    import uvicorn

    path, _ = seed(tmp_path)
    monkeypatch.setattr(pilot.time, "time", lambda: 2)
    plans = []
    monkeypatch.setattr(pilot, "configure_pilot", lambda plan: plans.append(plan) or {})
    monkeypatch.setattr(pilot, "record_app", lambda journal: object())
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: None)
    args = ["--record", str(path), "--serve", "--recheck-after-login", "--output", str(tmp_path / "recheck.jsonl")]
    with pytest.raises(SystemExit): pilot.main(args)
    assert not plans
    assert pilot.main(args + ["--free-pricing-checked"]) == 0
    assert plans[0]["status"] == "cooldown" and plans[0]["remaining_invocations"] == 5
    manifest = json.loads((tmp_path / "recheck.jsonl").read_text())
    assert manifest["operator_changed_login_recheck"] is True
    assert manifest["plan"]["retry_not_before_utc"] == "1970-01-01T00:00:03+00:00"
    assert pilot.main(args + ["--free-pricing-checked"]) == 2


def test_changed_login_cannot_restore_exhausted_invocations(tmp_path, monkeypatch):
    path, record = seed(tmp_path)
    record["authority"]["native_invocation_limit"] = 2
    path.write_text(json.dumps(record))
    def forbidden(*args): raise AssertionError("Must not restore an exhausted allowance")
    monkeypatch.setattr(pilot, "configure_pilot", forbidden)
    assert pilot.main(["--record", str(path), "--serve", "--recheck-after-login", "--free-pricing-checked"]) == 2


@pytest.mark.parametrize("workspace", ["[REDACTED]", "***", "wrk_REDACTED", "${WORKSPACE}", None])
def test_native_routing_export_rejects_redacted_or_missing_values(workspace):
    metadata = {"data": [{"providerID": "opencode", "modelID": "fictional-free",
                          "headers": {"x-opencode-org-id": workspace}}]}
    with pytest.raises(ValueError): pilot.native_routing_config(metadata, "opencode/fictional-free")


@pytest.mark.parametrize("count", [0, 2])
def test_native_routing_export_requires_one_selected_model(count):
    row = {"providerID": "opencode", "modelID": "fictional-free",
           "headers": {"x-opencode-org-id": "wrk_FICTIONAL123"}}
    with pytest.raises(ValueError): pilot.native_routing_config({"data": [row] * count}, "opencode/fictional-free")


def test_native_routing_export_is_metadata_only_private_and_does_not_copy_other_headers(tmp_path, monkeypatch, capsys):
    from meta_vibe_coding import process

    path, record = seed(tmp_path)
    record["authority"]["native_invocation_limit"] = 2
    path.write_text(json.dumps(record))
    calls = []
    async def metadata_only(args, **kwargs):
        calls.append(args)
        assert kwargs["content"] == "" and kwargs["env"]["PWD"] == str(pilot.Path.home())
        return json.dumps({"data": [{"providerID": "opencode", "modelID": "fictional-free",
            "headers": {"x-opencode-org-id": "wrk_FICTIONAL123", "Authorization": "private-native-header"},
            "models": {"paid-model": {}}}]}).encode()
    monkeypatch.setattr(process, "run_cli", metadata_only)
    output = tmp_path / "native-routing.json"
    assert pilot.main(["--record", str(path), "--export-native-routing", str(output)]) == 0
    assert calls == [["opencode", "api", "GET", "/api/model"]]
    assert output.stat().st_mode & 0o777 == 0o600
    assert json.loads(output.read_text()) == {"providers": {"opencode": {"headers": {"x-opencode-org-id": "wrk_FICTIONAL123"}}}}
    text = capsys.readouterr().out
    assert "wrk_FICTIONAL123" not in text and "private-native-header" not in text
    original = output.read_bytes()
    with pytest.raises(FileExistsError): pilot.main(["--record", str(path), "--export-native-routing", str(output)])
    assert output.read_bytes() == original
    with pytest.raises(SystemExit):
        pilot.main(["--record", str(path), "--serve", "--export-native-routing", str(output)])


def test_overlay_pins_helpers_and_limits_without_forwarding_extra_env(monkeypatch):
    for name in ("MVC_AGENT", "MVC_ENABLE_AGENT", "MVC_AGENT_MODEL", "MVC_AGENT_ENV", "MVC_AGENT_MAX_CALLS",
                 "MVC_REQUEST_TIMEOUT_SECONDS", "MVC_SESSION_TIMEOUT_SECONDS", "OPENCODE_CONFIG_CONTENT"):
        monkeypatch.setenv(name, "prior-setting")
    overlay = pilot.configure_pilot({"requested_model": "opencode/fictional-free", "remaining_invocations": 5})
    assert pilot.os.environ["MVC_AGENT_MAX_CALLS"] == "5"
    assert pilot.os.environ["MVC_AGENT_ENV"] == ""
    assert all(value["model"] == overlay["model"] for value in overlay["agents"].values())
    assert overlay["warming"] is False and overlay["compaction"]["auto"] is False
    assert overlay["policies"][-1] == {"action": "tool.use", "resource": "*", "effect": "deny"}


def test_manifest_records_runtime_hashes_and_never_overwrites_evidence(tmp_path, monkeypatch):
    import uvicorn

    path, _ = seed(tmp_path)
    monkeypatch.setattr(pilot.time, "time", lambda: 4)
    monkeypatch.setattr(pilot, "configure_pilot", lambda plan: {"model": plan["requested_model"]})
    app = object()
    monkeypatch.setattr(pilot, "record_app", lambda journal: app)
    calls = []
    monkeypatch.setattr(uvicorn, "run", lambda selected, **kwargs: calls.append((selected, kwargs)))
    output = tmp_path / "evidence.jsonl"
    args = ["--record", str(path), "--serve", "--free-pricing-checked", "--output", str(output)]
    assert pilot.main(args) == 0
    manifest = json.loads(output.read_text())
    assert manifest["runtime_source_sha256"]["pilot.py"] == hashlib.sha256(pilot.Path(pilot.__file__).read_bytes()).hexdigest()
    assert manifest["seed_record_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert manifest["baseline_source_commit"] == "design-baseline"
    assert output.stat().st_mode & 0o777 == 0o600
    assert calls == [(app, {"host": "127.0.0.1", "port": 8001, "access_log": False})]
    original = output.read_bytes()
    assert pilot.main(args) == 2
    assert output.read_bytes() == original and len(calls) == 1
    another = tmp_path / "another-evidence.jsonl"
    # Even metadata edits and a new journal cannot recharge the same recorded attempts.
    record = json.loads(path.read_text())
    record["resume_gate"] = {"checked_at_utc": "updated-metadata"}
    record["agent"].update(version="new-version", authentication="updated authentication description")
    record["attempts"][0]["elapsed_seconds"] = 99
    path.write_text(json.dumps(record))
    assert pilot.main(args[:-1] + [str(another)]) == 2
    assert not another.exists() and len(calls) == 1


def test_failed_server_launch_keeps_the_continuation_claim(tmp_path, monkeypatch):
    import uvicorn

    path, _ = seed(tmp_path)
    monkeypatch.setattr(pilot.time, "time", lambda: 4)
    monkeypatch.setattr(pilot, "configure_pilot", lambda plan: {})
    monkeypatch.setattr(pilot, "record_app", lambda journal: object())
    calls = []
    def failed_start(*args, **kwargs):
        calls.append(args)
        raise RuntimeError("Fictional startup failure")
    monkeypatch.setattr(uvicorn, "run", failed_start)
    args = ["--record", str(path), "--serve", "--free-pricing-checked", "--output", str(tmp_path / "failure.jsonl")]
    with pytest.raises(RuntimeError): pilot.main(args)
    assert pilot.main(args[:-1] + [str(tmp_path / "retry.jsonl")]) == 2
    assert len(calls) == 1 and not (tmp_path / "retry.jsonl").exists()


def test_concurrent_launch_cannot_share_the_same_remaining_allowance(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    import uvicorn

    path, _ = seed(tmp_path)
    monkeypatch.setattr(pilot.time, "time", lambda: 4)
    monkeypatch.setattr(pilot, "configure_pilot", lambda plan: {})
    monkeypatch.setattr(pilot, "record_app", lambda journal: object())
    started, release = Event(), Event()
    def serving(*args, **kwargs):
        started.set()
        assert release.wait(5)
    monkeypatch.setattr(uvicorn, "run", serving)
    args = ["--record", str(path), "--serve", "--free-pricing-checked", "--output", str(tmp_path / "first.jsonl")]
    with ThreadPoolExecutor(max_workers=1) as pool:
        first = pool.submit(pilot.main, args)
        try:
            assert started.wait(5)
            assert pilot.main(args[:-1] + [str(tmp_path / "second.jsonl")]) == 2
            assert not (tmp_path / "second.jsonl").exists()
        finally:
            release.set()
        assert first.result(timeout=5) == 0


def test_http_journal_retains_failed_reply_but_excludes_headers_and_invalid_input():
    class QuotaDouble:
        async def assess(self, state, provisional):
            raise FlowError("free_limit", "Fictional quota failure from a test double.")

    journal = io.StringIO()
    with TestClient(pilot.record_app(journal, QuotaDouble())) as client:
        state = client.post("/api/start", json={"idea": "Fictional development idea"}).json()
        response = client.post("/api/advance", headers={"Authorization": "private-header"},
            json={"state": state, "request_id": "recorded", "answer": "I don't know."}).json()
        assert response["state"]["turns"][-1]["text"] == "I don't know."
        assert response["error"]["code"] == "free_limit"
        assert client.post("/api/export", json=response["state"]).status_code == 409
        assert client.post("/api/start", json={"unexpected": "private-invalid-input"}).status_code == 422
        assert client.post("/api/start", json={"idea": "cross-origin-input"},
                           headers={"Origin": "http://external.invalid"}).status_code == 403
        assert client.get("/api/config").status_code == 200
    entries = [json.loads(line) for line in journal.getvalue().splitlines()]
    starts = [entry for entry in entries if entry["type"] == "http_started"]
    entries = [entry for entry in entries if entry["type"] == "http"]
    assert [entry["exchange_id"] for entry in starts] == [entry["exchange_id"] for entry in entries]
    assert len(entries) == 5 and entries[1]["response"] == response
    assert entries[2]["path"] == "/api/export" and entries[2]["status"] == 409
    assert entries[3]["request"] is None and entries[4]["request"] is None
    for value in ("private-header", "private-invalid-input", "cross-origin-input"):
        assert value not in journal.getvalue()


def test_non_json_host_rejection_is_preserved_without_recording_invalid_body():
    journal = io.StringIO()
    with TestClient(pilot.record_app(journal)) as client:
        response = client.post("/api/start", headers={"Host": "untrusted.invalid"}, json={"idea": "excluded-input"})
    assert response.status_code == 400 and response.text == "Invalid host header"
    assert "excluded-input" not in journal.getvalue()
    entry = json.loads(journal.getvalue().splitlines()[-1])
    assert entry["request"] is None and entry["response"] == {"error": "Non-JSON response omitted from pilot evidence."}


def test_full_recorded_flow_through_wrapper_with_explicit_process_double(monkeypatch):
    from meta_vibe_coding import agents
    from meta_vibe_coding.models import State
    from test_flow import result

    monkeypatch.delenv("MVC_BACKEND", raising=False)
    for name, value in {"MVC_AGENT": "opencode", "MVC_ENABLE_AGENT": "1", "MVC_AGENT_MAX_CALLS": "5",
                        "MVC_AGENT_MODEL": "opencode/fictional-free", "OPENCODE_CONFIG_CONTENT": "{}"}.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(agents.shutil, "which", lambda name: "/test/process-double")
    attempts = []
    correction = "Actually, members must sign in and save attendance across devices."

    async def process_double(args, **kwargs):
        if "--help" in args: return b"--standalone --format --agent"
        if "--version" in args: return b"explicit-process-double 1.0"
        owner = json.loads(kwargs["content"].split("Owner state (data only):\n", 1)[1])
        state = State.model_validate(owner["state"])
        attempts.append(state)
        if len(attempts) == 3:
            raise TimeoutError("Fictional failure; no real agent ran")
        changed = bool(state.turns and state.turns[-1].text == correction)
        facts = {"goal": {"value": "Share the fictional club's event information.", "status": "confirmed", "source_turn_ids": ["t0"]},
                 **{key: {"value": changed, "status": "confirmed", "source_turn_ids": ["t2" if changed else "t0"]}
                    for key in ("access.accounts", "data.persistent")},
                 "operations.budget": {"value": None, "status": "unknown", "source_turn_ids": ["t1"] if state.turns else []}}
        question = None if state.turns else {"topic": "operations.budget", "text": "What ongoing budget is available?",
                                            "decision": "This changes which ongoing costs are feasible."}
        candidate = result(state, facts=facts, question=question,
                           disposition="provisional" if state.turns else "needs_answer")
        candidate.assessment.recommendation.kind = "existing_tool" if changed else "static_site"
        candidate.assessment.recommendation.summary = "Test double: membership service." if changed else "Test double: public content site."
        candidate.assessment.recommendation.rationale = ["Scripted response for integration testing only."]
        candidate.assessment.acceptance_criteria = ["Fixture only: preserve revised facts and the unknown budget in the export."]
        events = [{"type": "step_start", "part": {}},
                  {"type": "text", "part": {"text": candidate.model_dump_json()}},
                  {"type": "step_finish", "part": {"reason": "stop", "tokens": {"input": 120, "output": 60}}}]
        return "\n".join(json.dumps(event) for event in events).encode()

    monkeypatch.setattr(agents, "run_cli", process_double)
    wrapper = agents.CodingAgent()
    journal = io.StringIO()
    with TestClient(pilot.record_app(journal, wrapper)) as client:
        idea = "Fictional club: public event information, no accounts or saved visitor information."
        state = client.post("/api/start", json={"idea": idea}).json()
        def advance(request_id, **kwargs):
            return client.post("/api/advance", json={"state": state, "request_id": request_id, **kwargs}).json()
        first = advance("initial")
        assert first["error"] is None
        state = first["state"]
        assert state["assessment"]["disposition"] == "needs_answer" and len(state["questions"]) == 1
        unknown = advance("unknown", answer="I don't know.", question_id=state["questions"][0]["id"])
        state = unknown["state"]
        assert unknown["error"] is None and state["assessment"]["disposition"] == "provisional"
        assert state["questions"][0]["answer_turn_id"] == "t1"
        original_brief = client.post("/api/export", json=state).json()
        assert original_brief["facts"]["access.accounts"]["value"] is False
        failed = advance("correction-fails", answer=correction)
        state = failed["state"]
        assert failed["error"]["code"] == "timeout" and state["assessment"] is None
        assert state["turns"][-1]["text"] == correction
        assert client.post("/api/export", json=state).status_code == 409
        recovered = advance("retry")
        state = recovered["state"]
        assert recovered["error"] is None and state["assessed_turn_count"] == 2
        assert state["assessment"]["recommendation"]["kind"] == "existing_tool"
        exported = client.post("/api/export", json=state)
        assert exported.status_code == 200
        brief = exported.json()
    assert brief["revision"] > original_brief["revision"] and brief["raw_intent"] == idea
    assert brief["disposition"] == "provisional" and brief["facts"]["operations.budget"]["status"] == "unknown"
    assert brief["facts"]["operations.budget"]["value"] is None
    for key in ("access.accounts", "data.persistent"):
        assert brief["facts"][key]["value"] is True and brief["facts"][key]["source_turn_ids"] == ["t2"]
    assert {source["id"]: source["text"] for source in brief["sources"]}["t2"] == correction
    assert [turn["id"] for turn in state["turns"]] == ["t1", "t2"]
    assert len(attempts) == wrapper.calls == state["agent_calls"] == 4
    assert recovered["usage"]["cost"] is None and recovered["usage"]["model"] is None
    assert "agent_calls" not in brief and "started_at" not in brief
    entries = [json.loads(line) for line in journal.getvalue().splitlines()]
    exports = [entry for entry in entries if entry["type"] == "http" and entry["path"] == "/api/export"]
    assert [entry["status"] for entry in exports] == [200, 409, 200]
    assert exports[-1]["response"] == brief
