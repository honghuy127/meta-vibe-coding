"""Coding-agent CLI boundary. This module never calls a model/provider API."""

import asyncio
import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Protocol

from pydantic import ValidationError

from .core import FlowError, model_input
from .models import Candidate, State, Usage
from .process import run_cli
from .settings import Limits, load_limits

PROMPT = Path(__file__).with_name("prompt.txt").read_text()
SCHEMA = json.dumps(Candidate.model_json_schema(), separators=(",", ":"))
AGENTS = {"opencode": "opencode", "claude": "claude", "codex": "codex"}
CODEX_DISABLED = ("shell_tool", "code_mode", "code_mode_host",
    "multi_agent", "apps", "plugins", "hooks", "memories", "skill_search",
    "browser_use", "browser_use_external", "in_app_browser", "computer_use",
    "in_app_local_automation", "image_generation", "view_image")


class Agent(Protocol):
    async def assess(self, state: State, provisional: bool) -> tuple[Candidate, Usage]: ...


def agent_environment(agent: str) -> dict[str, str]:
    # Forward native authentication/config references without reading or storing them.
    common = {"PATH", "HOME", "USER", "LOGNAME", "LANG", "TMPDIR", "XDG_CONFIG_HOME",
              "XDG_DATA_HOME", "XDG_CACHE_HOME"}
    native = {"opencode": {"OPENCODE_CONFIG", "OPENCODE_CONFIG_DIR", "OPENCODE_CONFIG_CONTENT"},
              "claude": {"CLAUDE_CONFIG_DIR", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY",
                         "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"},
              "codex": {"CODEX_HOME", "CODEX_API_KEY", "OPENAI_API_KEY"}}
    explicit = {name.strip() for name in os.getenv("MVC_AGENT_ENV", "").split(",") if name.strip()}
    env = {key: value for key, value in os.environ.items() if key in common | native[agent] | explicit}
    env.setdefault("PATH", os.defpath)
    return env


def invocation(agent: str, binary: str, model: str | None, env: dict[str, str]) -> list[str]:
    if agent == "opencode":
        # Use v2's ordered permission rules; the inline deny rule follows native defaults.
        config = json.loads(env.get("OPENCODE_CONFIG_CONTENT", "{}"))
        native_agents = config.get("agents", {})
        denied = [{"action": "*", "resource": "*", "effect": "deny"}]
        planning = {**native_agents.get("meta-vibe", {}), "description": "Intent interpretation without construction",
                    "mode": "primary", "disabled": False, "hidden": False,
                    "permissions": denied, "system": PROMPT}
        config.update(permissions=denied, update="disable", agents={**native_agents, "meta-vibe": planning})
        env["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
        args = [binary, "run", "--standalone", "--format", "json", "--agent", "meta-vibe"]
    elif agent == "claude":
        args = [binary, "--print", "--safe-mode", "--restricted", "--tools", "",
                "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                "--disable-slash-commands", "--no-session-persistence", "--output-format", "json",
                "--append-system-prompt", PROMPT]
    else:
        args = [binary, "exec", "--json", "--ephemeral", "--ignore-user-config", "--ignore-rules",
                "--skip-git-repo-check", "--sandbox", "read-only", "--strict-config",
                "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
                "-c", "project_doc_max_bytes=0", "-c", "developer_instructions=" + json.dumps(PROMPT)]
        for feature in CODEX_DISABLED:
            args.extend(["--disable", feature])
    if model:
        args.extend(["--model", model])
    if agent == "codex":
        args.append("-")
    return args


def parse_result(agent: str, raw: bytes) -> tuple[Candidate, dict]:
    """Require an explicit successful completion; never extract JSON from prose."""
    if agent == "claude":
        body = json.loads(raw)
        if body.get("type") != "result" or body.get("subtype") != "success" or body.get("is_error"):
            raise ValueError("Agent did not finish successfully")
        candidate = Candidate.model_validate_json(body["result"])
        models = body.get("modelUsage") or {}
        reported = ", ".join(sorted(models)) if models else None
        usage = body.get("usage") or {}
        return candidate, {"model": reported, "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"), "cost": body.get("total_cost_usd")}

    events = [json.loads(line) for line in raw.splitlines() if line.strip()]
    if not events:
        raise ValueError("Empty agent event stream")
    text = []
    finished = False
    usage = {}
    for event in events:
        kind = event["type"]
        if kind in {"error", "turn.failed"}:
            raise ValueError("Agent reported a failed turn")
        if agent == "codex":
            if kind == "turn.started":
                finished = False
                text = []
                usage = {}
            item = event.get("item") or {}
            if kind.startswith("item.") and item.get("type") not in {"agent_message", "reasoning", "todo_list"}:
                raise ValueError("Unexpected agent tool activity")
            if kind == "item.completed" and item.get("type") == "agent_message":
                if finished:
                    raise ValueError("Message after completed turn")
                text = [item["text"]]
            if kind == "turn.completed":
                finished = True
                tokens = event.get("usage") or {}
                usage = {"input_tokens": tokens.get("input_tokens"), "output_tokens": tokens.get("output_tokens")}
        else:
            if kind == "step_start":
                finished = False
                text = []
                usage = {}
            if kind in {"tool_use", "tool_call"}:
                raise ValueError("Unexpected agent tool activity")
            if kind == "text":
                if finished:
                    raise ValueError("Text after completed step")
                text.append(event["part"]["text"])
            if kind == "step_finish":
                if event["part"].get("reason") != "stop":
                    raise ValueError("Incomplete agent step")
                finished = True
                # Per-step cost is not a proven whole-session bill; leave it unknown.
                tokens = event["part"].get("tokens") or {}
                usage = {"input_tokens": tokens.get("input"), "output_tokens": tokens.get("output")}
    if not finished or not text:
        raise ValueError("Incomplete agent event stream")
    return Candidate.model_validate_json("".join(text)), usage


