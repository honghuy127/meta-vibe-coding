"""Fact-update contracts and process doubles; no native inference."""

import base64
import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from meta_vibe_coding import agents
from meta_vibe_coding.contracts import NativeResponse, native_schema
from meta_vibe_coding.core import FlowError, adopt, export_brief, prepare
from meta_vibe_coding.evaluation import BaselineResponse
from meta_vibe_coding.models import AdvanceRequest, Fact, Model, State
from test_flow import native_result, result


def payload(state=None, candidate=None):
    state = state or State(raw_intent='A household buzzer with no stored events.')
    return json.loads(native_result(state, candidate))


def update(key, *, value=None, status='unknown', evidence=None, owner_unknown=False):
    return {'key': key, 'value': value, 'status': status, 'reason': 'Scripted fixture.',
        'evidence': evidence or [], 'owner_unknown': owner_unknown}


def exposed_continuity_response(stage):
    # Recorded development output, already exposed; never inference or held-out evidence.
    path = Path(__file__).resolve().parents[1] / 'artifacts/2026-11-01-codex-luna-assessment-continuity.json'
    events = json.loads(path.read_text())['journal']['events']
    request = next(e['request'] for e in events if e['kind'] == 'http' and e.get('stage') == stage)
    state = prepare(AdvanceRequest.model_validate(request))
    state = state.model_copy(update={'agent_calls': state.agent_calls + 1})
    finished = next(e for e in events if e['kind'] == 'native_finished' and e['stage'] == stage)
    text, _ = agents.parse_completion('codex', base64.b64decode(finished['stdout_bytes_b64']))
    return state, json.loads(text)


@pytest.mark.parametrize('stage', ['scoped_sharing', 'download_access'])
def test_exposed_settled_question_is_rejected_without_claiming_semantic_omissions_are_detected(stage):
    state, body = exposed_continuity_response(stage)
    before = state.model_dump()
    candidate = NativeResponse.model_validate(body).candidate(state)
    with pytest.raises(FlowError, match='settled detail'): adopt(state, candidate)
    assert state.model_dump() == before and state.assessment is None
    with pytest.raises(FlowError, match='current recommendation'): export_brief(state)
    # Removing the bad question only diagnoses the remaining guard limit. It does
    # not repair or reclassify the historical response as an accepted result.
    candidate.question = None
    exported = export_brief(adopt(state, candidate))
    assert exported['facts']['access.catalogue_and_files']['value'] == 'Only the owner can see the catalogue and files for now.'
    assert exported['facts']['access.performer_clip_visibility']['status'] == 'confirmed'
    if stage == 'download_access':
        assert body['fact_updates'] == [] and candidate.facts == state.facts
        assert 't2' not in {source['id'] for source in exported['sources']}


def test_scripted_correction_updates_existing_access_and_separates_approval_from_request_capability():
    state, body = exposed_continuity_response('scoped_sharing')
    policy = 'workflow.title_correction_approval'
    body['question']['topic'] = policy
    for question in body['assessment']['open_questions']:
        if question['topic'] == 'workflow.performer_title_corrections': question['topic'] = policy
    body['fact_updates'].extend([
        update('access.catalogue_and_files', value='Owner access plus assigned-clip access for performers; private notes remain owner-only.',
            status='confirmed', evidence=[{'source_turn_id': 't0', 'quote': state.raw_intent},
                {'source_turn_id': 't1', 'quote': state.turns[-1].text}]),
        update(policy)])
    updated = adopt(state, NativeResponse.model_validate(body).candidate(state))
    assert updated.facts['access.catalogue_and_files'].source_turn_ids == ['t0', 't1']
    assert updated.facts['access.catalogue_and_files'].value != state.facts['access.catalogue_and_files'].value
    ability = updated.facts['workflow.performer_title_corrections'].model_dump()
    assert ability['status'] == 'confirmed' and updated.facts[policy].status == 'unknown'
    declared = prepare(AdvanceRequest(state=updated, request_id='approval-unknown', question_id=updated.questions[-1].id,
        answer="I don't know.", declares_unknown=True))
    assert declared.facts['workflow.performer_title_corrections'].model_dump() == ability
    assert declared.owner_unknowns[policy].source_turn_id == 't2'
    exported = export_brief(adopt(declared, result(declared, facts=declared.facts, disposition='provisional')))
    assert exported['facts'][policy]['status'] == 'unknown'
    assert exported['facts']['workflow.performer_title_corrections'] == ability
    assert exported['schema_version'] == 1


