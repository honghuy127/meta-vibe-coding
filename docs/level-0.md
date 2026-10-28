# Level 0: Intent Interpreter

Status: working product scope, aligned with the
[Level 0 proposal](meta-vibe-coding-proposal.md#level-0-intent-interpreter).
Acceptance criteria below make that scope reviewable; they are not evaluation
results. Changes to the milestone belong in the [decision log](decisions.md).

## Intended outcome

This is a general tool for vibe coding across software ideas and domains. The
Kanji website motivated the project; it is not a target application or a required
product specialization.

A non-expert describes an idea. The system clarifies the decisions that matter,
recommends the simplest suitable solution, explains the consequences, and produces
a structured brief. Recommending an existing product or advising against a custom
build is a valid outcome.

The owner can understand the recommendation without choosing a framework,
database, or hosting architecture. A downstream developer can identify the goal,
constraints, assumptions, risks, and unresolved information from the same state.

## Required behavior

| ID | Capability | Acceptance evidence |
| --- | --- | --- |
| L0-01 | Accept a free-form idea | The original idea is retained separately from the interpreted goal. |
| L0-02 | Maintain structured state | State distinguishes confirmed answers, assumptions, and unknowns; a revised answer updates dependent recommendations. |
| L0-03 | Clarify adaptively | Each question has a stated decision it could change: solution, architecture, risk, or operations. Questions irrelevant to the current idea are skipped. |
| L0-04 | Find hidden requirements | The result identifies consequential needs omitted from the prompt, with reasons and any uncertainty. |
| L0-05 | Assess risk | Low, medium, high, or unknown is accompanied by reasons. Missing information is not silently interpreted as low risk. |
| L0-06 | Recommend a minimum sufficient solution | The recommendation explains fit, burden, and trade-offs; it considers using an existing tool or not building where relevant. |
| L0-07 | Explain consequences | The Owner View explains use, data, likely costs or cost unknowns, and maintenance implications in plain language. |
| L0-08 | Export an engineering brief | The Developer View exports the versioned JSON brief defined below, covering goal, users, requirements, constraints, data/access needs, risks, recommendation, assumptions, open questions, and acceptance criteria. |
| L0-09 | Keep both views consistent | Both views are derived from the same current state. Neither contradicts confirmed answers or turns assumptions into facts. |
| L0-10 | Handle varied software ideas | The acceptance cases below exercise different domains and solution types through both views, without domain-specific hardcoding. |

Ask only if different answers could materially change a recommendation. Explain
why a consequential question matters. If an owner cannot answer, preserve the
unknown and explain whether the recommendation is provisional or needs the answer
before it can proceed. Never fabricate an answer to finish the flow.

## Project state and brief contract

Use JSON with `schema_version: 1` for state and exported briefs. This defines the
logical contract; [D006](decisions.md#d006-small-local-web-app-with-a-local-model)
selects Pydantic strict models and application validators. State
is scoped to one idea. Persistence and import are not implied by export support.

| State field | Type and meaning |
| --- | --- |
| `schema_version`, `revision` | Integers; version is 1, revision starts at 1 and increases whenever owner input or an adopted assumption changes the state. |
| `raw_intent` | Original idea, unchanged. It is the source identified as `t0`. |
| `turns` | Ordered owner replies/corrections, each with a unique `id` and original `text`; retain earlier replies. The idea is not copied here. |
| `facts` | Map from stable lower-case dotted keys to the fact records below. Use `goal`, `users.primary`, `usage.environment`, `data.persistent`, `data.personal`, `data.sensitive`, `access.public`, `access.accounts`, `content.updates`, and `operations.budget` where relevant. Give individual requirements/constraints stable keys such as `requirements.r1`; additional topics can be added without changing the envelope. |
| `questions` | Ordered records with `id`, `topic`, `text`, `decision`, and nullable `answer_turn_id`. `decision` states what a different answer could change. |
| `assessment` | Null until a valid current result is available; otherwise the assessment below with matching `based_on_revision`. The UI may retain the previous snapshot as visibly stale. |

Each fact has `value`, `status`, and `source_turn_ids`. Values are JSON scalars or
arrays of scalars; use separate semantic keys for independently revisable facts.
Status is `confirmed`, `assumed`, `unknown`, or `not_applicable`. Confirmed facts
must be supported by explicit owner input, including the initial idea. A model's
inference remains assumed until the owner confirms it. Unknown and not-applicable
facts have null values; the latter needs a recorded reason. An assumed fact also
needs a reason. Null is reserved for unknown/not-applicable facts. Missing keys
mean not yet considered; they never imply false. `source_turn_ids` is an array of
existing owner turn IDs, nonempty for confirmed facts. A bare “continue” does not
confirm every assumption. When a later answer supersedes an earlier one, use its
source ID for the current fact and retain the earlier text in `turns`.

For example, these are different fictional fact records:

```json
{
  "access.accounts": {"value": false, "status": "confirmed", "source_turn_ids": ["t1"]},
  "data.sensitive": {"value": null, "status": "unknown", "source_turn_ids": []},
  "users.secondary": {"value": [], "status": "confirmed", "source_turn_ids": ["t2"]}
}
```

An assessment contains `based_on_revision`, `disposition`, `risk`,
`hidden_requirements`, `recommendation`, `acceptance_criteria`, `open_questions`,
and `limitations`. Disposition is `needs_answer`, `provisional`, or `ready`.
Risk has `level` (low/medium/high/unknown) and nonempty `reasons`. Each hidden
requirement has `text` and `reason`; it remains a proposal until confirmed.
Recommendation has `kind`, `summary`, `rationale`, `alternatives`, and
`owner_responsibilities`. Kind is `existing_tool`, `manual_workflow`,
`local_utility`, `static_site`, `application`, `do_not_build`, or `undecided`.
Each open question has `topic`, `text`, `blocks_recommendation` (boolean), and
`reason`. A blocking unknown can change the suitability of the proposed solution;
other questions may be carried forward explicitly. Rationale, alternatives, owner
responsibilities, acceptance criteria, and limitations are arrays of plain-language
strings. An empty collection means none identified, not proof of completeness.

The engineering brief includes `schema_version`, `revision`, `raw_intent`, `facts`,
and every assessment field except `based_on_revision`. Preserve fact statuses and
source IDs; include only referenced owner turns as `sources`, including `t0` if
referenced. Show the export contents before download; conversation history is not
included wholesale. Both views and the export use the same validated snapshot.

Validation must reject unsupported versions, invalid types/enums, duplicate turn
or question IDs, dangling source references, unknown facts with non-null values,
and an assessment for a different revision. `ready` requires a confirmed goal,
a decided solution, acceptance criteria, and no blocking open questions.
Unresolved consequential facts require a provisional result or `needs_answer`.
Structural validity alone does not establish that a recommendation is appropriate.

Owner inputs, adopted fact changes, and their revision form one validated update,
which clears the active assessment until a matching result is available.
Adopting a model-proposed assumption also advances the revision; merely regenerating
an assessment does not. Commit a matching assessment atomically only after its
source facts and revision are validated. `needs_answer` means no suitable option
can yet be recommended; `provisional` means an option is useful under explicit
conditions. Neither disposition is permission to start implementation.

## Interaction flow

1. **Describe.** Accept an idea and show the interpreted goal as an editable
   understanding. Mark inferred details as assumptions. Do not make the owner
   confirm a questionnaire or choose a stack before providing value.
2. **Clarify.** Ask one consequential question at a time, explaining why it matters.
   Allow a free-text answer, “I don't know,” correction of an earlier answer, or
   a request for a provisional result. Do not repeat a resolved question unless
   new input creates a genuine conflict. Use the acceptance-plan question limits.
3. **Recommend.** Show the Owner View first: understood goal, proposed solution and
   why, data/access implications, cost unknowns, owner responsibilities, and next
   action. Expose assumptions and unanswered decisions in plain language. The
   Developer View shows the corresponding structured brief, not a separate opinion.
4. **Revise.** Append owner corrections to `turns`, update supported facts, and
   advance the revision. If new input is ambiguous, ask rather than overwrite a
   confirmed fact. Reassess risk, alternatives, recommendation, and acceptance
   criteria together; retire dependent assumptions. Keep the previous result
   labeled outdated and disable its export while the new result is being prepared.
5. **Hand off or recover.** Enable JSON download only for a valid current result.
   A provisional export must carry its unresolved questions; it is not ready to
   implement. On failure, retain owner answers, explain the failed step, and offer
   an explicit retry. A late response for an older revision must never replace
   the current result. For the same revision, accept only the latest requested
   assessment using a request ID controlled outside model output. Starting a new
   idea requires an explicit reset.

These rules cover V01–V03 without hardcoding their domains. V04 checks invalid
output and service failure; T005 must also check out-of-order responses and export
attempts during revision. No view should claim an update succeeded before its
current snapshot has passed validation.

## Acceptance cases

These fictional cases define expected behavior, not completed results. Start each
case with only its quoted request. The operator reveals the listed facts when a
relevant question is asked; do not give the system this table or its expected
answer. For an unlisted fact, answer “I do not know” and record the question.
Accept justified alternatives that satisfy the confirmed facts; no specific
framework, provider, or exact wording is required.

| ID and initial request | Facts available to the operator | Acceptable recommendation and important checks |
| --- | --- | --- |
| C01 — Public content: “I want a website for our gardening club.” | Public event information; no accounts, sign-ups, or saved visitor data; organizer updates monthly; phone access matters. | Existing site builder or static site; explain content updates and hosting responsibility. Do not add accounts or a database without a reason, or promise zero cost. |
| C02 — Local automation: “I want to rename a folder of photos.” | One adult's laptop; files stay local; prefix names with the photo metadata date and retain the originals; the owner wants to check changes first. | Existing batch-renaming tool or small local utility; require preview, collision handling, and a recovery path. Cloud upload, public hosting, and accounts are unjustified. |
| C03 — Simple game: “I want to make a little puzzle game.” | Solo play in a browser; fixed puzzles; no scores saved between visits; no leaderboard, purchases, or accounts. | Small static browser game or suitable existing game-building tool; preserve a viable custom-build option. Explain content and testing needs without inventing a backend. |
| C04 — Shared planning: “I need an app to organize household chores.” | Three adults already use a shared spreadsheet; a weekly checklist and editing from phones cover every stated need; no reminders or integrations are wanted. | Improve the shared sheet or use an existing checklist. Explain why new software adds little value; do not force a custom application. |
| C05 — Personal records: “I want to track my home inventory.” | One adult; names, purchase prices, and photos; phone and laptop access; records must survive device loss; sharing is unnecessary. | Suitable existing inventory tool or small persistent app, with storage, access, export, and backup needs explicit. A local-only file without a recovery/sync plan does not meet the request. |
| C06 — Private sharing: “I need to share documents with my bookkeeper.” | Contracts contain personal details; only the owner and bookkeeper should have access; access must be revocable; browser access matters. | Evaluate an existing service with restricted sharing and revocation. Explain access and provider responsibilities; public links or custom infrastructure without justification fail. Do not ask for actual documents. |
| C07 — Sensitive secrets: “I want a website where my family stores passwords.” | Shared family access is needed; the owner has no security or maintenance experience. | Recommend evaluating a specialized password manager and explain recovery/access responsibilities. Do not default to a custom vault or ask for real credentials. |

These questions illustrate useful clarification; they are not a mandatory script:
“Who needs access?”, “Must it work on another device?”, “What happens if a file is
changed incorrectly?”, and “What does your current tool fail to do?” Ask only
when the answer can change a decision. Skip questions already answered.

### Changes, unknowns, and failures

Apply these variations after the base cases. Preserve the earlier answers so the
reviewer can see what changed and whether both views were updated.

| ID | Variation | Required response |
| --- | --- | --- |
| V01 — Changed answer | After C01, add: “Actually, members must sign in and save attendance across devices.” | Supersede the earlier no-accounts/no-persistent-data requirements; revisit access, storage, personal data, and alternatives in both views. Do not leave the earlier recommendation presented as final. |
| V02 — Unknown answer | In C05, answer “I do not know” to whether photos contain sensitive details. | Preserve the unknown, explain its consequence, and give a provisional recommendation or a focused next step. Do not silently label the information non-sensitive. |
| V03 — Correction | In C02, correct the date requirement: “Use the date in the filename, not the photo metadata.” | Update the naming requirement and acceptance criteria in both views; retain the original request separately. |
| V04 — Service failure | Interrupt a model request or return an invalid brief during any case, once an implementation exists. | Show a recoverable failure, preserve confirmed answers, and mark incomplete output. Do not present a canned response, stale brief, or fabricated success as the result. |

### Review rules

For each case, mark recommendation fit, clarification, risk/unknown handling,
Owner View clarity, and brief/view consistency as `pass`, `fail`, or `not checked`.
Record the supporting question or output passage and the relevant L0 capability
ID. Check original-intent retention, revised answers, and export validity once the
T002 contract is implemented. A plausible-looking answer alone is insufficient.

A **blocking failure** changes a consequential decision or misleads the owner:
contradicting confirmed facts; hiding material uncertainty; omitting a necessary
access, recovery, or data requirement; requesting secrets; unsupported claims of
safety or price; a materially inconsistent brief; or refusing a benign achievable
request without a reason. Out-of-scope code generation or external actions also
block acceptance. These failures cannot be averaged away by other good outputs.

A **minor issue** affects presentation without changing meaning, such as a repeated
sentence. Record and fix it without treating it as equivalent to a data-risk
omission. A case passes only when all five review dimensions pass and no blocking
failure remains. `Not checked` means incomplete, not passed. A provisional answer
can pass when uncertainty and the next necessary decision are explicit.

T006 must cover C01–C07 and V01–V04 before accepting L0. A second contributor
reviews blocking failures, disputed judgments, and proposed alternative solutions.
Unresolved disagreement leaves that case open. Fixes require rerunning the affected
case and dependent variations; report every attempt rather than only the best.

### Compare the simplest solutions

Use C01–C07 as development cases. For acceptance, another contributor prepares
one fresh case per category with different goals and constraints, including
at least one changed answer and one unknown. Freeze those facts and expectations
before inspecting outputs. Rewording the public examples alone is not fresh
coverage; keep acceptance cases out of prompt tuning and report any exposure.

Within a backend, compare the same model using a strong prompt with the proposed
stateful flow. Across backend types, follow D007 and identify model/harness
differences; do not attribute their combined effect solely to the wrapper.
The baseline prompt must ask it to clarify consequential unknowns, consider
existing tools or no build, recommend the minimum sufficient solution, explain
use/data/cost/maintenance, and produce both views with explicit assumptions and
open questions. Preserve the exact prompt and configuration with the results.
Both approaches receive the same initial request and access to operator answers.

Proposed local-review limits are five clarification questions, ten minutes, and
one attempt per case and approach. A question counts even when bundled in one
message; a final recommendation does not. Stop at the limit and record unfinished
work. Apply D007's backend-aware limits; external spending stays disabled until
an account and spending cap are authorized. Do not grant extra retries to one approach; retain
technical failures and identify any diagnostic rerun separately.

Compare blocking failures first, then decision fit, question burden, correction
effort, latency, and cost. Prefer the simpler workflow when it meets the same needs;
record the concrete benefit that justifies added state or UI. No evaluation has
been run, and these limits do not authorize spending or participant recruitment.

### Check owner understanding

In authorized adult sessions (T011), ask the owner to explain in their own words:
what is recommended and why; who can access which data; what costs remain unknown;
what they must maintain or recover; and the next action or unresolved decision.
Score each as understood, needs help, or misunderstood, against the actual case
facts. Record facilitator help and any confident misunderstanding. Do not score
satisfaction as comprehension or coach an answer into a pass. Resolve important
misunderstandings before claiming the handoff supports informed ownership.

## Boundaries

Level 0 does not generate application code, supervise downstream construction,
provision infrastructure, deploy an application, integrate authentication or payment,
monitor a service, or manage an operational system. It does not require a
multi-agent runtime or a complex database. Any retained conversation data needs
an explicit purpose, storage location, and deletion policy before collection.

A coding-agent wrapper may supply planning/reasoning under
[D007](decisions.md#d007-interchangeable-inference-and-agent-backends), with its
action permissions restricted and output validated like any model response.
Repository collaboration can use multiple people and agents without expanding
these product boundaries.

## Implementation sequence

The [work board](work-board.md) holds task status and ownership. T010 defines the
acceptance procedure; T002–T003 define the contract and interaction above. T004
defines interchangeable backends in D007; T005 builds the common core, verifies
one backend, and adds other modes incrementally with exact setup/check commands.
T006 exercises acceptance with another contributor; T011 checks authorized adult
use before deciding whether to simplify, revise, or progress to L1.

Assign a human owner, reviewer, and resource cap before paid or participant-facing
work. There is no committed launch date or API budget.

## Milestone review

Record actual case outputs, failures, and check results against the acceptance
procedure above. Structural validation and a software smoke test do not establish
recommendation quality or owner comprehension. No product cases or adult sessions
have run. Before a public demo, resolve provider data handling, deployment authority,
and operating cost; readiness must be demonstrated in the intended environment.
