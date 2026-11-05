"""The acceptance harness on a synthetic plan and cases. Native processes are doubles."""
import asyncio
import hashlib
import importlib.util
import json
import time
from pathlib import Path

import pytest

from meta_vibe_coding import agents, evaluation
from meta_vibe_coding.core import FlowError
from meta_vibe_coding.process import CliFailure

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / 'scripts/acceptance_run.py'
spec = importlib.util.spec_from_file_location('acceptance_run', SCRIPT)
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
REAL_VERIFY = run.Harness.verify

CASES = {'cases': [
    {'id': 'C1', 'initial_request': 'A fictional shelf label idea.', 'operator_facts': [{'topic': 'colour', 'answer': 'Blue labels. Printed weekly.'}],
     'variations': [{'id': 'V1', 'type': 'correction', 'owner_text': 'Actually, make them green.'}]},
    {'id': 'C2', 'initial_request': 'A fictional door sign idea.', 'operator_facts': [], 'variations': []},
]}
LIMITS = {'clarification_questions': 5, 'session_seconds': 1800, 'request_seconds': 300, 'top_level_calls_per_case_and_approach': 7,
    'maximum_full_matrix_top_level_calls': 28}
LIMIT_MESSAGE = 'You have hit your usage limit.'
CLAUDE_FAILED = json.dumps({'type': 'result', 'subtype': 'success', 'is_error': True, 'terminal_reason': 'api_error', 'result': LIMIT_MESSAGE}).encode()


def claude_body(text, **extra):
    return json.dumps({'type': 'result', 'subtype': 'success', 'is_error': False, 'terminal_reason': 'completed', 'result': text, 'structured_output': {'note': text},
        'modelUsage': {'fictional-model': {}}, 'usage': {'input_tokens': 1, 'output_tokens': 1}, **extra}).encode()


def build(tmp_path, agent):
    cases_path = tmp_path / 'artifacts/cases.json'
    cases_path.parent.mkdir()
    cases_path.write_bytes(json.dumps(CASES).encode())
    plan = {'agent': {'name': agent, 'requested_model': 'fictional-model'}, 'limits': LIMITS, 'baseline_prompt': 'Fictional baseline policy.',
        'matrix': [{'case_id': 'C1', 'approaches': ['wrapper', 'baseline']}, {'case_id': 'C2', 'approaches': ['baseline', 'wrapper']}],
        'execution_directory': str(tmp_path / 'evidence'), 'frozen_cases': {'path': str(cases_path), 'sha256': hashlib.sha256(cases_path.read_bytes()).hexdigest()},
        'native_output': {'wrapper': json.loads(agents.SCHEMA), 'baseline': evaluation.native_schema(evaluation.BaselineResponse)},
        'harness_sha256': hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), 'live_authority': {'owner': 'fictional'},
        'frozen_runtime': {'wrapper_prompt': agents.PROMPT, 'source_snapshot': evaluation.source_snapshot(REPO),
            'requirements_lock_sha256': hashlib.sha256((REPO / 'requirements.lock').read_bytes()).hexdigest()}}
    plan_path = tmp_path / 'plan.json'
    plan_path.write_text(json.dumps(plan))
    return plan_path


@pytest.fixture(autouse=True)
def isolated_runtime(monkeypatch):
    """No native binary, login or real checkout comparison in these tests."""
    monkeypatch.setenv('MVC_ENABLE_AGENT', '1')
    monkeypatch.setenv('MVC_AGENT_MAX_CALLS', '7')
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    monkeypatch.setattr(agents.shutil, 'which', lambda name: '/test/' + name)
    monkeypatch.setattr(run.Harness, 'binary_hash', lambda self: 'fixed')
    monkeypatch.setattr(run.Harness, 'check_runtime', lambda self: {'agent_version': 'fictional 1', 'agent_binary_sha256': 'fixed'})
    monkeypatch.setattr(run.Harness, 'verify', lambda self: None)