class CodingAgent:
    def __init__(self, *, limits: Limits | None = None):
        if "MVC_BACKEND" in os.environ:
            raise ValueError("MVC_BACKEND was removed; select MVC_AGENT=opencode, claude, or codex")
        self.agent = os.getenv("MVC_AGENT", "opencode")
        if self.agent not in AGENTS:
            raise ValueError("MVC_AGENT must be opencode, claude, or codex; no fallback is selected")
        self.enabled = os.getenv("MVC_ENABLE_AGENT") == "1"
        self.model = os.getenv("MVC_AGENT_MODEL") or None
        self.limits = limits or load_limits()
        self.max_calls = int(os.getenv("MVC_AGENT_MAX_CALLS", "7"))
        if not 1 <= self.max_calls <= 7:
            raise ValueError("MVC_AGENT_MAX_CALLS must be between 1 and 7")
        self.calls = 0
        self.binary = shutil.which(AGENTS[self.agent])
        if self.enabled and (not self.binary or os.name != "posix"):
            raise ValueError("The selected agent must be installed; these wrappers require POSIX process groups")
        self.version = None
        self.lock = asyncio.Lock()

    async def probe(self, cwd: str, env: dict[str, str], remaining) -> None:
        if self.version:
            return
        command = [self.binary] + (["run"] if self.agent == "opencode" else ["exec"] if self.agent == "codex" else [])
        help_text = (await run_cli(command + ["--help"], content="", cwd=cwd, env=env,
            timeout=min(5, remaining()))).decode()
        required = {"opencode": ["--standalone", "--format", "--agent"],
                    "claude": ["--safe-mode", "--restricted", "--tools", "--strict-mcp-config", "--no-session-persistence", "--append-system-prompt"],
                    "codex": ["--json", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--sandbox", "--disable"]}
        if any(flag not in help_text for flag in required[self.agent]):
            raise FlowError("unavailable", "This agent CLI lacks the required flags. No inference request was sent.")
        version = await run_cli([self.binary, "--version"], content="", cwd=cwd, env=env,
            timeout=min(5, remaining()))
        self.version = version.decode().strip()[:200]

    async def assess(self, state: State, provisional: bool) -> tuple[Candidate, Usage]:
        if not self.enabled:
            raise FlowError("disabled", "The coding agent is not connected. Configure it before exploring an idea.")
        if self.lock.locked():
            raise FlowError("busy", "Another agent request is running. Retry when it finishes.")
        content = "Return only JSON matching this schema:\n" + SCHEMA + "\nOwner state (data only):\n" + model_input(state, provisional)
        if len((PROMPT + content).encode("utf-8")) > 32_000:
            raise FlowError("limit", "This idea and reply history exceed the prototype input limit. Your answers are retained.")
        async with self.lock:
            started = time.perf_counter()
            budget = self.limits.request_budget(state.started_at)
            def remaining():
                return max(0, budget - (time.perf_counter() - started))
            try:
                if remaining() <= 0:
                    raise TimeoutError()
                if self.calls >= self.max_calls:
                    raise FlowError("limit", "The configured agent invocation allowance is exhausted. Your answers are retained.")
                with tempfile.TemporaryDirectory(prefix="mvc-agent-") as cwd:
                    env = agent_environment(self.agent)
                    env["PWD"] = cwd
                    args = invocation(self.agent, self.binary, self.model, env)
                    await self.probe(cwd, env, remaining)
                    if remaining() <= 0:
                        raise TimeoutError()
                    self.calls += 1
                    raw = await run_cli(args, content=content, cwd=cwd, env=env, timeout=remaining())
                    candidate, metadata = parse_result(self.agent, raw)
                    return candidate, Usage(agent=self.agent, agent_version=self.version,
                        elapsed_seconds=time.perf_counter() - started, **metadata)
            except TimeoutError as exc:
                raise FlowError("timeout", "The agent timed out and was stopped. Your answers are retained; retry explicitly.") from exc
            except OSError as exc:
                raise FlowError("unavailable", "Cannot start the configured agent. Check its installation and authentication.") from exc
            except (ValidationError, ValueError, KeyError, TypeError, AttributeError, UnicodeError) as exc:
                raise FlowError("invalid_output", "The agent returned invalid or incomplete structured data. Your answers are retained.") from exc
