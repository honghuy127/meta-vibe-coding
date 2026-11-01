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
| T011 | Check whether adult owners understand and can use the L0 handoff | blocked | Unassigned | Authorized session artifacts; short result in this board | Depends on T006, named facilitator, consent/data-handling decisions, and owner authorization. Record comprehension, task completion, burden, and changes needed before L1. |
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
| T029 | Prepare fresh correction verification | ready | Unassigned | Reviewed development plan/harness, relevant docs | Freeze a fresh fictional correction flow, current source/settings and a new call cap. Review a feasible native HTTP and browser-check strategy so browser focus failures do not masquerade as model failures; label any UI replay separately. T027 remains partial and its unused calls stay closed; no allowance yet. |

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
acceptance claim; T027's unused allowance remains closed. Changes are uncommitted.
Next: T029 prepares fresh verification; unresolved status and key equality still
cannot establish that a question asks about the correct semantic property.

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