def open_harness(plan_path, directory):
    return run.Harness(plan_path, directory / 'evidence', directory)


def build_harness(tmp_path, agent, name, monkeypatch):
    monkeypatch.setenv('MVC_AGENT', agent)
    directory = tmp_path / name
    directory.mkdir()
    return open_harness(build(directory, agent), directory)


def install(monkeypatch, h, respond):
    calls = []

    async def native(args, **kwargs):
        if '--help' in args or '--version' in args:
            return b''
        calls.append(args)
        return respond(args, kwargs)
    monkeypatch.setattr(run, 'NATIVE', native)
    monkeypatch.setattr(agents, 'run_cli', h.native)
    run.connect_product(h)
    return calls


def begin(h):
    h.start({'verdict': 'pass'})


def reply(body: bytes, status=0):
    def respond(args, kwargs):
        kwargs['capture'](body, b'', status)
        if status:
            raise CliFailure(body)
        return body
    return respond


def first_step(h):
    return {'job': h.active['id'], 'after_calls': h.active['calls']}


def journal(h):
    return [json.loads(line) for line in (h.run_dir / 'journal.jsonl').read_text().splitlines()]


@pytest.mark.parametrize('stdout, expected', [
    (b'{"type":"item.completed"}\n{"type":"turn.completed"}\n', False),
    (b'{"type":"item.completed"}\n', True),
    (b'{"type":"turn.completed"}\n{"type":"turn.failed"}\n', True),
    (b'{"type":"item.completed","item":{"type":"error"}}\n{"type":"turn.completed"}\n', False),
])
def test_codex_stop_reads_top_level_events_only(stdout, expected):
    assert run.codex_stopped(stdout.decode()) is expected


@pytest.mark.parametrize('body, expected', [
    (claude_body('{}'), False),
    (CLAUDE_FAILED, True),
    (claude_body('{}', subtype='error_max_turns'), True),
    (claude_body('{}', terminal_reason='api_error'), True),
    (claude_body('{}', structured_output=None), True),
    (claude_body('{}', api_error='rate_limit'), True),
    (claude_body('{}', api_error_status=429), True),
    (claude_body('{}', safety_stops=1), True),
    (b'not json', True),
    (b'[]', True),
])
def test_claude_stop_trusts_is_error_over_subtype(body, expected):
    assert run.claude_stopped(body.decode()) is expected


def test_any_nonzero_exit_or_error_is_a_stop_for_every_agent():
    for adapter in run.ADAPTERS.values():
        assert run.native_stop(adapter, {'streams': {'returncode': 1, 'stdout': ''}})
        assert run.native_stop(adapter, {'error': {'type': 'TimeoutError'}, 'streams': {}})


def test_every_supported_agent_has_an_adapter():
    assert set(run.ADAPTERS) == set(agents.AGENTS)


@pytest.mark.parametrize('delivery, expected', [('argument', 'schema-text'), ('stdin', None)])
def test_schema_delivery_without_a_file(delivery, expected, tmp_path):
    adapter = run.Adapter(frozenset(), delivery, run.opencode_stopped)
    assert run.schema_option(adapter, 'schema-text', str(tmp_path)) == expected


def test_file_schema_is_private_and_belongs_to_the_request(tmp_path):
    adapter = run.ADAPTERS['codex']
    path = run.schema_option(adapter, '{}', str(tmp_path))
    assert run.delivered_schema(adapter, ['--output-schema', path], str(tmp_path)) == '{}'
    (tmp_path / 'other').mkdir()
    with pytest.raises(ValueError):
        run.delivered_schema(adapter, ['--output-schema', path], str(tmp_path / 'other'))


