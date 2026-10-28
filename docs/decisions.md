# Decision log

Record decisions that affect scope, interfaces, dependencies, data handling, or
evaluation. Routine local edits do not need an entry. Keep accepted entries as
history; supersede them with a linked new entry when a choice changes.

Use a stable ID, date, status (`proposed`, `accepted`, or `superseded`), decision
owner, context, choice, and consequences. An agent can propose a choice; human
approval is required for changes to scope, acceptable risk, or external authority.

## D001: Start with Level 0

- Date: 2026-10-28
- Status: accepted
- Owner/source: repository owner's supplied [proposal](meta-vibe-coding-proposal.md),
  sections 20, 21, and 25 at initialization; retained in the revised
  [Level 0 section](meta-vibe-coding-proposal.md#level-0-intent-interpreter).
- Context: the long-term vision spans engineering, delivery, and operations, but
  the first prototype must test intent interpretation and engineering judgment.
- Decision: build the Intent Interpreter first. Exclude coding-agent integration,
  autonomous deployment, and a multi-agent product runtime from this milestone.
- Consequences: prioritize clarification, risk reasoning, minimum sufficient
  solutions, and consistent owner/developer views. Work by multiple contributors
  does not expand product scope.

## D002: Share one lightweight collaboration workflow

- Date: 2026-10-28
- Status: proposed; implemented for review in T001
- Owner: repository owner; proposed by the initializing Codex session.
- Context: multiple people and agents need shared state without duplicating
  instructions or depending on private chat history.
- Decision: use one work board for ownership and handoffs, this log for durable
  choices, CONTRIBUTING for workflow, and AGENTS.md for agent instructions.
  CLAUDE.md points to the shared rules. Use isolated worktrees for parallel edits
  when practical and coordinate shared files when isolation is unavailable.
- Consequences: no orchestration service, routine agent diaries, or duplicate
  tool-specific rule sets. Revisit tracking if task volume makes the board hard
  to use; record a migration rather than silently splitting sources of truth.

## D003: Build a useful solution and reuse existing ideas

- Date: 2026-10-28
- Status: accepted
- Owner/source: repository owner’s explicit direction during proposal revision.
- Decision: the final objective is a useful solution, not a paper. Reuse ideas,
  products, and components based on fit, maintenance, cost, and applicable rights.
- Consequences: retain Level 0 as the first milestone. Use comparisons and user
  checks to improve delivery; novelty, publication, and a new architecture are not
  success requirements. Revisit only if the owner adds a research deliverable.

## Open choices

| Choice | Resolve in | Needed before |
| --- | --- | --- |
| State contract and brief serialization | T002 | Depending implementation and exported artifacts |
| Clarification interaction and presentation of uncertainty | T003 | Prototype interaction is accepted |
| Language, framework, model/provider, and local check commands | T004 | Implementation |
| Conversation retention, provider data handling, and cost limits | T004, revisited before external use | Real user input or a public demo |
| Product acceptance checks and reviewer assignments | T010, exercised in T006 | Acceptance review |
| Adult usability tasks, consent, and data handling | T011 | Participant-facing sessions |
| License and terms for external contribution or reuse | Repository owner | An intended external distribution or contribution arrangement |
