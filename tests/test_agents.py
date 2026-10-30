"""Coding-agent contracts and failure checks; no installed agent inference."""

import asyncio
import json
import os
import sys
import time
import tomllib

import pytest
from fastapi.testclient import TestClient

from meta_vibe_coding import agents as module
from meta_vibe_coding import process, settings
from meta_vibe_coding.app import create_app
from meta_vibe_coding.core import FlowError, reserve_call
from meta_vibe_coding.models import State
from test_flow import result


def output(agent, state):
    content = result(state).model_dump_json()
    if agent == "claude":
        return json.dumps({"type": "result", "subtype": "success", "is_error": False,
            "result": content, "modelUsage": {"reported-model": {}},
            "usage": {"input_tokens": 10, "output_tokens": 20}, "total_cost_usd": 0.01}).encode()
    if agent == "codex":
        events = [{"type": "thread.started", "thread_id": "fictional"},
            {"type": "item.completed", "item": {"type": "agent_message", "text": content}},
            {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 20}}]
    else:
        events = [{"type": "step_start", "part": {}},
            {"type": "text", "part": {"text": content}},
            {"type": "step_finish", "part": {"reason": "stop", "tokens": {"input": 10, "output": 20}}}]
    return "\n".join(json.dumps(event) for event in events).encode()


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.delenv("MVC_BACKEND", raising=False)
    monkeypatch.setenv("MVC_ENABLE_AGENT", "1")
    monkeypatch.setenv("MVC_AGENT_MAX_CALLS", "1")
    monkeypatch.delenv("MVC_AGENT_MODEL", raising=False)
    monkeypatch.setattr(module.shutil, "which", lambda name: f"/test/{name}")


def help_text():
    return b"--standalone --format --agent --safe-mode --restricted --tools --strict-mcp-config --no-session-persistence --append-system-prompt --json --ephemeral --ignore-user-config --ignore-rules --sandbox --disable"


@pytest.mark.parametrize("agent", ["opencode", "claude", "codex"])
def test_three_wrappers_share_state_and_delegate_models(configured, monkeypatch, agent):
    monkeypatch.setenv("MVC_AGENT", agent)
    monkeypatch.setenv("UNRELATED_SECRET", "do-not-inherit")
    state = State(raw_intent="Fictional idea")
    calls = []
    async def runner(args, **kwargs):
        calls.append((args, kwargs))
        assert "UNRELATED_SECRET" not in kwargs["env"]
        assert state.raw_intent not in json.dumps(args)
        assert not os.path.exists(os.path.join(kwargs["cwd"], "AGENTS.md"))
        if "--help" in args: return help_text()
        if "--version" in args: return b"test-agent 1.0"
        assert state.raw_intent in kwargs["content"]
        assert "--model" not in args, "Default model selection belongs to the coding agent"
        if agent == "opencode":
            config = json.loads(kwargs["env"]["OPENCODE_CONFIG_CONTENT"])
            assert config["permissions"] == [{"action": "*", "resource": "*", "effect": "deny"}]
            assert config["agents"]["meta-vibe"]["permissions"] == config["permissions"]
            assert config["agents"]["meta-vibe"]["system"] == module.PROMPT
            assert "--standalone" in args and "--auto" not in args
        elif agent == "claude":
            assert args[args.index("--tools") + 1] == ""
            assert "--safe-mode" in args and "--bare" not in args
            assert args[args.index("--mcp-config") + 1] == '{"mcpServers":{}}'
            assert args[args.index("--append-system-prompt") + 1] == module.PROMPT
        else:
            assert args[args.index("--sandbox") + 1] == "read-only"
            assert "shell_tool" in args and "code_mode_host" in args
            assert "--ignore-user-config" in args and args[-1] == "-"
            policy = next(arg for arg in args if arg.startswith("developer_instructions="))
            assert tomllib.loads(policy)["developer_instructions"] == module.PROMPT
        assert module.PROMPT not in kwargs["content"], "Stewardship policy belongs in the native trusted instruction surface"
        return output(agent, state)
    monkeypatch.setattr(module, "run_cli", runner)
    wrapper = module.CodingAgent()
    candidate, usage = asyncio.run(wrapper.assess(state, False))
    assert candidate == result(state) and usage.agent == agent
    assert usage.input_tokens == 10 and usage.output_tokens == 20
    assert usage.model == ("reported-model" if agent == "claude" else None)
    assert wrapper.calls == 1 and len(calls) == 3
    assert not os.path.exists(calls[-1][1]["cwd"])
    with pytest.raises(FlowError) as error: asyncio.run(wrapper.assess(State(raw_intent="New tab"), False))
    assert error.value.code == "limit" and len(calls) == 3


