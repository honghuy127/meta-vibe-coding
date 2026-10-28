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
| T004 | Choose the simplest viable solution and document local setup | review | Codex, requested by repository owner | D006–D007, README, Level 0 scope, proposal | Revised local-only choice to interchangeable local/API/agent backends. Official integration docs checked; no adapters implemented or calls launched. Self-reviewed; strict Markdown and whitespace checks pass. First adapter and account/budget choices remain T005 work. |
| T005 | Implement the Level 0 prototype | blocked | Unassigned | Source and test locations chosen in T004 | Depends on T002–T004 and T010. Implement L0-01–L0-09 and document exact run/check commands. |
| T006 | Review recorded demos and identify readiness gaps | blocked | Unassigned | Proposed: `docs/evaluation/`, README capability status | Depends on T005 and T010. Cover L0-10 and all review cases; obtain review from someone other than the implementer. Public release is a separate authorized action. |
| T007 | Initialize GitHub repository metadata | done | Codex, requested by repository owner | GitHub repository settings, labels, milestone; `docs/work-board.md` | Description, seven topics, three work-area labels, and [Level 0 milestone](https://github.com/honghuy127/meta-vibe-coding/milestone/1) saved and verified through the GitHub API on 2026-10-28. |
| T008 | Define code, writing, filename, and directory conventions | review | Codex, requested by repository owner | `CONTRIBUTING.md`, `docs/writing-guide.md`, `AGENTS.md`, `README.md`, this board | Existing guides updated; no new files. Checks passed across 11 Markdown files: relative links/anchors, headings, fences, and whitespace. Self-reviewed; repository owner to review conventions. |
| T009 | Improve the solution proposal and delivery plan using research skills | review | Codex, requested by repository owner | Proposal, Level 0 plan, work board, decision log, README | D003 applied; proposal condensed, sources checked, and acceptance tasks linked. Strict Markdown checks and local render review completed; owner review pending. |
| T010 | Define product acceptance cases and the simplest-solution comparison | review | Codex, requested by repository owner | `docs/level-0.md`, proposal, README, D004 | Seven general cases and four variations defined, with acceptable alternatives, blocking failures, comparison limits, and teach-back checks. Strict Markdown checks pass for all 11 documents; whitespace and acceptance-table checks pass. Self-reviewed, owner review pending. Product cases not run: no implementation or evaluation runner exists. |
| T011 | Check whether adult owners understand and can use the L0 handoff | blocked | Unassigned | Authorized session artifacts; short result in this board | Depends on T006, named facilitator, consent/data-handling decisions, and owner authorization. Record comprehension, task completion, burden, and changes needed before L1. |

Proposed paths are locations for future work, not existing artifacts. Split tasks
when contributors need independent ownership; do not reserve the whole repository
for a broad task.

## Task notes

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
