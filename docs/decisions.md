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
extraction still need review. Every clause of a confirmed value must be supported
by owner input; agent-derived consequences belong in advice or a separate assumed
fact. T030 found this boundary violated and prompted clearer guidance, not a new
semantic validator. Partial answers must settle their own properties and leave
genuinely different unresolved properties explicit. Do not rename a
topic to bypass an unknown or repeated-question guard. T023's deterministic checks
do not establish live reliability or repair T022's historical failures; another
live check needs a new reviewed plan and allowance. T024 and T025 record subsequent
seeded and unseeded checks; their scope and remaining semantic limits are on the
work board.

## D012: Retain one stale assessment for reconsideration

- Date: 2026-11-01; status: accepted implementation choice, design reviewed in T026.
- Context: T025 introduced an unlabeled approval policy, temporarily lost an
  existing-copy caveat and incompletely cited a revised aggregate goal. Preparing
  a request discarded the previous assessment, leaving earlier advice unavailable
  for comparison.
- Choice: pending runtime state carries one optional `previous_assessment`, never
  alongside a current assessment or from a future revision. Preserve it through
  failed requests and explicit retry, including a lost browser response; clear it
  on successful adoption. It is stale agent-written data, not owner evidence.
  Older states default to null; native contract 2 and exported brief 1 are unchanged.

Keep the existing input cap, including this context, and fail before CLI startup
when it is exceeded. Do not truncate context or automatically merge stale advice.
The prompt requires proposed policies to be labeled wherever used, still-relevant
consequences to remain in explanations and acceptance checks, and revised aggregate
facts to cite retained components as well as the correction. Latest owner sources
take priority over obsolete or erroneous agent advice. Existing source/confirmation
guards remain; keyword checks or unconditional source unions cannot establish
semantic correctness. Deterministic checks verify context handling and supplied
output only. Live improvement, complete source coverage and Level 0 acceptance
remain unestablished.

## D013: Ask only about unresolved properties

- Date: 2026-11-01; status: accepted implementation choice, design reviewed in T028.
- Context: T027 bound approval questions to a confirmed ability to request changes.
  An unknown-button answer could then replace that different known property.
  The same run retained an obsolete access fact and omitted new requirements.
- Choice: new proposed questions require an unknown or assumed target, checked
  before suppression or adoption. A genuine conflict must first make its same
  target unresolved using a later owner source under the existing guards.
  Preserve legacy state readability; reject unknown-button actions on settled
  targets in preparation and before browser optimistic edits. Disable that action
  for older mismatched questions and explain the correction/provisional route.

Keep native response 2 and brief 1. Refine the prompt to review affected current
facts, update superseded values at existing keys, and record independently
changeable requirements outside assessment prose. Do not automatically delete old
confirmed facts, force updates for no-change replies or use domain-specific text
matching to infer contradictions. Offline exposed-case checks verify the narrower
question rejection; scripted corrections verify supplied valid transitions. These
checks do not establish complete extraction, semantic consistency or live model
improvement. T027's raw failures remain unchanged.

## D014: Separate development HTTP checks from recorded-view review

- Date: 2026-11-01; status: accepted preparation choice, design reviewed in T029.
- Context: T027's browser failures interrupted a bounded model check and left its
  remaining stages unperformed.
- Choice: targeted development runs may use sequential production in-process
  ASGI/HTTP handlers with one coding agent. Inspect recorded results separately in
  a replay viewer with no agent or inference routes. Label its controller changes,
  rendered views and downloads as replay; original HTTP responses establish export
  gating. A viewer failure neither consumes nor restarts model calls.

This changes development procedure, not Level 0 acceptance or owner-comprehension
requirements. Freeze and review source, settings and limits before a later
authorized execution. Preparation, scripted rehearsal and replay alone establish
no model-quality result or actual live UI flow.

## D015: Name the agent in the plan and run acceptance through one harness

- Date: 2026-11-02; status: accepted; decision owner: repository owner.
- Context: T031's Codex run stopped at 15 of 98 calls on a shared usage limit. The
  owner then chose Claude Code with Haiku 4.5 for the test and agreed the harness
  should not depend on one agent. The T019, T022 and T031 harnesses were one-off
  `/tmp` scripts, and Codex assumptions ran through their schema, parsing, version
  and quota handling.
- Choice: acceptance runs use the tracked `scripts/acceptance_run.py`. A frozen plan
  names the agent, model, limits, cases and source. A small adapter holds what really
  differs: schema delivery, login check, how a native failure appears, and any
  inference-free quota read. Claude Code receives schemas through native
  `--json-schema`, with the same strict local validation; fenced text stays rejected.
  The package keeps no live execution mode. Operator and runner share files in the
  run directory, so no port or token is needed and actions stay as evidence.