def test_scripted_permissions_and_operating_requirements_are_separate_sourced_facts():
    base = State(raw_intent='Organize fictional design documents for assigned reviewers.')
    state = adopt(base, result(base, disposition='provisional'))
    state = prepare(AdvanceRequest(state=state, request_id='requirements',
        answer='Reviewers may download assigned files. Removing their access must stop future access.'))
    keys = ['access.reviewer_downloads', 'access.future_revocation']
    supplied = {**state.facts, **{key: Fact(value=True, status='confirmed', source_turn_ids=['t1']) for key in keys}}
    candidate = NativeResponse.model_validate(payload(state, result(state, facts=supplied,
        disposition='provisional'))).candidate(state)
    exported = export_brief(adopt(state, candidate))
    for key in keys:
        assert exported['facts'][key]['value'] is True
        assert exported['facts'][key]['source_turn_ids'] == ['t1']
    assert exported['sources'][-1] == {'id': 't1', 'text': state.turns[-1].text}
    # Supplied output tests representation/transport, not successful agent extraction.


def test_native_schemas_are_closed_required_and_keep_local_bounds_separate():
    for model in (NativeResponse, BaselineResponse):
        schema = native_schema(model)
        def check(node):
            assert not set(node).intersection({'title', 'default', 'minLength', 'maxLength', 'pattern', 'minimum', 'maxItems'})
            if node.get('type') == 'object':
                assert node['additionalProperties'] is False
                assert set(node['required']) == set(node['properties'])
                for field in node['properties'].values(): check(field)
            for definition in node.get('$defs', {}).values(): check(definition)
            for branch in node.get('anyOf', []): check(branch)
            if 'items' in node: check(node['items'])
        check(schema)
    assert next(iter(native_schema(NativeResponse)['$defs']['NativeFactUpdate']['properties'])) == 'key'
    class ArbitraryMap(Model):
        facts: dict[str, str]
    with pytest.raises(ValueError, match='closed objects'): native_schema(ArbitraryMap)


@pytest.mark.parametrize('version', [True, 2.0, '2', 1, 99])
def test_native_contract_version_is_an_exact_supported_integer(version):
    body = payload(); body['contract_version'] = version
    with pytest.raises(ValidationError): NativeResponse.model_validate(body)


def test_question_references_one_fact_without_copying_it():
    state = State(raw_intent='A household buzzer.')
    body = payload(state)
    body['assessment']['disposition'] = 'provisional'
    body['fact_updates'].append(update('use.power'))
    body['question'] = {'topic': 'use.power', 'text': 'Which power?',
        'decision': 'Changes portability.', 'conflict_turn_id': None}
    candidate = NativeResponse.model_validate(body).candidate(state)
    updated = adopt(state, candidate)
    assert updated.questions[-1].topic == 'use.power'
    assert updated.facts['use.power'].value is None
    body['question']['fact'] = update('use.power')
    with pytest.raises(ValidationError): NativeResponse.model_validate(body)


def test_question_target_and_goal_must_exist_in_result():
    state = State(raw_intent='A household buzzer.')
    body = payload(state)
    body['question'] = {'topic': 'missing.fact', 'text': 'Where?',
        'decision': 'Changes portability.', 'conflict_turn_id': None}
    with pytest.raises(ValueError, match='Question target'):
        NativeResponse.model_validate(body).candidate(state)
    body['question'] = None; body['fact_updates'] = []
    with pytest.raises(ValueError, match='goal'):
        NativeResponse.model_validate(body).candidate(state)


