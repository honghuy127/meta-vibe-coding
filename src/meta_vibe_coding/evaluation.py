"""Prepare acceptance inputs or rehearse HTTP plumbing. Never execute a coding agent."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from typing import Literal
from datetime import datetime, timezone
from pathlib import Path

from .contracts import native_schema
from .models import Model, Text, Risk


class BaselineQuestion(Model):
    text: Text
    decision: Text


class BaselineRecommendation(Model):
    summary: Text
    rationale: list[Text]
    alternatives: list[Text]


class BaselineDeveloperView(Model):
    disposition: Literal['needs_answer', 'provisional', 'ready']
    goal: Text
    users: list[Text]
    requirements: list[Text]
    constraints: list[Text]
    data_access: list[Text]
    risk: Risk
    recommendation: BaselineRecommendation
    assumptions: list[Text]
    open_questions: list[Text]
    acceptance_criteria: list[Text]
    owner_responsibilities: list[Text]


class BaselineResponse(Model):
    question: BaselineQuestion | None
    owner_view: Text
    developer_view: BaselineDeveloperView

PLAN_PATH = Path('artifacts/l0-acceptance-plan.json')
FROZEN_SHA256 = '1dacff58594ae1baa976ca3a5ec6c5d107c5064bbf7081525d4b8f3999da06ca'
APPROACHES = ('wrapper', 'baseline')
DIMENSIONS = ('recommendation_fit', 'clarification', 'risk_and_unknowns',
              'owner_view_clarity', 'brief_and_view_consistency')
REHEARSAL_IDEA = 'I want a small timer for desk stretches.'


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def verify_checkout(root: Path) -> None:
    expected = (root / 'src/meta_vibe_coding').resolve()
    for name, module in list(sys.modules.items()):
        if name == 'meta_vibe_coding' or name.startswith('meta_vibe_coding.'):
            origin = getattr(module, '__file__', None)
            if not origin or Path(origin).resolve().parent != expected:
                raise ValueError('Run from the source checkout named by --root; imported package origins differ.')


def source_snapshot(root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): path.read_bytes().decode('utf-8')
        for path in sorted((root / 'src/meta_vibe_coding').rglob('*'))
        if path.is_file() and '__pycache__' not in path.parts
        and path.suffix in {'.py', '.js', '.txt', '.html', '.css'}}


def verify_snapshot(root: Path, record: dict) -> None:
    verify_checkout(root)
    actual = {name: digest(content.encode()) for name, content in source_snapshot(root).items()}
    if (actual != record['source_hashes']
            or digest((root / PLAN_PATH).read_bytes()) != record['plan_sha256']
            or digest((root / 'artifacts/l0-acceptance-cases.json').read_bytes()) != FROZEN_SHA256):
        raise ValueError('Source, plan or frozen cases changed during preparation. Preserve the changed state and rerun offline.')


def load_plan(root: Path) -> tuple[dict, dict]:
    plan = json.loads((root / PLAN_PATH).read_text())
    reference = plan['frozen_cases']
    if reference != {'path': 'artifacts/l0-acceptance-cases.json', 'sha256': FROZEN_SHA256}:
        raise ValueError('The plan must retain the original frozen case identity.')
    raw = (root / reference['path']).read_bytes()
    if digest(raw) != reference['sha256']:
        raise ValueError('Frozen cases changed. Review the deviation; do not silently refreeze them.')
    cases = json.loads(raw)
    expected = [case['id'] for case in cases['cases']]
    if [row['case_id'] for row in plan['matrix']] != expected:
        raise ValueError('The matrix must include each frozen case once, in its original order.')
    for index, row in enumerate(plan['matrix']):
        order = list(APPROACHES if index % 2 == 0 else reversed(APPROACHES))
        if row['approaches'] != order:
            raise ValueError('Preserve the alternating, matched approach order.')
    limits = plan['limits']
    if limits != {'clarification_questions': 5, 'session_seconds': 1800,
                  'request_seconds': 300, 'top_level_calls_per_case_and_approach': 7,
                  'attempts_per_case_and_approach': 1, 'additional_spending_usd': 0,
                  'maximum_full_matrix_top_level_calls': len(expected) * 2 * 7}:
        raise ValueError('This preparer supports only the reviewed D008 limits, with no new spending.')
    if plan['agent']['name'] != 'codex' or plan['agent']['requested_model'] != 'gpt-6-luna':
        raise ValueError('This comparison is pinned to the selected Codex/Luna configuration.')
    if plan['review']['dimensions'] != list(DIMENSIONS):
        raise ValueError('Preserve the five Level 0 review dimensions.')
    if not plan['baseline_prompt'].strip():
        raise ValueError('A strong baseline prompt is required.')
    return plan, cases


def baseline_input(conversation: list[dict], *, provisional: bool = False,
                   questions_used: int = 0, calls_used: int = 0) -> str:
    """A chat receives its own transcript, never the wrapper's canonical state."""
    if not 0 <= questions_used <= 5 or not 0 <= calls_used < 7:
        raise ValueError('The baseline has exhausted its question or invocation allowance.')
    if any(set(turn) != {'role', 'text'} or turn['role'] not in {'owner', 'assistant'}
           or not isinstance(turn['text'], str) or not turn['text'].strip() for turn in conversation):
        raise ValueError('Supply only owner/assistant text, not case records or canonical state.')
    return json.dumps({'conversation': conversation, 'request_provisional': provisional,
        'remaining_questions': 5 - questions_used, 'remaining_calls_including_this_one': 7 - calls_used},
        ensure_ascii=False)