- Consequences: all fourteen jobs rerun on Haiku 4.5 under plan 4 with the same
  cases. Codex plan 3 rows stay separate evidence and are never combined with them,
  because a comparison across agents would not be matched. A run can only start or
  resume against an approval of its exact plan, harness and journal hashes. Claude
  has no inference-free quota read, so a usage limit can still cost the job that hits
  it, and the quota is shared with the coordinating session. Comparing agents is not
  an aim of Level 0; this choice says nothing about which agent is better.

## D016: Give Claude more structured-output attempts and match quotes by words

- Date: 2026-11-02; status: accepted; decision owner: repository owner.
- Context: in the plan 5 Sonnet run, Claude Code gave up on two wrapper jobs after its
  default five structured-output attempts. Each time it had sent about 5 KB of JSON
  that did not parse. Three more calls succeeded only on the fifth attempt, while the
  smaller baseline reply never needed more than two. The plan 4 Haiku run also lost
  N04-wrapper because quote matching compared bytes, so a model that flattened an
  owner's line break was rejected.
- Choice: the product sets Claude Code's `MAX_STRUCTURED_OUTPUT_RETRIES` to 10 for
  every Claude call, wrapper and baseline alike. The setting is undocumented and read
  by the installed CLI. Evidence quotes match when the owner wrote the same words in
  the same order, ignoring differences in spacing and line breaks; different words
  still fail. The owner chose the retry setting over shrinking the reply contract.
- Consequences: a call can make more hidden attempts and use more quota. Sonnet's
  recorded attempts took about 16 seconds each, so ten fit the unchanged 300-second
  request limit; Haiku's slower first responses would not, so a slower model needs
  its own limit. The setting overrides any user value. This treats the symptom; the
  large reply contract remains and may be worth simplifying later. A future CLI could
  rename or drop the setting, which would quietly restore five attempts.

## D017: Require provisional results to carry what they leave open, and size the baseline separately

- Date: 2026-11-03; status: accepted; decision owner: repository owner.
- Context: plan 6 adjudication confirmed that a provisional result with no open
  questions, limitations or criteria could replace a fuller result and be exported,
  although Level 0 step 5 requires a provisional export to carry its unresolved
  questions. The operator also missed seven of eight required provisional closes at
  the question limit. And two transcript baselines stopped on the product's
  32,000-byte input budget, which a plain chat would not face, while the wrapper's
  compact state stayed under it.
- Choice: a provisional result must list open questions and limitations, with every
  detail the owner said they do not know kept open under its fact key; the prompt says
  so. Across 62 earlier provisional results, this rule rejects none of the sound ones
  and both empty ones. The harness forces the provisional close from the question limit
  onward on both approaches and records that it did. A plan may give the transcript
  baseline its own input limit; the owner chose 64,000 bytes, while the wrapper keeps
  the product's 32,000.
- Consequences: a refused result fails like other invalid output, keeping the owner's
  answers and the earlier result as outdated and unexportable. Nothing yet stops a
  well-formed but weaker result from replacing a fuller one. The input limits now
  differ by approach on purpose, so a later comparison must say so. Plans 4 to 6 keep
  their recorded shared limit.


## D018: Account explicitly for changed assessment items

- Date: 2026-11-03; status: accepted implementation design; separate Codex design review passed
  in T033 before implementation.
- Context: D017 rejects empty provisional results but permits silent loss of
  material content from nonempty replacements. Prose length and list size cannot
  distinguish a concise rewrite from a weaker recommendation.
- Choice: native contract 3 adds `assessment_changes`. Enumerate the
  previous assessment's risk reasons, hidden requirements, recommendation
  rationale/alternatives/owner responsibilities, criteria, open questions and
  limitations by field and zero-based index. Unchanged items can move within the
  same list without a change record. Every other prior item requires one explicit
  record mapping it to replacement items in the same list, or explaining removal.
  Records contain a nonblank reason and a basis: `reworded`, `owner_update` or
  `advice_withdrawn`. Rewording requires replacement items. Owner updates quote
  substantive owner input newer than the last adopted assessment; withdrawal
  explicitly identifies earlier agent advice as unsupported or superseded and
  does not turn it into owner evidence. Validate references, duplicate records,
  source presence and complete accounting before adoption, for every disposition.
- Limits: this detects unaccounted changes, not whether a claimed rewrite retains
  meaning or a withdrawal is justified. Human semantic review remains necessary.
  Do not auto-merge old advice, retry, or replace a failed result with stale output.
  Scalar summary, recommendation kind and risk level are outside this list guard.
  Enforcement belongs in adoption against the retained anchor; failed requests
  keep that anchor and its owner-evidence boundary. With no prior assessment,
  only an empty change list is valid. Extra bookkeeping adds response size and may
  cause more native structured-output attempts or stops; no live reliability
  improvement is established. Retain prior state compatibility and export
  schema 1. The baseline remains
  transcript-only and does not have this wrapper-only gate.