@pytest.mark.parametrize('collection', ['fact_updates', 'remove_fact_keys'])
def test_duplicate_operation_keys_never_use_last_wins(collection):
    state = State(raw_intent='A household buzzer.')
    body = payload(state)
    if collection == 'fact_updates': body[collection].append(copy.deepcopy(body[collection][0]))
    else: body[collection] = ['use.power', 'use.power']
    with pytest.raises(ValueError, match='Duplicate native'):
        NativeResponse.model_validate(body).candidate(state)


@pytest.mark.parametrize('change', ['missing', 'quote', 'whitespace', 'source'])
def test_confirmed_updates_need_attached_exact_owner_evidence(change):
    state = State(raw_intent='A household buzzer.')
    body = payload(state); row = body['fact_updates'][0]
    if change == 'missing': row['evidence'] = []
    if change == 'quote': row['evidence'][0]['quote'] = 'Never said by the owner.'
    if change == 'whitespace': row['evidence'][0]['quote'] = ' '
    if change == 'source': row['evidence'][0]['source_turn_id'] = 't99'
    with pytest.raises(ValueError): NativeResponse.model_validate(body).candidate(state)


def test_other_facts_evidence_does_not_confirm_an_unsupported_update():
    state = State(raw_intent='A household buzzer.')
    body = payload(state)
    body['fact_updates'].append(update('use.power', value='mains', status='confirmed'))
    with pytest.raises(ValidationError, match='owner sources'):
        NativeResponse.model_validate(body).candidate(state)


def test_source_ids_are_derived_once_in_stable_order():
    state = State(raw_intent='A household buzzer.')
    body = payload(state)
    body['fact_updates'][0]['evidence'] *= 2
    candidate = NativeResponse.model_validate(body).candidate(state)
    assert candidate.facts['goal'].source_turn_ids == ['t0']


@pytest.mark.parametrize('sources', [['t0', 't1'], ['t0'], ['t1']])
def test_aggregate_evidence_keeps_source_coverage_a_semantic_review_responsibility(sources):
    base = State(raw_intent='Track equipment loans on my phone.')
    state = adopt(base, result(base))
    state = prepare(AdvanceRequest(state=state, request_id='access',
        answer='Coworkers may view only their own loans.'))
    aggregate = Fact(value='Track equipment loans on my phone with coworker-specific access.',
        status='confirmed', source_turn_ids=sources)
    candidate = NativeResponse.model_validate(payload(state,
        result(state, facts={'goal': aggregate}, disposition='provisional'))).candidate(state)
    if sources == ['t0']:
        with pytest.raises(FlowError, match='new owner reply'): adopt(state, candidate)
    else:
        exported = export_brief(adopt(state, candidate))
        assert exported['facts']['goal']['source_turn_ids'] == sources
        assert [source['id'] for source in exported['sources']] == sources
        # Latest-only quotes still pass structural checks without covering the aggregate.
        # Prompt guidance and semantic review, not source-ID unioning, address that gap.


def test_scripted_proposed_policy_and_copy_caveat_round_trip_without_confirmation():
    # Supplied prose checks transport, not the agent's ability to discover or label it.
    base = State(raw_intent='Track equipment loans.')
    state = prepare(AdvanceRequest(state=base, request_id='sharing',
        answer='Coworkers may see only their own loans and request extensions.'))
    policy = 'Proposed, if you choose owner approval: extensions change dates only after approval.'
    caveat = 'Ending future access cannot retrieve copies or derivatives already received.'
    candidate = result(state, disposition='provisional')
    candidate.facts['loan.approval'] = Fact(value=None, status='unknown', source_turn_ids=[],
        reason='The owner has not selected approval handling.')
    candidate.assessment.recommendation.summary = policy
    candidate.assessment.recommendation.owner_responsibilities = [policy, caveat]
    candidate.assessment.acceptance_criteria = [policy, caveat]
    candidate.assessment.limitations = [caveat]
    exported = export_brief(adopt(state, NativeResponse.model_validate(payload(state, candidate)).candidate(state)))
    assert exported['facts']['loan.approval']['status'] == 'unknown'
    assert exported['facts']['loan.approval']['source_turn_ids'] == []
    assert exported['recommendation']['summary'] == policy
    assert exported['recommendation']['owner_responsibilities'] == [policy, caveat]
    assert exported['acceptance_criteria'] == [policy, caveat]
    assert exported['limitations'] == [caveat]