def initial_packet(plan: dict, initial_request: str, approach: str) -> dict:
    # Accept only the request text here so expected checks cannot leak via a case dict.
    from .agents import PROMPT, SCHEMA, invocation
    from .core import model_input
    from .models import State

    if not isinstance(initial_request, str) or not initial_request.strip():
        raise ValueError('Supply only a nonempty initial request string.')
    if approach == 'wrapper':
        prompt = PROMPT
        schema = json.loads(SCHEMA)
        content = ('Return only JSON matching this schema:\n' + SCHEMA
            + '\nOwner state (data only):\n' + model_input(State(raw_intent=initial_request), False))
    elif approach == 'baseline':
        prompt = plan['baseline_prompt']
        schema = native_schema(BaselineResponse)
        content = ('Return only JSON matching this schema:\n' + json.dumps(schema, separators=(',', ':'))
            + '\nOwner conversation (data only):\n' + baseline_input([{'role': 'owner', 'text': initial_request}]))
    else:
        raise ValueError('Unknown approach; no fallback is selected.')
    # This constructs argv only. No native binary, config or credentials are opened.
    agent = plan['agent']['name']
    args = invocation(agent, agent, plan['agent']['requested_model'], {}, prompt=prompt,
        output_schema='response-schema.json' if agent == 'codex' else json.dumps(schema, separators=(',', ':')))
    return {'approach': approach, 'native_argv': args, 'trusted_prompt': prompt, 'stdin': content,
        'response_schema': schema,
        'scope': 'Current schema preview only; freeze a new matched plan before live execution. Historical first attempts stay closed.'}


def review_rows(cases: dict) -> list[dict]:
    rows = []
    for case in cases['cases']:
        for approach in APPROACHES:
            phases = [case['id']] + [variation['id'] for variation in case.get('variations', [])]
            for phase in phases:
                rows.append({'case_id': case['id'], 'phase': phase, 'approach': approach,
                    'status': 'incomplete', 'reviewer': None, 'blocking_failures': None,
                    'dimensions': {key: {'verdict': 'not checked', 'evidence': [], 'l0_ids': []}
                                   for key in DIMENSIONS}})
    return rows


