# Decision log

Record decisions that affect scope, interfaces, dependencies, data handling, or
evaluation. Routine local edits do not need an entry. Keep accepted entries as
history; supersede them with a linked new entry when a choice changes.

Use a stable ID, date, status (`proposed`, `accepted`, or `superseded`), decision
owner, context, choice, and consequences. An agent can propose a choice; human
approval is required for changes to scope, acceptable risk, or external authority.

## D001: Start with Level 0

- Date: 2026-10-28
- Status: accepted; backend restriction clarified by D007.
- Owner/source: repository owner's supplied [proposal](meta-vibe-coding-proposal.md),
  sections 20, 21, and 25 at initialization; retained in the revised
  [Level 0 section](meta-vibe-coding-proposal.md#level-0-intent-interpreter).
- Context: the long-term vision spans engineering, delivery, and operations, but
  the first prototype must test intent interpretation and engineering judgment.
- Decision: build the Intent Interpreter first. Initially exclude coding-agent
  integration, autonomous deployment, and a multi-agent product runtime. D007
  permits an agent as the reasoning backend while keeping construction out of L0.
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

- Date: 2026-10-28
- Status: superseded in part by D007 after the owner questioned the local-only choice.
- Initial choice: Python 3.12, FastAPI/Uvicorn, Pydantic 2, plain browser JavaScript,
  and local Ollama. Local models were convenient because they were installed;
  this did not establish a product need for local inference or superior quality.
- Retained: a thin web interface is a candidate for the owner experience; strict
  state validation and the strong-prompt baseline remain useful. Backend choice
  is independent of interface and must support the options in D007.
- Inspection: Python 3.12.12 and Pydantic 2.13.4 were available; FastAPI/Uvicorn
  were not installed. Local `qwen3.5:4b` was present (ID `2a654d98e6fb`, 3.4 GB).
  No inference, installation, or product acceptance run was performed.

### Qwen versus Gemma model choice

On 2026-10-28, compared the installed candidates `qwen3.5:4b` and `gemma3:4b`
against their publishers' post-trained/instruction-tuned model results:

| Benchmark | Qwen3.5-4B | Gemma 3 4B IT |
| --- | --- | --- |
| MMLU-Pro | 79.1 | 43.6 |
| GPQA Diamond | 76.2 | 30.8 |
| IFEval | 89.8 | 90.2 |

Sources: [Qwen model card, Language benchmarks](https://huggingface.co/Qwen/Qwen3.5-4B#benchmark-results)
and [Google model card, Evaluation](https://ai.google.dev/gemma/docs/core/model_card_3).
These are separately reported results with different protocols, not a matched
local experiment. Qwen's reasoning-mode configuration and generation budget can
affect results; do not assume the published scores hold under our 4,096-token,
60-second limits or for installed quantized weights. The small IFEval difference
does not establish a meaningful instruction-following advantage for Gemma.

For the optional local backend, Qwen remains the provisional candidate because
its reported knowledge/reasoning scores provide the stronger starting signal.
Keep Gemma configurable for the same acceptance cases. Neither source establishes
our clarification quality, schema validity, or local response time. T006 must
compare actual model digests, quantization, prompts, thinking settings, failures,
and latency under the same limits before finalizing the model choice.

## D007: Interchangeable inference and agent backends

- Date: 2026-10-28
- Status: selected direction following the repository owner's request for multiple
  options. Supersedes D006's local-only requirement and D001's blanket exclusion
  of agent integration; downstream construction remains outside L0.
- Decision: the product owns intent, state, clarification policy, validation, and
  owner/developer views. An interchangeable backend supplies candidate reasoning.
  A local LLM is optional; no specific model defines the product.

| Mode | Why offer it | What the adapter must handle |
| --- | --- | --- |
| Local model | Local/offline use, local data processing, and control over weights. | Ollama transport, model availability, schema support, and hardware/latency limits. |
| Commercial model API | Access to hosted models without managing inference hardware. | Vendor authentication, request/response format, schema support, usage, cost, and data handling. |
| Existing coding-agent harness | Reuse its prompting, context management, sessions, and integration surface; it may be the simplest first wrapper. | Harness lifecycle, structured result extraction, tool permissions, hidden retries, session storage, and underlying model/provider. |

These are alternative execution modes, not three agents working together. Local
and commercial APIs share the application interface, but their wire protocols need
not match. A coding-agent harness is a complete system that may itself use local
or commercial models; a locally running CLI does not imply local inference.

The core calls `assess(snapshot, schema, limits, request_id)`. Each adapter returns
candidate facts/assessment plus backend/model identity, usage, elapsed time, and
cost when available, or a normalized error. Unknown usage/cost stays unknown.
Adapters never mutate canonical state directly. The core validates output and
source references, applies revision/request checks, and then updates both views.
Prefer native structured output where available; otherwise normalize and validate
explicitly. Unsupported capabilities fail visibly rather than changing behavior.

Official integration paths checked on 2026-10-28:
[Codex non-interactive execution](https://developers.openai.com/codex/noninteractive)
supports JSON-schema final output; the [Codex SDK](https://developers.openai.com/codex/sdk)
controls threads programmatically. The [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)
exposes the Claude Code harness, with [structured output](https://code.claude.com/docs/en/agent-sdk/structured-outputs).
[OpenCode's SDK](https://docs.opencode.ai/docs/sdk/) provides a programmatic server
client and schema-based output through its v2 client. These establish possible
integration paths, not compatibility with our complete contract or an account's
access and billing terms; verify each adapter before claiming support.

At L0, agent-backed planning cannot create application code, change project files,
or deploy. Restrict filesystem, shell, network tools, inherited configuration, and
workspace access at the harness boundary; preserve any internal schema-return tool
needed to produce output. A prompt saying “planning only” is insufficient. If a
harness cannot enforce the required boundary, do not expose it as an L0 backend.
Later L1/L2 build handoff is a separate capability with explicit owner authority.

Keep app-managed session state in memory by default. Review provider retention and
agent transcripts separately: memory-only application state does not imply that a
remote API or harness stores nothing. Disclose the selected backend and destination
before sending an idea. Credentials stay server-side. Never silently fall back
between backends, change destination, or reuse an unrelated agent session.

Start T005 with the shared core and one thin direct-model adapter, selected by
available authorized access; add the second transport and one bounded agent wrapper
incrementally using the same acceptance cases. Do not implement all three agent
brands at once. Spike an existing harness first if it can satisfy the contract
with less work than custom orchestration. The FastAPI/static UI remains a candidate,
not a prerequisite for an agent wrapper. No extra dependency is added by this plan.

For comparisons, retain five questions/ten minutes and one attempt per case.
Initial direct-model limits are seven calls, 60 seconds per request, 4,096 generated
tokens per call, and 16,384 context tokens; record thinking settings and truncation.
Count harness-internal calls and retries too, or label unavailable counts and avoid
claiming equal budgets. Compare complete systems when the same model is unavailable.
Record versions, tools, permissions, failures, latency, and total effort alongside
recommendation quality. External spending remains zero until an explicit cap and
provider/account choice are authorized; existing subscriptions do not imply free
or interchangeable API access. This design change launches no model or agent runs.

## Open choices

| Choice | Resolve in | Needed before |
| --- | --- | --- |
| Review the drafted JSON state and brief contract (D005) | T002 | Depending implementation and exported artifacts |
| Review the drafted clarification and revision flow | T003 | Prototype interaction is accepted |
| Select and verify the first backend, dependencies, and setup/check commands under D007 | T005 | Claiming a runnable prototype |
| Verify backend permissions, data destination/retention, and usage limits under D007 | T005, revisited before external use | Real user input or a public demo |
| Product acceptance checks and reviewer assignments | T010, exercised in T006 | Acceptance review |
| Adult usability tasks, consent, and data handling | T011 | Participant-facing sessions |
| License and terms for external contribution or reuse | Repository owner | An intended external distribution or contribution arrangement |
