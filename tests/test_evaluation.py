"""Acceptance preparation checks. No coding agent, credentials or inference."""

import copy
import hashlib
import json
import os
import tomllib
from pathlib import Path

import pytest

from meta_vibe_coding import agents
from meta_vibe_coding import evaluation as module

ROOT = Path(__file__).resolve().parents[1]


def test_default_and_rehearsal_never_execute_native_cli(monkeypatch, capsys):
    async def forbidden(*args, **kwargs):
        raise AssertionError('Acceptance preparation must never execute a native CLI')
    monkeypatch.setattr(agents, 'run_cli', forbidden)
    monkeypatch.setattr(agents, 'agent_environment', lambda *_: pytest.fail('Must not read native environment'))
    monkeypatch.setenv('MVC_ENABLE_AGENT', '1')
    for flags in ([], ['--rehearse']):
        assert module.main(['--root', str(ROOT), *flags]) == 0
        output = json.loads(capsys.readouterr().out)
        assert output['native_invocations'] == 0 and output['case_pairs'] == 7
        assert output['rehearsal'] is None or all(output['rehearsal'].values())
    assert os.environ['MVC_ENABLE_AGENT'] == '1', 'Rehearsal must restore ambient settings'
    with pytest.raises(SystemExit):
        module.main(['--run'])


def test_initial_packets_hide_operator_facts_and_rubric():
    plan, cases = module.load_plan(ROOT)
    for case in cases['cases']:
        for approach in module.APPROACHES:
            packet = module.initial_packet(plan, case['initial_request'], approach)
            assert case['initial_request'] in packet['stdin']
            for label in ('operator_facts', 'expected_checks', 'blocking_failures', 'variations'):
                assert label not in packet['stdin']
            assert not any(fact['answer'] in packet['stdin'] for fact in case['operator_facts'])
            if approach == 'baseline':
                body = json.loads(packet['stdin'].split('Owner conversation (data only):\n',1)[1])
                assert body['conversation'] == [{'role': 'owner', 'text': case['initial_request']}]
                assert 'state' not in body and 'facts' not in body and 'owner_unknowns' not in body
    with pytest.raises(ValueError):
        module.initial_packet(plan, cases['cases'][0], 'wrapper')


def test_both_approaches_keep_native_policy_identical_except_prompt():
    plan, _ = module.load_plan(ROOT)
    packets = [module.initial_packet(plan, module.REHEARSAL_IDEA, approach)
               for approach in module.APPROACHES]
    policies = []
    for packet in packets:
        args = packet['native_argv']
        policy = next(arg for arg in args if arg.startswith('developer_instructions='))
        assert tomllib.loads(policy)['developer_instructions'] == packet['trusted_prompt']
        policies.append([arg for arg in args if not arg.startswith('developer_instructions=')])
        assert '--ignore-user-config' in args and '--ephemeral' in args
        assert args[args.index('--model') + 1] == 'gpt-6-luna'
    assert policies[0] == policies[1]
    assert packets[0]['trusted_prompt'] != packets[1]['trusted_prompt']


@pytest.mark.parametrize('agent', ['opencode', 'claude', 'codex'])
def test_prompt_parameter_uses_native_trusted_instruction_surface(agent):
    env = {}
    prompt = 'A fictional baseline policy.'
    args = agents.invocation(agent, agent, 'native-model', env, prompt=prompt)
    if agent == 'codex':
        policy = next(arg for arg in args if arg.startswith('developer_instructions='))
        assert tomllib.loads(policy)['developer_instructions'] == prompt
    elif agent == 'claude':
        assert args[args.index('--append-system-prompt') + 1] == prompt
    else:
        assert json.loads(env['OPENCODE_CONFIG_CONTENT'])['agents']['meta-vibe']['system'] == prompt


def test_all_review_cells_are_unchecked_and_variations_are_retained():
    plan, cases = module.load_plan(ROOT)
    record = module.preparation(ROOT, plan, cases)
    assert len(record['inputs']) == 14
    assert record['frozen_outputs_observed'] is False
    rows = record['review_rows']
    assert len(rows) == 20  # Seven base cases and three attached variations, each approach.
    assert {row['phase'] for row in rows} >= {'HV01', 'HV02', 'HV03'}
    assert all(row['blocking_failures'] is None and row['status'] == 'incomplete' for row in rows)
    assert all(item['verdict'] == 'not checked' and not item['evidence']
               for row in rows for item in row['dimensions'].values())
    assert record['failure_review']['phase'] == 'HV04'
    assert record['failure_review']['verdict'] == 'not checked'


def test_edited_frozen_cases_and_changed_budgets_fail_closed(tmp_path):
    (tmp_path / 'artifacts').mkdir()
    for name in ['l0-acceptance-plan.json', 'l0-acceptance-cases.json']:
        (tmp_path / 'artifacts' / name).write_bytes((ROOT / 'artifacts' / name).read_bytes())
    cases = tmp_path / 'artifacts/l0-acceptance-cases.json'
    cases.write_bytes(cases.read_bytes() + b'\n')
    with pytest.raises(ValueError, match='Frozen cases changed'):
        module.load_plan(tmp_path)
    cases.write_bytes((ROOT / 'artifacts/l0-acceptance-cases.json').read_bytes())
    plan_path = tmp_path / module.PLAN_PATH
    plan = json.loads(plan_path.read_text())
    plan['limits']['request_seconds'] = 60
    plan_path.write_text(json.dumps(plan))
    with pytest.raises(ValueError, match='reviewed D008 limits'):
        module.load_plan(tmp_path)