def test_unchanged_facts_need_no_updates_and_input_is_not_mutated_or_aliased():
    base = State(raw_intent='A household buzzer.')
    state = adopt(base, result(base))
    state = prepare(AdvanceRequest(state=state, request_id='explain', answer='What does standalone mean?'))
    before = state.model_dump()
    body = payload(state, result(state, facts=state.facts, disposition='provisional'))
    assert body['fact_updates'] == []
    candidate = NativeResponse.model_validate(body).candidate(state)
    updated = adopt(state, candidate)
    assert state.model_dump() == before and updated.assessed_turn_count == 1
    candidate.facts['goal'].value = 'Changed outside original state.'
    assert state.model_dump() == before
    assert export_brief(updated)['schema_version'] == 1


@pytest.mark.parametrize('key', ['goal', 'use.power', 'missing.fact'])
def test_protected_and_missing_removals_are_rejected(key):
    state = State(raw_intent='A buzzer. I do not know its power source.', facts={
        'goal': Fact(value='A buzzer.', status='confirmed', source_turn_ids=['t0']),
        'use.power': Fact(value=None, status='unknown', source_turn_ids=['t0'])},
        owner_unknowns={'use.power': {'source_turn_id': 't0', 'quote': 'I do not know its power source.'}})
    body = payload(state, result(state, facts=state.facts, disposition='provisional'))
    body['remove_fact_keys'] = [key]
    with pytest.raises(ValueError, match='Cannot remove'):
        NativeResponse.model_validate(body).candidate(state)


def test_obsolete_assumption_can_be_removed_but_not_also_updated():
    state = State(raw_intent='A buzzer.', facts={
        'goal': Fact(value='A buzzer.', status='confirmed', source_turn_ids=['t0']),
        'use.power': Fact(value='battery', status='assumed', source_turn_ids=[], reason='Fixture guess.')})
    body = payload(state, result(state, facts=state.facts, disposition='provisional'))
    body['remove_fact_keys'] = ['use.power']
    candidate = NativeResponse.model_validate(body).candidate(state)
    assert 'use.power' not in adopt(state, candidate).facts and 'use.power' in state.facts
    body['fact_updates'] = [update('use.power')]
    with pytest.raises(ValueError, match='updated and removed'):
        NativeResponse.model_validate(body).candidate(state)


def test_combined_result_fact_limit_includes_carried_facts():
    state = State(raw_intent='A buzzer.', facts={
        'goal': Fact(value='A buzzer.', status='confirmed', source_turn_ids=['t0']),
        **{f'unknown.k{i}': Fact(value=None, status='unknown', source_turn_ids=[]) for i in range(99)}})
    body = payload(state, result(state, facts=state.facts, disposition='provisional'))
    body['fact_updates'] = [update('unknown.extra')]
    with pytest.raises(ValueError, match='Too many'): NativeResponse.model_validate(body).candidate(state)


def declared_state():
    return State(raw_intent='A buzzer. I do not know its power source.', facts={
        'goal': Fact(value='A buzzer.', status='confirmed', source_turn_ids=['t0']),
        'use.power': Fact(value=None, status='unknown', source_turn_ids=['t0'])},
        owner_unknowns={'use.power': {'source_turn_id': 't0', 'quote': 'I do not know its power source.'}})


