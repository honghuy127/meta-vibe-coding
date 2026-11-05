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
contract tests. A [four-call Codex/Luna browser check](artifacts/2026-10-30-codex-luna-known-state.json)
verified goal display, retained explicit unknowns, distinct public/private data
requirements and a provisional export. New questions require unknown or assumed
fact targets; a retained “I don’t know” declaration prevents another question for
the same key. Quoted sources prove presence, not meaning; aliases remain a semantic
limitation.
The [seven-pair acceptance run](artifacts/2026-10-30-codex-luna-acceptance.json)
used 33 of 98 authorized native calls. One provisional wrapper case passed;
eleven attempts stopped technically and two completed outputs missed substantive
requirements. Level 0 is not accepted, no comparative advantage is established,
and owner understanding remains untested.
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

The live Codex development checks used `gpt-6-luna` with the existing native ChatGPT
login. To select that agent/model explicitly:

```sh
MVC_AGENT=codex MVC_AGENT_MODEL=gpt-6-luna MVC_ENABLE_AGENT=1 .venv/bin/python -m uvicorn meta_vibe_coding.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

Account access and usage limits still apply; this is not a free-usage guarantee.
After an update, reload the page and start a new idea to use the current runtime
contract. Older in-flight clients are not automatically migrated; exported briefs
still use schema version 1.

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
stdin, bounds output, and validates the final JSON through one native response
contract before applying the state guards. Native contract 3 returns fact updates
with attached evidence and questions referring to fact keys. The wrapper carries
untouched facts forward and derives source citations and explicit-unknown markers
from the evidence. Confirmed updates need exact owner quotes. Quotes establish source presence,
not semantic support or complete extraction. Native contract 3 also requires explicit
accounting for changed prior assessment list items: a rewrite points to replacements,
an owner update quotes new input, and withdrawn agent advice needs a reason. Missing
or invalid accounting blocks adoption. Unambiguous shorthand for the three
recommendation list fields and valid records for unchanged items are accepted;
[D021](docs/decisions.md#d021-tolerate-unambiguous-continuity-references-and-surface-sharing-authority)
keeps reference/evidence checks while reducing syntax friction. Prompt guidance
also asks about represented people and unresolved sharing authority when relevant.
These instructions require live semantic review. Accounting does not validate
preserved meaning or the justification for withdrawing advice, and it does not cover scalar summaries,
recommendation kind or risk level. State and export schema remain 1; see
[D018](docs/decisions.md#d018-account-explicitly-for-changed-assessment-items).
Native contract 2 responses from older sessions are rejected; reload and start a
new idea after updating. Historical results are unchanged.
Pending runtime state retains one previous assessment for the agent to reconsider
earlier caveats. It is stale context, never owner evidence or an exportable result,
and clears after successful adoption. Failed requests retain it for explicit retry,
including a lost browser response. It counts toward the unchanged 32 KB input cap;
oversized input stops before CLI startup. Prompt guidance asks the agent to label
proposed policies wherever used and cite retained parts of revised aggregate facts.
These instructions do not validate prose meaning or establish complete correction;
see [D012](docs/decisions.md#d012-retain-one-stale-assessment-for-reconsideration).
Settled question targets fail before adoption, even when a provisional request
would suppress the question. Older mismatched questions remain readable, but the
unknown action cannot replace their settled facts. Correction guidance asks the
agent to update superseded values at existing keys and record new requirements
separately from advice; semantic omissions remain undetected by these guards.
See [D013](docs/decisions.md#d013-ask-only-about-unresolved-properties).
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
2.1.316 and 2.1.317, Codex CLI 0.165.0 and 0.166.0.
Help/version inspection and mocked events do not establish live compatibility.
Codex development checks do not establish product acceptance. Its exact
disabled Code Mode host startup notice is accepted; other errors and tool activity
still fail.
References: [OpenCode CLI](https://opencode.ai/v2/docs/cli/),
[permissions](https://opencode.ai/v2/docs/permissions/),
[Claude CLI](https://code.claude.com/docs/en/cli-reference),
[Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).

Codex receives a private, request-owned `response-schema.json` through its native
`--output-schema` option, with identical schema content in stdin. This file is
wrapper input, not agent-created output. Claude Code receives the same schema text
through native `--json-schema`. OpenCode receives the schema in stdin only. All three
use the same strict local validation; native constrained decoding is not claimed
for OpenCode. Fenced or otherwise wrapped JSON stays rejected. Claude calls set
Claude Code's undocumented `MAX_STRUCTURED_OUTPUT_RETRIES` to 10, overriding any
value you set, so one request can make several hidden attempts. Sonnet's fit the
default 300-second limit; a slower model may need a longer `MVC_REQUEST_TIMEOUT_SECONDS`
([D016](docs/decisions.md#d016-give-claude-more-structured-output-attempts-and-match-quotes-by-words)). The schema-file invocation with native contract 1 was exercised in the
[version 2 regression run](artifacts/2026-10-31-codex-luna-comparison-v2.json).
All fourteen attempts closed using 50 calls: five wrapper protocol/state stops,
one baseline deadline expiry during a coordinator interruption, and eight delivered
final responses. Delivered responses still have material omissions. All cases were
previously exposed; this run does not establish Level 0 acceptance or superiority.
Some rendered-view checks remain incomplete because browser access failed.
The [five-call native contract 2 check](artifacts/2026-11-01-codex-luna-native-contract-2.json)
passed seeded HTTP development stages for carry-forward, partial answers, explicit
unknowns and correction on Codex 0.166.0. Facts remained stable on the final
no-change call, while recommendation wording/classification varied. This is not
unseeded requirement discovery, browser verification or a reliability estimate.
The subsequent [unseeded UI flow](artifacts/2026-11-01-codex-luna-unseeded-owner-flow.json)
completed five calls from a fictional book-loan idea through corrections and a
provisional brief. Both rendered views matched the exports, and the actual
download matched the final export. Independent review retained an unlabeled
approval-policy proposal, an intermediate caveat omission and incomplete aggregate
goal source coverage. This single development flow does not establish Level 0
acceptance, owner comprehension or reliability.
Historical responses are not repaired or accepted through a fallback.
The [T027 continuity check](artifacts/2026-11-01-codex-luna-assessment-continuity.json)
completed three actual UI-driven calls before browser automation failed. Follow-up
inputs contained the prior assessment, and proposed approval handling was labeled.
The current facts nevertheless retained an obsolete owner-only access rule and
omitted new download/revocation requirements that appeared only in prose. Three
saved pages match their exports; the last correction, closeout and actual final
download were not performed. This partial development run does not establish
semantic improvement or acceptance.

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
All seven [frozen case pairs](artifacts/l0-acceptance-cases.json) were attempted
once; the [results](artifacts/2026-10-30-codex-luna-acceptance.json) preserve failures,
raw native exchanges, source snapshots, rendered-view text and independent review.
The [matched comparison plan](artifacts/l0-acceptance-plan.json) preserves their
original bytes and records the limits used for that run. Check the plan, or rehearse
HTTP recovery and baseline input assembly without inference:

```sh
.venv/bin/python -m meta_vibe_coding.evaluation
.venv/bin/python -m meta_vibe_coding.evaluation --rehearse --output /tmp/mvc-acceptance-rehearsal.json
```

The default writes nothing. Rehearsal uses a separate fictional fixture and a
double; its new private output file includes source snapshots and unchecked review
rows. Run from this source checkout; a different installed package or changes
during capture fail the provenance check. Existing files are never overwritten.
This entry point has no live execution mode. Live runs use
[`scripts/acceptance_run.py`](scripts/acceptance_run.py), which needs a frozen plan
naming the agent and a separate approval of the exact plan, harness and journal
hashes; see [D015](docs/decisions.md#d015-name-the-agent-in-the-plan-and-run-acceptance-through-one-harness).
T019 used the audited local harness retained in its result artifact; it made no
repairs, retries or fallback requests.
The fourteen first attempts are closed. Current preparation previews separate
closed response schemas for both approaches; the baseline remains transcript-only.
Another live run needs a new versioned matched plan, reviewed settings and an
invocation allowance. It must account for the changed schemas and native flags.
Owner sessions remain separate.

The [fresh correction check](artifacts/2026-11-02-codex-luna-correction-verification.json)
completed five production HTTP calls. Scoped access and download corrections were
observed, and all five recorded views plus the replay download matched exports.
Independent review found a blocking fact that mixed the owner's requirement with
an agent-derived copy-retention consequence. Generic prompt guidance now separates
those claims; software checks do not establish live improvement. Browser evidence
is read-only replay, not live owner interaction.
The [Codex matrix](artifacts/2026-11-02-codex-luna-acceptance-v3-interrupted.json)
stopped at a usage limit after 15 calls and stays partial evidence. The
[Claude Code and Haiku 4.5 matrix](artifacts/2026-11-02-claude-haiku-acceptance-v4.json)
ran all fourteen jobs of [plan 4](artifacts/l0-comparison-plan-v4.json) in 54 calls.
No phase passes. Four of seven wrapper jobs stopped with no result, and 19 blocking
findings stand across wrapper and baseline after separate agent review and
adjudication. The [Sonnet 5.5 matrix](artifacts/2026-11-02-claude-sonnet-acceptance-v5.json)
reran [plan 5](artifacts/l0-comparison-plan-v5.json), identical except for the model,
in 46 calls. Six jobs pass every phase on recorded replay and one has a blocking
failure. Two wrappers stopped after exhausting structured-output retries, and five
baseline rows are open because a test answer wording misled the baseline. After
fixes, a [final run](artifacts/2026-11-02-claude-sonnet-acceptance-v6.json) of
[plan 6](artifacts/l0-comparison-plan-v6.json) on seven new cases found an export
defect for incomplete provisional results; operator protocol misses also changed
three wrapper outcomes. Level 0 acceptance is not met, and these cases are now exposed. Results do not establish
which approach is better, and owner comprehension is untested.

The [complete native contract 3 comparison](artifacts/2026-11-05-claude-sonnet-acceptance-v7-complete.json)
closed all fourteen original first attempts using 39 calls and 34 questions after
reviewed recovery. The [28-call partial record](artifacts/2026-11-03-claude-sonnet-acceptance-v7.json)
is unchanged. Six wrapper continuity stops and the original baseline quota stop
remain failures. Separate semantic review and scoped adjudication are complete;
preserved meaning in rejected outputs does not make those attempts successful.
The wrapper alone has fact-key, open-question readiness and continuity gates, and
its input limit is 32,000 bytes versus the transcript baseline's 64,000. These
protocol costs and semantic findings stay separate. Actual wrapper
rendering/download and adult comprehension remain unchecked. Level 0 is not
accepted; [T035](docs/work-board.md#t035-frozen-comparison-repair-and-browser-verification)
records the later D021 repair and remaining verification.

D021 passed separate code review, 366 Python tests and 14 UI checks. Its bounded
[browser development run](artifacts/2026-11-05-ui-development-t035-blocked.json)
stopped before any assessment because browser control was unavailable. No live
effect, actual download or full-interface AI walkthrough is established.


A [three-reader AI rehearsal](artifacts/2026-11-04-ai-owner-rehearsal.json) uses
recorded Owner Views and preserves the first generated teach-back answers. Separate
review found mostly faithful summaries, while the known N06 omission remained in
the source handoff. Two complaints about a missing provisional label came from
ambiguity in the replay pack; the actual disposition label was present. This is
synthetic explanation review, with no actual participants, product calls, browser
tasks or downloads. T011 and T032 remain incomplete.

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
