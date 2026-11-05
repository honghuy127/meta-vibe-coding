"""Explicit continuity checks with fictional supplied outputs; no inference."""

import json

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from meta_vibe_coding.app import create_app
from meta_vibe_coding.contracts import NativeResponse
from meta_vibe_coding.core import FlowError, adopt, export_brief, model_input, prepare
from meta_vibe_coding.models import AdvanceRequest, AssessmentChange, State, UnknownEvidence, Usage
from test_flow import native_result, result


def pending():
    base = State(raw_intent='Preview fictional photo renames locally.')
    candidate = result(base, disposition='provisional')
    candidate.assessment.limitations = ['Recovering an original requires retaining it.', 'Storage cost is unknown.']
    return prepare(AdvanceRequest(state=adopt(base, candidate), request_id='next'))


def change(previous='limitations/0', current=None, basis='reworded', reason='Same recovery condition, shorter wording.', evidence=None):
    return AssessmentChange(previous=previous, current=['limitations/0'] if current is None else current,
        basis=basis, reason=reason, evidence=evidence or [])


@pytest.mark.parametrize('field', ['risk.reasons', 'hidden_requirements', 'recommendation.rationale',
    'recommendation.alternatives', 'recommendation.owner_responsibilities',
    'acceptance_criteria', 'open_questions', 'limitations'])
def test_nonempty_replacement_cannot_silently_drop_a_prior_list_item(field):
    base = State(raw_intent='Rename fictional photos.')
    candidate = result(base, disposition='provisional')
    if field == 'hidden_requirements':
        from meta_vibe_coding.models import HiddenRequirement
        candidate.assessment.hidden_requirements = [HiddenRequirement(text='Preview first.', reason='Avoid unwanted changes.')]
    state = prepare(AdvanceRequest(state=adopt(base, candidate), request_id='next'))
    candidate = result(state, facts=state.facts, disposition='provisional')
    obj = candidate.assessment
    parts = field.split('.')
    for part in parts[:-1]: obj = getattr(obj, part)
    # Keep a well-formed nonempty list, with a different item in place of the old.
    rows = getattr(obj, parts[-1])
    if isinstance(rows[0], str): rows[0] = 'A different generic statement.'
    elif field == 'hidden_requirements': rows[0] = rows[0].model_copy(update={'text': 'Different suggestion.'})
    else: rows[0] = rows[0].model_copy(update={'text': 'A different open decision.'})
    candidate = NativeResponse.model_validate_json(native_result(state, candidate)).candidate(state)
    before = state.model_dump()
    with pytest.raises(FlowError, match='earlier assessment'): adopt(state, candidate)
    assert state.model_dump() == before and state.previous_assessment is not None
    with pytest.raises(FlowError): export_brief(state)


def test_rewording_consolidation_and_reordering_keep_state_and_export_in_agreement():
    state = pending()
    candidate = result(state, facts=state.facts, disposition='provisional')
    candidate.assessment.limitations = ['Keep originals for recovery; storage cost remains unknown.']
    candidate.assessment_changes = [change('limitations/0'), change('limitations/1')]
    updated = adopt(state, NativeResponse.model_validate_json(native_result(state, candidate)).candidate(state))
    assert updated.previous_assessment is None
    assert export_brief(updated)['limitations'] == updated.assessment.limitations
    assert 'assessment_changes' not in export_brief(updated)
    reordered = result(state, facts=state.facts, disposition='provisional')
    reordered.assessment.limitations.reverse()
    assert adopt(state, reordered).assessment.limitations == list(reversed(state.previous_assessment.limitations))


@pytest.mark.parametrize('fault', ['duplicate', 'missing', 'old_index', 'new_index', 'cross_field',
    'empty_reason', 'empty_rewrite', 'duplicate_replacement', 'unneeded', 'agent_evidence'])