def test_declaration_builds_fact_and_marker_from_the_same_evidence():
    state = State(raw_intent='A buzzer. I do not know its power source.')
    body = payload(state)
    body['fact_updates'].append(update('use.power', owner_unknown=True,
        evidence=[{'source_turn_id': 't0', 'quote': 'I do not know its power source.'}]))
    updated = adopt(state, NativeResponse.model_validate(body).candidate(state))
    assert updated.facts['use.power'].source_turn_ids == ['t0']
    assert updated.owner_unknowns['use.power'].source_turn_id == 't0'


@pytest.mark.parametrize('change', ['no_evidence', 'two_evidence', 'assumed'])
def test_declaration_cannot_be_an_inference_or_an_ambiguous_quote(change):
    state = State(raw_intent='A buzzer. I do not know its power source.')
    body = payload(state)
    row = update('use.power', owner_unknown=True,
        evidence=[{'source_turn_id': 't0', 'quote': 'I do not know its power source.'}])
    if change == 'no_evidence': row['evidence'] = []
    if change == 'two_evidence': row['evidence'] *= 2
    if change == 'assumed': row.update(value='battery', status='assumed')
    body['fact_updates'].append(row)
    with pytest.raises(ValueError, match='owner unknown'): NativeResponse.model_validate(body).candidate(state)


def test_retained_unknown_is_carried_and_cannot_be_cleared_by_a_false_flag():
    state = declared_state()
    body = payload(state, result(state, facts=state.facts, disposition='provisional'))
    assert not body['fact_updates']
    assert adopt(state, NativeResponse.model_validate(body).candidate(state)).owner_unknowns == state.owner_unknowns
    body['fact_updates'] = [update('use.power')]
    with pytest.raises(ValueError, match='keep its cited source'):
        NativeResponse.model_validate(body).candidate(state)
    body['fact_updates'][0]['evidence'] = [state.owner_unknowns['use.power'].model_dump()]
    assert adopt(state, NativeResponse.model_validate(body).candidate(state)).owner_unknowns == state.owner_unknowns


def test_retained_unknown_question_is_suppressed_only_with_an_open_decision():
    state = declared_state()
    body = payload(state, result(state, facts=state.facts, disposition='provisional'))
    body['question'] = {'topic': 'use.power', 'text': 'Which power?',
        'decision': 'Changes portability.', 'conflict_turn_id': None}
    with pytest.raises(FlowError, match='unresolved decision'):
        adopt(state, NativeResponse.model_validate(body).candidate(state))
    body['assessment']['open_questions'] = [{'topic': 'use.power', 'text': 'Power is unknown.',
        'blocks_recommendation': False, 'reason': 'Check available power before selection.'}]
    updated = adopt(state, NativeResponse.model_validate(body).candidate(state))
    assert updated.questions == [] and updated.owner_unknowns == state.owner_unknowns


def test_later_explicit_unknown_can_replace_a_marker_but_older_or_same_changed_evidence_cannot():
    original = declared_state()
    state = prepare(AdvanceRequest(state=original, request_id='still-unknown',
        answer='I still do not know its power source.'))
    body = payload(state, result(state, facts=state.facts, disposition='provisional'))
    body['fact_updates'] = [update('use.power', owner_unknown=True,
        evidence=[{'source_turn_id': 't1', 'quote': state.turns[-1].text}])]
    updated = adopt(state, NativeResponse.model_validate(body).candidate(state))
    assert updated.owner_unknowns['use.power'].source_turn_id == 't1'
    assert updated.facts['use.power'].source_turn_ids == ['t1']
    body = payload(updated, result(updated, facts=updated.facts, disposition='provisional'))
    for source, quote in [('t0', original.raw_intent), ('t1', 'do not know')]:
        body['fact_updates'] = [update('use.power', owner_unknown=True,
            evidence=[{'source_turn_id': source, 'quote': quote}])]
        with pytest.raises(FlowError, match='changed the source'):
            adopt(updated, NativeResponse.model_validate(body).candidate(updated))


@pytest.mark.parametrize('flag', [1, 'true', None])
def test_unknown_declaration_flag_is_a_strict_boolean(flag):
    body = payload(); body['fact_updates'][0]['owner_unknown'] = flag
    with pytest.raises(ValidationError): NativeResponse.model_validate(body)


