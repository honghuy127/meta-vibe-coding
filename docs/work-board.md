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
| T006 | Review demos and identify readiness gaps | blocked | Codex with separate reviewer, requested by repository owner | `artifacts/`, README, this board | Fresh cases remain frozen. Earlier direct-model checks are historical. Resume with real agent development responses after T012, then a matched same-agent baseline and held-out review. |
| T007 | Initialize GitHub repository metadata | done | Codex, requested by repository owner | GitHub repository settings, labels, milestone; `docs/work-board.md` | Description, seven topics, three work-area labels, and [Level 0 milestone](https://github.com/honghuy127/meta-vibe-coding/milestone/1) saved and verified through the GitHub API on 2026-10-28. |
| T008 | Define code, writing, filename, and directory conventions | review | Codex, requested by repository owner | `CONTRIBUTING.md`, `docs/writing-guide.md`, `AGENTS.md`, `README.md`, this board | Existing guides updated; no new files. Checks passed across 11 Markdown files: relative links/anchors, headings, fences, and whitespace. Self-reviewed; repository owner to review conventions. |
| T009 | Improve the solution proposal and delivery plan using research skills | review | Codex, requested by repository owner | Proposal, Level 0 plan, work board, decision log, README | D003 applied; proposal condensed, sources checked, and acceptance tasks linked. Strict Markdown checks and local render review completed; owner review pending. |
| T010 | Define product acceptance cases and the simplest-solution comparison | review | Codex, requested by repository owner | `docs/level-0.md`, proposal, README, D004 | Seven general cases and four variations defined, with acceptable alternatives, blocking failures, comparison limits, and teach-back checks. Strict Markdown checks pass for all 11 documents; whitespace and acceptance-table checks pass. Self-reviewed, owner review pending. No complete product case evaluation; T005 records the local timeout smoke attempts. |
| T011 | Check whether adult owners understand and can use the L0 handoff | blocked | Unassigned | Authorized session artifacts; short result in this board | Depends on T006, named facilitator, consent/data-handling decisions, and owner authorization. Record comprehension, task completion, burden, and changes needed before L1. |
| T012 | Replace direct inference with coding-agent wrappers | done | Codex with separate wrapper reviewer, requested by repository owner | `src/`, `tests/`, artifacts organization, README, proposal, Level 0 scope, decisions, agent guidance | OpenCode, Claude Code, and Codex CLI wrappers implemented; direct clients/runner removed. Native help/version and mocked contracts checked. See note for review and remaining live verification. |
| T013 | Self-audit the pending implementation before commit | done | Codex, requested by repository owner | Source, tests, package/lock files, docs, artifact provenance | Audited all 33 tracked/untracked candidate files against D008; fixed owner-confirmation, stale-question/ID, readiness, and instruction-boundary issues. Independent fix review passed; see note. No commit or live inference. |

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
session, or live external agent evaluation has run.

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
