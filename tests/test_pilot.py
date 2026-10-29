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