@pytest.mark.parametrize('reply', [None, 'Continue.', 'I do not know.', 'Use a battery.'])
def test_updates_do_not_bypass_original_state_unknown_promotion_guards(reply):
    state = declared_state()
    if reply: state = prepare(AdvanceRequest(state=state, request_id='reply', answer=reply))
    body = payload(state, result(state, facts=state.facts, disposition='provisional'))
    body['fact_updates'] = [update('use.power', value='battery', status='confirmed',
        evidence=[{'source_turn_id': 't1' if reply else 't0', 'quote': reply or state.raw_intent}])]
    candidate = NativeResponse.model_validate(body).candidate(state)
    before = state.model_dump()
    if reply == 'Use a battery.': assert not adopt(state, candidate).owner_unknowns
    else:
        with pytest.raises(FlowError): adopt(state, candidate)
    assert state.model_dump() == before


@pytest.mark.parametrize('value', [1, False])
def test_typed_confirmed_changes_still_require_fresh_owner_evidence(value):
    state = State(raw_intent='I need the option.', facts={
        'goal': Fact(value='An option.', status='confirmed', source_turn_ids=['t0']),
        'device.option': Fact(value=True, status='confirmed', source_turn_ids=['t0'])})
    body = payload(state, result(state, facts=state.facts))
    body['fact_updates'] = [update('device.option', value=value, status='confirmed',
        evidence=[{'source_turn_id': 't0', 'quote': state.raw_intent}])]
    with pytest.raises(FlowError, match='changed confirmed'):
        adopt(state, NativeResponse.model_validate(body).candidate(state))


def test_partial_context_can_be_followed_by_a_distinct_preference_but_not_same_topic():
    base = State(raw_intent='A household buzzer.')
    state = adopt(base, result(base, question={'topic': 'use.location', 'text': 'Where?',
        'decision': 'Changes portability.'}, disposition='provisional'))
    state = prepare(AdvanceRequest(state=state, request_id='partial', question_id='q1', answer='On my kitchen counter.'))
    facts = {**state.facts, 'use.location': Fact(value='kitchen counter', status='confirmed', source_turn_ids=['t1'])}
    followup = result(state, facts=facts, question={'topic': 'use.alert_preference',
        'text': 'Sound or light?', 'decision': 'Changes the alert.'}, disposition='provisional')
    body = payload(state, followup)
    updated = adopt(state, NativeResponse.model_validate(body).candidate(state))
    assert updated.facts['use.location'].value == 'kitchen counter'
    assert updated.questions[-1].topic == 'use.alert_preference'
    body['question']['topic'] = 'use.location'
    with pytest.raises(FlowError, match='settled detail'):
        adopt(state, NativeResponse.model_validate(body).candidate(state))


