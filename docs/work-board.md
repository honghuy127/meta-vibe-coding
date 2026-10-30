# Work board

This is the shared task tracker until the team explicitly chooses another one.
Keep rows short and use a task note below when a handoff needs more context.
Dates use `YYYY-MM-DD`; the initial snapshot is 2026-10-28.

## How to use it

Before substantial work, add or claim a row with a concrete outcome and affected
paths. Give each concurrent contributor an identifiable owner. For an agent,
include the requesting human when a decision needs a human owner. Coordinate
changes to this file; re-read the latest version before editing it.

Statuses are `ready`, `active`, `blocked`, `review`, and `done`. Ready tasks have
enough scope to begin. A blocked task names the dependency or question that must
be resolved. Review means the result exists but needs the required review. Done
means the acceptance evidence and required review are recorded.

## Tasks

| ID | Outcome | Status | Owner | Affected paths | Dependency / evidence / next action |
| --- | --- | --- | --- | --- | --- |
| T001 | Initialize shared docs and contribution conventions | review | Codex, requested by repository owner | Root docs, `docs/`, `.github/`, `.gitignore`, `.editorconfig` | Foundation prepared; see notes below. Repository owner to review conventions. |
| T002 | Define state and engineering brief contracts, including unknowns and answer changes | review | Codex, requested by repository owner | `docs/level-0.md`, D005 | Versioned JSON state/export, fact provenance, dispositions, and validation rules drafted. Self-reviewed; document checks pass, runtime validation is T005. |
| T003 | Design clarification and synchronized owner/developer flows | review | Codex, requested by repository owner | `docs/level-0.md`, D005 | Idea → clarification → recommendation → revision → export/recovery specified. Covers unknown answers, stale results, and late responses. Self-reviewed; implementation and user review remain. |
| T004 | Choose the simplest viable solution and document setup | review | Codex, requested by repository owner | D008, README, Level 0 scope, proposal | Agent-only architecture selected by owner. OpenCode, Claude Code, and Codex wrappers replace direct transports in T012; live access and permissions need verification. |
| T005 | Implement the Level 0 prototype | review | Codex, requested by repository owner | `src/meta_vibe_coding/`, `tests/`, dependency files, README | State, browser flow, corrections, and JSON export retained. Agent integration is being revised in T012. Product acceptance remains incomplete. |
| T006 | Review demos and identify readiness gaps | review | Codex with separate reviewer, requested by repository owner | `artifacts/`, pilot/agent boundary and tests, README, this board | Codex/Luna produced a live valid initial clarification after a narrow startup-notice parser fix. Two native calls recorded; 120 Python and ten UI checks pass; separate code and evidence reviews passed. Next: a bounded fictional conversation through answers/correction/export before frozen cases. |
| T007 | Initialize GitHub repository metadata | done | Codex, requested by repository owner | GitHub repository settings, labels, milestone; `docs/work-board.md` | Description, seven topics, three work-area labels, and [Level 0 milestone](https://github.com/honghuy127/meta-vibe-coding/milestone/1) saved and verified through the GitHub API on 2026-10-28. |
| T008 | Define code, writing, filename, and directory conventions | review | Codex, requested by repository owner | `CONTRIBUTING.md`, `docs/writing-guide.md`, `AGENTS.md`, `README.md`, this board | Existing guides updated; no new files. Checks passed across 11 Markdown files: relative links/anchors, headings, fences, and whitespace. Self-reviewed; repository owner to review conventions. |
| T009 | Improve the solution proposal and delivery plan using research skills | review | Codex, requested by repository owner | Proposal, Level 0 plan, work board, decision log, README | D003 applied; proposal condensed, sources checked, and acceptance tasks linked. Strict Markdown checks and local render review completed; owner review pending. |
| T010 | Define product acceptance cases and the simplest-solution comparison | review | Codex, requested by repository owner | `docs/level-0.md`, proposal, README, D004 | Seven general cases and four variations defined, with acceptable alternatives, blocking failures, comparison limits, and teach-back checks. Strict Markdown checks pass for all 11 documents; whitespace and acceptance-table checks pass. Self-reviewed, owner review pending. No complete product case evaluation; T005 records the local timeout smoke attempts. |
| T011 | Check whether adult owners understand and can use the L0 handoff | blocked | Unassigned | Authorized session artifacts; short result in this board | Depends on T006, named facilitator, consent/data-handling decisions, and owner authorization. Record comprehension, task completion, burden, and changes needed before L1. |
| T012 | Replace direct inference with coding-agent wrappers | done | Codex with separate wrapper reviewer, requested by repository owner | `src/`, `tests/`, artifacts organization, README, proposal, Level 0 scope, decisions, agent guidance | OpenCode, Claude Code, and Codex CLI wrappers implemented; direct clients/runner removed. Native help/version and mocked contracts checked. See note for review and remaining live verification. |
| T013 | Self-audit the pending implementation before commit | done | Codex, requested by repository owner | Source, tests, package/lock files, docs, artifact provenance | Audited all 33 tracked/untracked candidate files against D008; fixed owner-confirmation, stale-question/ID, readiness, and instruction-boundary issues. Independent fix review passed; see note. No commit or live inference. |
| T014 | Make the fictional pilot repeatable after the cooldown | done | Codex with separate reviewer, requested by repository owner | `src/meta_vibe_coding/pilot.py`, `tests/test_pilot.py`, `.gitignore`, README, this board | Opt-in runner prepared and independently reviewed. Default check sends no inference; serving requires cooldown expiry and a current pricing check. Exclusive claims prevent allowance resets. 101 pytest and ten UI checks pass; T006 remains blocked. |
| T015 | Verify the packaged pilot and rehearse the full flow offline | done | Codex with separate reviewer, requested by repository owner | `tests/test_pilot.py`, this board | Built/installed `0e9ebaa` offline; all 12 packaged files match. Full source suite: 102 pass. All 16 pilot tests also pass against the wheel, independently verified. Process doubles only; no new model calls or held-out cases. |

Proposed paths are locations for future work, not existing artifacts. Split tasks
when contributors need independent ownership; do not reserve the whole repository
for a broad task.

## Task notes

### T005–T006: Retained core and earlier checks

The design baseline is `6f7ec5d`. The prototype added strict state, clarification,
corrections, synchronized views, recovery, and export. Independent review found
and verified fixes for retry intent, reset isolation, typed revisions, reopening
conflicts, stale export errors, and subprocess deadlines. These core behaviors
remain covered by the current tests.

Earlier direct-model experiments did not establish acceptance. Their raw attempts
and reviews remain in `artifacts/legacy/`; they are not tests of the current agent
wrappers. The seven [fresh cases](../artifacts/l0-acceptance-cases.json) remain
unchanged and unrun. D008 supersedes their original timing metadata with the
current configurable 300/1,800-second limits. No matched baseline, adult owner
session, or completed live external agent evaluation has run.

The owner authorized a fictional development pilot on an OpenCode free plan,
with $0 additional spend. Pinned `opencode/glm-5.3-flash-free`, including native
title/summary/compaction helpers, disabled warming/automatic compaction, and
verified native deny-all planning permissions. Separate review checked routing
and free pricing. These settings do not enforce a monetary cap; global native
configuration was unchanged.

The [original record](../artifacts/2026-10-29-opencode-free-pilot.json) retains
seven failed requests. Attempts 1–2 used `87b0539`; the first native streams were
not captured, while the second reported `provider.free-limit` (429). A post-login
attempt on OpenCode 2.2.1 also returned 429. Attempts 4–7 replayed a redacted
workspace-header placeholder from native debug output and returned 400. Those
comparisons cannot establish a request-size or tool-eligibility cause. All seven
invocations remain consumed; prior failures and claims were preserved.

The owner supplied a working native reply from the same free model. Compared
native and standalone metadata, then corrected the routing handoff using resolved
model metadata. The private exporter copies only the native workspace header,
rejects redacted/ambiguous values, and never exports credentials or overwrites a
file. Quota messages now describe the failed request rather than implying every
native session is blocked. Recognized invalid-request errors have a static
configuration message; raw provider details stay outside the UI.

A [separate verification](../artifacts/2026-10-30-opencode-routing-verification.json)
records two corrected-profile standalone requests and one owned shared-session
request. The first pair used identical fictional stdin; the later request changed
only the new idea’s start time and ran after the earlier cooldown. All returned
429 without a Candidate.
The shared diagnostic verified free helper pins and deny-all permissions. After
the failure, interrupt returned false, waiting completed, and its inbox was empty;
active-inference cancellation was not exercised. Shared execution
is a diagnostic only, not a supported production mode. Three of this run’s seven
invocations were used. No automatic retry, paid fallback, or frozen case ran.

The browser retained the idea and showed the request-scoped error. No live
recommendation or token/cost report was received. Clarification, corrections,
result views/export, permission enforcement, retention, and recommendation
quality remain unverified live. The provider errors do not explain the owner’s
successful native session. The owner identified the interface as terminal. Current
interactive/login shell resolution selects the same v2.2.1 executable as the
wrapper; another installed v1.19.4 binary was not selected. Official documentation
supports `opencode run` for automation. Limited native source inspection did not
establish a terminal-only eligibility rule. Next: match the effective interactive
context before another inference comparison; the new request reported another
cooldown. A retry time is neither an account-wide outage nor assured availability.

The owner then requested Codex with Luna. Verified the official `gpt-6-luna`
selector, Codex CLI 0.165.0 and existing ChatGPT login. Used only fictional input,
a 300-second deadline, a read-only workspace, disabled tools, ignored user
config/rules, and ephemeral mode. API-key environment variables were excluded;
native subscription/credit usage and retention were not independently reconciled.
Global native configuration was unchanged.

The [Codex record](../artifacts/2026-10-30-codex-luna-pilot.json) preserves two calls.
The first completed in 11.4 seconds, but the wrapper rejected a startup notice
about the deliberately disabled Code Mode host. Its Candidate passed schema,
adoption and provisional-export checks in an offline replay. Added an exception
only for that exact notice immediately after `thread.started`; other errors, tool
items and incomplete output still fail. Separate review verified the captured
stream and adversarial variants without enabling the host or any tool.

A second live call passed through the fixed wrapper in about 9.9 seconds. It asked
what visitors should learn or do and who the site serves, retained unknown risk,
and returned `needs_answer`. Export correctly returned 409; no engineering brief
was completed. No workspace files or tool events were observed. These checks
verify an initial clarification, not a full conversation or product acceptance.
Next: continue a bounded fictional flow through answers, unknowns, correction and
export before running frozen cases.

Checks: 120 Python tests, ten Node UI checks, and whitespace pass. The existing
Starlette TestClient deprecation warning remains. Separate code and evidence
reviews passed, as did strict Markdown, relative links and dependency checks. The
earlier OpenCode reviews remain valid for their recorded sources. The owner
requested committing this reviewed snapshot before continuation. The frozen cases
remain unchanged and unrun.

### T014: Repeatable fictional pilot

Added the [pilot runner](../src/meta_vibe_coding/pilot.py) and usage in README.
It records local HTTP evidence and source hashes, and reserves one continuation
through an exclusive claim tied to the recorded request IDs. Claims survive
startup failure; review evidence and reconcile attempts/cooldowns before relaunch.
Separate review verified the cooldown, request allowance, concurrent launch guard,
private journal and preserved HTTP boundaries. All 101 pytest tests, ten Node UI
checks, strict Markdown, whitespace and dependency checks pass. Actual CLI checks
report the active cooldown and refuse serving; no new native request ran. Frozen
cases are unchanged. T014 prepares execution; T006 acceptance remains blocked.
The owner requested committing the reviewed changes after this preparation.

### T015: Packaged integration rehearsal

Committed T014 and quota handling as `0e9ebaa`, then added one integrated offline
test spanning clarification, unknown/provisional export, a correction that times
out, stale-export rejection, retry and corrected provenance. The full suite has
102 passing tests. Built the wheel without network access, installed it under
`/tmp`, and matched all 12 packaged files. All 16 pilot tests pass there with
repository pytest configuration disabled, using existing virtualenv dependencies.
A separate reviewer verified import locations, hashes and those installed tests.
This establishes process-double integration, not native CLI behavior, browser
rendering, recommendation quality or owner comprehension. T006 remains blocked;
the fresh cases are unchanged. The follow-up test is included in the reviewed
snapshot committed before the live conversation continuation.

### T012: Coding-agent-only revision

Applied the owner's major revision and clarification: support OpenCode, Claude
Code, and Codex. The repo owns stewardship/state/views; coding agents own model
execution, native credentials, providers, and any local hosting. Removed the direct
Ollama/API clients, wrapper API-key/rate configuration, and local-model runner.
Archived earlier evidence rather than presenting it as current capability.
Revised README, proposal, Level 0 plan, decisions, and agent guidance in place.

One shared process boundary now invokes each CLI from a temporary workspace,
checks required flags, passes state on stdin, validates successful final JSON,
and preserves deadline/cancellation and invocation limits. Agent execution is
opt-in. Native configuration/managed policy remains trusted bootstrap; no complete
isolation or live compatibility claim is made. Codex intentionally ignores saved
provider profiles; OpenCode handles custom/local routes. See README for details.

A separate reviewer checked vendor interfaces and reproduced incomplete-terminal
parsing and lost OpenCode inline-routing issues; both were fixed. Native help and
version inspection ran without inference. Final checks: 67 pytest tests and eight
Node regressions pass; strict Markdown, whitespace, and dependency checks pass.
The separate reviewer found no remaining
reproduced blocker in the wrapper implementation. Checks use process doubles,
not live agent inference. Remaining work: configure an authorized agent, verify
effective native permissions and retention with fictional inputs,
then obtain a valid development result before spending the held-out cases. No
agent inference, paid call, commit, push, or global agent-setting change is part
of this rewrite.

### T013: Pre-commit self-audit

Reviewed current source, tests, dependencies, docs, and archived evidence. Reproduced
and fixed retry-only confirmation/rewrite of previously assessed facts, answers to
retired questions, and ID collisions in valid nonsequential histories. Added an
assessed-reply count so failed requests can still retry new retained owner input.
Ready goals now require nonempty text. Unknown goals and inapplicable facts render
in human-readable language. Claude/Codex now receive static stewardship policy via
their native system/developer surface; owner text stays in stdin data.

Legacy records now state that their Git SHAs name the design baseline, not the
uncommitted code that executed. Full prior source snapshots are unavailable;
raw records were preserved. This is a replay limitation, not current acceptance.

Checks: 78 pytest tests, ten Node regressions, strict Markdown, whitespace, and
Python dependency consistency pass. Lock contents exactly match the declared
runtime/dev/build dependency closure. Built the wheel offline, matched all eleven
packaged source/assets to the working tree, and verified imports, served assets,
and the disabled-agent gate from an isolated wheel install. No credential-pattern
matches were found in the 33 candidate files; this is not an exhaustive secret scan.
The frozen acceptance-case hash is unchanged. A sandbox signal restriction required
rerunning subprocess checks with process-group permission; that full run passed.
The existing TestClient deprecation warning remains.

Self-audit fixes received a separate read-only regression review. Ready for a
prototype commit; live agent compatibility, effective native policy/retention,
semantic source support, held-out acceptance, and owner understanding remain open.
No agent inference, paid call, commit, or push ran during the audit.

### T009: Solution proposal and plan revision

Applied `conduct-cs-ai-research` in human-led mode from the supplied checkout,
revision `bbb098d678356ae7312b2a8f42e321b3619ddf56`. The owner clarified that a
useful solution is the objective and reuse is encouraged (D003). The proposal
holds the dated source notes and product validation approach; this board holds
ownership. No additional dossier or research deliverable is needed.

Self-review: planning can continue. Execution readiness remains conditional on
T002–T004/T010, assigned reviewers, provider access, and a resource cap; T011 also
needs authorized adult sessions and resolved data handling. No product efficacy,
novelty, or release-readiness claim is made. No waiver was requested. Strict
Markdown and whitespace checks pass. Local CommonMark/table previews were
inspected; the hosted GitHub render is unverified.

### T001: Collaboration foundation

- Result: entry points, agent guidance, contribution workflow, writing guide,
  Level 0 acceptance criteria, decision log, and optional GitHub templates.
- Proposal: retained its wording; normalized heading levels and hard line breaks.
- Validation: checked all Markdown relative links and section targets, heading
  hierarchy, and fenced blocks. Ran whitespace checks with
  `git diff --no-index --check /dev/null <file>` across new files. Verified that
  local credentials and macOS metadata are ignored while placeholder environment
  examples remain trackable. There is no application to build or evaluate yet.
- Review: self-reviewed by the initializing agent; human review is pending.
- Next action: review these conventions, then claim T002, T003, or T004. No
  implementation stack, license, public release, or research result is implied.

### T007: GitHub metadata

- Description: Research on AI technical stewardship for non-expert software
  creation, from intent and risk assessment to sustainable software ownership.
- Topics: `artificial-intelligence`, `human-ai-collaboration`, `llm`,
  `requirements-engineering`, `software-engineering`, `technical-stewardship`,
  and `vibe-coding`.
- Labels: `area:design`, `area:implementation`, and `area:evaluation`, each with
  a description. Existing default labels remain available, including documentation.
- Milestone: Level 0: Intent Interpreter, with scope and exclusions from the
  proposal. No deadline has been assigned. Acceptance criteria remain in
  [Level 0 scope](level-0.md); task status remains on this board.
- Verification: read back the repository, labels, and milestone using
  `gh api repos/honghuy127/meta-vibe-coding`, the `/labels` endpoint, and
  `/milestones/1`. Self-reviewed against the proposal and the requested setup.
- Follow-up: no project homepage exists yet. Repository files are published
  separately through Git; metadata updates alone do not publish them.

For later handoffs, record only what helps the next contributor: result and paths,
checks and their limits, unresolved issue, and next action. Link a pull request or
commit when one exists. Avoid transcripts and routine activity diaries.
