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

## Next phase: check the lighter wrapper, then decide

Updated 2026-11-14 under T037. This replaces the 2026-11-06 sequence; its steps 1
and 2 are implemented in T037 and await review. Stay within Level 0.

Current evidence: in plan 7 the transcript baseline delivered six of seven jobs and
five passed every dimension; the wrapper delivered one, and six stopped on change
accounting although review found the meaning mostly kept. S01 lost two of five tasks
to the same refusals. [D022](decisions.md#d022-weaken-and-report-instead-of-refusing)
therefore removes that accounting and reports weak updates to the owner instead of
refusing the result. None of this is verified with a live agent yet.

| Order | Work | Exit evidence |
| --- | --- | --- |
| 1 | A separate contributor reviews T037: adoption rules, native contract 4, prompt, browser controller, D022 and D023. | Review recorded on T037. The reviewer checks in particular that no weakened update can leave a confirmed fact without owner sources. |
| 2 | Operator: one bounded fictional browser flow on the T037 source, covering an unknown, a correction, a declared failure, recovery, reload and download. | One small result file with the journal and source hashes. Needs the owner's authorization for the calls. A failure goes back to the specific defect. |
| 3 | Evaluation author and owner: one matched comparison on new cases, wrapper against the transcript baseline. Plan 7's cases, the dance-video case and the earlier flows are exposed and cannot be reused as held-out. | Blocking failures and decision fit per approach. If the wrapper is no better, apply the proposal's rule and ship the simpler workflow with the thin parts that the baseline lacks: two views from one state, export gating, the unknown button and the saved session. |
| 4 | Facilitator and owner: independent adult sessions under T011, on whichever workflow step 3 keeps. | Five tasks and first teach-back answers per participant. S01 stays formative. |
| 5 | Owner: T032 sign-off. | Level 0 criteria reconciled against steps 2–4. |

Keep the evidence for each run to what a reviewer needs: the journal, the source
hashes and the findings. This plan does not authorize a release, spending or access
to personal data.

## Tasks

| ID | Outcome | Status | Owner | Affected paths | Dependency / evidence / next action |
| --- | --- | --- | --- | --- | --- |
| T001 | Initialize shared docs and contribution conventions | review | Codex, requested by repository owner | Root docs, `docs/`, `.github/`, `.gitignore`, `.editorconfig` | Foundation prepared; see notes below. Repository owner to review conventions. |
| T002 | Define state and engineering brief contracts, including unknowns and answer changes | review | Codex, requested by repository owner | `docs/level-0.md`, D005 | Versioned JSON state/export, fact provenance, dispositions, and validation rules drafted. Self-reviewed; document checks pass, runtime validation is T005. |
| T003 | Design clarification and synchronized owner/developer flows | review | Codex, requested by repository owner | `docs/level-0.md`, D005 | Idea → clarification → recommendation → revision → export/recovery specified. Covers unknown answers, stale results, and late responses. Self-reviewed; implementation and user review remain. |
| T004 | Choose the simplest viable solution and document setup | review | Codex, requested by repository owner | D008, README, Level 0 scope, proposal | Agent-only architecture selected by owner. OpenCode, Claude Code, and Codex wrappers replace direct transports in T012; live access and permissions need verification. |
| T005 | Implement the Level 0 prototype | review | Codex, requested by repository owner | `src/meta_vibe_coding/`, `tests/`, dependency files, README | State, browser flow, corrections, JSON export and T012 agent wrappers are implemented. T006 records live development checks; product acceptance remains incomplete. |
| T006 | Review demos and identify readiness gaps | review | Codex with separate reviewer, requested by repository owner | `artifacts/`, `src/`, `tests/`, README, Level 0 scope, this board | Development evidence remains in T016/T017. T019 completed seven frozen pairs: one provisional case passed, eleven technical stops and two substantive failures. Variations remain unreached; T020 owns repairs. Product acceptance and owner comprehension remain incomplete. |
| T007 | Initialize GitHub repository metadata | done | Codex, requested by repository owner | GitHub repository settings, labels, milestone; `docs/work-board.md` | Description, seven topics, three work-area labels, and [Level 0 milestone](https://github.com/honghuy127/meta-vibe-coding/milestone/1) saved and verified through the GitHub API on 2026-10-28. |
| T008 | Define code, writing, filename, and directory conventions | review | Codex, requested by repository owner | `CONTRIBUTING.md`, `docs/writing-guide.md`, `AGENTS.md`, `README.md`, this board | Existing guides updated; no new files. Checks passed across 11 Markdown files: relative links/anchors, headings, fences, and whitespace. Self-reviewed; repository owner to review conventions. |
| T009 | Improve the solution proposal and delivery plan using research skills | review | Codex, requested by repository owner | Proposal, Level 0 plan, work board, decision log, README | D003 applied; proposal condensed, sources checked, and acceptance tasks linked. Strict Markdown checks and local render review completed; owner review pending. |
| T010 | Define product acceptance cases and the simplest-solution comparison | review | Codex, requested by repository owner | `docs/level-0.md`, proposal, README, D004 | Seven general cases and four variations defined, with acceptable alternatives, blocking failures, comparison limits, and teach-back checks. Strict Markdown checks pass for all 11 documents; whitespace and acceptance-table checks pass. Self-reviewed, owner review pending. No complete product case evaluation; T005 records the local timeout smoke attempts. |
| T011 | Check whether adult owners understand and can use the L0 handoff | blocked | Claude Code facilitates on the repository owner's behalf; requested by repository owner | Private anonymous session observations outside Git; reviewed summary here | Owner chose AI rehearsal on 2026-11-04; T034 records synthetic observations. On 2026-11-05 Claude Code facilitated one actual session (S01) with the owner as participant: three of five tasks completed, the correction never produced a result, and all five teach-back topics were understood with the page open. The participant is the product designer, not independent; this gate needs further independent adult sessions. See [S01 notes](#t011-actual-adult-session-s01). |
| T012 | Replace direct inference with coding-agent wrappers | done | Codex with separate wrapper reviewer, requested by repository owner | `src/`, `tests/`, artifacts organization, README, proposal, Level 0 scope, decisions, agent guidance | OpenCode, Claude Code, and Codex CLI wrappers implemented; direct clients/runner removed. Native help/version and mocked contracts checked. See note for review and remaining live verification. |
| T013 | Self-audit the pending implementation before commit | done | Codex, requested by repository owner | Source, tests, package/lock files, docs, artifact provenance | Audited all 33 tracked/untracked candidate files against D008; fixed owner-confirmation, stale-question/ID, readiness, and instruction-boundary issues. Independent fix review passed; see note. No commit or live inference. |
| T014 | Make the fictional pilot repeatable after the cooldown | done | Codex with separate reviewer, requested by repository owner | `src/meta_vibe_coding/pilot.py`, `tests/test_pilot.py`, `.gitignore`, README, this board | Opt-in runner prepared and independently reviewed. Default check sends no inference; serving requires cooldown expiry and a current pricing check. Exclusive claims prevent allowance resets. 101 pytest and ten UI checks pass; T006 acceptance remains incomplete. |
| T015 | Verify the packaged pilot and rehearse the full flow offline | done | Codex with separate reviewer, requested by repository owner | `tests/test_pilot.py`, this board | Built/installed `0e9ebaa` offline; all 12 packaged files match. Full source suite: 102 pass. All 16 pilot tests also pass against the wheel, independently verified. Process doubles only; no new model calls or held-out cases. |
| T016 | Check independent constraints across corrections | done | Codex, requested by repository owner | `src/meta_vibe_coding/prompt.txt`, development evidence, README, Level 0 scope, this board | Committed prior snapshot as `bff1f17`. Four-call fresh Codex/Luna check retained analytics/payments/registration exclusions while accounts changed, kept unknowns and honored provisional control. Source and evidence reviews passed; 124 tests pass. Claims are limited to these three prohibitions; other semantic gaps remain in T017. |
| T017 | Align clarification and views with known state | done | Codex, requested by repository owner | Agent contract/prompt, core/views and tests, relevant scope and evidence | Committed prior changes as `fc13d10`. Added fact-bound questions, retained quoted unknowns and canonical text/null goal; source/evidence reviews passed. Four-call browser check verified visible goal, retained button/free-text unknowns, scoped data and export. 146 Python and 12 UI tests, document and dependency checks pass; brief schema 1 unchanged. No frozen cases. |
| T018 | Prepare the frozen acceptance run and matched baseline | done | Codex with separate reviewer, requested by repository owner | Evaluation entry point/tests, `artifacts/`, README, Level 0 scope, this board | Frozen bytes preserved; matched plan and no-inference rehearsal recorded. Source review passed after provenance fixes; 163 Python and 12 UI tests, strict Markdown and whitespace pass. No acceptance scores at this stage; T019 records the later authorized run. |
| T019 | Execute and review the bounded matched comparison | done | Codex with separate reviewer, requested by repository owner | Native parsing/stream capture and tests, `artifacts/`, README, Level 0 scope, this board | Owner authorized 98 native calls; all fourteen first attempts closed using 33. Source/raw/rendered-view reviews passed; one provisional case passes, eleven technical stops and two substantive failures. No retry, fallback, purchase or participant session. 166 Python and 12 UI tests pass. See result and T020. |
| T020 | Repair observed output and requirement-contract gaps | done | Codex with separate reviewer, requested by repository owner | Native contract/agent/prompt, evaluation preview, fresh fixtures/tests, relevant docs | D010 implemented and independently reviewed. Explicit question targets, quoted source linkage and private Codex schema file preserve canonical guards and brief schema 1. All 194 Python and 12 UI tests, dependency, strict Markdown/link and whitespace checks pass. T019 bytes are intact. Scripted fixtures do not establish live discovery or acceptance; see notes. |
| T021 | Verify the revised native contract and prepare a fresh comparison | done | Codex, requested by repository owner | Agent development evidence, versioned evaluation plan, relevant docs | Investigation reviewed; 195 Python tests pass. Version 2 plan freezes schemas/runtime and records exposed-case limits. Independent plan/harness review passed after provenance fixes; 15 offline harness checks pass. |
| T022 | Execute and review the revised matched comparison | done | Codex with separate reviewer, requested by repository owner | Version 2 result artifact, README, Level 0 scope, work board | All fourteen first attempts closed using 50 of 98 calls; server stopped. Five wrapper protocol/state stops, one coordinator-related baseline expiry, eight delivered final responses. Independent evidence review passed; semantic gaps and remaining view checks are explicit. Exposed regression only; Level 0 unaccepted and T019 preserved. |
| T023 | Reduce duplicate native records and clarify partial/unknown updates | done | Codex with separate reviewer, requested by repository owner | Native contract/prompt, tests, README/scope/decisions/board | Checkpoint committed as 73089ca. D011 implements native contract 2 with fact changes, attached evidence and key-only questions; original-state guards and brief 1 preserved. Independent design/code/docs review passed; 213 Python and 12 UI tests, strict Markdown/link and whitespace checks pass. No live calls during implementation; committed as 84280c7 before T024. |
| T024 | Verify native contract 2 on fresh development examples | done | Codex with separate reviewer, requested by repository owner | Bounded live development evidence, relevant docs | T023 committed as 84280c7. Five of five fresh calls completed on Codex 0.166.0/Luna; seeded carry/partial/unknown/correction/no-change HTTP stages replay exactly. Independent review passed 53 checks. Semantic wording limits and no browser/unseeded/reliability claim are recorded below. No retry/fallback/purchase. |
| T025 | Verify an unseeded owner-to-brief flow | done | Codex with separate reviewer, requested by repository owner | Fresh fictional development evidence, relevant docs | T024 committed as 2d0c27d. Five actual UI-driven Codex/Luna calls completed from empty facts through corrections and provisional closeout. Independent review passed 54 evidence checks, including both rendered views and actual download. Semantic findings remain below; no retry/fallback/purchase or acceptance claim. |
| T026 | Clarify proposed workflow rules and preserve consequential caveats | done | Codex with separate reviewer, requested by repository owner | `models.py`, `core.py`, `prompt.txt`, browser controller, targeted tests, relevant docs | T025 committed as 63ac46e. D012 retains one stale pending assessment and adds proposal/caveat/source-coverage guidance. Independent design/code/docs review passed; 224 Python and 12 UI tests, dependency and document checks pass. Native 2/brief 1 and historical evidence preserved; no live calls or demonstrated semantic improvement. |
| T027 | Verify revised assessment continuity on a fresh development flow | blocked | Codex with separate reviewer, requested by repository owner | Fresh live development evidence, README/scope/board | T026 committed as deb5997. Three actual UI calls completed before browser failure. Independent review passed 35 evidence and 17 archive checks, retaining stale access facts and missing new requirements as failures. Attempt closed; unused two calls cannot be reused. Remaining live stages/download need working browser access and a new reviewed plan/allowance. |
| T028 | Investigate stale corrections and omitted fact updates | done | Codex with separate reviewer, requested by repository owner | Core question/unknown guards, prompt, browser controller, targeted regressions, relevant docs | T027 committed as e364da7. D013 implements unresolved question targets, protected settled unknown actions and correction/extraction guidance. Independent design/code/docs review passed; 236 Python and 14 UI tests plus dependency/docs checks pass. Native 2/brief 1 and all 20 historical artifacts preserved; no live calls or demonstrated extraction improvement. |
| T029 | Prepare fresh correction verification | done | Codex with separate reviewer, requested by repository owner | Frozen development plan/harness artifact, README/scope/decisions/board | T028 committed as 37c25a0. Frozen craft-club plan and HTTP/read-only replay harness prepared; 56 offline, 19 independent and 14 final reconciliation checks pass. Zero native calls; proposed cap five requires later execution instruction/settings review. T027 stays partial and closed. |
| T030 | Execute the fresh correction check and review recorded views | done | Codex with separate reviewer, requested by repository owner | Bounded result evidence, recorded-view checks, relevant docs | Owner authorized all four Level 0 completion gates on 2026-11-02, including T029's reviewed maximum five-call check. Use exact plan/source and saved ChatGPT login; no API key, new purchase, fallback, retry or reused allowance. Five HTTP calls and replay views/download retained in the [result](../artifacts/2026-11-02-codex-luna-correction-verification.json); 67 independent mechanical checks pass. Blocking mixed owner/agent confirmed fact remains a failure. Generic prompt revision reviewed; 236 Python and 14 UI checks pass. Source frozen for T031; no semantic improvement or acceptance claimed. |
| T031 | Complete current-version Level 0 acceptance and comparison | blocked | Codex with separate case author, operator and reviewer; requested by repository owner | `scripts/`, tests, native Claude schema delivery, D015 and D016 fixes, plans 4 to 6, results, relevant docs | [Plan 7](../artifacts/l0-comparison-plan-v7.json) now has all fourteen first attempts closed using 39 calls after reviewed recovery. Original [28-call partial evidence](../artifacts/2026-11-03-claude-sonnet-acceptance-v7.json) is unchanged. Six wrapper continuity stops and one baseline quota stop remain failures; separate semantic review and scoped adjudication are complete. The [complete archive](../artifacts/2026-11-05-claude-sonnet-acceptance-v7-complete.json) binds the final journal. D021 follows this frozen run; Level 0 remains unaccepted. |
| T032 | Review Level 0 readiness and obtain owner sign-off | blocked | Codex prepares review; repository owner decides | Existing scope, proposal, work board, setup/data/usage evidence | Owner requested the final gate; prepare concrete review evidence after T030/T031 and T011. Actual owner approval, participant consent and unresolved operating choices cannot be supplied by an agent. No public deployment or release authorized. |

| T033 | Execute the plan for remaining Level 0 gaps | blocked | Codex with separate author/operator/reviewer; repository owner handles human gates | Core/models/contracts/prompt, evaluation, targeted tests, new v7 and human-review artifacts, README/scope/decisions/board | Continuity guard implemented/reviewed; all v7 attempts now closed and T035 browser correction/recovery/download completed. N06 blocking omission confirmed on 2026-11-04. Remaining correction semantics, failure usability, independent adult evidence and acceptance/sign-off follow the updated next-phase sequence above. Historical evidence below is retained. |

| T034 | Rehearse owner sessions with AI readers | done | Codex coordinates three separate AI reader contexts and an evidence reviewer; requested by repository owner | Synthetic rehearsal artifact, README, Level 0 scope, decisions and this board | Three separate-context AI readers completed the [synthetic rehearsal](../artifacts/2026-11-04-ai-owner-rehearsal.json); first answers and separate evidence review retained. Source/view/hash checks pass. No actual participants, product calls, browser tasks or downloads; T011/T032 remain incomplete. |

| T035 | Finish frozen attempts, repair continuity and sharing checks, verify browser flow and full-interface AI walkthrough | active | Codex with separate recovery/operator/code/evidence reviewers; requested by repository owner | Recovery/result artifacts first; then core/prompt/tests, browser evidence and existing docs | Owner authorized all three next steps on 2026-11-04. Frozen v7 execution/review complete; D021 implemented and separately reviewed, 366 Python and 14 UI tests pass. Browser access recovered; live check stopped on a real continuity failure after two calls. Full-interface AI reading completed as synthetic only. A focused prompt example is added. The new bounded check completed within caps: the unknown reply was accepted, the correction survived declared-timeout recovery, and the actual download matches the export. Open: a stale access question after the correction, unclear call-counter labels, and no AI reading of this flow's final page. Separate evidence review passed. See [current evidence](#t035-frozen-comparison-repair-and-browser-verification). No human acceptance inferred. |

| T036 | Refresh the next-phase plan from current evidence | done | Codex, requested by repository owner on 2026-11-06 | `docs/work-board.md` | Updated the next-phase sequence above and reconciled T033 status. Checked local links, headings and whitespace; self-review only. No runtime changes or live calls. Next: claim the focused failure-feedback repair. |

| T037 | Report weak updates instead of refusing results; shrink the native contract and prompt; fix counters, failure feedback and session loss | review | Claude Code, requested by repository owner on 2026-11-14 | `src/meta_vibe_coding/` (core, models, contracts, agents, app, prompt, static), `tests/`, README, Level 0 scope, D022, D023, this board and its archive | Implemented after the owner asked for the 2026-11-14 design review to be carried out. 316 Python and 17 UI checks pass with doubles only; no live agent call, so the new prompt and contract 4 are unverified with a model. Self-review only: needs a separate reviewer. See [note](#t037-soft-adoption-smaller-contract-and-failure-feedback). |

Proposed paths are locations for future work, not existing artifacts. Split tasks
when contributors need independent ownership; do not reserve the whole repository
for a broad task.

## Task notes

Notes for finished or superseded tasks (T001–T034) are in the
[archive](work-board-archive.md). Add a note here only while its task is open.

### T035: Frozen comparison, repair and browser verification

The four untouched v7 jobs closed before any runtime repair. The
[complete archive](../artifacts/2026-11-05-claude-sonnet-acceptance-v7-complete.json)
contains 177 hash-bound files and links the unchanged original partial archive.
Independent reconciliation verifies the original 180-line journal prefix and the
final 250-line journal: 39 native starts/finishes, fourteen distinct closed jobs
and 34 questions. Continuation used eleven calls and nine questions. Six wrapper
continuity stops and the original baseline quota failure remain closed failures;
seven jobs delivered final results. Four older support files remain in the linked
partial archive. No retry, fallback or replacement of failed evidence occurred.

Separate [complete review](../artifacts/l0-comparison-review-v7-complete.json) and
[scoped adjudication](../artifacts/l0-comparison-adjudication-v7-complete.json) are
finished. C06 baseline falsely attributed an unresolved answer to the owner; its
uncertainties were still visible, so this is a confirmed nonblocking dimension
failure. No new blocking finding or operator deviation was established. Wrapper
fact-key, open-question readiness and continuity rules remain stricter than the
transcript baseline, alongside the 32,000/64,000-byte input budgets. This frozen
run does not test the later D021 implementation or establish comparative advantage.

[D021](decisions.md#d021-tolerate-unambiguous-continuity-references-and-surface-sharing-authority)
now normalizes only the exact recommendation-list shorthands and outer spaces,
checks duplicates after normalization, and permits valid optional records for
unchanged items. All changed tracked items still require accounting. Prompt
wording favors retained relevant text and asks about represented people/sharing
authority where consequential, without inventing owner facts. Native contract 3
and canonical state/brief 1 are unchanged. Separate design/code review approved
the change; 52 focused tests include archived-response diagnostics. Those offline
diagnostics do not reclassify original v7 attempts.

Implementation checks completed before browser launch: `.venv/bin/python -m
pytest -q` passed 366 tests; `node --test tests/test_ui.cjs` passed fourteen;
`.venv/bin/python -m pip check` found no broken requirements. One existing
Starlette/httpx deprecation warning remains. Source hashes are recorded in the
[development evidence](../artifacts/2026-11-05-ui-development-t035-blocked.json).
No further runtime edit followed those checks.

The browser plan is a separate exposed fictional development check with at most
six native calls, seven assessments and one declared third-assessment timeout.
The first harness preflight failed because a later invalid request could bypass
its stop rule after that timeout. Failed bytes are preserved. The repaired
request-specific rule passed twenty synthetic checks across three fixtures and
separate repeated review. These fixtures made no native calls or browser tasks.

Actual launch verified the existing native first-party login, CLI version/binary,
source, plan and approval. Browser access reported an unavailable host; repeated
native Chrome fallback calls timed out. The server was stopped in order with
zero assessments, zero native calls and no injected fault. Its journal contains
only startup, configuration access and stop. No idea/advance, actual download or
reliable rendered-view check occurred. The full-interface AI walkthrough was not
substituted with another stripped replay. This is an automation-access blocker,
not a native-model or quota failure.

Next action: restore reliable browser access, then obtain separate contributor
review bound to the stopped journal and unchanged source/plan/harness/native
configuration for append-only continuation. Preserve the exclusive claim and
original journal; no reset, replacement or extra allowance is authorized. Finish
the browser flow and actual download before the full-interface AI reader task.
T035 remains blocked on that access. T011 actual adult sessions and T032 owner
sign-off remain incomplete; D019's human-confirmed N06 finding remains recorded.
Separate evidence review passed the final status text and all fifteen embedded
development files, including the exact stopped journal and unchanged runtime.
Four changed Markdown documents pass 128 relative link/anchor checks, heading
and fence checks; both new archives pass embedded byte/hash checks, and
`git diff --check` passes. The human-session template remains unchanged/unfilled.
No commit, push, deployment or global agent-setting change occurred.


T035 continuation: the owner requested a local commit and the next step. Commit
`9041d9a` records the reviewed repair/evidence; nothing was pushed. Native Chrome
navigation works again in a separate verification window although browser-host
access remains unavailable. Codex owns the board and actual UI evidence; a
separate operator prepares only the private append-only recovery helper and
synthetic checks, and another contributor reviews exact stopped-journal launch
approval. The original source, plan, claim and journal remain frozen; no additional
assessment or native-call allowance is granted.


The [reviewed recovery](../artifacts/l0-ui-development-recovery-t035.json) resumed
T035 with the original six-call/seven-assessment/one-fault bounds and no new
allowance. Thirty focused synthetic checks passed independently; the application
and stop-guard body remained identical. Native version/binary and saved first-party
login were checked again. A separate native Chrome window loaded the production
page and submitted the exact fictional idea through its real form.

The [live result](../artifacts/2026-11-05-ui-development-t035.json) preserves
seventeen journal events, both raw native outputs and full interface observations.
Call one delivered a provisional result and asked whether photos identify members
and whether they agreed to sharing, before any planned correction. The actual
unknown button submitted “I don't know.” Call two completed natively but failed
continuity adoption: `open_questions/0.reason` gained one explanatory sentence
while `assessment_changes` was empty. Separate native-output review found the
other seventeen old tracked items exact and two new additions; no material loss
was found on inspection. The unchanged guard correctly refused the missing record.
This shows one successful contextual question, not general hidden-need coverage.

The failed canonical state retains the unknown marker and exact owner quote,
with the earlier assessment stale and no current assessment. The real browser
shows “Outdated · awaiting a new result,” the failure message, the correction form,
and a disabled Download brief button. Opening Developer View shows its explicit
outdated/export-disabled warning. Top/bottom screenshots were inspected in CUA;
only task-page accessibility transcriptions are archived, without unrelated tabs
or screenshots as image files. Ten offline evidence checks pass; all twenty-two
anchor advice fragments match the observed transcription. The first provisional
API export succeeded automatically; this was not an actual browser download.

The run stopped after the real failure: two native calls, two assessments, no
retry/fallback and no injected timeout. The planned correction, third-attempt
software timeout, its retry, fresh final brief and actual download remain
unchecked. Four unspent native calls cannot transfer to a replacement attempt.
The original blocked archive and three-line stopped-journal prefix are unchanged.

Three new AI readers in isolated contexts received the full observed page,
including static notices, disposition, correction route and expanded Developer
warning. First answers were preserved without coaching or rerun. Separate review
coded fifteen teach-back topics and nine navigation answers as supported by the
shown text. This is generated-text fidelity, not human comprehension, source
quality or task completion. Reader intentions were not executed. Their suggestions
to use the visible Retry button are normal UI advice, not operator deviations.
Review also retained source-quality questions about account-availability wording,
detailed service recovery and jargon in the failure message. Temporal/isolation
provenance is parent-reported; hashes alone do not reconstruct orchestration.

After the failed run was archived, Codex added the focused D021 prompt example
for bare unknown replies. Core/schema/guard behavior did not change. The existing
52 assessment-change tests pass, including reason-rewrite refusal and valid
accounting; one existing Starlette/httpx warning remains. The new prompt has not
been sent to a model. Separate contributor review approved the example: its
`reworded` mapping is schema-valid, preserves the unknown and leaves the guard
unchanged. Current prompt SHA-256 is
`f340c8c4f72a33d5bc5f4d1d8d1337b89bd3beedd87fd8e1f004f893ae514ab6`.
Next action: prepare a new bounded development check with an explicit allowance
and fresh fictional flow. Preserve this closed failure and the frozen v7 comparison. Successful
correction/recovery/download verification remains incomplete, so T035 is blocked
on that remaining technical outcome; T011 and T032 remain incomplete.


Final continuation checks: all 23 embedded live-result entries and the original
stopped-journal prefix validate. Four Markdown documents pass 131 relative
link/anchor checks, heading and fence checks; `git diff --check` passes. The prompt
example validates against `AssessmentChange`; no schema/core change followed the
committed baseline. The human-session template remains unfilled and unchanged.
Commit `9041d9a` precedes this continuation; the new evidence, prompt example and
status updates are uncommitted. No push or public deployment occurred.


T035 next check: the owner's “Continue to the next step” authorizes a new exposed
fictional development flow for the reviewed prompt example, with at most four
native calls, five assessments and one declared software timeout. This is a new
bounded allowance through the existing saved first-party Claude login; no new
purchase or fallback. The earlier real failure and its unused calls stay closed.
Codex owns browser operation, result evidence and docs; the operator owns the
private helper/plan/checks, with a separate contributor's exact preflight before
launch. The adult choir-sharing case exercises unknown replies, a public/private
correction, a declared timeout, its explicit retry and an actual download if all
real responses validate. No initial question means unknown handling is unchecked;
no question is manufactured. Stop on a real native/state failure without retry.


The [next plan](../artifacts/l0-ui-development-plan-t035-next.json) and
[exact preflight](../artifacts/l0-ui-development-preflight-t035-next.json) passed
27 independent synthetic checks. Native Claude Code updated to 2.1.318 before
launch; its binary/version are pinned, all seven required CLI flags are present,
and no routing/config/auth override environment names were present. Outcomes
cannot isolate the prompt change from this CLI update.

The new browser run has one valid provisional native result and an unresolved
access/membership question. The actual task tab and first response remain open;
no unknown click, correction, timeout or download has executed. A floating Google
Meet window repeatedly becomes the native control target. The owner was asked
to minimize it and reply “Ready”; this is an interaction-availability blocker,
not a model/state failure. No further native request is running. The server is
idle on port 8026 with its existing claim and counters; do not restart/reset it.
The [partial snapshot](../artifacts/2026-11-05-ui-development-t035-next-partial.json)
preserves first output, exact journal prefix, source/plan/approval and the
session deadline. Resume only the same in-memory task while that session remains
valid. Do not extend its clock or replace the first attempt if it expires.
T035 is temporarily blocked on browser availability; the two earlier closed
failures remain unchanged. No source changes, commit or push occurred in this
next-check turn.

Independent partial-record review passes: all twelve embedded file hashes/bytes,
exact eight-event live journal prefix, plan/approval/manifest bindings and remaining
limits agree. This confirms record integrity only, without source-quality or
completed-flow claims. `git diff --check` and board relative-target checks pass.


The owner replied “Continue” while the original session was still valid. Codex
selected the preserved task tab without reload/reset and clicked the actual
unknown button. Native call two is processing; old advice is labelled outdated
and download is disabled. The existing claim, source/native pins and four-call
limit remain in force.

The next check completed within its caps: four native calls (all valid), five
assessments and the one declared fault. The unknown reply was accepted and
retained. The correction triggered the labelled timeout once, before any native
process; the correction and unknown survived, the prior result was marked outdated
and no export ran until the retried result. Retry did not reinject the fault and
produced revision 5. The bounded provisional handoff (call four) returned an
identical assessment, so the brief stayed at revision 5. The actual browser download
is byte- and JSON-identical to that production export (7,923 bytes, SHA-256
`06cc5d33892e9395a488f88a952a1ac0f0a5d6810e39f154f560189b70481947`). Chrome saved
it to the home directory rather than Downloads, which is why the first comparison
attempt found no file. No real native/state error occurred, so the stop-on-failure
path was not exercised.

The Codex operator turn then stopped on a usage limit at 14:18:59Z. The server
command it had launched was reported finished at 14:24:00Z (failed, exit -1)
without its shutdown handler, so the journal has no `run_stopped` event. Its last
write was at about 14:15Z and nothing was appended. All four calls had finished. Claude Code
resumed the session, verified the download and archived the
[completed run](../artifacts/2026-11-05-ui-development-t035-next.json). The archive
embeds the journal (which keeps the partial snapshot's prefix), download proof,
execution summary and verbatim final-stage accessibility captures copied from the
operator log. The port 8026 server and in-memory session no longer exist. This
completes the remaining browser outcome, so the earlier notes that T035 is blocked
on browser availability or on correction/recovery/download verification, that call
two is processing, and that only the same in-memory task may resume are superseded.

Findings remain open. First, after the correction the facts confirm that the
public sees only dates and that recordings and notes are member-only, yet the
`access.members_only` fact stays unknown (“The owner does not know yet”), its
carried-over question still asks whether anyone outside the choir should ever
have access, and the risk and limitation lines still describe access as
undecided. How members join and leave is still legitimately open. This is a
continuity gap inside a valid result, not a guard failure. Smaller wording issues:
the responsible-admin reason says “Not yet asked” although that question was
asked; “members can play recordings on their own devices” is an unlabelled
assumption; and “not uploaded until permission is recorded” is stronger than the
owner's “check permission before sharing”. Second, the footer
shows “agent request 5/7”, which counts session assessment requests against
the hard-coded product limit and includes the synthetic attempt, beside “At most
4 agent invocations per server run”. The two counters are not labelled as distinct.
Third, plan step 8 is incomplete: the final full-page capture is archived, but no
separate-context AI reading of this successful flow was run.

The unknown reply succeeded this time, but this one exposed flow cannot credit the
prompt example alone: Claude Code changed to 2.1.318 and provider revision may
differ. No held-out acceptance, reliability rate, human comprehension, N06
adjudication or owner sign-off follows.

A separate read-only evidence review passed archive integrity (18 embedded files),
every journal count above, the download comparison, the verbatim captures and both
main findings; its precision corrections are reflected here and in the regenerated
archive. Next action: owner decision on the stale-question gap, counter labels and
whether to run the step 8 AI reading. T011 and T032 remain incomplete.

### T011: Actual adult session S01

This summary was reviewed and approved by the participant on 2026-11-05. One
actual adult session took place; the participant was the product designer, so
they were neither independent nor randomly selected. Claude Code facilitated on
the owner's behalf. It gave the consent and retention notice, then observed
through the participant's reports, page prints and saved brief, not their screen.
The build was `e28e72e`, using Claude Code with `claude-sonnet-5-5` and a 4-call
cap. The fictional idea was a shared family finance web app.

Tasks: describing the idea and saving the brief were completed. Answering the
consequential question was completed after one Retry, because the continuity
check refused the first response. The correction was attempted but never produced
a result: after it failed, two retries ended on the session limit. The updated
Owner View was therefore never seen. The facilitator gave help twice, each time
after the participant asked whether the agent was still running.

Teach-back used the pre-correction brief. All five topics were rated understood,
with no help after the first answers and no confident misunderstanding. The
participant had the page open while answering, so this shows that the page can be
read accurately, not that the content was remembered.

Usability findings:

- Twice, a failed step was read as the agent still running. The failure status
  line did not make clear what had happened or what to do next.
- While export was disabled, the participant printed the page to PDF instead.
- The submitted correction text is not shown anywhere after a failure, although
  the status says answers are retained.
- “Start a new idea to continue” would discard the session, and it may not work
  once the server's call cap is used up.
- Continuity refusals blocked two of the five tasks.

Limits: this was one non-independent participant in a formative check. It does
not complete T011's evidence or establish usability for other owners. Raw notes
were kept outside Git and deleted after this summary was approved. The app kept
no journal, so the call count before each failure is inferred, not logged.

### T037: Soft adoption, smaller contract and failure feedback

The owner asked for a review of the design and implementation on 2026-11-14 and then
for its proposals to be implemented. [D022](decisions.md#d022-weaken-and-report-instead-of-refusing)
and [D023](decisions.md#d023-keep-the-session-in-the-browser-and-count-only-started-calls)
record the choices.

What changed:

- Adoption refuses a result only when it would break the state. An update the owner's
  words do not support keeps the earlier record, or is recorded as an assumption, and
  a misplaced question is left out. Each case is listed for the owner under “Check
  these”, with the advice removed and added since the last result.
- Native contract 4 drops `assessment_changes` and the `owner_unknown` flag. The
  prompt went from 12,882 to 4,630 bytes and the schema from 3,902 to 3,345, so fixed
  input is 7,975 of the 32,000-byte budget instead of 16,784. The case-derived
  examples are gone from the prompt.
- An idea is charged an assessment only when an agent process started. The page shows
  the idea's assessments and the server's remaining calls as two labelled numbers.
- A failure says the agent has stopped, what the owner can do, and shows the input
  that is kept. Retry is hidden when it cannot help.
- The browser no longer rebuilds state itself; it resends the owner's input. The
  current idea is saved in the browser and survives a reload.

Checks on 2026-11-14: `.venv/bin/python -m pytest -q` passed 316; `node --test
tests/test_ui.cjs` passed 17; `pip check` found nothing broken; the no-inference
rehearsal passed its eight checks. `tests/test_assessment_changes.py` was removed with
the guard it tested; flow, unknown and contract tests that expected a refusal now
expect the weakened result and its report.

Not verified: any live agent behavior, including whether a model follows the shorter
prompt, whether quoted evidence on unknown facts is used only for real declarations,
and whether owners read the new “Check these” section. The English-only list of bare
replies in `substantive()` is unchanged. Frozen plans 1–7 name contract 3 or earlier
and cannot run against this source. Nothing was committed.

Separate review on 2026-11-14 (read-only agent, doubles only) found no blocking
issue and ten others. Fixed in a follow-up commit: context quotes no longer become
owner declarations; a renamed key cannot confirm old text; an omitted open decision
is added instead of refusing the result; a late export cannot enable Download for an
outdated result; a kept input cannot be silently replaced; rejected input offers no
Retry; an idea is charged only after the process spawned; the provisional flag
survives a reload. Checks after the fixes: 317 Python and 21 UI tests pass.

Next action: step 2 of the next-phase plan above.
