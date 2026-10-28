# Meta Vibe Coding: Technical stewardship for non-expert software creation

Meta Vibe Coding aims to help a non-expert choose, build, use, and maintain useful
software. The intended outcome is a working solution the owner can understand
and control. A paper, a new model, or a novel architecture is not a deliverable.
We can reuse good ideas, existing products, and open-source components wherever
that gives the owner a better result. The scope is general vibe coding across
websites, applications, games, utilities, and automations.

This is an internal product proposal, revised on 2026-10-28. The repository
currently contains planning and collaboration documents; no prototype or user
validation has been completed. The first delivery milestone is Level 0, described
in [the implementation plan](level-0.md). Later lifecycle capabilities remain
conditional on what we learn from real use.

## The problem to solve

A person may know what they want to accomplish without knowing what software it
requires. A parent asking for a Kanji learning website may not have considered
whether children need accounts, how lessons will be updated, or who will manage
hosting. That example motivated this project; the solution is not a Kanji learning
product. Turning any underspecified request directly into code can leave
consequential decisions hidden.

The proposed service makes consequential decisions visible before implementation
and carries them through delivery and maintenance. It should help the owner
understand what information is stored, what the service costs, who controls it,
and what happens when something goes wrong.

For the initial prototype, the intended users are adults without professional
software-engineering experience who need a small website, utility, or workflow.
The Kanji scenario is an example involving a parent; it does not require recruiting
children or collecting their data. The first validation will use fictional tasks
and, when authorized, consenting adult users.

## What success means

At Level 0, the owner receives an appropriate recommendation and understands its
important consequences. A developer receives a consistent, actionable brief with
explicit assumptions and open questions. Advising the owner to use an existing
product, simplify the request, or avoid a custom build can be a successful result.

For the eventual complete solution, success also requires that the intended users
can reach and use the product in its real environment, and that the owner can
manage access, cost, changes, backups, and recovery. A local demo cannot establish
those outcomes. Each later milestone must demonstrate the capability it adds.

We will judge the product by useful decisions and completed owner tasks. We will
not require a research novelty claim, a benchmark ranking, or publication before
adopting an approach that works.

## Ideas to borrow and adapt

A focused orientation search on 2026-10-28 found useful starting points below.
This is a selected reading list, not a comprehensive review or a comparison of
current commercial products. The adaptation column contains our design choices,
not claims that the sources have validated this product.