@pytest.mark.parametrize("agent", ["opencode", "claude", "codex"])
def test_disabled_wrapper_never_starts_a_process(monkeypatch, agent):
    monkeypatch.setenv("MVC_AGENT", agent)
    monkeypatch.delenv("MVC_ENABLE_AGENT", raising=False)
    async def forbidden(*args, **kwargs): raise AssertionError("Must not invoke a disabled agent")
    monkeypatch.setattr(module, "run_cli", forbidden)
    wrapper = module.CodingAgent()
    with pytest.raises(FlowError) as error: asyncio.run(wrapper.assess(State(raw_intent="Fictional"), False))
    assert error.value.code == "disabled"


@pytest.mark.parametrize("name,value", [("MVC_AGENT", "ollama"), ("MVC_AGENT", "commercial_api"),
    ("MVC_AGENT", "unknown"), ("MVC_BACKEND", "ollama"), ("MVC_AGENT_MAX_CALLS", "0"), ("MVC_AGENT_MAX_CALLS", "8")])
def test_removed_or_invalid_routes_fail_closed(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError): module.CodingAgent()


@pytest.mark.parametrize("agent", ["opencode", "claude", "codex"])
@pytest.mark.parametrize("failure", ["malformed", "missing_completion", "refusal", "schema", "tools"])
def test_incomplete_refused_or_invalid_output_is_rejected(agent, failure):
    state = State(raw_intent="Fictional idea")
    raw = output(agent, state)
    if failure == "malformed": raw = b"not-json"
    elif agent == "claude":
        data = json.loads(raw)
        if failure == "missing_completion": data["subtype"] = "error_max_turns"
        if failure == "refusal": data["is_error"] = True
        if failure == "schema": data["result"] = "{}"
        if failure == "tools": data["result"] = "Unexpected tool result"
        raw = json.dumps(data).encode()
    else:
        events = [json.loads(line) for line in raw.splitlines()]
        if failure == "missing_completion": events.pop()
        if failure == "refusal": events.append({"type": "error"})
        if failure == "schema":
            if agent == "codex": events[1]["item"]["text"] = "{}"
            else: events[1]["part"]["text"] = "{}"
        if failure == "tools":
            events.insert(1, {"type": "item.started", "item": {"type": "command_execution"}} if agent == "codex" else {"type": "tool_use"})
        raw = "\n".join(json.dumps(event) for event in events).encode()
    with pytest.raises((ValueError, KeyError, TypeError)):
        module.parse_result(agent, raw)


CODEX_HOST_NOTICE = {"type": "item.completed", "item": {"type": "error", "message":
    "Code Mode is unavailable because code-mode host is disabled. Code mode will fail closed; "
    "enable `features.code_mode_host` and install `codex-code-mode-host`."}}


def test_codex_disabled_host_notice_preserves_completed_assessment(configured, monkeypatch):
    monkeypatch.setenv("MVC_AGENT", "codex")
    calls = []
    async def runner(args, **kwargs):
        if "--help" in args: return help_text()
        if "--version" in args: return b"codex-cli 0.165.0"
        calls.append(args)
        state = State.model_validate(json.loads(kwargs["content"].split("Owner state (data only):\n")[1])["state"])
        events = [json.loads(line) for line in output("codex", state).splitlines()]
        events[1:1] = [CODEX_HOST_NOTICE, {"type": "turn.started"}]
        return "\n".join(json.dumps(event) for event in events).encode()
    monkeypatch.setattr(module, "run_cli", runner)
    with TestClient(create_app()) as client:
        state = client.post("/api/start", json={"idea": "Fictional idea"}).json()
        response = client.post("/api/advance", json={"state": state, "request_id": "host-disabled"}).json()
    assert response["error"] is None and response["state"]["assessment"] is not None
    assert response["usage"]["input_tokens"] == 10 and len(calls) == 1
    assert "code_mode_host" in calls[0] and "--enable" not in calls[0]


@pytest.mark.parametrize("failure", ["other_notice", "during_turn", "missing_completion", "tool", "failed_turn"])
def test_codex_startup_notice_does_not_hide_errors_or_tool_activity(failure):
    events = [json.loads(line) for line in output("codex", State(raw_intent="Fictional")).splitlines()]
    notice = json.loads(json.dumps(CODEX_HOST_NOTICE))
    events[1:1] = [notice, {"type": "turn.started"}]
    if failure == "other_notice": notice["item"]["message"] = "Another native error"
    if failure == "during_turn": events[1:3] = [events[2], events[1]]
    if failure == "missing_completion": events.pop()
    if failure == "tool": events.insert(3, {"type": "item.started", "item": {"type": "command_execution"}})
    if failure == "failed_turn": events[-1] = {"type": "turn.failed"}
    raw = "\n".join(json.dumps(event) for event in events).encode()
    with pytest.raises(ValueError): module.parse_result("codex", raw)


