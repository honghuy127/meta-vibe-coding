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
| T011 | Check whether adult owners understand and can use the L0 handoff | blocked | Facilitator pending; Codex prepares materials | Private anonymous session observations; reviewed summary here | Owner chose AI rehearsal on 2026-11-04; T034 records synthetic observations. The actual-adult gate remains deferred and incomplete; no participant consent or responses have been collected. Existing [human-session template](../artifacts/l0-adult-session-template.json) remains unfilled. |
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

| T033 | Execute the plan for remaining Level 0 gaps | blocked | Codex with separate author/operator/reviewer; repository owner handles human gates | Core/models/contracts/prompt, evaluation, targeted tests, new v7 and human-review artifacts, README/scope/decisions/board | Continuity guard implemented/reviewed; partial v7 comparison, adjudication, recovery checks, N06 packet and consent materials retained. N06 blocking omission confirmed by the repository owner on 2026-11-04. Quota/recovery, native bookkeeping reliability, actual UI/download and T011/T032 gates remain unresolved. No sign-off. |

| T034 | Rehearse owner sessions with AI readers | done | Codex coordinates three separate AI reader contexts and an evidence reviewer; requested by repository owner | Synthetic rehearsal artifact, README, Level 0 scope, decisions and this board | Three separate-context AI readers completed the [synthetic rehearsal](../artifacts/2026-11-04-ai-owner-rehearsal.json); first answers and separate evidence review retained. Source/view/hash checks pass. No actual participants, product calls, browser tasks or downloads; T011/T032 remain incomplete. |