def test_invalid_accounting_is_refused(fault):
    state = pending()
    candidate = result(state, facts=state.facts, disposition='provisional')
    candidate.assessment.limitations[0] = 'Keep originals to recover.'
    row = change()
    if fault == 'old_index': row.previous = 'limitations/9'
    if fault == 'new_index': row.current = ['limitations/9']
    if fault == 'cross_field': row.current = ['acceptance_criteria/0']
    if fault == 'empty_reason': row.reason = ' '
    if fault == 'empty_rewrite': row.current = []
    if fault == 'duplicate_replacement': row.current *= 2
    if fault == 'unneeded': row.previous = 'limitations/1'
    if fault == 'agent_evidence': row.evidence = [UnknownEvidence(source_turn_id='t0', quote=state.raw_intent)]
    candidate.assessment_changes = [] if fault == 'missing' else [row, row] if fault == 'duplicate' else [row]
    # Validate the supplied candidate too, including nested evidence types.
    from meta_vibe_coding.models import Candidate
    candidate = Candidate.model_validate(candidate.model_dump())
    with pytest.raises(FlowError): adopt(state, candidate)


@pytest.mark.parametrize('answer,source,quote,accepted', [
    ('I have backed up the originals.', 't1', 'backed up the originals', True),
    ('I have backed up the originals.', 't0', 'Preview fictional photo renames locally.', False),
    ('I have backed up the originals.', 't1', 'A fabricated quote', False),
    ('Continue.', 't1', 'Continue.', False),
    ("I don't know.", 't1', "I don't know.", False),
])
def test_owner_resolution_requires_new_substantive_quoted_evidence_even_after_failure(answer, source, quote, accepted):
    state = prepare(AdvanceRequest(state=pending(), request_id='answer', answer=answer))
    retry = prepare(AdvanceRequest(state=state, request_id='retry'))
    assert retry.previous_assessment == state.previous_assessment and retry.assessed_turn_count == 0
    candidate = result(retry, facts=retry.facts, disposition='provisional')
    candidate.assessment.limitations.pop(0)
    candidate.assessment_changes = [change(current=[], basis='owner_update',
        reason='The owner now reports a backup.', evidence=[{'source_turn_id':source, 'quote':quote}])]
    if accepted:
        updated = adopt(retry, candidate)
        assert updated.assessed_turn_count == 1 and export_brief(updated)['limitations'] == ['Storage cost is unknown.']
    else:
        with pytest.raises(FlowError, match='new quoted owner input'): adopt(retry, candidate)


def test_first_assessment_and_direct_adoption_cannot_bypass_the_guard():
    base = State(raw_intent='Fictional idea.')
    candidate = result(base)
    candidate.assessment_changes = [change()]
    with pytest.raises(FlowError): adopt(base, candidate)
    candidate.assessment_changes = []
    state = adopt(base, candidate)
    candidate = result(state, facts=state.facts)
    candidate.assessment.limitations = ['Changed without preparation.']
    with pytest.raises(FlowError, match='earlier assessment'): adopt(state, candidate)


def test_advice_withdrawal_is_explicit_but_its_justification_still_needs_semantic_review():
    state = pending()
    candidate = result(state, facts=state.facts, disposition='provisional')
    candidate.assessment.limitations.pop(0)
    candidate.assessment_changes = [change(current=[], basis='advice_withdrawn',
        reason='The earlier advice was incorrect in this scripted example.')]
    assert adopt(state, candidate).assessment.limitations == ['Storage cost is unknown.']
    # The structural guard intentionally does not judge this reason's truth.


