# Contributing

People and agents use the same tasks, documents, and review process. Keep enough
shared context for someone else to continue without reading a private chat.

## Pick up work

Read the [Level 0 scope](docs/level-0.md), [work board](docs/work-board.md), and
relevant [decisions](docs/decisions.md). Check the working tree before editing.
Add or claim a task with a short outcome, owner, and affected paths. An owner can
be a person or an identifiable agent session; record the requesting human when an
agent needs someone to resolve a decision.

The work board is the initial source of task status. GitHub issues and pull
requests can hold discussion and diffs; link them from the row instead of copying
the full discussion. If the team later moves task tracking to issues, record that
change and retire the board rather than maintaining two competing trackers.

## Work concurrently

Prefer one short-lived branch per task, such as `docs/l0-acceptance` or
`feat/intent-state`. For simultaneous edits, use separate worktrees or clones.
Branches alone do not isolate files in a shared working directory.

Once the repository has its first commit, a contributor can create an isolated
worktree from the agreed base, for example:

```sh
git worktree add ../meta-vibe-coding-intent -b feat/intent-state main
```

If contributors must share one checkout, reserve affected paths in the task row.
Coordinate edits to shared files such as the board, README, and dependency locks.
Do not switch branches, stage, commit, stash, or clean up another contributor's
work without coordination. Re-read a file before editing it if others may have
changed it. A path claim is an agreement, not an automatic lock.

When blocked or handing off, record the current result, changed paths, checks,
remaining question, and next action in the task's notes. Stop conflicting edits
while ownership is being resolved. A separate handoff document is unnecessary.

## Code conventions

Use this baseline for human-written and agent-generated code. Follow the selected
language's established conventions; record formatter, linter, type-checking, and
test commands when T004 establishes the stack. There is no code toolchain yet.

- Choose clear names that describe the domain. Avoid unexplained abbreviations,
  clever expressions, and boolean flags whose meaning is unclear at the call site.
- Keep functions and modules focused. Add an abstraction when it serves a real
  need; avoid speculative frameworks, generic wrappers, and layers with no work.
- Keep decision logic independently testable from model calls, storage, and UI
  effects. This does not require a separate folder or class for every concern.
- Define explicit contracts at boundaries. Validate user input and model output
  before using them; parseable JSON alone does not establish a valid brief.
- Preserve the distinction between unknown, absent, empty, and false. Derive both
  product views from the same state and update them when an answer changes.
- Handle expected failures explicitly. Give useful errors, bound network timeouts
  and retries, and do not silently replace a failed model call with a canned result.
- Keep secrets in local configuration. Avoid logging private prompts or answers;
  use fictional fixtures and label test doubles clearly.
- Add dependencies for concrete needs, use the ecosystem's dependency manifest
  and application lockfile, and document required configuration with placeholders.
- Follow existing formatting and naming in the affected code. Prefer automated
  formatting once configured; keep unrelated cleanup out of a functional change.
- Comment on intent, constraints, or surprising behavior. Document public contract
  semantics where needed; do not narrate obvious code or add boilerplate docstrings.
- Test behavior and meaningful failure cases. For L0, cover unknown answers,
  revised answers, brief validation, and view consistency. Assert important outcomes
  rather than exact model wording; keep live provider checks explicit and separate
  from deterministic local tests. Small prose edits need document checks, not tests.

## Filenames and directories

- Use descriptive lower-case hyphenated names for new Markdown files and general
  directories, such as `writing-guide.md` or `demo-scenarios/`. Avoid spaces.
- Keep standard discovery names such as `README.md`, `CONTRIBUTING.md`,
  `AGENTS.md`, and `CLAUDE.md`. Follow ecosystem conventions for source files,
  tests, components, and generated files instead of forcing one casing everywhere.
- Name files for their subject, not their author or tool. Use Git for revisions
  rather than names such as `final-v2.md` or `claude-notes.md`. Use a `YYYY-MM-DD-`
  prefix only when the date identifies a real record, such as an evaluation run.
- Put contributor entry points at the root and supporting documents in `docs/`.
  Keep GitHub templates in `.github/`. Prefer an existing relevant document or
  directory before adding another.
- Add `src/`, `tests/`, `examples/`, or `scripts/` only when they contain useful
  artifacts, adapting to the chosen framework's layout. Do not create empty
  scaffolding or per-person and per-agent directory trees.
- Keep the hierarchy shallow. Introduce a subdirectory when it groups a distinct
  body of work, not for every feature or anticipated architectural layer. Keep
  reusable examples separate from generated results and private local data.
- When moving or renaming a file, update its references in the same change.

## Keep decisions and documents useful

Use the [writing guide](docs/writing-guide.md). Keep each fact in one authoritative
place and link to it elsewhere:

| Information | Source |
| --- | --- |
| Purpose and long-term direction | Proposal |
| Current milestone and acceptance criteria | Level 0 scope |
| Current capability and entry points | README |
| Ownership, progress, and check results | Work board |
| Accepted trade-offs and changes to direction | Decision log |
| Collaboration workflow | This document |
| Code, filename, and directory conventions | This document |
| Language, tone, and document size | Writing guide |
| Agent-specific operating instructions | AGENTS.md |

When changing scope, ask the requesting human or repository maintainer to resolve
the choice and record it in the decision log. Update affected scope and capability
documents together. Technical details can evolve within an agreed task without a
new approval for every edit.

## Review and finish

Keep each change focused. Its description should explain the problem, resulting
behavior, validation, and any unresolved limitation. The optional
[pull request template](.github/pull_request_template.md) provides this outline.

For document changes, verify links, headings, formatting, and agreement with the
proposal and active scope. `git diff --check` checks tracked changes; also inspect
new files before staging. For implementation changes, run the relevant tests and
record the exact commands and results. The first implementation must add usable
setup and check instructions to README.

Ask a different contributor to review meaningful changes to behavior, scope,
privacy, or evaluation. A second agent can review implementation evidence; human
decisions about scope, acceptable risk, and external actions remain with the
requesting human or maintainer. If only self-review was possible, say so and leave
the task in review until the required reviewer has assessed it.

Move a task to done when its outcome and checks are recorded and required review
is complete. Link the resulting files and pull request or commit when available.
Agents should not infer permission to commit, push, merge, publish, or spend from
an implementation assignment.
