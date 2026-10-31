# Decision log

Record decisions that affect scope, interfaces, dependencies, data handling, or
evaluation. Routine local edits do not need an entry. Keep accepted entries as
history; supersede them with a linked new entry when a choice changes.

Use a stable ID, date, status (`proposed`, `accepted`, or `superseded`), decision
owner, context, choice, and consequences. An agent can propose a choice; human
approval is required for changes to scope, acceptable risk, or external authority.

## D001: Start with Level 0

- Date: 2026-10-28
- Status: accepted; agent boundary defined by D008.
- Owner/source: repository owner's supplied [proposal](meta-vibe-coding-proposal.md),
  sections 20, 21, and 25 at initialization; retained in the revised
  [Level 0 section](meta-vibe-coding-proposal.md#level-0-intent-interpreter).
- Context: the long-term vision spans engineering, delivery, and operations, but
  the first prototype must test intent interpretation and engineering judgment.
- Decision: build the Intent Interpreter first. Initially exclude coding-agent
  integration, autonomous deployment, and a multi-agent product runtime. D008
  requires a coding-agent wrapper while keeping construction out of L0.
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

## D004: Support general vibe coding

- Date: 2026-10-28
- Status: accepted; source: repository owner's explicit clarification during T010.
- Decision: Kanji is the motivating example, not the target product. Use varied
  software ideas for acceptance and remove the Kanji-specific demo requirement.
- Consequence: keep the L0 process general; examples must not hardcode its behavior.

## D005: Versioned JSON and one source for both views

- Date: 2026-10-28
- Status: proposed for review in T002–T003; owner: Codex for the requesting human.
- Choice: use the JSON contract in [Level 0](level-0.md#project-state-and-brief-contract)
  for state and brief export. Render both views from one validated revision.
- Reason: explicit types, source references, and revision checks support a portable
  handoff and prevent stale or contradictory views. Runtime tooling remains T004.
- Revisit before implementation if the selected approach cannot support the contract.

## D006: Small local web app with a local model

- Date: 2026-10-28; status: superseded by D007, then D008.
- Earlier choice: Python/FastAPI, strict Pydantic state, plain JavaScript, and
  direct Ollama inference. Installed model comparisons did not establish product
  quality. The UI/state work remains useful; the direct transport is removed.
- Earlier fictional runs remain in `artifacts/legacy/`. They are not current
  wrapper acceptance evidence. Detailed model-selection history is in Git.

## D007: Interchangeable inference and agent backends

- Date: 2026-10-28; status: superseded by D008.
- Earlier direction: support direct local inference, commercial APIs, and a coding
  agent. A subsequent Codex-first preference also belongs to this superseded plan.
- Retained: shared state, validation, explicit deadlines, visible failures, and
  separate structural/semantic checks. Remove direct transports, wrapper-owned
  API credentials/rates, model benchmarks, and the local evaluation runner.

## D008: Wrap coding agents only

- Date: 2026-10-28; status: accepted.
- Owner/source: repository owner's explicit major revision and clarification:
  support **OpenCode, Claude Code, and Codex**, rather than OpenCode alone.
- Decision: this product is a stewardship layer over a coding agent. It owns
  intent, questions, versioned state, validation, and synchronized views. The
  selected agent owns model execution, authentication, provider integration,
  and any local hosting. There is no direct local-inference or commercial API path.

Use one thin CLI wrapper per supported agent behind the same assessment contract.
The initial implementation shares process handling and validation rather than
building a model router, agent framework, or agent orchestration service. Select
one agent explicitly and never switch after failure. Model selectors, when given,
are forwarded to the agent; the app does not interpret them as provider endpoints.

At Level 0, pass only the owner-state snapshot in a fresh temporary working
directory. Request planning without construction, restrict action tools using the
agent's controls, and validate the completed response before adopting it. Hooks,
plugins, managed configuration, native transcripts, and provider retention remain
part of the trusted agent environment. CLI flags and mocked tests are not proof
of complete isolation. Review actual permissions and data destinations before
live/private use; construction and deployment remain later milestones.

OpenCode preserves native provider settings beneath a deny-all planning policy.
Claude safe/restricted mode preserves native authentication while excluding model
tools. Codex ignores user config/rules and disables command/extension features in a
read-only sandbox; it reuses authentication but currently supports its built-in
provider defaults or a forwarded model selector, not arbitrary saved provider
profiles. Use OpenCode for locally hosted or custom-provider configurations.

Interfaces checked on 2026-10-28: [OpenCode CLI](https://opencode.ai/v2/docs/cli/)
and [permissions](https://opencode.ai/v2/docs/permissions/),
[Claude CLI](https://code.claude.com/docs/en/cli-reference), and
[Codex automation](https://learn.chatgpt.com/docs/non-interactive-mode).
Installed help/version inspection covered OpenCode 2.0.12, Claude Code 2.1.312,
and Codex CLI 0.165.0. Live compatibility remains unverified.

Keep execution disabled until explicitly configured. Defaults remain 300 seconds
per request, 1,800 seconds per interaction, five questions, and seven top-level
agent invocations. The per-server invocation allowance survives new browser tabs
but resets on restart. These are not model-token or dollar limits; use native
agent/provider spending controls. Unknown internal calls, tokens, and cost stay
unknown. Record exact agent/model/configuration and limits for comparisons.

Compare the stewardship wrapper with a strong prompt through the **same coding
agent**, not a direct-model API. Preserve the frozen fictional cases and previous
failures. Before acceptance, establish a useful development response through a
real agent, then review fresh cases, corrections, unknowns, and failures. Adult
owner sessions still need separate authorization and data handling.

## D009: Bind clarification to facts and retain explicit uncertainty

- Date: 2026-10-30; status: accepted implementation choice, reviewed in T017.
- Owner: Codex for the repository owner’s requested next task; within Level 0.
- Context: development runs repeated explicit unknowns and returned a goal under
  a key the Owner View did not read.
- Choice: new questions identify a fact key; new results contain text/null `goal`.
  Runtime `owner_unknowns` stores a fact key, source turn and exact short quote.
  The button records uncertainty before inference; free-text declarations are
  proposed by the agent and checked against source text. Only a later substantive
  reply can resolve a retained declaration. Suppressed questions must remain in
  assessment open decisions; the app does not invent their blocking status.
- Limits: exact quotes prove presence, not meaning. Same-key suppression does not
  detect semantic aliases. Runtime defaults accept older state envelopes, while
  new agent results follow the tighter contract. Exported brief schema 1 is
  unchanged; this is not a migration of old grouped facts or saved clients.

## D010: Separate native responses from canonical state

- Date: 2026-10-30; status: accepted in T020; native encoding superseded by D011.
- Context: T019 exposed malformed JSON, dangling question targets, state-guard
  failures and omitted requirements. Keep that failed run and its inputs intact.
- Choice: native response contract 1 uses keyed fact arrays and an embedded
  question target, then converts to canonical state. Duplicate array keys and
  conflicting question targets fail; an identical target may also appear in facts.
  New or changed confirmed facts require exact owner quotes linked
  to every cited source. Unchanged facts and explanations need no invented fact.
  Canonical guards, owner-unknown evidence and exported brief schema 1 stay intact.

Codex supports a schema file through
[`--output-schema`](https://learn.chatgpt.com/docs/non-interactive-mode).
Write it privately within the request directory and also send its content in
stdin. Compile a closed schema with required fields and nullable alternatives,
following the documented [structured-output constraints](https://developers.openai.com/api/docs/guides/structured-outputs).
Local validation retains bounds and checks that the native subset cannot express.
OpenCode and Claude use the same stdin contract and local validation; this change
does not establish native constrained decoding for those agents. Invalid output
fails without JSON repair, fallback parsing, another agent or automatic retry.

Quotes establish source presence and linkage, not correct interpretation or
complete requirement extraction. Prompt guidance distinguishes independently
answerable properties and asks about copies, derivatives and unattended identities
when relevant; it does not relax confirmation, repeated-topic or unknown guards.
Fresh scripted consequence fixtures check preservation and export of supplied
content, not live agent discovery. At implementation, actual schema compatibility
and model-quality improvement were unverified live; T021–T022 record subsequent
development and exposed-case regression evidence on the work board.
Future preparation previews separate closed
schemas for wrapper and transcript-only baseline; another comparison requires a
new versioned matched plan and allowance rather than reusing T019's unused calls.

## D011: Return fact changes with attached evidence

- Date: 2026-11-01; status: accepted implementation choice, design reviewed in T023.
- Context: T022 rejected duplicated facts, inconsistent question copies and an
  explicit-unknown marker whose fact lacked its source. Repeated-topic failures
  also exposed the need to distinguish independently answerable properties.
- Choice: native contract 2 returns `fact_updates`, `remove_fact_keys`, `assessment`
  and a nullable question referencing a resulting fact key. Each update contains
  its key, value, status, reason, quoted `evidence` and an `owner_unknown` flag.
  Derive stable unique source IDs from that evidence. A new explicit unknown needs
  unknown/null and exactly one quote; derive its marker and citation together.

Carry untouched facts locally without asking the agent to reproduce them. Decode
into a separate candidate and apply adoption guards against the original state.
Reject duplicate/overlapping operations, removals of missing facts or missing question targets,
confirmed/retained-unknown deletions and more than 100 resulting facts. A false
unknown flag does not clear a retained marker; a later explicit declaration may
refresh it under the existing source-order guard. Confirmation, typed changes,
repeated-topic and unknown-resolution guards remain unchanged. Native contract 1
is rejected; canonical state and exported brief schema 1 are unchanged.

Carrying facts forward does not prove the agent noticed a correction: omitted
updates can preserve stale interpretations. Semantic aliases and incomplete
extraction still need review. Partial answers must settle their own properties
and leave genuinely different unresolved properties explicit. Do not rename a
topic to bypass an unknown or repeated-question guard. T023's deterministic checks
do not establish live reliability or repair T022's historical failures; another
live check needs a new reviewed plan and allowance.

## Open choices

| Choice | Resolve in | Needed before |
| --- | --- | --- |
| Review the drafted JSON state and brief contract (D005) | T002 | Depending implementation and exported artifacts |
| Review the drafted clarification and revision flow | T003 | Prototype interaction is accepted |
| Verify the selected agent wrapper, dependencies, and setup/check commands under D008 | T005 | Claiming a runnable prototype |
| Verify agent permissions, data destination/retention, and usage limits under D008 | T005, revisited before external use | Real user input or a public demo |
| Product acceptance checks and reviewer assignments | T010, exercised in T006 | Acceptance review |
| Adult usability tasks, consent, and data handling | T011 | Participant-facing sessions |
| License and terms for external contribution or reuse | Repository owner | An intended external distribution or contribution arrangement |