def test_claude_receives_the_plan_schema_natively_and_stops_on_a_limit(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'a', monkeypatch)
    begin(h)
    seen = []

    def respond(args, kwargs):
        seen.append(json.loads(args[args.index('--json-schema') + 1]))
        return reply(CLAUDE_FAILED, 1)(args, kwargs)
    install(monkeypatch, h, respond)
    h.select('C1', 'wrapper')
    summary = asyncio.run(h.step(first_step(h)))
    assert seen == [h.plan['native_output']['wrapper']] and summary['failure']['code'] == 'unavailable'
    h.finish({'job': h.active['id'], 'reason': 'stopped'})
    with pytest.raises(ValueError, match='Native stop'):
        h.select('C1', 'baseline')
    assert not (h.run_dir / 'C1-baseline.claim').exists()


def test_limit_inside_an_exit_zero_call_still_stops_the_matrix(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'b', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(CLAUDE_FAILED))
    h.select('C1', 'wrapper')
    assert asyncio.run(h.step(first_step(h)))['failure']['code'] == 'invalid_output'
    h.finish({'job': h.active['id'], 'reason': 'stopped'})
    with pytest.raises(ValueError, match='Native stop'):
        h.select('C1', 'baseline')


def test_model_output_failure_is_a_first_attempt_result_not_a_stop(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'c', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(claude_body('not the contract')))
    h.select('C1', 'wrapper')
    assert asyncio.run(h.step(first_step(h)))['failure']['code'] == 'invalid_output'
    h.finish({'job': h.active['id'], 'reason': 'closed'})
    assert h.select('C1', 'baseline')['job'] == 'C1-baseline'


def test_matrix_order_and_caps_come_from_the_plan(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'd', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(claude_body('x')))
    with pytest.raises(ValueError, match='matrix order'):
        h.select('C2', 'baseline')
    h.select('C1', 'wrapper')
    h.reservations = LIMITS['maximum_full_matrix_top_level_calls']
    with pytest.raises(FlowError) as error:
        asyncio.run(h.native(['claude'], content='', cwd=str(tmp_path), env={}, timeout=1))
    assert error.value.code == 'limit'


def test_fallback_model_is_refused_before_any_native_process(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'e', monkeypatch)
    begin(h)
    calls = install(monkeypatch, h, reply(claude_body('x')))
    h.select('C1', 'wrapper')
    schema = agents.SCHEMA
    with pytest.raises(ValueError, match='Fallback'):
        asyncio.run(h.native(['claude', '--fallback-model', 'other', '--json-schema', schema], content=schema, cwd=str(tmp_path), env={}, timeout=1))
    assert calls == [] and h.reservations == 0


def test_known_passages_can_combine_with_the_unknown_reply(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'f', monkeypatch)
    job = {'case': CASES['cases'][0]}
    text = h.answer_text(job, {'fact_passages': [{'topic': 'colour', 'text': 'Blue labels.'}], 'unknown': True}, None)
    assert text == 'Blue labels.\nI do not know the rest of this question.'
    assert h.answer_text(job, {'unknown': True}, None) == 'I do not know.'
    with pytest.raises(ValueError, match='exact substrings'):
        h.answer_text(job, {'fact_passages': [{'topic': 'colour', 'text': 'Red labels.'}]}, None)
    with pytest.raises(ValueError, match='one recorded answer source'):
        h.answer_text(job, {'fact_passages': [{'topic': 'colour', 'text': 'Blue labels.'}], 'fact_topics': ['colour']}, None)


def test_declares_unknown_is_not_an_operator_field(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'g', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(claude_body('x')))
    h.select('C1', 'wrapper')
    with pytest.raises(ValueError, match='Unknown operator action'):
        asyncio.run(h.step({**first_step(h), 'declares_unknown': True}))