- Observed limit: the partial plan 7 run stopped four of its first five wrapper
  jobs on accounting, with trigger items largely retaining meaning under separate
  review. This is a protocol burden, not evidence those revisions lost material
  content. T033 records the failures; no relaxation or rerun changed that frozen
  run. Semantic weakening remains outside the structural guarantee.


## D019: Confirm the N06 hidden-need omission

- Date: 2026-11-04; status: accepted; decision owner: repository owner.
- Context: plan 6's N06 wrapper discussed private access to a daughter's dance-show
  videos but never asked whether other people appear or carried sharing permission
  as an open decision. Agent reviewers disagreed on applicability of undisclosed
  facts; the adjudicator requested human confirmation of this hidden-need omission.
- Choice: the repository owner answered “Confirm” after Codex recommended confirming
  the blocking omission and explained the evidence and limits. A conditional question
  or explicit open decision would address this consequential uncertainty without
  asserting that undisclosed people actually appear. The accepted rationale is the
  one presented by Codex; the owner's response did not supply a separate rationale.
- Consequences: confirm N06-wrapper's blocking risk/unknown-handling finding under
  L0-04/L0-05. Preserve original reviews and outputs; the
  [human review packet](../artifacts/l0-n06-human-review.json) records the ruling.
  This decision does not itself rule the invite-only recommendation unsafe, change
  other case verdicts, establish Level 0 acceptance, supply participant consent or
  approve T032 sign-off. Adult-session arrangements remain to be agreed.


## D020: Rehearse owner sessions with AI readers

- Date: 2026-11-04; status: accepted rehearsal choice; source: repository owner
  instructed “Use AI agents to mimic human” while choosing the T011 approach.
- Choice: use three separate AI reader contexts to walk through recorded fictional
  handoffs and give first teach-back answers before any corrective feedback. Label
  personas, intended actions and responses as generated simulation. Preserve source
  hashes, actual handoff content and failed states. An evidence reviewer compares
  responses with visible text and case facts separately.
- Limits: this is a rehearsal of materials and explanations. It supplies no actual
  adult participant, voluntary consent, browser interaction, comprehension estimate
  or owner sign-off. No product inference call or acceptance retry is needed to read
  the recorded outputs. T011 and T032 remain incomplete under the current scope.
  The human-session template stays unfilled. The owner selected simulation now;
  no change to the adult-evidence criterion is inferred from that selection.


## D021: Tolerate unambiguous continuity references and surface sharing authority

- Date: 2026-11-04; status: implemented and separately reviewed under T035;
  366 Python tests and 14 UI checks pass. The 2026-11-05 browser check asked a
  sharing-permission question, then stopped on an unaccounted reason rewrite.
  A later prompt example has 52 focused checks. One fresh exposed browser run
  then accepted an unknown reply and completed correction, recovery and download,
  with one stale access question; it cannot isolate the example's effect. No
  general semantic improvement or reliable completion is established.
- Context: four v7 wrapper attempts stopped on accounting although trigger items
  largely preserved meaning. Two used `owner_responsibilities/0` instead of the
  full recommendation field. One included a redundant unchanged-item record;
  other genuine rewrites were still unaccounted. D019 confirmed an omitted
  consequential sharing-permission question.
- Choice: keep native contract 3, canonical state/brief 1 and complete
  accounting for changed tracked items. Normalize only the unambiguous shorthand
  list fields `rationale`, `alternatives` and `owner_responsibilities` to their
  `recommendation.` paths, plus outer spaces. Check previous/current references
  in their own snapshots. Reject duplicate prior references after normalization,
  unknown/out-of-range references, cross-list replacements and all unaccounted
  changed items. Permit optional records for unchanged prior items, while still
  validating their reason, replacement and owner-evidence rules. Ask the agent to
  copy still-relevant wording rather than rewrite it for style, append independent
  new items, and account for even a changed explanation/reason. Do not infer
  semantic equivalence from wording or guess a missing change record.
- Sharing guidance: before advising collection or sharing of content about people,
  consider who is represented and whether authority or permission remains unknown.
  Ask a consequential question or carry an explicit condition when relevant;
  record no undisclosed person or permission as an owner-confirmed fact. This is
  contextual risk clarification, not a universal consent question or legal ruling.
- Limits: alias tolerance and redundant-record handling reduce syntax friction,
  not semantic uncertainty. Missing accounting for a reason rewrite still stops
  adoption. Prompt guidance needs live verification; software tests cannot prove
  hidden-need discovery. Preserve all frozen v7 outputs and finish its unstarted
  jobs before changing runtime source.
- Follow-up on 2026-11-05: after preserving the closed two-call browser failure,
  add a context-neutral unknown-reply example. Copy the still-relevant prior
  open-question object exactly, put independent status advice in a new limitation,
  or account explicitly for a rewritten reason with `reworded` and no evidence.
  A bare unknown is not substantive owner evidence or resolution. The accounting
  guard is unchanged. This is a prompt hypothesis requiring a new bounded check;
  the failed attempt is not retried or reclassified.

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
