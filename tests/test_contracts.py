"""Fresh response-contract fixtures and process doubles; no native inference."""

import copy
import json

import pytest
from pydantic import ValidationError

from meta_vibe_coding import agents
from meta_vibe_coding.contracts import NativeResponse, native_schema
from meta_vibe_coding.core import FlowError, adopt, export_brief, prepare
from meta_vibe_coding.evaluation import BaselineResponse
from meta_vibe_coding.models import AdvanceRequest, Fact, Model, State, Turn
from test_flow import native_result, result


def payload(state=None, candidate=None):
    state = state or State(raw_intent='A household buzzer with no stored events.')
    return json.loads(native_result(state, candidate))


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
    assert next(iter(native_schema(NativeResponse)['$defs']['NativeFact']['properties'])) == 'key'
    class ArbitraryMap(Model):
        facts: dict[str, str]
    with pytest.raises(ValueError, match='closed objects'):
        native_schema(ArbitraryMap)


@pytest.mark.parametrize('version', [True, 1.0, '1', 2])
def test_native_contract_version_is_an_exact_supported_integer(version):
    body = payload()
    body['contract_version'] = version
    with pytest.raises(ValidationError): NativeResponse.model_validate(body)


def test_embedded_target_decodes_to_a_bound_unknown_without_guessing_a_value():
    state = State(raw_intent='A household buzzer with no stored events.')
    body = payload(state)
    body['assessment']['disposition'] = 'provisional'
    body['question'] = {'fact': {'key': 'use.power', 'value': None, 'status': 'unknown',
        'source_turn_ids': [], 'reason': 'Power source is not provided.'},
        'text': 'Where can it get power?', 'decision': 'Changes portability.', 'conflict_turn_id': None}
    candidate = NativeResponse.model_validate(body).candidate(state)
    assert candidate.facts['use.power'].value is None
    updated = adopt(state, candidate)
    assert updated.questions[-1].topic == 'use.power'
    assert updated.facts['use.power'].status == 'unknown'
    body['facts'].append(copy.deepcopy(body['question']['fact']))
    assert NativeResponse.model_validate(body).candidate(state) == candidate


@pytest.mark.parametrize('value', [1, False])
def test_question_target_conflicts_are_type_sensitive(value):
    state = State(raw_intent='A household buzzer.')
    body = payload(state)
    target = {'key': 'device.option', 'value': True, 'status': 'assumed',
        'source_turn_ids': [], 'reason': 'Fixture inference.'}
    body['facts'].append(target)
    body['question'] = {'fact': {**target, 'value': value}, 'text': 'Which option?',
        'decision': 'Changes the option.', 'conflict_turn_id': None}
    with pytest.raises(ValueError, match='conflicts'):
        NativeResponse.model_validate(body).candidate(state)


@pytest.mark.parametrize('collection', ['facts', 'owner_unknowns'])
def test_duplicate_array_keys_never_use_last_wins(collection):
    state = State(raw_intent='A household buzzer; I do not know its power source.')
    body = payload(state)
    if collection == 'facts': body['facts'].append(copy.deepcopy(body['facts'][0]))
    else:
        entry = {'key': 'use.power', 'source_turn_id': 't0', 'quote': 'I do not know its power source.'}
        body['owner_unknowns'] = [entry, entry]
    with pytest.raises(ValueError, match='Duplicate native'):
        NativeResponse.model_validate(body).candidate(state)


@pytest.mark.parametrize('change', ['missing', 'quote', 'whitespace', 'source', 'key', 'link'])
def test_new_confirmation_needs_exact_source_linked_grounding(change):
    state = State(raw_intent='A household buzzer with no stored events.')
    body = payload(state)
    if change == 'missing': body['grounding'] = []
    if change == 'quote': body['grounding'][0]['quote'] = 'The owner never said this.'
    if change == 'whitespace': body['grounding'][0]['quote'] = ' '
    if change == 'source': body['grounding'][0]['source_turn_id'] = 't99'
    if change == 'key': body['grounding'][0]['fact_keys'] = ['missing.key']
    if change == 'link': body['facts'][0]['source_turn_ids'] = ['t1']
    with pytest.raises(ValueError): NativeResponse.model_validate(body).candidate(state)


def test_quote_group_cannot_link_an_unknown_fact_without_the_cited_source():
    state = State(raw_intent='A shared rota. Reminder preferences are undecided.')
    body = payload(state)
    body['facts'].append({'key': 'reminders.preference', 'value': None,
        'status': 'unknown', 'source_turn_ids': [], 'reason': 'Undecided.'})
    body['grounding'][0]['fact_keys'].append('reminders.preference')
    with pytest.raises(ValueError, match='existing fact and its cited source'):
        NativeResponse.model_validate(body).candidate(state)
    # A quote for the confirmed goal need not also ground the unknown preference.
    body['grounding'][0]['fact_keys'].remove('reminders.preference')
    candidate = NativeResponse.model_validate(body).candidate(state)
    assert candidate.facts['reminders.preference'].value is None