def test_resume_closes_a_failed_job_and_keeps_the_count(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'h', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(CLAUDE_FAILED, 1))
    h.select('C1', 'wrapper')
    asyncio.run(h.step(first_step(h)))
    before = (h.run_dir / 'journal.jsonl').read_bytes()

    later = open_harness(h.plan_path, h.plan_path.parent)
    later.resume('offline')
    assert (later.run_dir / 'journal.jsonl').read_bytes().startswith(before)
    assert later.reservations == 1 and later.jobs['C1-wrapper']['closed']
    closed = [e for e in journal(later) if e['type'] == 'job_finished']
    assert len(closed) == 1 and closed[0]['failure']['code'] == 'unavailable' and closed[0]['phases_not_checked'] == ['V1']
    with pytest.raises(ValueError, match='matrix order'):
        later.select('C1', 'wrapper')
    again = open_harness(h.plan_path, h.plan_path.parent)
    (h.run_dir / 'journal.jsonl').write_bytes(before)
    with pytest.raises(FileExistsError):
        again.resume('replay')


def test_resume_refuses_an_open_job_without_a_failure(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'i', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(claude_body('x')))
    h.select('C1', 'wrapper')
    later = open_harness(h.plan_path, h.plan_path.parent)
    with pytest.raises(ValueError, match='without a recorded failure'):
        later.resume('offline')
    assert not list(h.run_dir.glob('resume-*.claim'))


def test_resume_refuses_a_call_with_no_recorded_finish(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'j', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(CLAUDE_FAILED, 1))
    h.select('C1', 'wrapper')
    asyncio.run(h.step(first_step(h)))
    rows = [e for e in journal(h) if e['type'] != 'native_finished']
    (h.run_dir / 'journal.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in rows))
    with pytest.raises(ValueError, match='no recorded finish'):
        open_harness(h.plan_path, h.plan_path.parent).resume('offline')


def launch_arguments(tmp_path, journal_sha=None, run_dir=None):
    plan_path = build(tmp_path, 'claude')
    approval = tmp_path / 'approval.json'
    approval.write_text(json.dumps({'verdict': 'pass', 'plan_sha256': hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        'harness_sha256': hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), 'journal_sha256': journal_sha, 'reason': 'offline'}))
    return run.argparse.Namespace(plan=plan_path, run_dir=run_dir or tmp_path / 'evidence', approval=approval)


def test_launch_requires_an_approval_of_the_exact_journal(tmp_path):
    arguments = launch_arguments(tmp_path)
    arguments.run_dir.mkdir()
    (arguments.run_dir / 'journal.jsonl').write_bytes(b'{}\n')
    with pytest.raises(ValueError, match='current journal'):
        run.serve(arguments)


def test_a_second_directory_cannot_start_a_fresh_allowance(tmp_path):
    with pytest.raises(ValueError, match='plan names'):
        run.serve(launch_arguments(tmp_path, run_dir=tmp_path / 'other'))


def test_queued_requests_block_a_launch(tmp_path):
    arguments = launch_arguments(tmp_path)
    (arguments.run_dir / 'inbox').mkdir(parents=True)
    (arguments.run_dir / 'inbox/1-step.json').write_text('{}')
    with pytest.raises(ValueError, match='Queued'):
        run.serve(arguments)


def test_approved_launch_reaches_the_watch_loop(tmp_path, monkeypatch):
    for name in ('MVC_AGENT', 'MVC_AGENT_MODEL', 'MVC_AGENT_ENV', 'MVC_AGENT_MAX_CALLS', 'MVC_REQUEST_TIMEOUT_SECONDS', 'MVC_SESSION_TIMEOUT_SECONDS'):
        monkeypatch.setenv(name, '1')  # Restored afterwards, because serve sets them.
    watched = []

    async def watch(harness):
        watched.append(harness)
    monkeypatch.setattr(run, 'watch', watch)
    run.serve(launch_arguments(tmp_path))
    assert watched[0].agent_name == 'claude' and json.loads((tmp_path / 'evidence/journal.jsonl').read_text().splitlines()[0])['type'] == 'run_started'


@pytest.mark.parametrize('body', ['[]', 'not json', '"text"'])
def test_a_malformed_request_is_a_reply_and_the_run_survives(tmp_path, monkeypatch, body):
    h = build_harness(tmp_path, 'claude', 'n', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(claude_body('x')))
    for folder in ('inbox', 'outbox', 'operator'):
        (h.run_dir / folder).mkdir()
    (h.run_dir / 'inbox/1-step.json').write_text(body)
    asyncio.run(run.process_inbox(h))
    assert 'error' in json.loads((h.run_dir / 'outbox/1-step.json').read_text())