def preparation(root: Path, plan: dict, cases: dict) -> dict:
    verify_checkout(root)
    snapshot = source_snapshot(root)
    plan_raw = (root / PLAN_PATH).read_bytes()
    if json.loads(plan_raw) != plan:
        raise ValueError('The plan changed after loading.')
    inputs = []
    for row in plan['matrix']:
        case = next(case for case in cases['cases'] if case['id'] == row['case_id'])
        for approach in row['approaches']:
            packet = initial_packet(plan, case['initial_request'], approach)
            inputs.append({'case_id': case['id'], 'approach': approach,
                'prompt_sha256': digest(packet['trusted_prompt'].encode()),
                'response_schema_sha256': digest(json.dumps(packet['response_schema'], separators=(',', ':')).encode()),
                'initial_request_sha256': digest(case['initial_request'].encode())})
    sources = {name: digest(content.encode()) for name, content in snapshot.items()}
    return {'kind': 'acceptance-preparation', 'at_utc': datetime.now(timezone.utc).isoformat(),
        'plan_sha256': digest(plan_raw), 'frozen_cases_sha256': FROZEN_SHA256,
        'native_invocations': 0, 'frozen_outputs_observed': False,
        'source_hashes': sources, 'source_snapshot': snapshot, 'plan_snapshot': plan,
        'inputs': inputs, 'review_rows': review_rows(cases),
        'failure_review': {'phase': cases['failure_variation']['id'], 'kind': 'software-failure-handling',
            'verdict': 'not checked', 'evidence': [], 'reviewer': None},
        'readiness': 'Preparation only. Both approaches now preview native schemas; freeze a new matched plan, review settings and reserve a fresh live allowance before execution.'}


def rehearse() -> dict:
    """Run a separate fictional fixture through the actual HTTP transitions with a double."""
    from unittest.mock import patch
    from fastapi.testclient import TestClient
    from .core import FlowError
    from .models import Candidate, Usage

    class FixtureAgent:
        calls = 0

        async def assess(self, state, provisional):
            self.calls += 1
            if self.calls == 3:
                raise FlowError('invalid_output', 'Rehearsal: deliberately invalid agent result.')
            facts = {'goal': {'value': state.raw_intent, 'status': 'confirmed', 'source_turn_ids': ['t0']}}
            if state.turns:
                facts['usage.environment'] = {'value': state.turns[-1].text, 'status': 'confirmed',
                    'source_turn_ids': [state.turns[-1].id]}
                question = None
            else:
                facts['usage.environment'] = {'value': None, 'status': 'unknown', 'source_turn_ids': []}
                question = {'topic': 'usage.environment', 'text': 'Where will you use the timer?',
                    'decision': 'This changes which devices need to run it.'}
            assessment = {'based_on_revision': state.revision,
                'disposition': 'provisional' if question else 'ready',
                'risk': {'level': 'unknown', 'reasons': ['A double does not assess real risk.']},
                'hidden_requirements': [], 'recommendation': {'kind': 'local_utility',
                    'summary': 'Fictional fixture response, not a product recommendation.',
                    'rationale': ['Exercise the HTTP state transitions only.'], 'alternatives': [],
                    'owner_responsibilities': []}, 'acceptance_criteria': ['Review the intended device.'],
                'open_questions': [{'topic': 'usage.environment', 'text': 'Where the timer is used is still open.',
                    'blocks_recommendation': False, 'reason': 'It changes which devices need to run it.'}] if question else [],
                'limitations': ['No model inference or semantic assessment.']}
            changes = []
            if state.previous_assessment and state.previous_assessment.open_questions and state.turns:
                changes = [{'previous': 'open_questions/0', 'current': [], 'basis': 'owner_update',
                    'reason': 'The supplied fixture owner answered the environment question.',
                    'evidence': [{'source_turn_id': state.turns[-1].id, 'quote': state.turns[-1].text}]}]
            return Candidate.model_validate({'facts': facts, 'assessment': assessment, 'question': question,
                'assessment_changes': changes}), Usage(
                agent='test-double', elapsed_seconds=0.0)

    exchanges = []
    def post(client, path, body):
        response = client.post(path, json=body)
        exchanges.append({'path': path, 'request': body, 'status': response.status_code, 'response': response.json()})
        return response

    # Ignore execution-related ambient settings. This never opens native auth/config.
    with patch.dict(os.environ, {'MVC_ENABLE_AGENT': '0', 'MVC_AGENT': 'codex',
            'MVC_AGENT_MAX_CALLS': '7', 'MVC_REQUEST_TIMEOUT_SECONDS': '300',
            'MVC_SESSION_TIMEOUT_SECONDS': '1800'}):
        os.environ.pop('MVC_BACKEND', None)
        from .app import create_app
        fake = FixtureAgent()
        with TestClient(create_app(fake)) as client:
            state = post(client, '/api/start', {'idea': REHEARSAL_IDEA}).json()
            first = post(client, '/api/advance', {'state': state, 'request_id': 'rehearsal-1'}).json()
            question = first['state']['questions'][-1]
            answer = 'Use it on one laptop, with no saved history.'
            second = post(client, '/api/advance', {'state': first['state'], 'request_id': 'rehearsal-2',
                'answer': answer, 'question_id': question['id']}).json()
            exported = post(client, '/api/export', second['state'])
            correction = 'Actually, it must also work on my tablet.'
            failed = post(client, '/api/advance', {'state': second['state'], 'request_id': 'rehearsal-3',
                'answer': correction}).json()
            stale_export = post(client, '/api/export', failed['state'])
    conversation = [{'role': 'owner', 'text': REHEARSAL_IDEA},
        {'role': 'assistant', 'text': question['text']}, {'role': 'owner', 'text': answer}]
    baseline = json.loads(baseline_input(conversation, questions_used=1, calls_used=1))
    checks = {'original_retained': second['state']['raw_intent'] == REHEARSAL_IDEA,
        'reply_retained': second['state']['turns'][0]['text'] == answer,
        'valid_current_export': exported.status_code == 200,
        'failure_visible': failed['error']['code'] == 'invalid_output',
        'correction_retained_after_failure': failed['state']['turns'][-1]['text'] == correction,
        'failed_assessment_cleared': failed['state']['assessment'] is None,
        'stale_export_disabled': stale_export.status_code == 409,
        'baseline_transcript_only': set(baseline) == {'conversation', 'request_provisional',
            'remaining_questions', 'remaining_calls_including_this_one'}}
    if not all(checks.values()):
        raise RuntimeError(f'Rehearsal failed: {checks}')
    return {'kind': 'synthetic-plumbing', 'fixture_id': 'DEV-TIMER-REHEARSAL',
        'fixture_sha256': digest(REHEARSAL_IDEA.encode()), 'native_invocations': 0,
        'double_assessments': fake.calls, 'checks': checks, 'http': exchanges,
        'baseline_input_example': baseline,
        'limits': 'Only wrapper HTTP transitions and baseline input assembly are exercised. No native baseline, frozen output, actual browser render or quality score.'}