| T035 | Finish frozen attempts, repair continuity and sharing checks, verify browser flow and full-interface AI walkthrough | blocked | Codex with separate recovery/operator/code/evidence reviewers; requested by repository owner | Recovery/result artifacts first; then core/prompt/tests, browser evidence and existing docs | Owner authorized all three next steps on 2026-11-04. Frozen v7 execution/review complete; D021 implemented and separately reviewed, 366 Python and 14 UI tests pass. Browser development stopped at zero assessments because browser control is unavailable; full-interface AI walkthrough awaits it. See [current evidence](#t035-frozen-comparison-repair-and-browser-verification). No human acceptance inferred. |

Proposed paths are locations for future work, not existing artifacts. Split tasks
when contributors need independent ownership; do not reserve the whole repository
for a broad task.

## Task notes

### T005–T006: Prototype and live development checks

The retained prototype supports strict state, clarification, corrections,
synchronized views, recovery and export. The design baseline is `6f7ec5d`;
[D008](decisions.md#d008-wrap-coding-agents-only) defines the current coding-agent
boundary. Independent reviews checked state/provenance, failed requests, stale
exports, subprocess limits and native CLI contracts. Earlier direct-model evidence
in `artifacts/legacy/` does not establish current wrapper acceptance.

The owner’s OpenCode free-plan investigation remains in the
[original record](../artifacts/2026-10-29-opencode-free-pilot.json) and
[routing comparison](../artifacts/2026-10-30-opencode-routing-verification.json).
The original seven calls are closed; attempts 4–7 used a redacted workspace-header
placeholder and cannot isolate request-size or tool-eligibility causes. Three
corrected-profile comparisons still returned request-scoped free-limit errors,
including shared execution and an after-cooldown request. The owner’s successful
terminal context remains unmatched. Private routing export and static error
messages were reviewed; no global configuration, paid fallback or production tool
permission was changed. Earlier source hashes and the explicit erratum preserve
these limitations.

The owner switched to Codex with `gpt-6-luna`. The
[initial two-call record](../artifacts/2026-10-30-codex-luna-pilot.json) captured a
completed response rejected because of the deliberately disabled Code Mode host’s
startup notice. A narrow parser fix accepts only that exact notice in its observed
position. Separate review and a second live call verified initial clarification;
unknown errors, tools and incomplete output remain rejected. These reviewed
changes were committed as `438f61d` before the requested next step.

The [browser conversation](../artifacts/2026-10-30-codex-luna-conversation.json)
used all seven allowed native calls through saved ChatGPT authentication,
with 300/1,800-second limits, read-only workspaces, disabled tools, ignored user
config/rules and ephemeral mode. All replies were scripted fictional inputs.
The flow covered a public information site, explicit unknown budget and public
personal content, the “I don’t know” button, and a correction requiring member
sign-in and private attendance across devices. No API-key route, automatic retry,
other model, new purchase or frozen case was used. Credit usage/cost, retention and
complete isolation remain unverified.

The fifth response renamed two confirmed fact keys. The validator rejected it;
the browser retained the correction, marked the old result outdated and disabled
download. A direct local export check also returned 409. Clarified the generic
prompt: keep existing confirmed keys and revise their values/status/sources.
Separate review passed. Restarted only the backend with the two remaining calls,
preserving the browser state, consumed allowance and session timer. Explicit retry
6 succeeded; no validator was relaxed. The failed attempt remains in the record.

The sixth result recommends assessing an established membership service, explains
private member/organizer access and recovery responsibilities, and keeps budget
and public identifiable content unknown. Its displayed brief, server export and
downloaded `engineering-brief.json` match at revision 9. The browser event monitor
timed out; the owner supplied the actual path and file comparison established
success. The original intent and correction provenance are retained.

Independent review found that the earlier “no analytics” restriction survived
only in source history, not current facts. It also found questions repeating
information explicitly marked unknown. A reviewed generic prompt clarification
used the final call through “Show a provisional result.” The seventh response
did not repair the constraint omission and still proposed a new question. Its
revised export is separate from the owner’s earlier download, which was preserved.
All seven attempts remain recorded; the server was stopped without further calls.

Enforced explicit provisional requests in application/core code: retire pending
questions, add no new clarification, and retain open decisions in the assessment.
Separate review caught and verified a fix preserving the existing rejection of
contradictory ready-plus-question output. Captured attempt 7 passes an offline
HTTP replay with unchanged facts/turns and no new question. This is not another
live verification, and it does not resolve the omitted constraint. The prompt
changes alone did not establish reliable requirement retention or clarification.

Checks: 124 Python and ten UI tests pass, along with strict Markdown, relative
links, whitespace and dependency checks. The existing Starlette TestClient warning
remains. Source and prompt reviews passed. A separate contributor verified calls
1–6; the seventh-call evidence delta was self-reviewed after that reviewer reached
a usage limit. All seven native/HTTP/state replays, source stages, offline guard,
download and frozen-case hashes reconcile. The owner requested committing the reviewed follow-up snapshot after `438f61d`
before addressing the remaining development findings. The seven
[frozen cases](../artifacts/l0-acceptance-cases.json) remain unchanged and unrun.
Next: repair and recheck non-superseded constraint retention and unknown-question
behavior in a new bounded development run, including the provisional guard, before
frozen cases and a matched baseline. This conversation does not pass acceptance
or establish general recommendation quality or owner comprehension. Adult sessions
still need their own authorization.

### T016: Independent constraints in a fresh conversation

Committed the reviewed T006 follow-up as `bff1f17`, then clarified the existing
fact representation: separate independently changeable permissions/prohibitions
into scalar facts; do not hide several exclusions in an empty list or a reason.
Genuine collection-valued requirements remain lists. No model-specific examples,
new schema, dependency, validator relaxation or tool permission was added.

The [four-call check](../artifacts/2026-10-30-codex-luna-constraint-retention.json)
uses the same Codex/Luna boundaries and saved ChatGPT login as the earlier run.
The fictional initial input provides the public-site details up front. The agent
recorded accounts, registration forms, payments, analytics and stored visitor
information as separate confirmed booleans. After a correction adding private
member attendance, the three unaffected exclusions stayed false and cited `t0`;
the account change cited correction `t1`. Unknown budget and public
identifiable content remained null. An explicit provisional request added no new
question even though the native response proposed one. Export returned 200.

All four calls are consumed, with no retries or purchases. The prior seven-call
record and the owner’s download were preserved. This is an observed improvement
for one fresh development example, not a matched comparison or a migration of
older grouped states. Extraction completeness and semantic support still need
review; source IDs alone do not establish either.

The normal clarification path still repeated questions about explicit unknowns.
The model also used `project.goal` instead of the canonical `goal` field used by
the Owner View; browser rendering was not exercised here. A visitor-storage key
was reused for member storage, leaving scope ambiguous despite member-specific
access and data fields. T017 owns these gaps; retention claims cover only the
three checked prohibitions. Source and evidence reviews passed, as do 124 Python
tests. Strict Markdown, relative links, whitespace and evidence-hash checks pass.
No frozen case, baseline or owner session ran.

### T017: Questions and views use known state

Implemented [D009](decisions.md#d009-bind-clarification-to-facts-and-retain-explicit-uncertainty):
new questions identify facts, results contain text/null `goal`, and explicit owner
unknowns retain quoted evidence through failures/retries. Only a later substantive
reply can resolve a declaration. Brief schema 1 is unchanged; old in-flight clients
need a new idea. Source review also found and verified the provisional control
remaining reachable when suppression leaves `needs_answer` without a question.

The [four-call browser check](../artifacts/2026-10-30-codex-luna-known-state.json)
verified the visible goal, button declaration before inference, quoted budget
uncertainty, distinct public/private storage, and a matching provisional export.
A new sensitivity question remained allowed because that fact was not declared
unknown. Calls 2 and 4 themselves proposed no question: backend interception,
marker resolution and the `needs_answer` edge case are tested with doubles, not
observed live here. Quotes and keys do not prove semantic intent or detect aliases.
No new dependency or extra per-assessment agent call was added.

Source and raw evidence reviews passed. The server stopped after four calls;
old records, the owner’s download and frozen cases were preserved. The exact live
source patch is retained, before later plain-language error wording. All 146 Python
and 12 UI tests pass, as do dependency, strict Markdown, relative-link and whitespace
checks. Changes after `fc13d10` join T018–T020 in the reviewed checkpoint. T018 prepares bounded
acceptance/baseline execution; no frozen case or owner-comprehension session ran.

### T018: Prepare the matched comparison

The [plan](../artifacts/l0-acceptance-plan.json) preserved frozen cases and defined
the matched comparison. The [rehearsal](../artifacts/2026-10-30-acceptance-rehearsal.json)
used a separate timer fixture and HTTP doubles. Review verified fixes for source
provenance, changes during capture and ambient legacy settings. All 163 Python
and 12 UI tests, strict Markdown/link and whitespace checks passed. No native
calls or acceptance scores came from rehearsal. T019 records the later run.

### T019: Seven frozen pairs

The [result](../artifacts/2026-10-30-codex-luna-acceptance.json) records all fourteen
first attempts, using 33 of the owner's 98 allowed native calls. Source and plan
stayed fixed; claims and fsynced reservations prevented resets. A shared native
completion parser kept baseline output separate from Candidate/state adoption;
optional stream capture retained exact bytes/hashes. Independent source, raw-record
and rendered-text reviews passed. The server stopped with all attempts closed.
Final archive review passed for `900838356cc8` (SHA-256 prefix).

H04 wrapper passed narrowly as a provisional checklist/board solution; its latest
maintenance answer still lacks a fact/export source reference. Five wrapper attempts
failed state protocols; six baselines failed JSON parsing. Completed H06 wrapper
omitted the prior-copy limit on revocation; H07 baseline omitted unattended service
versus human credentials. Neither omission was a cross-view contradiction. All six
attached variation phases remain `not checked`. HV04 passed only its separate
no-native-call HTTP recovery checks on a state copy.

Read-only replay disables controls, so HTTP statuses establish export gating.
Setup status can overwrite its error label. Owner comprehension, billing, native
internal calls and general superiority remain unverified. All 166 Python and 12 UI
tests and dependency checks pass; Markdown/link and whitespace checks pass. The
existing Starlette warning remains; hosted Markdown rendering was not checked.
T020 repairs follow in the same checkpoint; a new evaluated version remains pending.

### T020: Native response contract repair

[D010](decisions.md#d010-separate-native-responses-from-canonical-state) separates
the native response from canonical state. Keyed arrays and embedded question
targets remove ambiguous map generation; exact quotes link new or changed confirmed
facts to cited sources. Existing confirmation, repeated-topic and owner-unknown
guards stay intact. Codex receives a private schema input file; other agents use
stdin and local validation. Baseline preparation previews its own closed schema
and still receives only the owner transcript and limits.

Independent code review found no blocker; 109 focused offline checks passed.
Final commands: `python -m pytest -q` (194 passed),
`node --test tests/test_ui.cjs` (12 passed), `python -m pip check`, strict Markdown
checks on README/scope/decisions/board, and `git diff --check` all pass. Python
commands used `.venv/bin/python`. The existing Starlette deprecation warning remains.
T019 archive, plan and frozen cases retain their hashes; canonical core/models
remain as captured in T019. No native call was made for T020; its changes join
the owner's requested checkpoint commit.

Fresh fixtures verify partial-answer state transitions and preservation/export of
scripted consequences. They do not show live consequence discovery, complete
extraction or semantic support. Native schema compatibility, recommendation quality,
owner understanding and Level 0 acceptance remain open. T021 needs fresh settings,
plan and allowance; the closed T019 run is not reopened.

### T021: Revised contract development

The [fictional development record](../artifacts/2026-10-30-codex-luna-contract-development.json)
contains an initial success, a failed follow-up and a later diagnostic retry and
correction. A separate initial success and sandbox failure are summarized only;
the failed follow-up's raw invalid output was not captured, so its cause is unknown.
Six top-level attempts ran in total,
using saved Codex authentication and requested `gpt-6-luna`; actual model and cost
are unknown. No paid fallback was selected.

The successful correction retained the coordinator and volunteer permissions,
unknown budget and alert preference, and separately recorded service-account use
and the prohibition on sharing its credentials. This is a single fictional case,
not evidence of broad reliability. The investigation preceded the version 2
plan and comparison recorded in T022. T019's cases were exposed during
repair and cannot be represented as held out. No new acceptance claim is made.

The [investigation](../artifacts/2026-10-30-codex-luna-contract-investigation.json)
captures a separate reproduction: a quote group linked `volunteer_alerts` to `t1`,
but that unknown fact cited no source. Local validation correctly rejected it.
The original uncaptured failure's cause remains unknown. The prompt now explicitly
limits grounding to new or changed confirmed facts and requires each linked fact
to cite the quote's source. Validators and canonical guards are unchanged.
Three new native calls produced a pre-change pass/failure and one post-change pass;
this is not a reliability estimate. A regression test covers the inconsistent
quote group; `python -m pytest -q` using `.venv/bin/python` passes all 195 tests
with the existing Starlette warning. Independent review passed: saved successful
responses replay exactly, the captured failure reproduces, source/capture hashes
reconcile and all 29 contract tests pass separately. No comparison, commit or push
ran during this investigation. T022 records the subsequent plan and execution.

### T022: Exposed-case regression comparison

The [version 2 plan](../artifacts/l0-comparison-plan-v2.json) froze the runtime,
both native schemas and a fresh 98-call maximum. Independent harness review and
15 offline checks passed after imported-source and actual schema-file provenance
fixes. The [result](../artifacts/2026-10-31-codex-luna-comparison-v2.json) preserves
all fourteen first attempts and 50 calls, raw streams, HTTP/export evidence,
three rendered DOM captures and independent judgments. The server stopped cleanly.

Five wrapper attempts stopped on duplicate/conflicting facts, repeated-topic or
unknown-source guards. H04 baseline expired during a coordinator interruption;
this is not a model-quality failure. Eight attempts delivered final responses.
H03 wrapper passes narrowly; H05 wrapper's uncertainty variation passes separately
from its base risk-calibration gap. Delivered baselines still omit consequences
such as collision handling, portable export, copied-data revocation or key rotation.
These findings cannot be averaged into a general winner or Level 0 acceptance.

Call/schema/stream/source checks and independent review passed. The separate HV04
copy check passed seven HTTP recovery assertions without inference; its first
expired-fixture failure is disclosed. Remaining page captures failed because browser
access was unavailable and native Chrome returned `cgWindowNotFound`; missing view
checks remain not checked. No full visual QA or owner comprehension is claimed.
T019 and frozen inputs retain their hashes. Changes remain uncommitted; T023 owns
the next contract simplification before another live run.

### T023: Fact changes with attached evidence

Committed the reviewed investigation/comparison checkpoint as `73089ca`, then
implemented [D011](decisions.md#d011-return-fact-changes-with-attached-evidence).
Native contract 2 returns changes with attached evidence and question references;
untouched facts carry locally. Sources and explicit-unknown markers derive together.
The decoder copies the original facts and adoption still checks the original state.
Explicit removal is limited to unconfirmed facts without retained unknown markers.

Independent design, code and docs review passed. Review caught and verified a fix
allowing a later explicit unknown declaration to refresh its marker, while same/older
changed evidence remains rejected. All 213 Python tests and 12 UI tests pass;
the separate reviewer also ran 167 focused tests. Strict Markdown/link and whitespace
checks pass. The existing Starlette warning remains. Core/models/agent invocation
and historical artifacts are unchanged; no new dependency or native call was added.
T023 was committed as `84280c7`. T024 owns live verification; semantic omissions, stale
interpretations and aliases remain open rather than being repaired by the decoder.

### T024: Live native contract 2 development

The [five-call record](../artifacts/2026-11-01-codex-luna-native-contract-2.json)
preserves the frozen plan/source, seeds, native schema inputs, lossless streams,
HTTP states/exports and independent review. Codex 0.166.0 used saved ChatGPT login
with requested `gpt-6-luna`; served model, internal calls and cost remain unknown.
All five planned stages completed with no wrapper retry, fallback or purchase.

The agent omitted unchanged facts, confirmed location from a partial answer and
asked separately about reminder style, then supplied the unknown marker and source
together. The later correction confirmed workshop location, visible-only style and
40 minutes from its new source, preserving the no-history/no-account facts. The
last call omitted updates and retained facts/sources. A newly raised shared-device
question stayed unknown; no live suppression interception was demonstrated.

Independent review passed 53 byte/provenance/state/export checks and exact replays.
The seeds include confirmed facts, an assumed 20-minute interval and a compound
question; this is not requirement discovery. Recommendation kind changed on the
no-change call, and some prose says shared laptop despite the device-sharing fact
remaining unknown. These wording/scope issues remain explicit. No browser, full
visual QA, owner comprehension, held-out acceptance or reliability claim is made.
T024 evidence/docs were committed as `2d0c27d`; T025 records the unseeded flow check.

### T025: Unseeded owner-to-brief UI flow

The [five-call record](../artifacts/2026-11-01-codex-luna-unseeded-owner-flow.json)
preserves the frozen plan/runtime, lossless native streams, HTTP journal, five
saved live pages, actual downloaded brief and separate review. Codex 0.166.0 used
saved ChatGPT login with requested `gpt-6-luna`; served model, internal calls and
cost remain unknown. The source was unchanged. A reviewed temporary harness
enforced one shared adapter, a durable five-call cap and frozen owner updates;
its exception path was made fail-closed before the first call.

The production UI began with empty facts/questions/turns and extracted a fictional
book-loan idea. Three proactive owner corrections supplied unknown sensitivity,
friend-specific visibility and extension requests, then recovery and readable
exit-copy needs. These were not answers to unrelated clarification questions.
The visible provisional control closed the flow without inventing a cloud-storage
answer. All five advances and exports succeeded; no retry, fallback or purchase.

Independent review passed 54 provenance, state-replay, rendered-text and download
checks. Both views matched each export; the actual downloaded JSON matched the
final export. Saved-page line endings are normalized only for text comparison.
Pending/outdated controls and final viewports were observed by the coordinator;
screenshots were not retained. This is not exhaustive pixel QA or comprehension.

The access-correction assessment introduced owner approval for extensions without
clearly labeling it a proposal, and temporarily omitted the existing-copy limit
on revocation. Later stages acknowledged unspecified approval behavior and restored
the copies/derivatives caveat; the earlier findings remain. The corrected aggregate
goal cites the new correction alone although some context comes from the initial
idea. Quote presence establishes linkage, not complete semantic source coverage.

The final brief remains provisional with cloud-storage acceptability and personal
details unknown. No real service permissions, recovery, retention, prices or
implementation were verified. One fictional development flow does not establish
held-out acceptance, reliability or owner understanding. T026 is the next proposed
task; it has no additional live-call allowance.

Final separate archive/docs review passed 19 reconciliation checks with no
blocker. Strict Markdown/link and whitespace checks pass; historical artifact
hashes are unchanged. No production code changed, so the software suites were not
rerun. T025 evidence/docs were committed as `63ac46e`.

### T026: Proposed policies and consequential caveats

Separate design review approved [D012](decisions.md#d012-retain-one-stale-assessment-for-reconsideration)
before implementation. Pending state now retains one `previous_assessment` through
failure and explicit retry, including a lost browser response, then clears it on
successful adoption. Simultaneous current and previous assessments, and future
snapshots, are rejected; equal revisions are valid for no-answer requests. Stale
advice never supplies owner confirmation
or an exportable result. No history, automatic merge or brief migration was added.

The prompt requires labels on unconfirmed policies wherever used, asks to retain
still-relevant caveats in explanation and engineering checks, and requires aggregate evidence for
retained components as well as the latest correction. Obsolete advice and sources
must be reconsidered. Meaning remains subject to semantic review, not keyword
guards or indiscriminate source unions.

Checks: all 224 Python tests and 12 UI tests pass, as do dependency consistency,
strict Markdown/link and whitespace checks. The existing Starlette deprecation
warning remains. New regressions cover context lifecycle, failed adoption, retries,
lost replies, stale evidence, aggregate citations and supplied proposal/caveat
export. Oversized snapshots retain input and stop before any CLI process under the
unchanged 32 KB cap. Offline serialization of the five archived T025 requests also
fits that cap; this is not a new inference run. Native response 2 is byte-identical
to the frozen schema, brief 1 is unchanged, and all 19 historical artifacts match
the committed bytes.

Independent code/docs review passed and separately ran 161 focused Python tests
and all 12 UI tests. No blocker remains. Changes were committed as `deb5997`; no live calls,
semantic improvement or acceptance claim. T027 owns fresh live verification after
a new reviewed plan and allowance.

### T027: Fresh assessment continuity check

The [partial run](../artifacts/2026-11-01-codex-luna-assessment-continuity.json)
retains the frozen plan/runtime, durable five-call claim, lossless native streams,
HTTP journal and three saved live pages. Independent pre-live review passed 36
checks. Codex 0.166.0 used saved ChatGPT login and requested `gpt-6-luna`; served
model, internal calls and cost remain unknown. Source stayed at `deb5997`.

After initial browser blockers, the owner's retry resumed the same harness and
claim. The production UI started with empty facts and submitted the first two
frozen proactive corrections to a fictional theatre-audio idea. All three advances
and exports succeeded; each follow-up input contained the exact prior assessment.
Three expanded saved pages preserve both views. A default-named second capture
was identified by exact exported JSON and copied losslessly to its stage filename;
a later overwrite confirmation was canceled before saving the third page correctly.
No earlier response or capture was replaced.

The revised goal cites original and correction sources, proposed approval handling
is labeled, and explanations retain copy/revocation caveats. These observations
coexist with substantive failures: an obsolete owner-only access fact remains
current beside performer access, and the download/future-revocation update changes
no facts despite being discussed in prose. Approval questions also bind to the
confirmed correction-request capability rather than a distinct unknown policy.
The risk from applying the unknown button to that different property was not tested.
Copy limits remain in explanations, but the second stage's engineering criteria
omit the explicit already-received-copy distinction; it returns in the third.

Repeated browser/native automation failures and kernel resets blocked the fourth
correction. The server then stopped cleanly after three of five allowed calls;
no model call was retried and no HTTP fallback was used. The harness's sequence
`closed` flag remains false because the sequence is incomplete; the coordinator
closed the attempt and its unused two calls cannot be reused. Browser listening,
provisional closeout and an actual final download are unperformed. Unrelated
browser content is excluded from project evidence. This partial run is neither a
semantic pass nor Level 0 acceptance.

Independent review passed 35 raw/context/state/export/rendered-text checks and
17 final archive/docs reconciliation checks, with the substantive findings retained.
Strict Markdown/link and whitespace checks pass; all 19 earlier artifacts remain
byte-identical to the committed versions. No production code changed, so software
suites were not rerun. Evidence/docs were committed as `e364da7`. T027's remaining live
checks are blocked pending working browser access and a new reviewed plan/allowance;
T028 records the investigation of the observed state and question-target gaps.

### T028: Corrections, extraction and question targets

T027's stale access and omitted download/revocation facts were model omissions
accepted by structural checks, not mutations introduced by carry-forward. Separate
design review approved [D013](decisions.md#d013-ask-only-about-unresolved-properties)
before implementation. The prompt now explicitly asks to update superseded values
at existing keys and record independently changeable requirements outside advice.
No automatic deletion, domain-specific contradiction detector, forced update for a
no-change reply or native field was added.

New questions require unknown or assumed targets before any suppression/adoption.
The unknown button cannot replace settled facts in core preparation or browser
optimistic edits; older mismatched questions disable that action and explain the
correction/provisional route. Legacy state remains readable. A genuine conflict
can reopen the same property only after newer owner evidence makes it unresolved;
the existing confirmation and repeated-topic guards remain.

All 236 Python and 14 UI tests pass, including exposed T027 known-target rejection,
failed HTTP adoption with retained context, settled legacy unknown actions and
genuine confirmed-fact conflict reopening. Supplied corrections/requirements check
representation and source handling, not extraction. A diagnostic copy with the bad
question removed still passes structural checks while retaining stale/missing facts;
this documents the semantic limit and does not repair the historical response.
Dependency consistency, strict Markdown/link and whitespace checks pass; the
existing Starlette warning remains. Native response 2 is byte-identical to the
frozen schema, brief 1 is unchanged, and all 20 historical artifacts match HEAD.
Independent code/docs review passed and separately ran 128 focused Python tests
and all 14 UI tests, with no blocker. No live calls, semantic improvement or
acceptance claim; T027's unused allowance remains closed. Changes were committed as `37c25a0`.
Next: T029 prepares fresh verification; unresolved status and key equality still
cannot establish that a question asks about the correct semantic property.

### T029: Prepare fresh correction verification

The [frozen plan](../artifacts/2026-11-01-codex-luna-correction-plan.json)
retains source `37c25a0`, prompt/schema, lock, harness and separate timer-fixture
rehearsal. Its fresh fictional craft-club scenario covers changed member access,
correction requests, service download/revocation, browser preview and portability.
[D014](decisions.md#d014-separate-development-http-checks-from-recorded-view-review)
separates sequential production ASGI/HTTP checks from later recorded-view review.
This remains targeted development, not held-out acceptance or a matched comparison.

The proposed allowance is five Codex/Luna calls, 300 seconds per request and 1,800
per idea. Preparation makes zero native calls or native authentication/environment
reads; no live claim exists. Later execution needs an explicit instruction and
settings/cap review, exact plan-byte hash and one fixed exclusive claim before
native startup. Every partial failure is retained; no retry, fallback or reuse of
T027's closed allowance. The viewer has no agent and rejects start/advance; its
altered controller, views and downloads are labeled replay. Original HTTP statuses,
not disabled viewer controls, establish export gating.

All 56 offline checks and 19 independent checks pass. Review found and verified
fixes for typed replay matching (`false` versus `0`, `1` versus `1.0`) and a final
source-freeze check after HTTP/export. Rehearsal covers optional four/five-step
completion, first-error stopping, retained context, durable limits, stream capture,
source drift and read-only routes with real native access denied. No production
code changed; existing historical artifacts remain unchanged. Actual model outputs,
browser rendering/download, comprehension and general semantic quality are untested.
Final archive/docs reconciliation passed 14 checks. Plan SHA-256 is
`cd05f816b6638ac0a12625ecf0e9882cdc3896b62463d1dc29d6b6999033880f`.
Strict Markdown/link and whitespace checks pass; all 20 earlier artifacts remain
byte-identical to HEAD. No production code changed, so software suites were not
rerun. T030 owns later authorized execution and recorded
view checks; this preparation establishes no active allowance.

### T030–T032: Complete the four Level 0 gates

The owner requested all four completion gates on 2026-11-02: targeted correction
verification and fixes, complete acceptance/comparison, adult owner understanding
(T011), and final review/sign-off. Apply the supplied research skill's evaluation
guidance in agent-led mode within this scope; the proposal, Level 0 contract,
work board and versioned artifacts remain authoritative without duplicate dossiers.
Native runs remain bounded and independently reviewed. Participant/facilitator
availability has been requested; no actual session or human approval is invented.

T031 stopped on 2026-11-02 at 15 of 98 native calls. The Codex usage limit reached
the coordinator, reviewer, operator and native calls together, because all four
share one Plus allowance with no credits. Rate-limit logs show the 5-hour window
resetting at 14:17:38 JST with 78% of the weekly window used. The harness process
then exited with status 137, losing in-memory state; its journal survives.

N01-wrapper failed after one call (`invalid_output`): a question referenced a fact
it did not create. N01-baseline and N02-baseline delivered provisional results and
their variations in five calls each. N02-wrapper reached its variation; call 15
returned the usage-limit error, so NV03 is not checked and the job is a technical
stop rather than a retry candidate. N03 to N07 are unstarted. No semantic, view or
comparison judgment exists for any job. From N02-baseline onward the harness could
not combine known passages with the unlisted-fact reply, so the known part was
supplied and the rest left unanswered on both approaches; affected rows are
protocol deviations, not equal received information.

The [interrupted record](../artifacts/2026-11-02-codex-luna-acceptance-v3-interrupted.json)
holds the journal, claims, reviews, operator selections and frozen harness, because
those existed only under `/tmp`. Its 51 files reconcile byte-for-byte; the local
operator token is excluded and a credential-pattern scan found nothing. This is
not an exhaustive secret scan. Plan, cases, source, lock, harness and Codex binary
hashes all still match the freeze.

The owner then replaced Codex with Claude Code and Haiku 4.5 for this test and
agreed the harness should not depend on one agent, so plan 3 closed without resuming.
A journal-based resume launcher had passed review by then but never ran; it is kept
in the closed record and its logic moved into the new harness.
[D015](decisions.md#d015-name-the-agent-in-the-plan-and-run-acceptance-through-one-harness)
records the choice. All fourteen jobs run again under plan 4 with the same cases,
because mixing agents would not be a matched comparison.

The Claude wrapper had never made a live call. One development call showed Haiku
wrapping JSON in a Markdown fence, which the strict parser rejects, so every wrapper
job would have failed for a reason unrelated to stewardship. The wrapper now uses
native `--json-schema`, like Codex's `--output-schema`, without relaxing validation.
Stewardship and baseline prompts and both schemas are byte-identical to plan 3. A
live rehearsal on a synthetic case used three Haiku calls, two wrapper and one
baseline: all completed with Haiku reported as served, no workspace files and a
real export. Wrapper calls took about 75 seconds and 8,600 output tokens, baseline
about 22 seconds. The Claude CLI reported about $0.15 across those calls; on a
subscription that is a notional figure, not a charge.

The operator and runner share files in the run directory because the Claude sandbox
denies localhost, which removed the port and control token. A separate reviewer,
blind to cases, failed the launcher twice and the new harness three times before
passing `d659d14c5972`. Fixes included a run directory that could have granted a
fresh allowance, a malformed request that stranded the run, wrapper and baseline text
being escaped differently, and a usage-limit shape that could pass unnoticed.

The [plan 4 run](../artifacts/2026-11-02-claude-haiku-acceptance-v4.json) closed all
fourteen jobs in 54 of 98 calls, about 28 minutes of native time. Claude Code reported
Haiku 4.5 as served on every call, with no native stops, tool denials or workspace
files. It reported 181,000 output tokens and a notional $1.36, which is not a charge
on the subscription. A separate agent reviewed each job and variation against the
frozen rubric, and another adjudicated its findings against the raw evidence,
reproducing all 17 wrapper calls.

No phase passes on either approach. Of 18 blocking findings, 16 stood and 2 were
overturned, and adjudication added 3, leaving 19: 7 on the wrapper and 12 on the
baseline. Only N04 and N07 baselines have no blocking failure, and neither passes
every dimension. These counts do not show which approach is better, because the
wrapper produced fewer results to fault.

The wrapper's main problem is reaching a result. N03, N04, N06 and N07 stopped with
`invalid_output`, so four of seven jobs have no current result. N03, N06 and N07 were
model output defects stopped by guards working as designed, though N06's guard is
heavy. N04 is a product and harness defect: byte-exact quote matching fails when the
model flattens a line break, and the harness's passage joining supplied the line
break. A real multi-line owner reply can fail the same way. Normalize whitespace on
both sides of both containment checks. Without it, N04 would have reached a result
but was unlikely to pass. Wrapper results that did finish keep unknowns visible, yet
under-clarify and leave cost and upkeep out of the Owner View. N05 asked nothing.
Every baseline finished, but baselines repeated questions after unknowns and made
unsupported price or safety claims. T030's mixed owner and agent fact did not recur
in adopted values, on thin coverage.

Recorded deviations invalidate no row: provisional was set on all six variation
calls rather than only final ones, which affected N01 unequally; seven answers were
fragments rather than clauses; one matched question received unequal clauses.
Baseline pages omit pending questions, so those were judged from the journal.
Wrapper view dimensions come from recorded replay, so no wrapper row can pass on
them. Live UI, actual downloads, owner comprehension and vendor claims are unchecked.
Agent review is not human review; human review is advised on one disputed block and
on N04 baseline, where one dimension alone prevents a pass. Coordinators stayed blind
to N03 to N07 text throughout, but those cases are now exposed and are regression
evidence only.

The owner then asked to rerun the test with Sonnet. [Plan 5](../artifacts/l0-comparison-plan-v5.json)
changes only the requested model, `claude-sonnet-5-5`, plus its run directory, owner
instruction, version and description. Plan 4 regenerates byte-identically, so
source, harness, cases and protocol match. A separate agent checked the bindings, and
a two-call rehearsal on a synthetic case confirmed the model ID. The known quote
whitespace defect was deliberately left in place so that the model is the only
variable.

The [plan 5 run](../artifacts/2026-11-02-claude-sonnet-acceptance-v5.json) closed all
fourteen jobs in 46 of 98 calls, with Sonnet reported as served on every call. It
stopped twice because Claude Code exhausted its structured-output retries on
N02-wrapper and N05-wrapper. A separate agent reviewed each stop from provider fields
as a model output failure, not a limit, and the run resumed against an approval of
the exact journal. Each failed job keeps its failure, no allowance was added, and no
further job was lost. Wrapper calls averaged about 36 seconds and baseline calls
about 23; the CLI reported a notional $2.94.

After separate review and adjudication, six jobs pass every phase: N01, N03, N04 and
N06 wrappers, and N02 and N04 baselines. N07-wrapper has one blocking failure, hidden
material uncertainty: it gave a ready result without settling a decision-critical
scope. N05 fails a non-blocking dimension on both approaches, and N02 and N05
wrappers stopped technically. Calibration paired jobs across both runs and found
plan 5's review consistent with plan 4's on price, safety, recovery and hidden
uncertainty. Sonnet's outputs hedge where Haiku's asserted. The quote whitespace
defect did not recur.

The comparison exposed a test defect. The mixed-answer line chosen for plan 4, "For
anything else you asked: I do not know.", is tied to no question. Baselines read it
as closing their own listed open questions, recorded unasked items as owner unknowns
and stopped asking. That overturned five disputed baseline blocks, but N01, N03, N06
and N07 baseline clarification cannot be scored and is left open. It also appears,
more weakly, in two plan 4 rows that its reviews missed, with no verdict change. The
wrapper was unaffected because the product ties each reply to one question. Next
time, name the uncovered part of the question, send a plain "I do not know" when
nothing is covered, and check each owner unknown against the questions actually asked.

Reaching a result is now Sonnet's main wrapper cost. Sixteen of 24 wrapper calls
needed more than one structured-output attempt and five hit Claude Code's limit of
five; two of the four fully passing wrappers relied on a last attempt. Baseline calls
never needed more than two. Haiku needed at most two attempts on every call, but
produced weaker content that failed the product's guards.

Open: the five artefact rows need a corrected rerun, which would be regression
evidence only, since these cases are now exposed. Whether replay pages count as a
rendered check is disputed. Plan 4's adjudicator ruled them ineligible for wrapper
view dimensions, and under that reading only the two baseline jobs pass. The N05
wrapper risk call, live UI, actual downloads and owner comprehension are unchecked,
and agent review is not human review. Level 0 acceptance is therefore not met.

Before the final run, three fixes were made and reviewed separately with no blocker:
word-based quote matching, ten Claude structured-output attempts (D016, the owner's
choice), and a mixed-answer reply tied to the current question. A live probe
confirmed safe-mode Claude Code honours the attempt setting; Sonnet's measured pace
keeps ten attempts inside the unchanged 300-second limit. A separate agent wrote
seven new cases that the coordinator never saw. A rehearsal hit the owner's Claude
5-hour limit, was rerun after the reset, and plan 6 passed a separate binding check.

The [plan 6 run](../artifacts/2026-11-02-claude-sonnet-acceptance-v6.json) closed all
fourteen jobs in 57 calls with no native stop. Eight wrapper calls needed more than
the old five attempts and all completed, so the retry change worked. A separate agent
reviewed the run and another adjudicated it against raw evidence.

Adjudication confirmed a product defect. On N05-wrapper, a provisional result with
one-line text and no acceptance criteria, open decisions or limitations was adopted
over a fuller earlier result and exported with HTTP 200. Level 0 requires a
provisional export to carry its unresolved questions. Content rules apply only to
ready results (`models.py:150-166`); text and lists may be minimal (`models.py:83-103`);
adoption has no continuity check (`core.py:118-119`); and export blocks only a missing
or `needs_answer` result (`core.py:148-150`). It occurred once in 30 adopted wrapper
results, and the unknown facts stayed visible.

Eight jobs or phases pass: N02 baseline and wrapper bases, N03 and N04 baselines,
N04 wrapper, N05 baseline with its unknown variation, and N07 wrapper and baseline.
Only N05 baseline and both N07 jobs pass with no deviation that could have changed
them. N06-wrapper has a new blocking finding, a hidden need the baseline raised and
the wrapper never did, which awaits human confirmation. N03-wrapper and N06-baseline
over-asked. N01-baseline wrongly attributed an unknown to the owner, which is not
blocking.

The operator was required to close provisionally at the five-question limit eight
times and did so once. Three misses, on N01, N02 and N05 wrappers, changed outcomes
to question-limit failures; N01-wrapper also had a miscounted step. Only the wrapper
was hurt, because the baseline is told how many questions remain. N01 and N02
baselines stopped on the shared 32,000-byte input limit at their variation calls,
with inputs of 33,667 and 33,837 bytes: the transcript baseline resends every earlier
reply, while the wrapper peaked at 24,239 bytes. So the two approaches are not
equally exposed to that limit. NV01, N02-baseline NV03 and N05-wrapper NV02 are not
checked.

Level 0 acceptance is not met. Live UI, downloads, owner comprehension and the
separate failure double are unchecked, and agent review is not human review. The
plan 6 cases are now exposed.

Follow-up on 2026-11-03,
[D017](decisions.md#d017-require-provisional-results-to-carry-what-they-leave-open-and-size-the-baseline-separately):
a provisional result must now list open questions and limitations and keep each
owner unknown open by fact key, matching case-insensitively; the prompt says so.
This rule rejects none of 62 earlier sound provisional results and both empty ones.
A refusal keeps the owner's answers and leaves the earlier result outdated and
unexportable. The harness now forces the provisional close from the question limit
onward on both approaches and records that it did. At the owner's choice, a plan can
give the transcript baseline its own input limit, 64,000 bytes, while the wrapper
keeps the product's 32,000. A separate review passed harness `a51847a47f73` and the
product change with no blocker. The case-insensitive topic match came after that
review and is self-reviewed. All 313 Python and 14 UI tests pass. No live call or
acceptance run used these changes.

The remaining gaps and their closure order are tracked in [T033](#t033-plan-to-close-the-remaining-level-0-gaps).
T011, T031 and T032 stay blocked; no sign-off is implied.

### T033: Plan to close the remaining Level 0 gaps

Prepared on 2026-11-03. This is proposed follow-up work, not an implemented
continuity safeguard, a new run authorization or an acceptance decision. Codex
owns technical preparation; the repository owner assigns the human reviewer and
facilitator. No dates depend on assumed participant or reviewer availability.

1. **Define and check assessment continuity.** Codex prepares a small design and
   regression fixtures for `core.py`, `models.py`, `contracts.py`, `prompt.txt` and
   the relevant flow/contract/UI tests. Compare a replacement with the retained
   previous assessment and current owner evidence. Cover lost material open
   decisions, limitations, acceptance criteria and owner responsibilities, even
   when every required list remains nonempty. Start with decisions tied to stable
   fact keys; assess whether other material items need explicit carry-forward or
   removal reasons. Any contract change needs separate design review and a
   decision-log entry before implementation. String length, list counts and exact
   prose matching cannot decide whether a result is substantively weaker.

   The design must allow resolved questions, superseded advice and concise
   rewrites, giving later owner corrections priority over stale advice. It must
   also handle the first assessment, no-change replies and repeated failed
   requests. On refusal, retain the owner's answers and leave the earlier result
   outdated and unexportable; do not silently merge stale text or retry. Exit when
   meaningful regressions cover both lost-content refusal and valid revision,
   both views and export agree, and another contributor has reviewed the change.
   Record any semantic losses the selected design still cannot detect. Offline
   checks alone will not establish live improvement.

2. **Prepare an explicit comparison of the different contracts.** After technical
   changes are reviewed, Codex prepares a new versioned T031 plan, updates its
   review/report instructions and obtains independent preflight review. Keep
   D017's rule: provisional wrapper results must retain each declared unknown as
   an open question under its fact key, ignoring case and outer spaces. The plain
   chat baseline has no equivalent key validator or adoption gate. Disclose that
   difference before running and next to the results, including any new
   continuity gate. Assess preservation of uncertainty by meaning in both
   approaches; report wrapper validation stops separately from omissions in
   delivered outputs. A baseline-only retrospective audit may inform review but
   must not feed state or validator feedback into its transcript.

   Set `baseline_input_bytes` explicitly to the owner's selected 64,000 bytes;
   retain the wrapper's 32,000. Record the different input/schema contracts,
   shared question/call/time limits, native hidden attempts, and enforced
   provisional close. Verify the topic guard's later case-normalization change
   separately; its existing review is self-review only. Have another contributor
   freeze seven genuinely new cases after source freeze; exposed cases remain
   regression evidence. Bind plan, source, harness and journal hashes, confirm the
   selected native settings and invocation allowance under D015, and preserve
   every first attempt without retries or fallback. Do not assume unused old
   allowance is reusable. Close out the still-unchecked live UI, actual download
   and failure-double evidence explicitly, labeling replay separately. Exit when
   all required phases and review dimensions have evidence or remain openly
   blocked; only complete reviewed evidence can support acceptance.

3. **Obtain human adjudication of N06-wrapper.** In parallel with technical
   preparation, Codex prepares a compact review packet from the unchanged
   [plan 6 result](../artifacts/2026-11-02-claude-sonnet-acceptance-v6.json): embedded
   `review-v6.json` at `rows[17]`, `review-v6-adjudication.json` at
   `blocking_rulings[7]` (both zero-based), the
   frozen case/applicability rule, initial request, disclosed answers and all four
   wrapper outputs. The dispute is whether failing to ask or flag that other
   families' children might appear in dance-show videos is a blocking hidden-need
   omission. The first reviewer treated undisclosed facts as inapplicable; the
   adjudicator treated this need as inferable from the initial request. Include
   the baseline's relevant question as context, not proof of a wrapper failure.

   The repository owner or a named human reviewer decides whether the frozen rule
   supports the finding and records confirmed, overturned or unresolved, with
   passages, rationale and affected review dimensions. Append that ruling without
   rewriting the original reviews or rerunning the case to decide its old verdict.
   An unresolved dispute leaves the case open; overturning this finding alone
   does not establish Level 0 acceptance. Any fix informed by N06 is development
   work and must precede the next source/case freeze.

4. **Unblock T011's adult sessions.** Materials can be prepared alongside steps
   1–3. The repository owner names a facilitator and confirms adult availability,
   intended participant count/selection, private storage and a deletion rule.
   The facilitator confirms voluntary consent and the destination/retention notice
   before collecting responses; existing gate authorization is not participant
   consent. Use the existing [procedure](level-0.md#check-owner-understanding) and
   [empty template](../artifacts/l0-adult-session-template.json), a technically
   reviewed build and fictional tasks. Discuss remaining material risks before
   sessions; do not use participants as substitutes for technical review.

   Check idea entry, a consequential answer, a correction, the updated Owner View
   and brief download. Record the first uncoached teach-back on recommendation,
   access, cost unknowns, maintenance/recovery and next action, followed by any
   help and confident misunderstandings. Keep raw observations outside Git.
   Exit when actual sessions and separate review exist, important
   misunderstandings are resolved and a non-identifying summary records build,
   participant count, incomplete tasks and limits. If those conditions fail,
   revise and recheck the affected flow; keep T011 blocked rather than inferring
   comprehension from software or agent checks.

5. **Prepare T032 and request the owner's decision last.** Codex assembles the
   concrete readiness review in the existing board and scope documents after
   T031's technical/semantic review and T011's evidence are complete. Include
   T030's retained mixed-provenance failure and the evidence for any later fix,
   continuity limits, the human N06 ruling, comparison asymmetries, live view and
   download checks, failure recovery, comprehension results, and remaining native
   permissions, data/retention and usage choices. Keep a missing item visible and
   distinguish an accepted residual limitation from an unmet acceptance criterion.

   Codex can recommend readiness with stated limits; the repository owner gives
   the actual sign-off. Record the decision, reviewed build and evidence, scope
   and conditions. T032 remains blocked while required evidence or a human
   decision is missing. Sign-off does not itself authorize public deployment,
   spending or a release.

Next action: start step 1's design review and prepare step 3's human review packet;
steps 2 and 4 can be prepared while those reviews are pending. Implementation and
execution evidence belong in the affected task notes, not in new routine logs.
Planning checks: all 43 relative links/anchors, 28 headings, code fences and
whitespace in this board pass; `git diff --check` passes. Self-reviewed against
current scope, D015–D017 and the retained plan 6 reviews; separate review remains
pending. Runtime tests were not run for this documentation-only change. No code,
historical result, live call, participant record, commit or push changed in this task.


Execution update, 2026-11-03: the owner instructed Codex to proceed with this plan.
[D018](decisions.md#d018-account-explicitly-for-changed-assessment-items) was reviewed
by a separate Codex contributor before implementation. Native contract 3 now
accounts explicitly for changes to tracked prior assessment lists in adoption;
state/export schema 1 remains. The same reviewer found no implementation blocker
and ran 170 targeted checks. This guards against unaccounted loss, not weaker
meaning hidden in a claimed rewrite or unjustified withdrawal. Scalar summaries,
recommendation kind and risk level remain outside the guard. The topic
normalization mismatch between provisional validation and question suppression is
fixed and separately reviewed. A later boundary regression also checks that an
already-assessed owner turn cannot justify a new removal.

The [N06 human review packet](../artifacts/l0-n06-human-review.json) contains all
four original wrapper exchanges, the frozen applicability rule and both agent
positions. Its embedded-source hashes were verified. On 2026-11-04 the repository
owner answered “Confirm” to the evidence-backed recommendation and confirmed the
blocking omission. The accepted rationale is failure to ask about or leave open
other people appearing and permission to share, under the frozen hidden-need rule.
This confirms the risk/unknown-handling failure; it does not rule the invite-only
recommendation itself unsafe. [D019](decisions.md#d019-confirm-the-n06-hidden-need-omission)
records the human decision. Original reviews and run outputs remain unchanged. The existing
[adult-session template](../artifacts/l0-adult-session-template.json) now includes
a consent script and unfilled logistics fields. Facilitator role, adult count and
availability, private storage and deletion arrangements were requested; no consent
or participant response has been collected.

Fresh-case preparation preserves an unsuccessful author assignment: the first
independent author opened a source-freeze file that included runtime source and
prompt text. No cases were authored and that assignment was disqualified. A new
blind author receives hash-only metadata. Historical attempts remain unchanged.
The browser access host reports unavailable; native Chrome access took unusually
long. No completed live UI flow or actual download is claimed from that attempt.

T032's current readiness review remains blocked:

| Required evidence | Current state / next action |
| --- | --- |
| Current build and continuity guard | D018 reviewed; four of five attempted wrappers stopped on accounting despite largely preserved trigger meaning. Reliability/semantic improvement is unestablished. |
| T030 provenance failure | Retained failure and generic prompt fix remain development evidence; check meaning in fresh outputs. |
| T031 comparison | Frozen plan discloses both wrapper-only gates and 32,000/64,000-byte budgets. Ten jobs reviewed/adjudicated; four unstarted at quota stop. See result and recovery below. |
| N06 human ruling | Repository owner confirmed the blocking omission on 2026-11-04; D019 and the packet retain the decision and its limits. |
| Actual live views/download and failure handling | Browser flow/download incomplete. Both frozen [failure-double paths](../artifacts/l0-failure-double-v7.json) pass through production HTTP with local process doubles and zero model calls; software recovery evidence only. |
| T011 adult understanding | Owner selected AI rehearsal now (T034/D020). Actual adult observations and individual consent remain absent; the human-evidence criterion is still incomplete. |
| Native permissions, destination/retention and usage | Recheck selected native settings before execution or participant-facing use; unknowns stay explicit. |
| Owner decision | Codex recommends against sign-off on current evidence. Actual owner decision remains pending; unmet gates are explicit. |

The replacement blind author froze seven new categories and three owner variations
in [cases 7](../artifacts/l0-acceptance-cases-v7.json), with an
[authorship manifest](../artifacts/l0-case-freeze-v7.json); no native calls were made.
The coordinator has inspected only IDs and structural metadata. The new
[plan 7](../artifacts/l0-comparison-plan-v7.json) binds the reviewed runtime, source
snapshot, current schemas, case bytes and harness. It states both wrapper-only
gates and the 32,000/64,000-byte input budgets before execution. Independent
[preflight](../artifacts/l0-comparison-preflight-v7.json) passed after resolving
three draft instruction/rubric conflicts; all exact hashes match. The first
sandbox launch stopped at native authentication before a claim, journal or
inference. The same approved launch succeeded outside the sandbox with platform
approval and no added allowance. Claude Code 2.1.317 and its binary hash are in the
run manifest; inference-free help confirms the required native flags. First
attempts were executed through the separate operator; the partial run is closed
for now at the native quota stop described below.

Execution checks: `.venv/bin/python -m pytest -q` passes all 344 checks;
`node --test tests/test_ui.cjs` passes all 14; `.venv/bin/python -m pip check`
finds no broken requirements. The existing Starlette/httpx deprecation warning
remains. The no-inference evaluation rehearsal passes all eight transition checks;
four changed Markdown documents pass relative links/anchors, headings, fences
and whitespace checks, and `git diff --check` passes. These are software and
preparation checks, not Level 0 acceptance, comprehension or live improvement.
The [partial result](../artifacts/2026-11-03-claude-sonnet-acceptance-v7.json)
retains all 28 native starts and ten closed jobs, with four jobs unstarted. Five
jobs delivered final outputs: four baselines and one wrapper. Four wrappers stopped
on D018 accounting; one baseline stopped on the provider's HTTP 429 usage limit.
The fifth wrapper delivered its base and unknown variation. Across all jobs,
three variations were delivered; unreached phases stay unchecked. Native retries
or fallback did not replace any first attempt. The server was stopped after all
attempted jobs closed and its inbox was empty; the journal hash is unchanged.

The [separate review](../artifacts/l0-comparison-review-v7.json) and
[adjudication](../artifacts/l0-comparison-adjudication-v7.json) cover 20 phase rows,
including the four unstarted jobs. Four baseline phase rows pass all dimensions;
two C02 baseline rows fail risk/unknown handling for omitted read/output-error and
incomplete-catalog handling. No semantic blocking finding was confirmed within
this limited review. C05 wrapper base and unknown variation pass semantic dimensions,
but wrapper rendering and actual download remain unchecked. The four refused
wrapper candidates largely preserved meaning in their trigger items; wrong
responsibility reference prefixes, an unaccounted reason rewrite, and missing or
redundant records stopped them. This is a substantial accounting burden; the
software guard cannot be treated as demonstrated semantic improvement. No source
relaxation or output repair changed the frozen run.

The operator's C04 routing ambiguity remains in the original review. Independent
adjudication found no confirmed deviation: a prior one-off capability did not
establish recurring monthly counts after the changed workflow. The affected
clarification dimension passes on recorded evidence; counterfactual outcome impact
remains unestablished. The exact pre-adjudication review snapshot is retained in
the result archive, so both positions and their hashes remain recoverable.

The [recovery review](../artifacts/l0-comparison-recovery-v7.json) passes technical
checks but is `not_ready` for launch before the reported next reset at
2026-11-04 02:00 JST. The date is inferred from the native message and its timestamp;
quota restoration is unverified. Only C06 baseline/wrapper and C07 wrapper/baseline
may resume, with at most 28 additional calls across those four original first
attempts. Closed jobs cannot be reopened and their unused calls cannot transfer.
Recheck exact journal/source/plan/harness and native login/version/binary, and obtain
fresh exact-journal launch approval after the time condition. No new allowance,
retry, fallback or source change is authorized by that recovery preparation.

Next action: use T034’s synthetic observations to improve the next walkthrough; review the
native accounting burden before readiness claims, and complete the four unstarted
jobs only under the recorded recovery conditions. T031, T011, T032 and this task
remain blocked. Codex recommends against Level 0 sign-off on this evidence.
Final reconciliation on 2026-11-04 JST verifies all 129 embedded archive files and
the unchanged journal, runtime and pre-/post-adjudication hash chain. The four
changed Markdown documents pass 110 relative links/anchors, heading, fence and
whitespace checks; `git diff --check` passes. No commit, push, global agent-setting
change or public deployment has occurred.


### T034: AI owner-session rehearsal

The owner selected AI agents to mimic human owners on 2026-11-04; see
[D020](decisions.md#d020-rehearse-owner-sessions-with-ai-readers). Three readers in
separate contexts received two recorded Owner View states each and the same five
teach-back prompts. Their packs excluded the code, case answer bank, expected
answers and earlier reviewer judgments. Personas are fictional prompts, not a
model of the adult population. First responses were retained without coaching or
rerun in one [rehearsal artifact](../artifacts/2026-11-04-ai-owner-rehearsal.json).

The inputs cover a completed planning handoff with unknown photo metadata,
family-video sharing, and a refused revision whose earlier recommendation is
outdated. The current production controller generated text in a DOM/HTTP double;
five exports match original recorded HTTP responses and one failed state remains
unexportable. The source snapshots span historical model/runtime versions. This
replay does not rerun reasoning or establish current model quality. Nine proposed
reader actions were not executed; no actual browser task or download occurred.

A separate evidence reviewer coded the 15 generated first-topic answers: 14 were
supported by shown text and one partly supported answer explicitly added its own
stop/seek-help precaution. These counts describe AI text, not a human comprehension
rate. The family-sharing reader faithfully summarized a source that still omits
the D019 sharing-permission question. Repetition of visible advice does not make
that source complete.

Two additional complaints about a missing provisional label were unsupported:
the readers confused the hidden request-provisional action with the supplied
provisional disposition. The packs also omitted static correction-form labels
and the no-software-built notice. A navigation question based on those excerpts
cannot establish that the real UI lacks a correction route. No new UI defect was
confirmed. Questions about provider access, metadata handling, backup scope,
account recovery and technical maintenance are prompts for a later walkthrough,
not independently verified defects or proposed policy adopted by the owner.

Checks: all 11 embedded input/first-response/review files are hash-bound; the
original response hashes, historical source archives, controller and frozen plan 7
runtime are unchanged. Five successful exports and the failed state agree with
their sources. The human-session template remains unfilled and unchanged. JSON,
Markdown relative links/anchors, headings, fences and whitespace are checked for
the changed artifacts/documents. No production source changed, so runtime suites
were not rerun. No product-agent CLI invocation, model acceptance retry, participant
consent, commit or push occurred. The three AI reader sessions and AI evidence
review are model-generated simulation.

T034 is complete as a synthetic rehearsal. T011's actual-adult evidence and T032
sign-off remain incomplete under the current scope; no waiver is inferred. The
next rehearsal should include all visible page context and label controls by their
visible action names before drawing UI conclusions. Technical reliability and
browser verification remain the next product checks.

### T014: Repeatable fictional pilot

Added the [pilot runner](../src/meta_vibe_coding/pilot.py) and usage in README.
It records local HTTP evidence and source hashes, and reserves one continuation
through an exclusive claim tied to the recorded request IDs. Claims survive
startup failure; review evidence and reconcile attempts/cooldowns before relaunch.
Separate review verified the cooldown, request allowance, concurrent launch guard,
private journal and preserved HTTP boundaries. All 101 pytest tests, ten Node UI
checks, strict Markdown, whitespace and dependency checks pass. Actual CLI checks
report the active cooldown and refuse serving; no new native request ran. Frozen
cases are unchanged. T014 prepares execution; T006 acceptance remains blocked.
The owner requested committing the reviewed changes after this preparation.

### T015: Packaged integration rehearsal

Committed T014 and quota handling as `0e9ebaa`, then added one integrated offline
test spanning clarification, unknown/provisional export, a correction that times
out, stale-export rejection, retry and corrected provenance. The full suite has
102 passing tests. Built the wheel without network access, installed it under
`/tmp`, and matched all 12 packaged files. All 16 pilot tests pass there with
repository pytest configuration disabled, using existing virtualenv dependencies.
A separate reviewer verified import locations, hashes and those installed tests.
This establishes process-double integration, not native CLI behavior, browser
rendering, recommendation quality or owner comprehension. T006 remains blocked;
the fresh cases are unchanged. The follow-up test is included in the reviewed
snapshot committed before the live conversation continuation.

### T012: Coding-agent-only revision

Applied the owner's major revision and clarification: support OpenCode, Claude
Code, and Codex. The repo owns stewardship/state/views; coding agents own model
execution, native credentials, providers, and any local hosting. Removed the direct
Ollama/API clients, wrapper API-key/rate configuration, and local-model runner.
Archived earlier evidence rather than presenting it as current capability.
Revised README, proposal, Level 0 plan, decisions, and agent guidance in place.

One shared process boundary now invokes each CLI from a temporary workspace,
checks required flags, passes state on stdin, validates successful final JSON,
and preserves deadline/cancellation and invocation limits. Agent execution is
opt-in. Native configuration/managed policy remains trusted bootstrap; no complete
isolation or live compatibility claim is made. Codex intentionally ignores saved
provider profiles; OpenCode handles custom/local routes. See README for details.

A separate reviewer checked vendor interfaces and reproduced incomplete-terminal
parsing and lost OpenCode inline-routing issues; both were fixed. Native help and
version inspection ran without inference. Final checks: 67 pytest tests and eight
Node regressions pass; strict Markdown, whitespace, and dependency checks pass.
The separate reviewer found no remaining
reproduced blocker in the wrapper implementation. Checks use process doubles,
not live agent inference. Remaining work: configure an authorized agent, verify
effective native permissions and retention with fictional inputs,
then obtain a valid development result before spending the held-out cases. No
agent inference, paid call, commit, push, or global agent-setting change is part
of this rewrite.

### T013: Pre-commit self-audit

Reviewed current source, tests, dependencies, docs, and archived evidence. Reproduced
and fixed retry-only confirmation/rewrite of previously assessed facts, answers to
retired questions, and ID collisions in valid nonsequential histories. Added an
assessed-reply count so failed requests can still retry new retained owner input.
Ready goals now require nonempty text. Unknown goals and inapplicable facts render
in human-readable language. Claude/Codex now receive static stewardship policy via
their native system/developer surface; owner text stays in stdin data.

Legacy records now state that their Git SHAs name the design baseline, not the
uncommitted code that executed. Full prior source snapshots are unavailable;
raw records were preserved. This is a replay limitation, not current acceptance.

Checks: 78 pytest tests, ten Node regressions, strict Markdown, whitespace, and
Python dependency consistency pass. Lock contents exactly match the declared
runtime/dev/build dependency closure. Built the wheel offline, matched all eleven
packaged source/assets to the working tree, and verified imports, served assets,
and the disabled-agent gate from an isolated wheel install. No credential-pattern
matches were found in the 33 candidate files; this is not an exhaustive secret scan.
The frozen acceptance-case hash is unchanged. A sandbox signal restriction required
rerunning subprocess checks with process-group permission; that full run passed.
The existing TestClient deprecation warning remains.

Self-audit fixes received a separate read-only regression review. Ready for a
prototype commit; live agent compatibility, effective native policy/retention,
semantic source support, held-out acceptance, and owner understanding remain open.
No agent inference, paid call, commit, or push ran during the audit.

### T009: Solution proposal and plan revision

Applied `conduct-cs-ai-research` in human-led mode from the supplied checkout,
revision `bbb098d678356ae7312b2a8f42e321b3619ddf56`. The owner clarified that a
useful solution is the objective and reuse is encouraged (D003). The proposal
holds the dated source notes and product validation approach; this board holds
ownership. No additional dossier or research deliverable is needed.

Self-review: planning can continue. Execution readiness remains conditional on
T002–T004/T010, assigned reviewers, provider access, and a resource cap; T011 also
needs authorized adult sessions and resolved data handling. No product efficacy,
novelty, or release-readiness claim is made. No waiver was requested. Strict
Markdown and whitespace checks pass. Local CommonMark/table previews were
inspected; the hosted GitHub render is unverified.

### T001: Collaboration foundation

- Result: entry points, agent guidance, contribution workflow, writing guide,
  Level 0 acceptance criteria, decision log, and optional GitHub templates.
- Proposal: retained its wording; normalized heading levels and hard line breaks.
- Validation: checked all Markdown relative links and section targets, heading
  hierarchy, and fenced blocks. Ran whitespace checks with
  `git diff --no-index --check /dev/null <file>` across new files. Verified that
  local credentials and macOS metadata are ignored while placeholder environment
  examples remain trackable. There is no application to build or evaluate yet.
- Review: self-reviewed by the initializing agent; human review is pending.
- Next action: review these conventions, then claim T002, T003, or T004. No
  implementation stack, license, public release, or research result is implied.

### T007: GitHub metadata

- Description: Research on AI technical stewardship for non-expert software
  creation, from intent and risk assessment to sustainable software ownership.
- Topics: `artificial-intelligence`, `human-ai-collaboration`, `llm`,
  `requirements-engineering`, `software-engineering`, `technical-stewardship`,
  and `vibe-coding`.
- Labels: `area:design`, `area:implementation`, and `area:evaluation`, each with
  a description. Existing default labels remain available, including documentation.
- Milestone: Level 0: Intent Interpreter, with scope and exclusions from the
  proposal. No deadline has been assigned. Acceptance criteria remain in
  [Level 0 scope](level-0.md); task status remains on this board.
- Verification: read back the repository, labels, and milestone using
  `gh api repos/honghuy127/meta-vibe-coding`, the `/labels` endpoint, and
  `/milestones/1`. Self-reviewed against the proposal and the requested setup.
- Follow-up: no project homepage exists yet. Repository files are published
  separately through Git; metadata updates alone do not publish them.

For later handoffs, record only what helps the next contributor: result and paths,
checks and their limits, unresolved issue, and next action. Link a pull request or
commit when one exists. Avoid transcripts and routine activity diaries.


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