def test_http_failure_retains_the_anchor_answers_and_closed_export_until_accounted_retry():
    class ScriptedAgent:
        async def assess(self, state, provisional):
            candidate = result(state, facts=state.facts, disposition='provisional')
            candidate.assessment.limitations[0] = 'Retain originals to recover.'
            if state.agent_calls > 1: candidate.assessment_changes = [change()]
            return candidate, Usage(agent='test-double', elapsed_seconds=0)
    original = pending()
    with TestClient(create_app(ScriptedAgent())) as client:
        failed = client.post('/api/advance', json={'state':original.model_dump(), 'request_id':'first',
            'answer':'Please explain recovery.', 'provisional':True}).json()
        assert failed['error']['code'] == 'invalid_output'
        state = failed['state']
        assert state['previous_assessment'] == original.previous_assessment.model_dump()
        assert state['turns'][0]['text'] == 'Please explain recovery.'
        assert client.post('/api/export',json=state).status_code == 409
        success = client.post('/api/advance',json={'state':state,'request_id':'retry','provisional':True}).json()
        assert success['error'] is None
        exported = client.post('/api/export',json=success['state']).json()
        assert exported['limitations'] == success['state']['assessment']['limitations']
        assert exported['schema_version'] == 1 and len(success['state']['turns']) == 1
        assert 'assessment_changes' not in json.loads(model_input(State.model_validate(success['state']), True))['state']


def test_normalized_open_topic_is_valid_when_the_question_is_suppressed():
    state = State(raw_intent='Fictional idea.')
    candidate = result(state, question={'topic':'operations.budget','text':'Budget?', 'decision':'Changes options.'},
        disposition='provisional')
    candidate.assessment.open_questions[0].topic = '  Operations.Budget '
    updated = adopt(state, candidate, allow_question=False)
    assert updated.questions == [] and export_brief(updated)['open_questions'][0]['topic'] == '  Operations.Budget '


def test_contract_three_requires_accounting_field_and_rejects_old_native_output():
    body = json.loads(native_result(State(raw_intent='Fictional idea.')))
    body.pop('assessment_changes')
    with pytest.raises(ValidationError): NativeResponse.model_validate(body)
    body['assessment_changes'] = []; body['contract_version'] = 2
    with pytest.raises(ValidationError): NativeResponse.model_validate(body)


def test_previously_assessed_owner_turn_cannot_justify_a_later_removal():
    first = prepare(AdvanceRequest(state=pending(), request_id='first-answer', answer='I saved a copy.'))
    adopted = adopt(first, result(first, facts=first.facts, disposition='provisional'))
    assert adopted.assessed_turn_count == 1
    state = prepare(AdvanceRequest(state=adopted, request_id='later', answer='The label should be blue.'))
    candidate = result(state, facts=state.facts, disposition='provisional')
    candidate.assessment.limitations.pop(0)
    candidate.assessment_changes = [change(current=[], basis='owner_update',
        reason='The owner saved a copy.', evidence=[{'source_turn_id':'t1','quote':'I saved a copy.'}])]
    with pytest.raises(FlowError, match='new quoted owner input'): adopt(state, candidate)


@pytest.mark.parametrize('field', ['rationale', 'alternatives', 'owner_responsibilities'])
@pytest.mark.parametrize('outer_spaces', [False, True])
def test_unambiguous_recommendation_aliases_work_without_mutating_the_response(field, outer_spaces):
    state = pending()
    candidate = result(state, facts=state.facts, disposition='provisional')
    rows = getattr(candidate.assessment.recommendation, field)
    rows[0] += ' Retain the same condition.'
    alias = f'{field}/0'
    if outer_spaces: alias = f'  {alias}  '
    candidate.assessment_changes = [change(previous=alias, current=[alias])]
    wire = native_result(state, candidate)
    decoded = NativeResponse.model_validate_json(wire).candidate(state)
    before = decoded.model_dump()
    updated = adopt(state, decoded)
    assert export_brief(updated)['recommendation'][field] == rows
    assert decoded.model_dump() == before