| Source and inspected passage | Relevant idea | Proposed adaptation |
| --- | --- | --- |
| Robinson et al., 2024, [Requirements are All You Need](https://arxiv.org/pdf/2405.13708), introduction; author version of an accepted SE 2030 workshop paper | End users expressing requirements across the software lifecycle. | Treat requirements and owner decisions as durable project state, carried from planning into later maintenance. |
| Liu et al., CHI 2023, [What It Wants Me To Say](https://arxiv.org/pdf/2304.06597), section 3 | Grounded abstraction matching connects user language to the system's interpretation in a spreadsheet setting. | Let owners inspect and correct the interpreted goal; keep their explanation consistent with the technical brief. |
| Chen et al., 2026, [Don't Guess, Just Ask](https://arxiv.org/html/2610.13022v1), sections 3–4; arXiv preprint | ReqClarifyBench evaluates interactive clarification and resulting requirement documents using simulated users. | Check the usefulness of questions and the resulting recommendation separately. Use simulated dialogues for development, then check comprehension with people. |

The search used web queries `site.arxiv.org non programmers generative AI software
development requirements clarification end user programming`,
`site.microsoft.com research "Why Johnny Can’t Prompt"`, and
`site.arxiv.org ChatDev MetaGPT software development requirements`. We followed
relevant results to primary sources and inspected the passages cited above.
Selection favored lifecycle ownership, understandable representations, and
clarification. It stopped after these design needs had concrete starting points;
other useful approaches may exist. Refresh the comparison when selecting actual
components. Access and publication metadata were checked on the same date.

Reuse should be evaluated against user fit, integration effort, maintenance,
license compatibility, and operating cost. If a well-designed prompt or an existing
product satisfies the need, that may be the solution. A custom application must
justify the additional effort through a better owner experience or reliability.

## Level 0: Intent Interpreter

The first useful version accepts an idea, clarifies consequential unknowns,
recommends a solution, and presents two synchronized views. It does not generate
application code or provision infrastructure. It can use a local model, a
commercial API, or a constrained coding-agent wrapper for reasoning, as specified
in [the backend design](decisions.md#d007-interchangeable-inference-and-agent-backends).
Its purpose is to settle the right
problem and prepare a trustworthy handoff.

The interaction is:

```text
Idea → interpreted goal → consequential questions → recommendation
                                      ↓
                         shared structured project state
                                      ↓
                     Owner View + Developer View
```

Questions should change a decision. Ask whether saved information must follow a
user between devices when that affects storage and access. Do not ask an owner to choose
between databases to express that need. When an answer is unavailable, keep it
unknown and explain whether a provisional recommendation is still useful.

The recommendation should compare only plausible alternatives: an existing tool,
a spreadsheet, a local utility, a static site, or an application. Explain why the
chosen option meets the need and what it asks of the owner. More features are not
inherently better. Refusing every request is not good judgment either.

The Owner View explains use, data, cost uncertainty, control, and maintenance in
natural language. The Developer View records the goal, users, requirements,
constraints, risk reasons, assumptions, open questions, and acceptance criteria.
Both views must reflect the same current answers. A changed answer must trigger a
review of the affected recommendation, not just update a displayed field.

Keep the stewardship policy and state independent of the chosen backend or UI.
Reuse an existing agent harness when it satisfies the interaction and permission
requirements; a thin model API integration is another valid route. Keep decision
logic, validation, and presentation independently testable, and compare the result
with a strong-prompt workflow before adding custom orchestration.
The detailed contract belongs in [Level 0 scope](level-0.md#required-behavior).

## Examples that guide development

Use varied software ideas to check general behavior. A public club website, local
file automation, simple game, shared checklist, personal inventory, private document
sharing, and password storage exercise different decisions. Their fictional inputs,
clarifying facts, acceptable alternatives, and blocking failures are defined once
in the [Level 0 acceptance cases](level-0.md#acceptance-cases).

The Kanji website remains a motivating illustration, not a required product demo
or a domain-specific implementation target. New ideas should follow the same
intent, clarification, and recommendation process. Successful development examples
do not establish that every software domain is supported.

## How we will choose and validate the solution

Start with the cheapest useful comparison: the same model with a strong stewardship
prompt versus the proposed stateful interaction. Give both the same initial ideas,
access to clarifying answers, and comparable limits on interaction and generation.
Allow both to recommend an existing tool or no build. Record the exact prompts,
model version or alias, dates, configuration, questions, answers, failures, latency,
and token usage. Differences in model access or budget must remain visible.

The [acceptance plan](level-0.md#acceptance-cases) defines fictional cases spanning
public content, local automation, games, shared planning, persistent personal data,
document sharing, and sensitive secrets.
Include unknown answers, changed requirements, and requests that need no new app.
A reviewer should specify acceptable alternatives and serious mistakes before
seeing outputs. Keep separate cases for tuning and final acceptance; paraphrases
of the same scenario do not count as independent coverage.

| Check | Evidence to collect | Decision it informs |
| --- | --- | --- |
| Recommendation fit | Reviewer checks fit to stated needs, unjustified complexity, omissions, and plausible alternatives. | Whether the recommendation is useful enough to hand off. |
| Risk and uncertainty | Count unsupported claims, serious risk omissions, and assumptions presented as facts; inspect each failure. | Whether to repair or narrow supported use cases. |
| Clarification burden | Record which questions changed a decision, unanswered questions, elapsed time, and abandonment. | Whether stateful interaction earns its extra effort. |
| View consistency | Check both views after initial answers and revisions; validate the exported brief. | Whether the handoff can be trusted to reflect the owner's intent. |
| Owner understanding | Ask adults to explain data, cost uncertainty, responsibility, and next action in their own words. | Whether the explanation supports informed ownership. |
| Operating effort | Measure model cost, latency, manual correction, and maintenance effort for each approach. | Whether a simpler implementation is sufficient. |

For early product checks, report case-level outcomes and recurring problems. Keep
repeated model responses grouped by case; do not inflate coverage by counting each
response as a new user or task. Have a second contributor review important failures
and disputed judgments. Automated checks can assess structure; a model's own score
cannot establish user understanding or safety.

Begin adult usability sessions only after the owner resolves recruitment, consent,
data handling, provider disclosure, and any applicable institutional review. Define
session tasks and a short teach-back checklist beforehand. A facilitator should
record assistance and confusion instead of coaching the participant into a pass.
Confidence and satisfaction are useful feedback but do not replace task completion
or demonstrated understanding. Sample size and language coverage should match the
intended release audience and available resources; neither is committed yet.

Continue with the stateful product if it improves important decisions or the owner
experience enough to justify its cost. If a strong prompt performs as well, ship
or adapt the simpler workflow. Fix repeated serious risk omissions, contradictory
views, or fabricated facts before broadening access. If users cannot explain key
consequences, revise the interaction and retest. If evaluation is too small or
judgments remain disputed, report uncertainty and gather targeted evidence.

## Delivery path and responsibilities

The [work board](work-board.md) tracks owners and dependencies. The following are
stages with exit conditions, not promised dates. Assign people and estimate effort
before scheduling; staffing, provider access, API budget, and user access remain
unconfirmed.

| Stage | Deliverable | Exit condition |
| --- | --- | --- |
| Decide the smallest useful form | Compared existing options, strong prompt, and interaction sketch | A chosen approach with a concrete reason and a bounded cost estimate. |
| Implement Level 0 | Working flow, explicit state, two views, exported brief | Acceptance cases pass and changed or missing answers behave correctly. |
| Validate owner use | Recorded scenario review and authorized adult usability checks | Important failures addressed; owner can explain the recommendation and next step. |
| Introduce Level 1 planning | Specification usable by a selected coding backend | A developer or coding agent can act on it without inventing consequential decisions. |
| Add Level 2 supervision | Build, review, and correction loop | Requirement coverage and recoverable corrections demonstrated on bounded tasks. |
| Add Level 3 delivery | Product in its intended environment and owner handover | Reachability, access, cost, and deployment/rollback responsibilities verified. |
| Add Level 4 operations | Maintained system record and supported maintenance tasks | Owner can request an update, diagnose a problem, and recover through a tested process. |
| Consider Level 5 autonomy | Carefully bounded delegated actions | Earlier capabilities are reliable enough for the owner to grant specific authority. |

The repository owner chooses priorities, acceptable operating cost, supported use
cases, and external release. Contributors implement and review bounded tasks.
Agents may assist those contributors; their presence does not require a multi-agent
product architecture. Assign a technical reviewer and a person responsible for
owner-facing checks before declaring a milestone ready.

Estimate API cost from expected sessions, calls per session, input/output tokens,
and current provider rates; include retries and a contingency. Estimate review and
user-session effort separately. The owner sets the spending cap before paid runs.
Start locally with fictional inputs while those choices are unresolved.

## Risks and practical limits

The model may infer the wrong need, overlook a consequential risk, or sound more
certain than the evidence permits. Explicit unknowns, correctable state, independent
review, and a narrow supported scope reduce these risks but do not eliminate them.
A warning label is not a substitute for a suitable recommendation.

Minimize retained conversations and explain any transfer to a model provider.
Choose storage, access, retention, and deletion behavior before accepting real user
information. Keep credentials and participant records out of the repository. Use
references to secrets in any future system record, never secret values.

Provider changes, quotas, and service failures can change behavior and cost. Record
versions and dates, make failures visible, and repeat the relevant acceptance checks
when models or prompts change. Verify licensing and terms before incorporating
external code, datasets, lesson content, or services.

The initial scenarios and adult users cannot establish that every domain, language,
or population is supported. In particular, a parent-facing Kanji example does not
validate a child-facing deployed product. Deployment, maintenance, and long-term
ownership must be demonstrated in their own milestones.
