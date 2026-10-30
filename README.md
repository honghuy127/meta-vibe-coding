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
contract tests. A [Codex/Luna pilot](artifacts/2026-10-30-codex-luna-pilot.json)
verified one live initial clarification and blocked premature export. The full
conversation, recommendation quality, and owner understanding remain unverified.
Agent execution is disabled by default.

The [OpenCode pilot](artifacts/2026-10-29-opencode-free-pilot.json) and
[routing comparison](artifacts/2026-10-30-opencode-routing-verification.json)
retain failed requests. The owner reported a working terminal chat, but the
restricted wrapper still received free-limit errors; that difference is unresolved.

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

The initial live Codex check used `gpt-6-luna` with the existing native ChatGPT
login. To select that agent/model explicitly:

```sh
MVC_AGENT=codex MVC_AGENT_MODEL=gpt-6-luna MVC_ENABLE_AGENT=1 .venv/bin/python -m uvicorn meta_vibe_coding.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

Account access and usage limits still apply; this is not a free-usage guarantee.

For an OpenCode free plan, select an exact currently free model from
`opencode --standalone models` and pin `MVC_AGENT_MODEL`. OpenCode can choose
helper models separately: pin its native `title`, `summary`, and `compaction`
agents too. The dated pilot artifact records the process-local configuration used;
it leaves global settings unchanged. Free availability and quotas can change.
The wrapper reports native errors without retrying or selecting a paid route.
A free-limit response applies to that request and routing context; it does not
establish that every session on the account is blocked.

The pilot runner checks the recorded cooldown without starting an agent:

```sh
.venv/bin/python -m meta_vibe_coding.pilot
```

Before a live continuation, review native settings and [current free pricing](https://opencode.ai/v2/docs/console/models/).
Only then use the explicit confirmation flag to start the fictional pilot:

```sh
.venv/bin/python -m meta_vibe_coding.pilot --serve --free-pricing-checked
```

This reserves the remaining recorded invocations for one continuation. An ignored
claim file blocks later or concurrent launches until the attempts and any new
cooldown are reconciled in the pilot record. Claims remain after startup failures;
review the evidence before authorizing another run. A private JSONL file under
`/tmp` records source hashes and HTTP inputs/results/exports, including failures.
It contains fictional owner text; inspect it before sharing. Raw CLI events and
browser observations are not captured. Model pins do not enforce a dollar cap.
After changing the native login, `--recheck-after-login` permits an explicit retry
before the old cooldown, with the same pricing check, allowance and claim rules.
It records the reason for retrying; it does not establish renewed quota.

For a native Console workspace, export its resolved routing to a private file:

```sh
.venv/bin/python -m meta_vibe_coding.pilot --export-native-routing /tmp/mvc-native-routing.json
```

Reference it with `OPENCODE_CONFIG=/tmp/mvc-native-routing.json` when starting the
pilot. The exporter makes no inference request and copies no credentials or model
catalog. It rejects redacted values and never overwrites an existing file. Do not
replay values from `opencode debug config`: its header values are redacted.
Keep this native routing file private and regenerate it after workspace changes.

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

CLI contracts checked: OpenCode 2.0.12, 2.2.0 and 2.2.1, Claude Code 2.1.312,
Codex CLI 0.165.0.
Help/version inspection and mocked events do not establish live compatibility.
The Codex pilot verifies only the initial planning response. Its exact disabled
Code Mode host startup notice is accepted; other errors and tool activity still fail.
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