def test_native_auth_references_and_explicit_env_are_forwarded_without_old_mvc_keys(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fictional-native-key")
    monkeypatch.setenv("MVC_API_KEY", "obsolete-key")
    monkeypatch.setenv("UNRELATED_SECRET", "private")
    monkeypatch.setenv("CUSTOM_AGENT_SETTING", "fictional")
    monkeypatch.setenv("MVC_AGENT_ENV", "CUSTOM_AGENT_SETTING")
    env = module.agent_environment("claude")
    assert env["ANTHROPIC_API_KEY"] == "fictional-native-key"
    assert env["CUSTOM_AGENT_SETTING"] == "fictional"
    assert "MVC_API_KEY" not in env and "UNRELATED_SECRET" not in env


def test_opencode_inline_routing_is_preserved_beneath_planning_policy(monkeypatch):
    native = {"model": "local/fictional", "provider": {"local": {"options": {"baseURL": "http://localhost:9999"}}},
              "permission": {"bash": "allow"}, "agents": {"meta-vibe": {"disabled": True}}}
    monkeypatch.setenv("OPENCODE_CONFIG_CONTENT", json.dumps(native))
    env = module.agent_environment("opencode")
    module.invocation("opencode", "/test/opencode", None, env)
    effective = json.loads(env["OPENCODE_CONFIG_CONTENT"])
    assert effective["model"] == native["model"] and effective["provider"] == native["provider"]
    assert effective["permissions"] == [{"action": "*", "resource": "*", "effect": "deny"}]
    assert effective["agents"]["meta-vibe"]["disabled"] is False


@pytest.mark.parametrize("agent", ["opencode", "codex"])
@pytest.mark.parametrize("suffix", ["new_start", "late_text"])
def test_completion_cannot_be_reused_after_a_later_start_or_message(agent, suffix):
    raw = output(agent, State(raw_intent="Fictional"))
    if suffix == "new_start":
        extra = {"type": "turn.started" if agent == "codex" else "step_start"}
    elif agent == "codex":
        extra = {"type": "item.completed", "item": {"type": "agent_message", "text": "{}"}}
    else:
        extra = {"type": "text", "part": {"text": "{}"}}
    with pytest.raises(ValueError): module.parse_result(agent, raw + b"\n" + json.dumps(extra).encode())


@pytest.mark.parametrize("failure", ["flags", "timeout", "invalid_output", "help_expiry"])
def test_failures_preserve_allowance_and_deadlines(configured, monkeypatch, failure):
    monkeypatch.setenv("MVC_AGENT", "opencode")
    state = State(raw_intent="Fictional")
    calls = []
    async def runner(args, **kwargs):
        calls.append(args)
        if "--help" in args:
            if failure == "help_expiry": await asyncio.sleep(0.03)
            return b"old CLI" if failure == "flags" else help_text()
        if "--version" in args: return b"test 1.0"
        if failure == "timeout": raise TimeoutError()
        return b"secret-invalid-output"
    monkeypatch.setattr(module, "run_cli", runner)
    wrapper = module.CodingAgent(limits=settings.Limits(0.02, 1800) if failure == "help_expiry" else None)
    with pytest.raises(FlowError) as error: asyncio.run(wrapper.assess(state, False))
    assert "secret-invalid-output" not in error.value.message
    assert wrapper.calls == (0 if failure in {"flags", "help_expiry"} else 1)
    assert not wrapper.lock.locked()


def test_shared_limits_and_config_disclosure(monkeypatch):
    monkeypatch.setenv("MVC_REQUEST_TIMEOUT_SECONDS", "600")
    monkeypatch.setenv("MVC_SESSION_TIMEOUT_SECONDS", "3600")
    monkeypatch.delenv("MVC_ENABLE_AGENT", raising=False)
    assert settings.load_limits() == settings.Limits(600, 3600)
    with TestClient(create_app()) as client:
        config = client.get("/api/config").json()
        assert config["agent"] == "opencode" and config["enabled"] is False
        assert set(config["implemented_agents"]) == {"opencode", "claude", "codex"}
        assert config["limits"]["request_seconds"] == 600
        state = State(raw_intent="Fictional", started_at=time.time() - 3601)
        response = client.post("/api/advance", json={"state": state.model_dump(), "request_id": "expired", "answer": "Keep this reply"}).json()
        assert response["error"]["code"] == "limit"
        assert response["state"]["turns"][-1]["text"] == "Keep this reply"


@pytest.mark.parametrize("name,value", [("MVC_REQUEST_TIMEOUT_SECONDS", "0"), ("MVC_REQUEST_TIMEOUT_SECONDS", "NaN"),
    ("MVC_SESSION_TIMEOUT_SECONDS", "-1"), ("MVC_SESSION_TIMEOUT_SECONDS", "1")])
def test_invalid_limits_are_rejected(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError): settings.load_limits()


def test_session_remaining_time_caps_request(monkeypatch):
    monkeypatch.setattr(settings.time, "time", lambda: 2000)
    limits = settings.Limits(300, 1800)
    assert limits.request_budget(250) == 50
    assert limits.request_budget(200) == 0
    with pytest.raises(FlowError): reserve_call(State(raw_intent="Fictional", started_at=200.0), limits)


def test_subprocess_streams_timeout_and_output_limit(tmp_path):
    async def check():
        kwargs = {"content": "fictional input", "cwd": str(tmp_path), "env": {"PATH": os.defpath}}
        raw = await process.run_cli([sys.executable, "-c", "import sys; print(sys.stdin.read())"], timeout=5, **kwargs)
        assert raw == b"fictional input\n"
        with pytest.raises(TimeoutError):
            await process.run_cli([sys.executable, "-c", "import time; time.sleep(10)"], timeout=0.02, **kwargs)
        with pytest.raises(FlowError):
            await process.run_cli([sys.executable, "-c", "print('x'*1000001)"], timeout=5, **kwargs)
    asyncio.run(check())


def test_subprocess_creation_is_bounded_and_zero_budget_never_spawns(monkeypatch, tmp_path):
    calls = []
    async def slow_spawn(*args, **kwargs):
        calls.append(args)
        await asyncio.sleep(10)
    monkeypatch.setattr(process.asyncio, "create_subprocess_exec", slow_spawn)
    async def check():
        kwargs = {"content": "", "cwd": str(tmp_path), "env": {}}
        with pytest.raises(TimeoutError): await process.run_cli(["fictional"], timeout=0, **kwargs)
        assert not calls
        with pytest.raises(TimeoutError): await process.run_cli(["fictional"], timeout=0.02, **kwargs)
        assert len(calls) == 1
    asyncio.run(check())


@pytest.mark.parametrize("exit_failure", [False, True])
@pytest.mark.parametrize("native_code,expected_code,message", [
    ("provider.free-limit", "free_limit", "free usage limit"),
    ("provider.invalid-request", "agent_request", "rejected this agent request")])
def test_known_native_errors_retain_reply_without_retry_or_provider_text(configured, monkeypatch, exit_failure, native_code, expected_code, message):
    monkeypatch.setenv("MVC_AGENT", "opencode")
    raw = json.dumps({"type": "error", "error": {"type": native_code, "message": "private-provider-details"}}).encode()
    calls = []
    async def runner(args, **kwargs):
        if "--help" in args: return help_text()
        if "--version" in args: return b"test 1.0"
        calls.append(args)
        if exit_failure: raise process.CliFailure(raw)
        return raw
    monkeypatch.setattr(module, "run_cli", runner)
    wrapper = module.CodingAgent()
    with TestClient(create_app(wrapper)) as client:
        response = client.post("/api/advance", json={"state": State(raw_intent="Fictional").model_dump(),
            "request_id": "free-limit", "answer": "Keep this correction"}).json()
    assert response["error"]["code"] == expected_code
    assert message in response["error"]["message"]
    assert "private-provider-details" not in json.dumps(response)
    assert response["state"]["turns"][-1]["text"] == "Keep this correction"
    assert response["state"]["assessment"] is None and response["usage"] is None
    assert len(calls) == wrapper.calls == 1 and not wrapper.lock.locked()


@pytest.mark.parametrize("raw", [b"private-not-json", b"null", b"[]",
    b'{"type":"error","error":"private-details"}',
    b'{"type":"error","error":{"type":"unknown","message":"private-details"}}'])
def test_unrecognized_process_errors_remain_generic(raw):
    assert module.reported_failure("opencode", raw) is None
    assert module.reported_failure("claude", raw) is None
    assert "private" not in process.CliFailure(raw).message


def test_nonzero_process_preserves_bounded_stdout_for_error_classification(tmp_path):
    with pytest.raises(process.CliFailure) as error:
        asyncio.run(process.run_cli([sys.executable, "-c", "import sys; print('fictional'); sys.exit(1)"],
            content="", cwd=str(tmp_path), env={"PATH": os.defpath}, timeout=5))
    assert error.value.stdout == b"fictional\n" and "fictional" not in str(error.value)