@pytest.mark.parametrize('which', ['previous', 'current'])
def test_alias_and_canonical_duplicates_are_rejected_after_normalization(which):
    state = pending()
    candidate = result(state, facts=state.facts, disposition='provisional')
    candidate.assessment.recommendation.owner_responsibilities[0] = 'Retain originals before making changes.'
    row = change(previous='owner_responsibilities/0', current=['owner_responsibilities/0'])
    if which == 'previous':
        candidate.assessment_changes = [row, change(previous=' recommendation.owner_responsibilities/0 ',
            current=['recommendation.owner_responsibilities/0'])]
    else:
        row.current.append(' recommendation.owner_responsibilities/0 ')
        candidate.assessment_changes = [row]
    with pytest.raises(FlowError): adopt(state, candidate)


def test_optional_unchanged_record_is_valid_but_does_not_account_for_a_different_loss():
    state = pending()
    candidate = result(state, facts=state.facts, disposition='provisional')
    candidate.assessment_changes = [change(previous=' limitations/0 ', current=['limitations/0'],
        reason='Retained the same recovery condition.')]
    assert adopt(state, candidate).assessment.limitations == state.previous_assessment.limitations
    candidate.assessment.limitations.pop(1)
    with pytest.raises(FlowError, match='earlier assessment'): adopt(state, candidate)


@pytest.mark.parametrize('fault', ['blank_reason', 'missing_previous', 'missing_current', 'cross_list', 'stale_owner_source'])
def test_optional_unchanged_record_still_obeys_all_validation(fault):
    state = pending()
    candidate = result(state, facts=state.facts, disposition='provisional')
    row = change()
    if fault == 'blank_reason': row.reason = ' '
    if fault == 'missing_previous': row.previous = 'limitations/99'
    if fault == 'missing_current': row.current = ['limitations/99']
    if fault == 'cross_list': row.current = ['acceptance_criteria/0']
    if fault == 'stale_owner_source':
        row.basis = 'owner_update'
        row.evidence = [UnknownEvidence(source_turn_id='t0', quote=state.raw_intent)]
    candidate.assessment_changes = [row]
    with pytest.raises(FlowError): adopt(state, candidate)


@pytest.mark.parametrize('path', ['Owner_responsibilities/0', 'owner_responsibilities /0',
    'owner_responsibilities/00', 'assessment.owner_responsibilities/0'])
def test_reference_normalization_does_not_guess_other_spellings_or_indices(path):
    state = pending()
    candidate = result(state, facts=state.facts, disposition='provisional')
    candidate.assessment.recommendation.owner_responsibilities[0] = 'Retain originals.'
    candidate.assessment_changes = [change(previous=path, current=['owner_responsibilities/0'])]
    with pytest.raises(FlowError): adopt(state, candidate)


@pytest.mark.parametrize('job,accepted', [('C01-wrapper',False),('C02-wrapper',True),
    ('C03-wrapper',True),('C04-wrapper',False)])
def test_exposed_v7_refusals_are_diagnostics_and_never_replace_the_frozen_attempt(job, accepted):
    import hashlib
    from pathlib import Path
    from meta_vibe_coding import agents
    path = Path(__file__).parents[1] / 'artifacts/2026-11-03-claude-sonnet-acceptance-v7.json'
    raw = path.read_bytes(); before = hashlib.sha256(raw).hexdigest()
    archive = json.loads(raw)
    events = [json.loads(line) for line in archive['files']['acceptance-v7/journal.jsonl']['text'].splitlines()]
    start = [e for e in events if e['type']=='native_started' and e.get('job')==job][-1]
    finish = next(e for e in events if e['type']=='native_finished' and e['number']==start['number'])
    packet = json.loads(start['stdin'].split('Owner state (data only):\n',1)[1])
    state = State.model_validate(packet['state'])
    candidate, _ = agents.parse_result('claude',finish['streams']['stdout'].encode(),state)
    if accepted:
        updated = adopt(state,candidate,allow_question=not packet['request_provisional'])
        assert export_brief(updated)['schema_version']==1
    else:
        with pytest.raises(FlowError,match='earlier assessment'):adopt(state,candidate)
    assert next(e for e in events if e['type']=='job_finished' and e.get('job')==job)['failure']['code']=='invalid_output'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==before