def test_an_unknown_variation_is_refused_without_stranding_the_job(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'o', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(claude_body('x')))
    h.select('C1', 'wrapper')
    h.active['calls'] = 1
    reply_value = asyncio.run(run.handle(h, 'step', {**first_step(h), 'variation': 'NOPE'}))
    assert 'Unknown variation' in reply_value['error'] and not h.active['failure'] and not h.active['closed']


def test_a_retried_step_cannot_land_on_a_newer_state(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'p', monkeypatch)
    begin(h)
    calls = install(monkeypatch, h, reply(claude_body('x')))
    h.select('C1', 'wrapper')
    stale = {'job': 'C1-wrapper', 'after_calls': 3}
    assert 'call count' in asyncio.run(run.handle(h, 'step', stale))['error'] and calls == []
    assert 'current job' in asyncio.run(run.handle(h, 'finish', {'job': 'C2-wrapper', 'reason': 'x'}))['error']


def test_resume_refuses_a_claim_that_differs_from_the_plan(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'q', monkeypatch)
    begin(h)
    claim = json.loads((h.run_dir / 'run.claim').read_text())
    (h.run_dir / 'run.claim').write_text(json.dumps({**claim, 'native_invocation_limit': 999}))
    with pytest.raises(ValueError, match='Run claim'):
        open_harness(h.plan_path, h.plan_path.parent).resume('offline')


def test_codex_quota_refusals_start_nothing(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'codex', 'k', monkeypatch)
    begin(h)
    full = {'ordinaryUsageAllowed': False}
    adapter = run.Adapter(h.adapter.forbidden_environment, 'file', run.codex_stopped, None, lambda env: full, run.codex_quota_refusal)
    h.adapter = adapter
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('CODEX_API_KEY', raising=False)
    with pytest.raises(ValueError, match='usage limit'):
        h.select('C1', 'wrapper')
    assert 'C1-wrapper' not in h.jobs and not (h.run_dir / 'C1-wrapper.claim').exists()


def test_codex_quota_read_honours_its_deadline_with_a_child_holding_the_pipe(tmp_path, monkeypatch):
    fake = tmp_path / 'codex'
    fake.write_text('#!/bin/sh\nprintf \'{"id":1\'\nsleep 30\n')
    fake.chmod(0o755)
    began = time.monotonic()
    with pytest.raises((TimeoutError, ValueError)):
        run.codex_quota({'PATH': f'{tmp_path}:/bin:/usr/bin'}, timeout=1)
    assert time.monotonic() - began < 8


def test_failed_wrapper_step_records_paired_http_for_replay(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'l', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(CLAUDE_FAILED, 1))
    h.select('C1', 'wrapper')
    asyncio.run(h.step(first_step(h)))
    assert [e['status'] for e in journal(h) if e['type'] == 'http' and e['path'] == '/api/advance'] == [200]
    assert [e['status'] for e in journal(h) if e['type'] == 'http' and e['path'] == '/api/export'] == [409]


def frozen_plan(tmp_path):
    plan_path = build(tmp_path, 'claude')
    return plan_path, json.loads(plan_path.read_text())


def test_verify_accepts_the_exact_frozen_inputs(tmp_path, monkeypatch):
    plan_path, _ = frozen_plan(tmp_path)
    monkeypatch.setattr(run.evaluation, 'verify_checkout', lambda root: None)
    REAL_VERIFY(run.Harness(plan_path, tmp_path / 'evidence', REPO))