def test_old_native_and_canonical_json_are_not_fallbacks():
    state = State(raw_intent='A household buzzer.')
    for content in (result(state).model_dump_json(), json.dumps({'contract_version': 1,
            'facts': [], 'owner_unknowns': [], 'grounding': [], 'question': None})):
        raw = '\n'.join(json.dumps(e) for e in [
            {'type': 'thread.started'}, {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': content}},
            {'type': 'turn.completed'}]).encode()
        with pytest.raises(ValidationError): agents.parse_result('codex', raw, state)


@pytest.mark.parametrize('idea,constraint,consequence', [
    ('I need to hand study files to a visiting mentor.', 'Keep the existing originals unchanged.',
     'Ending future access does not recover copies or derivatives already handed out.'),
    ('I need a build bot to publish releases.', 'It must run while I am away.',
     'The automated process needs a service identity and scoped credentials separate from a person.')])
def test_fresh_handoff_and_automation_fixtures_preserve_supplied_consequences(idea, constraint, consequence):
    # These are scripted transport/export examples, not evidence the model discovers the consequence.
    base = State(raw_intent=idea)
    state = prepare(AdvanceRequest(state=base, request_id='constraint', answer=constraint))
    facts = {'goal': Fact(value=idea, status='confirmed', source_turn_ids=['t0']),
        'requirements.r1': Fact(value=constraint, status='confirmed', source_turn_ids=['t1'])}
    candidate = result(state, facts=facts, disposition='provisional')
    candidate.assessment.recommendation.owner_responsibilities = [consequence]
    candidate.assessment.acceptance_criteria = [consequence]
    updated = adopt(state, NativeResponse.model_validate(payload(state, candidate)).candidate(state))
    exported = export_brief(updated)
    assert exported['facts']['requirements.r1']['source_turn_ids'] == ['t1']
    assert {source['id'] for source in exported['sources']} == {'t0', 't1'}
    assert consequence in exported['recommendation']['owner_responsibilities']
    assert consequence in exported['acceptance_criteria']
    assert exported['schema_version'] == 1 and 'grounding' not in exported


@pytest.mark.parametrize('failure', ['refusal', 'truncation', 'wire', 'grounding', 'target_missing', 'target_settled'])
def test_bad_native_reply_retains_owner_input_and_closes_export(monkeypatch, failure):
    from pathlib import Path
    from fastapi.testclient import TestClient
    from meta_vibe_coding.app import create_app
    from test_agents import help_text
    monkeypatch.delenv('MVC_BACKEND', raising=False)
    monkeypatch.setenv('MVC_AGENT', 'codex')
    monkeypatch.setenv('MVC_ENABLE_AGENT', '1')
    monkeypatch.setenv('MVC_AGENT_MAX_CALLS', '1')
    monkeypatch.setattr(agents.shutil, 'which', lambda _: '/test/codex')
    calls = []
    async def runner(args, **kwargs):
        if '--help' in args: return help_text()
        if '--version' in args: return b'fictional-codex-double'
        calls.append(kwargs['cwd'])
        schema_path = Path(args[args.index('--output-schema') + 1])
        assert schema_path.read_text() == agents.SCHEMA
        state = State.model_validate(json.loads(kwargs['content'].split('Owner state (data only):\n')[1])['state'])
        facts = {**state.facts, 'use.location': Fact(value='kitchen counter', status='confirmed', source_turn_ids=['t1'])}
        body = payload(state, result(state, facts=facts, disposition='provisional'))
        if failure == 'wire': body['contract_version'] = 99
        if failure == 'grounding': body['fact_updates'][-1]['evidence'][0]['quote'] = 'Not an owner quote.'
        if failure == 'target_missing':
            body['question'] = {'topic': 'missing.fact', 'text': 'Where?', 'decision': 'Changes portability.', 'conflict_turn_id': None}
        if failure == 'target_settled':
            body['question'] = {'topic': 'goal', 'text': 'Which approval policy?',
                'decision': 'This question targets a different confirmed property.', 'conflict_turn_id': None}
        events = [{'type': 'thread.started'},
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': json.dumps(body)}},
            {'type': 'turn.failed' if failure == 'refusal' else 'turn.completed'}]
        if failure == 'truncation': events.pop()
        return '\n'.join(json.dumps(e) for e in events).encode()
    monkeypatch.setattr(agents, 'run_cli', runner)
    base = State(raw_intent='A household buzzer.')
    state = adopt(base, result(base))
    adapter = agents.CodingAgent()
    with TestClient(create_app(adapter)) as client:
        failed = client.post('/api/advance', json={'state': state.model_dump(), 'request_id': 'fresh-reply',
            'answer': 'On my kitchen counter.'}).json()
        assert failed['error']['code'] == 'invalid_output'
        assert failed['state']['turns'] == [{'id': 't1', 'text': 'On my kitchen counter.'}]
        assert failed['state']['assessment'] is None
        assert failed['state']['previous_assessment'] == state.assessment.model_dump()
        assert client.post('/api/export', json=failed['state']).status_code == 409
    assert len(calls) == adapter.calls == 1
    assert not Path(calls[0]).exists(), 'Private schema and workspace must be removed on failure'