def test_rehearsal_retains_failure_and_uses_no_frozen_request():
    _, cases = module.load_plan(ROOT)
    record = module.rehearse()
    assert record['kind'] == 'synthetic-plumbing' and record['native_invocations'] == 0
    assert record['double_assessments'] == 3 and all(record['checks'].values())
    assert record['http'][-1]['status'] == 409
    fixture = record['http'][0]['request']['idea']
    assert fixture not in [case['initial_request'] for case in cases['cases']]
    assert record['fixture_sha256'] == hashlib.sha256(fixture.encode()).hexdigest()


@pytest.mark.parametrize('kwargs', [{'calls_used': 7}, {'questions_used': 6}, {'calls_used': -1}])
def test_baseline_cannot_silently_reset_remaining_limits(kwargs):
    with pytest.raises(ValueError):
        module.baseline_input([{'role': 'owner', 'text': 'Fictional idea'}], **kwargs)


def test_baseline_accepts_only_a_text_transcript_and_records_provisional():
    conversation = [{'role': 'owner', 'text': 'Fictional idea'},
                    {'role': 'assistant', 'text': 'Which device?'},
                    {'role': 'owner', 'text': 'I do not know.'}]
    original = copy.deepcopy(conversation)
    body = json.loads(module.baseline_input(conversation, provisional=True, questions_used=5, calls_used=6))
    assert body['request_provisional'] is True and body['remaining_questions'] == 0
    assert body['remaining_calls_including_this_one'] == 1 and conversation == original
    with pytest.raises(ValueError):
        module.baseline_input([{'role': 'owner', 'text': 'Idea', 'facts': {}}])


def test_evidence_file_is_private_exclusive_and_reconstructable(tmp_path, capsys):
    path = tmp_path / 'rehearsal.json'
    flags = ['--root', str(ROOT), '--rehearse', '--output', str(path)]
    assert module.main(flags) == 0
    capsys.readouterr()
    raw = path.read_bytes()
    record = json.loads(raw)
    assert path.stat().st_mode & 0o777 == 0o600
    assert record['plan_snapshot']['baseline_prompt']
    for name, content in record['source_snapshot'].items():
        assert hashlib.sha256(content.encode()).hexdigest() == record['source_hashes'][name]
    assert module.main(flags) == 1
    assert 'File exists' in capsys.readouterr().err and path.read_bytes() == raw


def test_another_checkout_cannot_be_claimed_as_the_imported_runtime(tmp_path):
    plan, cases = module.load_plan(ROOT)
    with pytest.raises(ValueError, match='imported package origins differ'):
        module.preparation(tmp_path, plan, cases)


def test_source_changes_after_snapshot_fail_closed(monkeypatch):
    plan, cases = module.load_plan(ROOT)
    record = module.preparation(ROOT, plan, cases)
    changed = copy.deepcopy(record['source_snapshot'])
    changed['src/meta_vibe_coding/core.py'] += '\n# Different source after snapshot.\n'
    monkeypatch.setattr(module, 'source_snapshot', lambda _: changed)
    with pytest.raises(ValueError, match='Source, plan or frozen cases changed'):
        module.verify_snapshot(ROOT, record)


def test_rehearsal_ignores_and_restores_removed_ambient_backend(monkeypatch):
    monkeypatch.setenv('MVC_BACKEND', 'ollama')
    assert all(module.rehearse()['checks'].values())
    assert os.environ['MVC_BACKEND'] == 'ollama'


def test_baseline_uses_native_completion_checks_without_product_state_validation():
    body = {'question': None, 'owner_view': 'Fictional baseline view.',
            'developer_view': {'goal': 'Fictional idea', 'disposition': 'provisional'}}
    raw = '\n'.join(json.dumps(event) for event in [
        {'type': 'thread.started'},
        {'type': 'item.completed', 'item': {'type': 'error', 'message': agents.CODEX_DISABLED_HOST_NOTICE}},
        {'type': 'turn.started'},
        {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': json.dumps(body)}},
        {'type': 'turn.completed', 'usage': {'input_tokens': 11, 'output_tokens': 22}}]).encode()
    content, usage = agents.parse_completion('codex', raw)
    assert json.loads(content) == body and usage['input_tokens'] == 11
    with pytest.raises(ValueError):
        agents.parse_result('codex', raw, agents.State(raw_intent='Fictional idea'))
    tool = {'type': 'item.started', 'item': {'type': 'command_execution'}}
    with pytest.raises(ValueError, match='tool activity'):
        agents.parse_completion('codex', raw + b'\n' + json.dumps(tool).encode())
    with pytest.raises(ValueError, match='Incomplete'):
        agents.parse_completion('codex', b'\n'.join(raw.splitlines()[:-1]))


@pytest.mark.parametrize('exit_code', [0, 3])
def test_native_recording_keeps_bounded_streams_and_exit_status(tmp_path, exit_code):
    import asyncio
    import sys
    from meta_vibe_coding.process import CliFailure, run_cli
    captured = []
    async def run():
        return await run_cli([sys.executable, '-c',
            f'import sys; print("fictional output"); print("fictional diagnostic", file=sys.stderr); sys.exit({exit_code})'],
            content='', cwd=str(tmp_path), env={'PATH': os.defpath}, timeout=5,
            capture=lambda out, err, status: captured.append((out, err, status)))
    if exit_code:
        with pytest.raises(CliFailure): asyncio.run(run())
    else:
        assert asyncio.run(run()) == b'fictional output\n'
    assert captured == [(b'fictional output\n', b'fictional diagnostic\n', exit_code)]