@pytest.mark.parametrize('change, message', [
    (lambda plan: plan['frozen_runtime'].update(wrapper_prompt='Changed.'), 'prompt differs'),
    (lambda plan: plan['native_output'].update(wrapper={}), 'wrapper schema differs'),
    (lambda plan: plan['native_output'].update(baseline={}), 'baseline schema differs'),
    (lambda plan: plan['frozen_runtime'].update(source_snapshot={}), 'Runtime source changed'),
    (lambda plan: plan['frozen_cases'].update(sha256='0' * 64), 'Cases changed'),
    (lambda plan: plan.update(harness_sha256='0' * 64), 'Harness changed'),
    (lambda plan: plan['frozen_runtime'].update(requirements_lock_sha256='0' * 64), 'Dependency lock changed'),
])
def test_every_frozen_input_blocks_the_run_when_it_drifts(tmp_path, monkeypatch, change, message):
    plan_path, plan = frozen_plan(tmp_path)
    change(plan)
    plan_path.write_text(json.dumps(plan))
    monkeypatch.setattr(run.evaluation, 'verify_checkout', lambda root: None)
    with pytest.raises(ValueError, match=message):
        REAL_VERIFY(run.Harness(plan_path, tmp_path / 'evidence', REPO))


def test_a_changed_plan_blocks_the_run_while_it_is_running(tmp_path, monkeypatch):
    plan_path, plan = frozen_plan(tmp_path)
    monkeypatch.setattr(run.evaluation, 'verify_checkout', lambda root: None)
    h = run.Harness(plan_path, tmp_path / 'evidence', REPO)
    plan_path.write_text(json.dumps({**plan, 'kind': 'edited'}))
    with pytest.raises(ValueError, match='Plan changed'):
        REAL_VERIFY(h)


def test_finish_without_a_reason_changes_nothing(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'r', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(claude_body('x')))
    h.select('C1', 'wrapper')
    assert 'reason' in asyncio.run(run.handle(h, 'finish', {'job': 'C1-wrapper', 'question_count': 2}))['error']
    assert not h.active['closed'] and h.active['questions'] == 0
    assert h.finish({'job': 'C1-wrapper', 'reason': 'closed'})['closed']


def test_a_request_name_without_an_action_is_a_reply(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 's', monkeypatch)
    begin(h)
    for folder in ('inbox', 'outbox', 'operator'):
        (h.run_dir / folder).mkdir()
    (h.run_dir / 'inbox/stray.json').write_text('{}')
    asyncio.run(run.process_inbox(h))
    assert json.loads((h.run_dir / 'outbox/stray.json').read_text()) == {'error': 'Unknown action.'}


