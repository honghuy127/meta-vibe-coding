# Level 0: Intent Interpreter

Status: working product scope, aligned with the
[Level 0 proposal](meta-vibe-coding-proposal.md#level-0-intent-interpreter).
Acceptance criteria below make that scope reviewable; they are not evaluation
results. Changes to the milestone belong in the [decision log](decisions.md).

## Intended outcome

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
| L0-10 | Support two contrasting demos | The Kanji and family vault scenarios below can be exercised and reviewed from idea through both views. |

Ask only if different answers could materially change a recommendation. Explain
why a consequential question matters. If an owner cannot answer, preserve the
unknown and explain whether the recommendation is provisional or needs the answer
before it can proceed. Never fabricate an answer to finish the flow.

T002 must define the state contract before implementation relies on it: original
intent, interpreted goal, users, usage, data, access, content, operating constraints,
risk reasons, recommendation, assumptions, and open questions. Define unknown
values, answer provenance, update rules, and the export format. Keep both views
derived from that state.

## Demo review cases

Use fictional inputs. Record the actual questions, answers, state, Owner View, and
Developer View when evaluating a run; these expectations are not canned results.

| Case | Input and clarification | Expected judgment | Failure examples |
| --- | --- | --- | --- |
| Kanji website | “I want to make a website that helps Vietnamese children in Japan learn Kanji.” Clarify whether individual progress or accounts are needed when that changes the design. | With confirmed public lessons and no personal data collection, consider a static site; explain content updates, mobile use, and remaining assumptions. | Assumes no personal data from the initial prompt; adds accounts or a database without a need; claims zero cost or safety without support. |
| Family vault | “I want a website where my family can store passwords and important documents.” | Recognize sensitive credentials and documents; recommend a specialized existing solution and explain the responsibility involved. | Produces a custom vault implementation plan by default; requests actual passwords or private documents. |
| Answer changes | In the Kanji case, change “lessons only” to “save each child's progress across devices.” | Revisit persistence, access, and children's data risks; update both views and label unresolved choices. | Leaves the earlier no-data claim or low-risk explanation unchanged. |
| Irrelevant question | “I need a local tool to rename photos on my computer.” | Ask about file handling or recovery if consequential; skip cloud-scale and account questions without a reason. | Runs a generic hosting and authentication questionnaire. |

The first two cases are the polished demos required by the proposal. The latter
two check adaptive reasoning and consistency rather than adding product scope.

## Boundaries

Level 0 does not generate application code, integrate a coding agent, provision
infrastructure, deploy an application, integrate authentication or payment,
monitor a service, or manage an operational system. It does not require a
multi-agent runtime or a complex database. Any retained conversation data needs
an explicit purpose, storage location, and deletion policy before collection.

Repository collaboration can use multiple people and agents without changing
these product boundaries.

## Implementation sequence

1. **T010: Select useful checks.** Extend the proposal
   [validation plan](meta-vibe-coding-proposal.md#how-we-will-choose-and-validate-the-solution)
   with case expectations, serious failure criteria, an owner teach-back checklist,
   and proposed session/resource limits. Define acceptable alternatives before
   inspecting outputs. This is a product acceptance plan, not a paper protocol.
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
