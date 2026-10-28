# Meta Vibe Coding

Meta Vibe Coding wraps a coding agent to help non-experts decide what software
they need, understand the consequences, and prepare a useful handoff. It can
recommend an existing tool or advise against building. The goal is a working
solution for general vibe coding, not a paper or a Kanji-specific product.

**Architecture:** owner → stewardship and shared state → OpenCode, Claude Code,
or Codex → the agent's model provider. This repository does not run inference,
manage model servers, or call model APIs directly. A local model is an option
only through a configured coding agent, such as OpenCode.

**Current state:** a Level 0 web prototype with clarification, corrections, owner
and developer views, and JSON export. All three CLI wrappers have deterministic
contract tests; live agent compatibility, recommendation quality, and owner
understanding remain unverified. Agent execution is disabled by default.

## Run the prototype

Use Python 3.12 and install/configure at least one supported coding agent through
its own tooling. The lockfile captures the checked Python dependencies on macOS.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m uvicorn meta_vibe_coding.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

Open <http://127.0.0.1:8000>. Without enabling an agent, the page shows setup status
and sends no ideas. Once its account, data destination, permissions, and spending
controls are agreed, restart with `MVC_AGENT=opencode`, `claude`, or `codex` and
`MVC_ENABLE_AGENT=1`. These settings select one agent; there is no fallback.
Configure authentication through that agent, not application-specific API keys.
No live agent request was made as part of the wrapper rewrite.

| Variable | Meaning |
| --- | --- |
| `MVC_AGENT` | `opencode` (default), `claude`, or `codex`. |
| `MVC_ENABLE_AGENT` | Set to `1` only when agent execution is authorized. |
| `MVC_AGENT_MODEL` | Optional native model selector forwarded to the agent's `--model` flag. No model download or provider call is made by this app. |
| `MVC_AGENT_ENV` | Optional comma-separated names of extra native configuration/auth environment variables to forward. Values are never written to the repo. |
| `MVC_AGENT_MAX_CALLS` | Maximum top-level agent invocations per server run, 1–7; default 7. |
| `MVC_REQUEST_TIMEOUT_SECONDS` | Request deadline including CLI startup; default 300. |
| `MVC_SESSION_TIMEOUT_SECONDS` | Whole interaction limit; default 1,800, at least the request deadline. |

The app forwards normal authentication/config references for the selected agent.
For extra providers or organization-specific settings, explicitly forward the
required native environment names. Removed `MVC_BACKEND` settings fail startup
instead of silently selecting another route. Old `MVC_API_*` and local-model
settings have no supported execution path.

## Agent boundaries

Each request uses a fresh temporary working directory, passes the state through
stdin, bounds output, and validates the final JSON against the same contract.
Stewardship policy uses each agent’s native system/developer instruction surface;
owner text stays in the data input. The wrapper stops the process group at the
deadline and never resumes another
session, auto-retries, or switches agents. Five questions and seven assessment request
attempts are allowed per idea. Internal model calls/retries are separate and
may not be reported; unknown token usage or cost stays unknown.

| Agent | Planning boundary and configuration |
| --- | --- |
| OpenCode | Private `--standalone` process, JSON events, custom planning agent with v2 deny-all permission rules. Native inline/provider settings are preserved beneath the planning policy. Local inference is configured in OpenCode, outside this repo. |
| Claude Code | Safe/restricted mode, no built-in tools or MCP servers, no slash commands, and no saved session. Safe mode preserves native authentication rather than requiring wrapper-owned API credentials. |
| Codex | Read-only sandbox, command/browser/extension features disabled, no saved session, user config/rules ignored. Saved authentication is reused; model selection uses the native default or explicit `MVC_AGENT_MODEL`. Custom provider profiles are not currently preserved by this restricted wrapper. |

These flags constrain model actions; they are not an OS isolation guarantee.
Installed agent code and operator-managed configuration remain trusted. OpenCode
can load native plugins/MCP during startup and persist sessions; managed policy can
override permissions. Claude managed hooks may still run. Review these native
settings before live or private-data use. This app's in-tab state does not control
agent/provider retention. Invocation counts and time limits are not dollar caps;
use the selected agent/provider's spending controls before enabling calls.

CLI contracts checked: OpenCode 2.0.12, Claude Code 2.1.312, Codex CLI 0.165.0.
Help/version inspection and mocked events do not establish live compatibility.
References: [OpenCode CLI](https://opencode.ai/v2/docs/cli/),
[permissions](https://opencode.ai/v2/docs/permissions/),
[Claude CLI](https://code.claude.com/docs/en/cli-reference),
[Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).

## Check and review

```sh
.venv/bin/python -m pytest -q
node --test tests/test_ui.cjs
.venv/bin/python -m pip check
```

Checks use agent/process doubles and small local subprocesses, without inference.
Subprocess checks need permission to launch and terminate their process groups.
They cover contract validation, revised answers, recovery, limits, and stale
responses. They cannot judge recommendation quality or owner understanding.
The [frozen acceptance cases](artifacts/l0-acceptance-cases.json) remain unrun.
Earlier direct-model experiments are retained under `artifacts/legacy/`; they are
historical evidence, not acceptance of the current agent wrappers. Their Git
SHAs identify the design baseline; the prior uncommitted implementation snapshots
are not retained, so those attempts cannot be replayed exactly from this checkout.

The app keeps state in the current tab. Reloading or starting a new idea clears
it. Failed requests retain replies, mark older results outdated, and disable stale
exports. Review the JSON before downloading: referenced owner text is included.
Provisional briefs retain unresolved decisions and are not ready to implement.

## Repository guide

| Purpose | Source |
| --- | --- |
| Product vision and delivery path | [Proposal](docs/meta-vibe-coding-proposal.md) |
| Level 0 contract and acceptance | [Level 0](docs/level-0.md) |
| Current tasks and evidence | [Work board](docs/work-board.md) |
| Human/agent workflow, code, filename, and directory conventions | [Contributing](CONTRIBUTING.md) |
| Shared coding-agent instructions | [AGENTS.md](AGENTS.md) |
| Natural writing and documentation size | [Writing guide](docs/writing-guide.md) |
| Architecture choices | [Decisions](docs/decisions.md) |

Source lives in `src/meta_vibe_coding/`, checks in `tests/`, and useful recorded
evidence in `artifacts/`. Prefer these existing locations over new folders or
routine handoff documents. Multiple contributors can build the repository without
adding multi-agent orchestration to the Level 0 product.