def test_replay_viewer_reads_a_failed_run_and_cannot_infer(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    spec_view = importlib.util.spec_from_file_location('acceptance_view', REPO / 'scripts/acceptance_view.py')
    view = importlib.util.module_from_spec(spec_view)
    spec_view.loader.exec_module(view)
    h = build_harness(tmp_path, 'claude', 'u', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(CLAUDE_FAILED, 1))
    h.select('C1', 'wrapper')
    asyncio.run(h.step(first_step(h)))
    h.finish({'job': 'C1-wrapper', 'reason': 'stopped'})
    client = TestClient(view.create_app(h.plan_path, h.run_dir))
    assert 'Recorded HTTP replay' in client.get('/?job=C1-wrapper').text
    assert client.get('/?job=C1-baseline').status_code == 404
    row = client.get('/review/snapshot?job=C1-wrapper').json()
    assert row['failure']['code'] == 'unavailable' and row['export']['status'] == 409
    assert client.post('/api/export', json=row['state']).status_code == 409
    assert client.post('/api/advance', json={}).status_code == 410
    assert client.get('/app.js').text.count('const replayConfigReady') == 1


def test_the_baseline_runs_with_the_same_claude_environment_as_the_wrapper(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'v', monkeypatch)
    begin(h)
    seen = []

    def respond(args, kwargs):
        seen.append(kwargs['env'].get('MAX_STRUCTURED_OUTPUT_RETRIES'))
        return reply(claude_body('{}'))(args, kwargs)
    install(monkeypatch, h, respond)
    h.select('C1', 'wrapper')
    asyncio.run(h.step(first_step(h)))
    h.finish({'job': 'C1-wrapper', 'reason': 'closed'})
    h.select('C1', 'baseline')
    asyncio.run(h.step(first_step(h)))
    assert seen == ['10', '10']


@pytest.mark.parametrize('approach', ['wrapper', 'baseline'])
def test_reaching_the_question_limit_forces_a_provisional_close_on_both_approaches(tmp_path, monkeypatch, approach):
    h = build_harness(tmp_path, 'claude', 'w' + approach, monkeypatch)
    begin(h)
    question = {'text': 'Fictional?', 'decision': 'Fictional.'}
    install(monkeypatch, h, reply(claude_body('{}')))
    if approach == 'baseline':
        h.select('C1', 'wrapper'); h.active['failure'] = {'code': 'offline'}; h.finish({'job': 'C1-wrapper', 'reason': 'offline'})
        h.select('C1', 'baseline')
        monkeypatch.setattr(run.evaluation.BaselineResponse, 'model_validate_json', classmethod(lambda cls, text: type('R', (), {'model_dump': lambda self: {'question': question, 'developer_view': {'disposition': 'needs_answer'}}})()))
    else:
        h.select('C1', 'wrapper')
        h.active['state'] = {'questions': [{'id': 'q1', 'retired': False, 'answer_turn_id': None}], 'assessment': {'disposition': 'needs_answer'}}
        monkeypatch.setattr(h, 'advance_wrapper', lambda *a, **k: asyncio.sleep(0))
    h.active['calls'] = 1
    h.active['questions'] = 3
    if approach == 'baseline':
        h.active['baseline'] = {'question': question, 'developer_view': {'disposition': 'needs_answer'}}
    asyncio.run(h.step({**first_step(h), 'question_count': 2, 'unknown': True}))
    action = [e for e in journal(h) if e['type'] == 'operator_action'][-1]
    assert action['provisional'] is True and action['provisional_enforced'] is True


def test_crossing_the_limit_in_one_bundled_message_still_fails(tmp_path, monkeypatch):
    h = build_harness(tmp_path, 'claude', 'x', monkeypatch)
    begin(h)
    install(monkeypatch, h, reply(claude_body('x')))
    h.select('C1', 'wrapper')
    h.active['state'] = {'questions': [{'id': 'q1', 'retired': False, 'answer_turn_id': None}], 'assessment': {'disposition': 'needs_answer'}}
    h.active['calls'], h.active['questions'] = 1, 4
    summary = asyncio.run(h.step({**first_step(h), 'question_count': 2, 'unknown': True}))
    assert summary['failure']['code'] == 'question_limit'


@pytest.mark.parametrize('approach, plan_limit, size, allowed', [
    ('baseline', None, 33000, False), ('baseline', 64000, 33000, True), ('baseline', 64000, 65000, False),
    ('wrapper', 64000, 33000, False)])
def test_input_budget_is_the_product_s_for_the_wrapper_and_the_plan_s_for_the_baseline(tmp_path, monkeypatch, approach, plan_limit, size, allowed):
    h = build_harness(tmp_path, 'claude', 'y', monkeypatch)
    if plan_limit:
        h.limits['baseline_input_bytes'] = plan_limit
    begin(h)
    calls = install(monkeypatch, h, reply(claude_body('x')))
    if approach == 'baseline':
        h.select('C1', 'wrapper'); h.active['failure'] = {'code': 'offline'}; h.finish({'job': 'C1-wrapper', 'reason': 'offline'})
    h.select('C1', approach)
    schema = json.dumps(h.plan['native_output'][approach], separators=(',', ':'))
    content = schema + 'x' * (size - len(schema))
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    try:
        asyncio.run(h.native(['claude', '--json-schema', schema], content=content, cwd=str(workspace), env={}, timeout=1))
        assert allowed and len(calls) == 1
    except FlowError as exc:
        assert not allowed and exc.code == 'limit' and calls == []