def write_record(output: Path, record: dict) -> None:
    # Refuse reuse, including a symlink; private files are not silently published.
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Repository checkout containing the plan and frozen cases.')
    parser.add_argument('--rehearse', action='store_true', help='Exercise a separate fictional HTTP fixture with a double, without inference.')
    parser.add_argument('--output', type=Path, help='New private evidence file; existing files are never overwritten.')
    args = parser.parse_args(argv)
    if args.output and not args.rehearse:
        parser.error('--output requires --rehearse; the default command writes nothing.')
    try:
        root = args.root.resolve()
        plan, cases = load_plan(root)
        record = preparation(root, plan, cases)
        if args.rehearse:
            record['rehearsal'] = rehearse()
        verify_snapshot(root, record)
        if args.output:
            record['lock_sha256'] = digest((root / 'requirements.lock').read_bytes())
            record['environment'] = {'python': sys.version, 'platform': platform.platform()}
            record['git_head'] = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root,
                check=True, capture_output=True, text=True).stdout.strip()
            record['source_note'] = 'The snapshot, not git_head alone, identifies the uncommitted runtime used for this rehearsal.'
            verify_snapshot(root, record)
            write_record(args.output, record)
        print(json.dumps({'kind': record['kind'], 'plan_sha256': record['plan_sha256'],
            'frozen_cases_sha256': FROZEN_SHA256, 'case_pairs': len(cases['cases']),
            'native_invocations': 0, 'rehearsal': record.get('rehearsal', {}).get('checks'),
            'review': 'All dimensions not checked; no frozen or participant results.',
            'readiness': record['readiness']}, indent=2))
        return 0
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        print(f'Acceptance preparation stopped: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