def test_unchanged_fact_and_owner_explanation_question_need_no_invented_fact():
    base = State(raw_intent='A household buzzer with no stored events.')
    state = adopt(base, result(base))
    state = prepare(AdvanceRequest(state=state, request_id='explain', answer='What does standalone mean?'))
    body = payload(state, result(state, facts=state.facts, disposition='provisional'))
    body['grounding'] = []
    body['facts'][0]['reason'] = 'Only explanatory wording changed.'
    updated = adopt(state, NativeResponse.model_validate(body).candidate(state))
    assert set(updated.facts) == {'goal'}
    assert updated.assessed_turn_count == 1
    assert export_brief(updated)['sources'] == [{'id': 't0', 'text': base.raw_intent}]


def test_grounding_cannot_override_confirmation_or_unknown_answer_guards():
    base = State(raw_intent='A household buzzer.', facts={
        'goal': Fact(value='A household buzzer.', status='confirmed', source_turn_ids=['t0']),
        'use.power': Fact(value=None, status='unknown', source_turn_ids=[])})
    state = prepare(AdvanceRequest(state=base, request_id='unknown', answer='I do not know.'))
    facts = {**state.facts, 'use.power': Fact(value='mains', status='confirmed', source_turn_ids=['t1'])}
    candidate = NativeResponse.model_validate(payload(state, result(state, facts=facts))).candidate(state)
    with pytest.raises(FlowError, match='substantive'):
        adopt(state, candidate)
    state = prepare(AdvanceRequest(state=base, request_id='continue', answer='Continue.'))
    candidate = NativeResponse.model_validate(payload(state, result(state, facts=facts))).candidate(state)
    with pytest.raises(FlowError, match='substantive'):
        adopt(state, candidate)


def test_partial_context_can_be_followed_by_a_genuinely_different_preference():
    base = State(raw_intent='A household buzzer.')
    first = result(base, question={'topic': 'use.location', 'text': 'Where will it be used?',
        'decision': 'Changes portability.'}, disposition='provisional')
    state = adopt(base, first)
    state = prepare(AdvanceRequest(state=state, request_id='partial', question_id='q1', answer='On my kitchen counter.'))
    facts = {**state.facts, 'use.location': Fact(value='kitchen counter', status='confirmed', source_turn_ids=['t1'])}
    followup = result(state, facts=facts, question={'topic': 'use.alert_preference',
        'text': 'Would a sound or a light work better?', 'decision': 'Changes the alert.'}, disposition='provisional')
    updated = adopt(state, NativeResponse.model_validate(payload(state, followup)).candidate(state))
    assert updated.questions[0].answer_turn_id == 't1'
    assert updated.questions[-1].topic == 'use.alert_preference'
    assert updated.facts['use.location'].value == 'kitchen counter'


def test_old_canonical_json_is_not_a_native_fallback():
    state = State(raw_intent='A household buzzer.')
    content = result(state).model_dump_json()
    raw = '\n'.join(json.dumps(e) for e in [
        {'type': 'thread.started'}, {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': content}},
        {'type': 'turn.completed'}]).encode()
    with pytest.raises(ValidationError): agents.parse_result('codex', raw, state)


def test_goal_retention_and_owner_unknown_controls_still_apply_after_decoding():
    state = State(raw_intent='A household buzzer; I do not know its power source.')
    body = payload(state)
    unknown = {'key': 'use.power', 'value': None, 'status': 'unknown', 'source_turn_ids': ['t0'], 'reason': ''}
    body['question'] = {'fact': unknown, 'text': 'Which power?', 'decision': 'Changes portability.', 'conflict_turn_id': None}
    body['owner_unknowns'] = [{'key': 'use.power', 'source_turn_id': 't0', 'quote': 'I do not know its power source.'}]
    body['assessment']['disposition'] = 'provisional'
    body['assessment']['open_questions'] = [{'topic': 'use.power', 'text': 'Power remains unknown.',
        'blocks_recommendation': False, 'reason': 'Check available power before choosing.'}]
    updated = adopt(state, NativeResponse.model_validate(body).candidate(state))
    assert updated.questions == [] and 'use.power' in updated.owner_unknowns
    body['facts'] = []
    body['grounding'] = []
    with pytest.raises(FlowError, match='goal'):
        adopt(state, NativeResponse.model_validate(body).candidate(state))


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


@pytest.mark.parametrize('failure', ['refusal', 'truncation', 'wire', 'grounding', 'target_conflict'])
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
        if failure == 'grounding': body['grounding'][-1]['quote'] = 'Not an owner quote.'
        if failure == 'target_conflict':
            body['question'] = {'fact': {'key': 'use.location', 'value': False, 'status': 'confirmed',
                'source_turn_ids': ['t1'], 'reason': ''}, 'text': 'Where?', 'decision': 'Changes portability.', 'conflict_turn_id': None}
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
        assert client.post('/api/export', json=failed['state']).status_code == 409
    assert len(calls) == adapter.calls == 1
    assert not Path(calls[0]).exists(), 'Private schema and workspace must be removed on failure'
