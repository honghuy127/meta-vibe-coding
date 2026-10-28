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
| L0-08 | Export an engineering brief | The Developer View provides a parseable structured artifact with goal, users, requirements, constraints, data/access needs, risks, recommendation, assumptions, open questions, and acceptance criteria. Its format will be selected in T002. |
| L0-09 | Keep both views consistent | Both views are derived from the same current state. Neither contradicts confirmed answers or turns assumptions into facts. |
| L0-10 | Handle varied software ideas | The acceptance cases below exercise different domains and solution types through both views, without domain-specific hardcoding. |

Ask only if different answers could materially change a recommendation. Explain
why a consequential question matters. If an owner cannot answer, preserve the
unknown and explain whether the recommendation is provisional or needs the answer
before it can proceed. Never fabricate an answer to finish the flow.

T002 must define the state contract before implementation relies on it: original
intent, interpreted goal, users, usage, data, access, content, operating constraints,
risk reasons, recommendation, assumptions, and open questions. Define unknown
values, answer provenance, update rules, and the export format. Keep both views
derived from that state.

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

Compare the same model using a strong prompt with the proposed stateful flow.
The baseline prompt must ask it to clarify consequential unknowns, consider
existing tools or no build, recommend the minimum sufficient solution, explain
use/data/cost/maintenance, and produce both views with explicit assumptions and
open questions. Preserve the exact prompt and configuration with the results.
Both approaches receive the same initial request and access to operator answers.

Proposed local-review limits are five clarification questions, ten minutes, and
one attempt per case and approach. A question counts even when bundled in one
message; a final recommendation does not. Stop at the limit and record unfinished
work. T004 must set matching token limits and an owner-approved total monetary cap
before paid calls. Do not silently grant extra retries to one approach; retain
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

Level 0 does not generate application code, integrate a coding agent, provision
infrastructure, deploy an application, integrate authentication or payment,
monitor a service, or manage an operational system. It does not require a
multi-agent runtime or a complex database. Any retained conversation data needs
an explicit purpose, storage location, and deletion policy before collection.

Repository collaboration can use multiple people and agents without changing
these product boundaries.

## Implementation sequence

1. **T010: Define acceptance.** Review the [cases and procedure](#acceptance-cases)
   above before evaluating outputs. These define product checks, not a paper
   protocol or completed evidence.
2. **T002–T004: Define and compare.** Specify state and interaction in this document;
   compare an existing tool or strong prompt with the smallest custom prototype.
   Record the selected approach, dependency reuse, and cost assumptions in the
   decision log. Review model/provider data handling before real input is sent.
3. **T005: Build one complete path.** Implement idea entry through export, including
   one changed-answer path. Then cover the contrasting demos, unknown answers, and
   failure handling. Add focused tests and exact local setup/run/check commands.
4. **T006: Review acceptance.** Exercise the cases with a second contributor. Keep
   raw outputs and failures in an appropriate artifact location; summarize only
   decisions and blockers in the board. Fix serious omissions and contradictions.
5. **T011: Check owner use.** After authorization and data-handling decisions, run
   bounded adult sessions. Check whether owners can explain consequences and the
   next action. Decide whether to simplify, revise, release a limited demo, or
   progress to L1. Publication is not an exit condition.

Assign a human owner, reviewer, and resource cap before scheduling paid or
participant-facing work. There is no committed launch date or API budget.

## Milestone review

Exercise the acceptance criteria against recorded demo runs, including a changed
answer and an unresolved answer. Review both the plain-language experience and
the structured artifact. Record failures and their severity, not only successful
screenshots or plausible-looking briefs.

A software smoke test establishes that a flow runs. Expert review can assess its
engineering recommendations. Claims about comprehension, cognitive burden, or
improved ownership need an evaluation protocol and participant evidence. No such
study has been conducted in this repository.

Before a public demo, resolve model/provider choice, handling of submitted ideas,
deployment authority, and expected operating cost. A working local prototype
alone does not establish readiness to collect real user data or publish it.
