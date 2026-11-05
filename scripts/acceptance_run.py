"""Run one approved acceptance matrix through any supported coding agent.

The frozen plan names the agent, limits, cases and source. Everything that differs
between agents lives in an adapter; the run logic below does not branch on them.
An operator selects frozen answers; nothing retries automatically. The product
package deliberately has no live execution mode, so this entry point stays outside it.

    acceptance_run.py serve --plan PLAN --run-dir DIR --approval FILE
    acceptance_run.py control --run-dir DIR status
    acceptance_run.py control --run-dir DIR select|step|finish '<json>'

The operator and the server share files in the run directory, not a network port, so
an operator can run inside a sandbox that denies localhost. Actions stay as evidence.
"""
import argparse, asyncio, base64, hashlib, json, os, shutil, signal, subprocess, tempfile, threading, time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from uuid import uuid4

import httpx

from meta_vibe_coding import agents, evaluation
from meta_vibe_coding.core import FlowError
from meta_vibe_coding.settings import Limits

NATIVE = agents.run_cli
ACTIONS = ('status', 'select', 'step', 'finish')
ACTIVE_QUESTION = lambda state: next((q for q in reversed(state['questions']) if not q['retired'] and not q['answer_turn_id']), None)


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message + ' Preserve all evidence.')


def exclusive(path: Path, value) -> None:
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.write('\n')
        file.flush()
        os.fsync(file.fileno())


def record_streams(stdout: bytes, stderr: bytes, status) -> dict:
    result = {'returncode': status}
    for name, raw in (('stdout', stdout), ('stderr', stderr)):
        result[name + '_sha256'] = sha(raw)
        try:
            result[name] = raw.decode('utf-8')
        except UnicodeError:
            result[name] = raw.decode('utf-8', errors='replace')
            result[name + '_base64'] = base64.b64encode(raw).decode('ascii')
    return result


def json_lines(text: str) -> list[dict]:
    records = []
    for line in text.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def codex_stopped(stdout: str) -> bool:
    kinds = {record.get('type') for record in json_lines(stdout)}
    return bool(kinds & {'error', 'turn.failed'}) or 'turn.completed' not in kinds


def claude_stopped(stdout: str) -> bool:
    try:
        body = json.loads(stdout)
    except ValueError:
        return True
    # Every call carries a schema, so a reply without structured output is not a normal completion.
    return (not isinstance(body, dict) or body.get('type') != 'result' or body.get('subtype') != 'success'
        or body.get('is_error') is not False or body.get('terminal_reason') != 'completed'
        or body.get('api_error') is not None or body.get('api_error_status') is not None
        or bool(body.get('safety_stops')) or not isinstance(body.get('structured_output'), dict))


def opencode_stopped(stdout: str) -> bool:
    return any(record.get('type') == 'error' for record in json_lines(stdout))


def codex_login(env: dict) -> bool:
    login = subprocess.run(['codex', 'login', 'status'], env=env, check=True, capture_output=True, text=True)
    return 'Logged in using ChatGPT' in login.stdout + login.stderr


def claude_login(env: dict) -> bool:
    status = subprocess.run(['claude', 'auth', 'status'], env=env, check=True, capture_output=True, text=True)
    body = json.loads(status.stdout)
    return body.get('loggedIn') is True and body.get('authMethod') == 'claude.ai'


def codex_quota(env: dict, timeout: float = 25) -> dict:
    """Read rate limits through the Codex app server. No inference; no credential is read here."""
    with tempfile.TemporaryDirectory(prefix='mvc-quota-') as cwd:
        process = subprocess.Popen(['codex', 'app-server'], cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1, start_new_session=True)

        def stop():
            try:
                os.killpg(process.pid, signal.SIGKILL)  # A child holding the pipe would keep a read blocked.
            except (ProcessLookupError, PermissionError):
                pass

        deadline = threading.Timer(timeout, stop)
        deadline.start()
        try:
            def send(message):
                process.stdin.write(json.dumps(message) + '\n')
                process.stdin.flush()

            def wait(request_id):
                for line in process.stdout:
                    reply = json.loads(line)
                    if reply.get('id') == request_id:
                        return reply
                raise TimeoutError('No app-server reply.')

            send({'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'mvc-acceptance', 'version': '1'}}})
            wait(1)
            send({'method': 'initialized'})
            send({'id': 2, 'method': 'account/rateLimits/read'})
            return wait(2)['result']
        finally:
            deadline.cancel()
            stop()
            process.wait()


def codex_quota_refusal(quota: dict) -> str | None:
    """Keep about one seven-call job in reserve. Anything unreadable refuses."""
    if quota.get('ordinaryUsageAllowed') is not True:
        return 'Codex reports the usage limit as reached.'
    for limits in [quota.get('rateLimits'), *(quota.get('rateLimitsByLimitId') or {}).values()]:
        limits = limits if isinstance(limits, dict) else {}
        window, weekly = limits.get('primary') or {}, limits.get('secondary') or {}
        if limits.get('rateLimitReachedType') or limits.get('spendControlReached'):
            return 'Codex reports the usage limit as reached.'
        if not isinstance(window.get('usedPercent'), (int, float)) or not isinstance(weekly.get('usedPercent'), (int, float)):
            return 'Codex quota is unreadable.'
        if window['usedPercent'] > 88:
            return 'The 5-hour window is too full to finish another job.'
        if weekly['usedPercent'] > 96:
            return 'The weekly window is too full to finish another job.'
    return None


@dataclass(frozen=True)
class Adapter:
    """What differs between agents. Quota stays None where no inference-free read exists."""
    forbidden_environment: frozenset[str]
    schema_delivery: str  # 'file', 'argument' or 'stdin'
    stopped: Callable[[str], bool]
    login: Callable[[dict], bool] | None = None
    quota: Callable[[dict], dict] | None = None
    quota_refusal: Callable[[dict], str | None] | None = None


ADAPTERS = {
    'codex': Adapter(frozenset({'OPENAI_API_KEY', 'CODEX_API_KEY'}), 'file', codex_stopped, codex_login, codex_quota, codex_quota_refusal),
    'claude': Adapter(frozenset({'ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_BASE_URL', 'CLAUDE_CODE_OAUTH_TOKEN'}), 'argument', claude_stopped, claude_login),
    'opencode': Adapter(frozenset(), 'stdin', opencode_stopped),
}


def schema_option(adapter: Adapter, schema: str, cwd: str) -> str | None:
    if adapter.schema_delivery == 'file':
        path = Path(cwd) / 'response-schema.json'
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as file:
            file.write(schema)
        return str(path)
    return schema if adapter.schema_delivery == 'argument' else None


def delivered_schema(adapter: Adapter, args: list[str], cwd: str) -> str | None:
    """Return the schema text a request carries natively, checking a file belongs to the request."""
    if adapter.schema_delivery == 'file':
        path = Path(args[args.index('--output-schema') + 1])
        require(not path.is_symlink() and path.resolve().parent == Path(cwd).resolve(), 'Schema input must belong to request workspace.')
        require(path.stat().st_mode & 0o777 == 0o600, 'Schema input must be private.')
        return path.read_text()
    if adapter.schema_delivery == 'argument':
        return args[args.index('--json-schema') + 1]
    return None


def native_stop(adapter: Adapter, event: dict) -> bool:
    """True when native evidence shows a failed call, whatever failure code it became."""
    streams = event.get('streams') or {}
    return bool(event.get('error')) or streams.get('returncode') != 0 or adapter.stopped(streams.get('stdout') or '')


def read_journal(run_dir: Path) -> tuple[bytes, list[dict]]:
    raw = (run_dir / 'journal.jsonl').read_bytes()
    require(raw.endswith(b'\n'), 'The journal ends mid-record.')
    return raw, [json.loads(line) for line in raw.splitlines()]


def job_events(events: list[dict], job: str) -> list[dict]:
    return [event for event in events if event.get('job') == job]


class Harness:
    def __init__(self, plan_path: Path, run_dir: Path, repo: Path):
        self.repo, self.plan_path, self.run_dir = repo, plan_path, run_dir
        self.plan = json.loads(plan_path.read_text())
        self.agent_name = self.plan['agent']['name']
        self.model = self.plan['agent']['requested_model']
        self.adapter = ADAPTERS[self.agent_name]
        self.limits = self.plan['limits']
        self.cases = json.loads((repo / self.plan['frozen_cases']['path']).read_text())
        self.matrix = [(row['case_id'], approach) for row in self.plan['matrix'] for approach in row['approaches']]
        self.jobs = {}
        self.active = None
        self.reservations = 0
        self.log = None
        self.version = None
        self.plan_sha256 = sha(plan_path.read_bytes())

    def event(self, kind: str, **data) -> None:
        self.log.write(json.dumps({'type': kind, 'at_utc': utc(), **data}, ensure_ascii=False) + '\n')
        self.log.flush()
        os.fsync(self.log.fileno())

    def verify(self) -> None:
        frozen = self.plan['frozen_runtime']
        evaluation.verify_checkout(self.repo)
        require(sha(self.plan_path.read_bytes()) == self.plan_sha256, 'Plan changed.')
        require(agents.PROMPT == frozen['wrapper_prompt'], 'Imported prompt differs.')
        require(json.loads(agents.SCHEMA) == self.plan['native_output']['wrapper'], 'Imported wrapper schema differs.')
        require(evaluation.native_schema(evaluation.BaselineResponse) == self.plan['native_output']['baseline'], 'Imported baseline schema differs.')
        require(evaluation.source_snapshot(self.repo) == frozen['source_snapshot'], 'Runtime source changed.')
        require(sha((self.repo / self.plan['frozen_cases']['path']).read_bytes()) == self.plan['frozen_cases']['sha256'], 'Cases changed.')
        require(sha(Path(__file__).read_bytes()) == self.plan['harness_sha256'], 'Harness changed.')
        require(sha((self.repo / 'requirements.lock').read_bytes()) == frozen['requirements_lock_sha256'], 'Dependency lock changed.')

    def environment(self) -> dict:
        env = agents.agent_environment(self.agent_name)
        require(not (set(env) & self.adapter.forbidden_environment), 'API-key routes are excluded.')
        return env

    def binary_hash(self) -> str:
        return sha(Path(shutil.which(agents.AGENTS[self.agent_name])).resolve().read_bytes())

    def check_runtime(self) -> dict:
        """Confirm the CLI and native login without sending inference."""
        env = self.environment()
        binary = agents.AGENTS[self.agent_name]
        version = subprocess.run([binary, '--version'], env=env, check=True, capture_output=True, text=True).stdout.strip()
        if self.adapter.login:
            require(self.adapter.login(env), 'Saved native login required.')
        if self.adapter.quota:
            self.adapter.quota(env)  # Also proves the route from this exact environment.
        return {'agent_version': version, 'agent_binary_sha256': self.binary_hash()}

    def open_log(self) -> None:
        self.log = os.fdopen(os.open(self.run_dir / 'journal.jsonl', os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600), 'w')

    def start(self, approval: dict) -> None:
        self.verify()
        require(not (self.run_dir / 'journal.jsonl').exists(), 'A run already exists; resume needs its journal hash.')
        self.run_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        runtime = self.check_runtime()
        self.version = runtime['agent_version']
        exclusive(self.run_dir / 'run.claim', {'native_invocation_limit': self.limits['maximum_full_matrix_top_level_calls'],
            'matrix': self.matrix, 'authority': self.plan['live_authority']})
        exclusive(self.run_dir / 'manifest.json', {'kind': 'acceptance-matrix', 'started_at_utc': utc(), 'plan_sha256': self.plan_sha256,
            'harness_sha256': self.plan['harness_sha256'], 'harness_source': Path(__file__).read_text(), 'approval': approval,
            'agent': self.agent_name, 'requested_model': self.model, 'agent_environment_names': sorted(self.environment()), **runtime})
        self.open_log()
        self.event('run_started', manifest_sha256=sha((self.run_dir / 'manifest.json').read_bytes()))

    def rebuild_job(self, events: list[dict], job: str) -> dict:
        case_id, approach = job.rsplit('-', 1)
        rows = job_events(events, job)
        states = [e['response'] if e['path'] == '/api/start' else e['response']['state']
            for e in rows if e['type'] == 'http' and e['path'] in ('/api/start', '/api/advance')]
        finished = [e for e in rows if e['type'] == 'job_finished']
        require(len(finished) <= 1, 'Duplicate close for ' + job + '.')
        actions = [e for e in rows if e['type'] == 'operator_action']
        baselines = [e['result'] for e in rows if e['type'] == 'baseline_result']
        steps = [e for e in rows if e['type'] == 'step_finished']
        return {'id': job, 'case_id': case_id, 'approach': approach,
            'case': next(c for c in self.cases['cases'] if c['id'] == case_id),
            'calls': sum(e['type'] == 'native_started' for e in rows), 'questions': sum(a['question_count'] for a in actions),
            'started_at': datetime.fromisoformat(next(e for e in rows if e['type'] == 'job_started')['at_utc']).timestamp(),
            'closed': bool(finished), 'state': states[-1] if states else None,
            'previous': next((s for s in reversed(states[:-1]) if s and s.get('assessment')), None),
            'baseline': baselines[-1] if baselines else None, 'failure': finished[0]['failure'] if finished else (steps[-1]['summary']['failure'] if steps else None),
            'conversation': finished[0]['conversation'] if finished else None,
            'phases': [a['variation'] for a in actions if a['variation']]}

    def resume(self, reason: str) -> None:
        """Continue from the journal. Adds no allowance and repeats no attempt."""
        self.verify()
        raw, events = read_journal(self.run_dir)
        manifest = json.loads((self.run_dir / 'manifest.json').read_text())
        require(events[0]['type'] == 'run_started' and events[0]['manifest_sha256'] == sha((self.run_dir / 'manifest.json').read_bytes()), 'Manifest differs.')
        require(manifest['plan_sha256'] == self.plan_sha256, 'Run belongs to another plan.')
        limit = self.limits['maximum_full_matrix_top_level_calls']
        require(json.loads((self.run_dir / 'run.claim').read_text())['native_invocation_limit'] == limit, 'Run claim differs from the plan.')
        opened = [e['job'] for e in events if e['type'] == 'job_started']
        require(opened == [c + '-' + a for c, a in self.matrix][:len(opened)], 'Jobs are out of matrix order.')
        require(sorted(p.stem for p in self.run_dir.glob('*.claim') if '-' in p.stem and not p.stem.startswith('resume-')) == sorted(opened), 'Job claims differ from the journal.')
        numbers = [e['number'] for e in events if e['type'] == 'native_started']
        require(numbers == list(range(1, len(numbers) + 1)) and len(numbers) <= limit, 'Native call numbers are not contiguous and within the limit.')
        require(numbers == [e['number'] for e in events if e['type'] == 'native_finished'], 'A native call has no recorded finish.')
        jobs = {job: self.rebuild_job(events, job) for job in opened}
        unfinished = [job for job in jobs.values() if not job['closed']]
        require(len(unfinished) <= 1, 'More than one job is open.')
        for job in unfinished:
            require(job['failure'], job['id'] + ' is open without a recorded failure.')
        exclusive(self.run_dir / ('resume-' + sha(raw)[:16] + '.claim'), {'prior_journal_sha256': sha(raw), 'new_allowance': 0, 'reason': reason})
        self.version = manifest['agent_version']
        self.reservations, self.jobs = len(numbers), jobs
        self.open_log()
        self.event('run_resumed', reason=reason, prior_journal_sha256=sha(raw), native_calls_before_resume=len(numbers), new_allowance=0)
        for job in unfinished:
            last = next(e for e in reversed(job_events(events, job['id'])) if e['type'] == 'operator_action')
            job['closed'] = True
            self.event('job_finished', job=job['id'], reason='Closed at resume as its recorded technical stop; no call repeated.',
                calls=job['calls'], questions=job['questions'], failure=job['failure'], phases=job['phases'],
                phases_not_checked=[v['id'] for v in job['case'].get('variations', []) if v['id'] not in job['phases'] or v['id'] == last['variation']],
                state=job['state'], baseline=job['baseline'], conversation=None, conversation_source='native_started stdin', closed_by_resume=True)

    def select(self, case_id: str, approach: str) -> dict:
        self.verify()
        require(not self.active or self.active['closed'], 'Finish the active first attempt.')
        index = len(self.jobs)
        require(index < len(self.matrix) and self.matrix[index] == (case_id, approach), 'Preserve frozen matrix order.')
        if self.active:
            stopped = any(e['type'] == 'native_finished' and native_stop(self.adapter, e)
                for e in job_events(read_journal(self.run_dir)[1], self.active['id']))
            require(not stopped, 'Native stop: end this server and review before another first attempt.')
        require(self.binary_hash() == json.loads((self.run_dir / 'manifest.json').read_text())['agent_binary_sha256'], 'Agent binary changed.')
        job_id = case_id + '-' + approach
        if self.adapter.quota:
            try:
                quota = self.adapter.quota(self.environment())
            except Exception as exc:
                self.event('quota_refused', next_job=job_id, error_type=type(exc).__name__)
                raise ValueError('Quota read failed; no first attempt started.')
            refusal = self.adapter.quota_refusal(quota)
            self.event('quota_checked', next_job=job_id, refusal=refusal)
            require(refusal is None, str(refusal))
        case = next(c for c in self.cases['cases'] if c['id'] == case_id)
        exclusive(self.run_dir / (job_id + '.claim'), {'job': job_id, 'started_at_utc': utc(), 'attempt': 1, 'max_calls': self.limits['top_level_calls_per_case_and_approach']})
        job = {'id': job_id, 'case_id': case_id, 'approach': approach, 'calls': 0, 'questions': 0, 'started_at': time.time(), 'closed': False,
            'state': None, 'previous': None, 'baseline': None, 'conversation': [{'role': 'owner', 'text': case['initial_request']}],
            'failure': None, 'phases': [], 'case': case}
        if approach == 'wrapper':
            job['agent'] = agents.CodingAgent(limits=Limits(self.limits['request_seconds'], self.limits['session_seconds']))
            job['agent'].version = self.version
        self.jobs[job_id] = job
        self.active = job
        self.event('job_started', job=job_id, initial_request=case['initial_request'], attempt=1)
        return self.summary(job)

    async def native(self, args: list[str], **kwargs) -> bytes:
        if '--help' in args or '--version' in args:  # Product probes send no inference.
            return await NATIVE(args, **kwargs)
        self.verify()
        job = self.active
        session, per_job, total = self.limits['session_seconds'], self.limits['top_level_calls_per_case_and_approach'], self.limits['maximum_full_matrix_top_level_calls']
        if not job or job['closed'] or job['calls'] >= per_job or self.reservations >= total:
            raise FlowError('limit', 'The authorized first-attempt allowance is exhausted.')
        if time.time() - job['started_at'] >= session:
            raise FlowError('limit', 'Case deadline exhausted.')
        prompt = agents.PROMPT if job['approach'] == 'wrapper' else self.plan['baseline_prompt']
        # The wrapper keeps the product's own budget. A plain chat is not bound by it, so a plan
        # may give the transcript baseline more room (D017); older plans share 32000 bytes.
        budget = 32000 if job['approach'] == 'wrapper' else self.limits.get('baseline_input_bytes', 32000)
        if len(kwargs['content'].encode()) + len(prompt.encode()) > budget:
            raise FlowError('limit', f'Input exceeds the {budget}-byte limit for this approach.')
        require('--fallback-model' not in args, 'Fallback models are excluded.')
        expected = self.plan['native_output'][job['approach']]
        schema = delivered_schema(self.adapter, args, kwargs['cwd'])
        if schema is not None:
            require(json.loads(schema) == expected, 'Native schema differs from the plan.')
            require(schema in kwargs['content'], 'Native schema differs from stdin.')
        kwargs['timeout'] = min(kwargs['timeout'], session - (time.time() - job['started_at']))
        job['calls'] += 1
        self.reservations += 1
        number, began = self.reservations, time.perf_counter()
        self.event('native_started', job=job['id'], number=number, job_call=job['calls'],
            argv=[agents.AGENTS[self.agent_name], *args[1:]], stdin=kwargs['content'], stdin_sha256=sha(kwargs['content'].encode()), timeout_seconds=kwargs['timeout'])
        streams, error = {}, None

        def capture(stdout, stderr, status):
            streams.update(record_streams(stdout, stderr, status))

        try:
            return await NATIVE(args, **kwargs, capture=capture)
        except BaseException as exc:
            error = {'type': type(exc).__name__, 'code': getattr(exc, 'code', None)}
            raise
        finally:
            input_files = {'response-schema.json'} if self.adapter.schema_delivery == 'file' else set()
            created = [str(p.relative_to(kwargs['cwd'])) for p in Path(kwargs['cwd']).rglob('*') if p.is_file() and p.name not in input_files]
            self.event('native_finished', job=job['id'], number=number, elapsed_seconds=time.perf_counter() - began,
                error=error, streams=streams, unexpected_workspace_files=created)
            self.verify()
            if created:
                raise FlowError('invalid_output', 'Agent-created workspace files are forbidden.')

    def summary(self, job: dict) -> dict:
        common = {'job': job['id'], 'calls': job['calls'], 'questions_counted': job['questions'], 'closed': job['closed'], 'failure': job['failure']}
        if job['approach'] == 'wrapper':
            state = job['state']
            return {**common, 'question': ACTIVE_QUESTION(state) if state else None, 'assessment': state.get('assessment') if state else None}
        return {**common, 'response': job['baseline']}

    def answer_text(self, job: dict, body: dict, variation: str | None) -> str | None:
        """Compose exactly one recorded owner reply from frozen material."""
        passages, topics, unknown = body.get('fact_passages', []), body.get('fact_topics', []), body.get('unknown', False)
        facts = {fact['topic']: fact['answer'] for fact in job['case']['operator_facts']}
        require(bool(variation) + bool(topics) + bool(passages or unknown) <= 1, 'Choose one recorded answer source.')
        if variation:
            return next(v for v in job['case']['variations'] if v['id'] == variation)['owner_text']
        if topics:
            require(len(set(topics)) == len(topics) and all(t in facts for t in topics), 'Unknown or duplicate fact topic.')
            return '\n'.join(facts[t] for t in topics)
        for passage in passages:
            require(isinstance(passage, dict) and set(passage) == {'topic', 'text'} and passage['topic'] in facts
                and passage['text'].strip() and passage['text'] in facts[passage['topic']], 'Passages must be exact substrings of their frozen topic.')
        require(len({(p['topic'], p['text']) for p in passages}) == len(passages), 'Duplicate fact passage.')
        known = '\n'.join(p['text'] for p in passages)
        if known and unknown:
            # Tie the unknown to this question, so it cannot read as answering other open items.
            return known + '\nI do not know the rest of this question.'
        return known or ('I do not know.' if unknown else None)

    async def step(self, body: dict) -> dict:
        job = self.active
        require(job and not job['closed'] and not job['failure'], 'No active healthy first attempt.')
        require(not set(body) - {'job', 'after_calls', 'question_count', 'fact_topics', 'fact_passages', 'variation', 'unknown', 'provisional', 'rationale', 'as_answer'}, 'Unknown operator action fields.')
        require(body.get('job') == job['id'] and body.get('after_calls') == job['calls'], 'Step does not match the current job and call count; check status first.')
        count = body.get('question_count', 0)
        per_job = self.limits['top_level_calls_per_case_and_approach']
        require(type(count) is int and count >= 0, 'Count separate information requests.')
        require(job['calls'] < per_job, 'No invocations remain; close the attempt.')
        variation, provisional = body.get('variation'), body.get('provisional', False)
        answered = body.get('fact_passages') or body.get('fact_topics') or body.get('unknown')
        state, last = job['state'], job['baseline']
        if job['approach'] == 'wrapper':
            outstanding, assessment = (ACTIVE_QUESTION(state), state.get('assessment')) if state else (None, None)
        else:
            outstanding, assessment = (last.get('question'), last.get('developer_view')) if last else (None, None)
        if job['calls'] == 0:
            require(not (answered or variation or provisional or count), 'First inference receives the initial request only.')
        else:
            require(answered or variation or provisional, 'No blank regeneration or retry.')
            require(outstanding or not answered, 'Fact answers require an outstanding question.')
            require(count or not outstanding, 'Count the outstanding question before answering or ending clarification.')
            require(outstanding or not count, 'No outstanding question to count.')
            if provisional and not variation and not outstanding:
                require(assessment and assessment.get('disposition') == 'needs_answer', 'A completed result cannot be regenerated as provisional.')
            if variation:
                item = next((v for v in job['case'].get('variations', []) if v['id'] == variation), None)
                require(item, 'Unknown variation for this case.')
                require(variation not in job['phases'], 'Variation already supplied.')
                if body.get('as_answer'):
                    require(item['type'] == 'unknown' and outstanding, 'Only the unknown variation can answer a question.')
                else:
                    require(not outstanding and assessment and assessment.get('disposition') in {'ready', 'provisional'}, 'Post-result variation requires a completed base result.')
        answer = self.answer_text(job, body, variation)
        if variation and job['calls'] == per_job - 1:
            require(provisional, 'The final variation call must request provisional output.')
        undisclosed = any(v['id'] not in job['phases'] for v in job['case'].get('variations', []))
        if job['calls'] == per_job - 2 and undisclosed and not variation:
            require(provisional, 'Reserve the last call for the attached variation; close the base provisionally now.')
        job['questions'] += count
        if job['questions'] > self.limits['clarification_questions']:
            job['failure'] = {'code': 'question_limit', 'message': 'More than the allowed information requests were asked.'}
            self.event('operator_question_limit', job=job['id'], count=job['questions'])
            return self.summary(job)
        # At the question limit no further question may be asked, so every later call closes
        # provisionally. The harness enforces this rather than relying on the operator.
        enforced = job['questions'] == self.limits['clarification_questions'] and not provisional
        provisional = provisional or enforced
        if variation:
            job['phases'].append(variation)
        self.event('operator_action', job=job['id'], question_count=count, fact_topics=body.get('fact_topics', []), fact_passages=body.get('fact_passages', []),
            variation=variation, unknown=body.get('unknown', False), answer=answer, provisional=provisional, provisional_enforced=enforced,
            rationale=body.get('rationale', ''))
        self.verify()
        if time.time() - job['started_at'] >= self.limits['session_seconds']:
            job['failure'] = {'code': 'session_limit'}
            return self.summary(job)
        try:
            if job['approach'] == 'wrapper':
                await self.advance_wrapper(job, body, answer, variation, provisional)
            else:
                await self.advance_baseline(job, answer, provisional)
        except BaseException as exc:
            job['failure'] = {'code': getattr(exc, 'code', 'invalid_output'), 'type': type(exc).__name__,
                'message': str(exc) if isinstance(exc, FlowError) else 'The first attempt failed; inspect native evidence.'}
            self.event('job_error', job=job['id'], failure=job['failure'])
            if not isinstance(exc, Exception):
                raise
        self.event('step_finished', job=job['id'], summary=self.summary(job))
        return self.summary(job)

    async def post_product(self, path: str, payload: dict):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.product), base_url='http://localhost') as client:
            result = await client.post(path, json=payload)
        body = result.json()
        self.event('http', job=self.active['id'], path=path, request=payload, status=result.status_code, response=body)
        return body

    async def advance_wrapper(self, job: dict, body: dict, answer, variation, provisional) -> None:
        if job['state'] is None:
            job['state'] = await self.post_product('/api/start', {'idea': job['case']['initial_request']})
        if job['state'].get('assessment'):
            job['previous'] = job['state']
        active = ACTIVE_QUESTION(job['state'])
        question_id = active['id'] if active and answer is not None and (not variation or body.get('as_answer')) else None
        result = await self.post_product('/api/advance', {'state': job['state'], 'request_id': str(uuid4()), 'answer': answer,
            'question_id': question_id, 'declares_unknown': False, 'provisional': provisional})
        require('state' in result, 'Invalid HTTP transition.')
        job['state'], job['failure'] = result['state'], result['error']
        await self.post_product('/api/export', job['state'])

    async def advance_baseline(self, job: dict, answer, provisional: bool) -> None:
        if answer is not None:
            job['conversation'].append({'role': 'owner', 'text': answer})
        conversation = evaluation.baseline_input(job['conversation'], provisional=provisional, questions_used=job['questions'], calls_used=job['calls'])
        schema = json.dumps(self.plan['native_output']['baseline'], separators=(',', ':'))
        content = 'Return only JSON matching this schema:\n' + schema + '\nOwner conversation (data only):\n' + conversation
        env = self.environment()
        with tempfile.TemporaryDirectory(prefix='mvc-agent-') as cwd:
            env['PWD'] = cwd
            args = agents.invocation(self.agent_name, shutil.which(agents.AGENTS[self.agent_name]), self.model, env,
                prompt=self.plan['baseline_prompt'], output_schema=schema_option(self.adapter, schema, cwd))
            raw = await self.native(args, content=content, cwd=cwd, env=env,
                timeout=min(self.limits['request_seconds'], self.limits['session_seconds'] - (time.time() - job['started_at'])))
        text, usage = agents.parse_completion(self.agent_name, raw)
        result = evaluation.BaselineResponse.model_validate_json(text).model_dump()
        job['baseline'] = result
        job['conversation'].append({'role': 'assistant', 'text': text})
        self.event('baseline_result', job=job['id'], result=result, usage=usage)

    def finish(self, body: dict) -> dict:
        job = self.active
        require(job and not job['closed'], 'No open attempt.')
        require(body.get('job') == job['id'], 'Finish does not match the current job; check status first.')
        require(isinstance(body.get('reason'), str) and body['reason'].strip(), 'Finish needs a reason.')
        count = body.get('question_count', 0)
        require(type(count) is int and count >= 0, 'Invalid count.')
        if not job['failure']:
            outstanding = (ACTIVE_QUESTION(job['state']) if job['state'] else None) if job['approach'] == 'wrapper' else (job['baseline'] or {}).get('question')
            require(count or not outstanding, 'Count the final outstanding question before closing.')
        job['questions'] += count
        if job['questions'] > self.limits['clarification_questions'] and not job['failure']:
            job['failure'] = {'code': 'question_limit', 'message': 'More than the allowed information requests were asked.'}
        job['closed'] = True
        self.event('job_finished', job=job['id'], reason=body['reason'], calls=job['calls'], questions=job['questions'],
            elapsed_seconds=time.time() - job['started_at'], failure=job['failure'], phases=job['phases'],
            state=job['state'], baseline=job['baseline'], conversation=job['conversation'])
        return self.summary(job)


def connect_product(harness: Harness) -> None:
    from meta_vibe_coding.app import create_app

    class Relay:
        agent, model, enabled, max_calls = harness.agent_name, harness.model, False, harness.limits['top_level_calls_per_case_and_approach']

        async def assess(self, state, provisional):
            job = harness.active
            if not job or job['closed'] or job['approach'] != 'wrapper':
                raise FlowError('disabled', 'Recorded session is closed.')
            return await job['agent'].assess(state, provisional)

    harness.product = create_app(Relay())


async def handle(harness: Harness, action: str, body: dict) -> dict:
    """Run one operator action. A refusal or bad request is a reply, not a server failure."""
    try:
        require(isinstance(body, dict), 'The action body must be a JSON object.')
        if action == 'status':
            rest = harness.matrix[len(harness.jobs):]
            active = harness.active if harness.active and not harness.active['closed'] else None
            # Status carries no case-derived text, so a blind coordinator can read it.
            return {'reserved': harness.reservations, 'closed': sum(j['closed'] for j in harness.jobs.values()), 'next': list(rest[0]) if rest else None,
                'active': {key: (active or {}).get(key) for key in ('id', 'calls', 'questions')} if active else None,
                'active_failure': (active.get('failure') or {}).get('code') if active else None}
        if action == 'select':
            return harness.select(body['case_id'], body['approach'])
        if action == 'step':
            return await harness.step(body)
        return harness.finish(body)
    except Exception as exc:
        return {'error': type(exc).__name__ + ': ' + str(exc)}


async def process_inbox(harness: Harness) -> int:
    """Handle waiting actions in order. Each request moves to the evidence folder once answered."""
    inbox, outbox, done = (harness.run_dir / name for name in ('inbox', 'outbox', 'operator'))
    handled = 0
    for path in sorted(inbox.glob('*.json')):
        action = path.stem.rpartition('-')[2]
        try:
            body = json.loads(path.read_text())
        except ValueError:
            body = None
        reply = await handle(harness, action, body) if action in ACTIONS else {'error': 'Unknown action.'}
        partial = outbox / (path.name + '.part')
        partial.write_text(json.dumps(reply, ensure_ascii=False))
        partial.replace(outbox / path.name)
        path.replace(done / path.name)
        handled += 1
    return handled


async def watch(harness: Harness) -> None:
    for name in ('inbox', 'outbox', 'operator'):
        (harness.run_dir / name).mkdir(mode=0o700, exist_ok=True)
    print('ready', flush=True)
    while True:
        await process_inbox(harness)
        await asyncio.sleep(0.25)


def serve(args) -> None:
    repo = Path(__file__).resolve().parent.parent
    plan_path = args.plan.resolve()
    run_dir = args.run_dir.resolve()
    require(run_dir == Path(json.loads(plan_path.read_text())['execution_directory']).resolve(), 'The run directory must be the one the plan names.')
    require(not list((run_dir / 'inbox').glob('*.json')), 'Queued operator requests exist; review them before launching.')
    approval = json.loads(args.approval.read_text())
    journal = args.run_dir / 'journal.jsonl'
    journal_sha = sha(journal.read_bytes()) if journal.exists() else None
    require(approval.get('verdict') == 'pass', 'Independent approval required.')
    require(approval.get('plan_sha256') == sha(plan_path.read_bytes()) and approval.get('harness_sha256') == sha(Path(__file__).read_bytes()), 'Approval must bind the exact plan and harness.')
    require(approval.get('journal_sha256') == journal_sha, 'Each launch needs an approval of the current journal.')
    probe = json.loads(plan_path.read_text())['agent']
    for name in ADAPTERS[probe['name']].forbidden_environment | {'MVC_BACKEND'}:
        os.environ.pop(name, None)
    limits = json.loads(plan_path.read_text())['limits']
    os.environ.update(MVC_AGENT=probe['name'], MVC_ENABLE_AGENT='1', MVC_AGENT_MODEL=probe['requested_model'], MVC_AGENT_ENV='',
        MVC_AGENT_MAX_CALLS=str(limits['top_level_calls_per_case_and_approach']),
        MVC_REQUEST_TIMEOUT_SECONDS=str(limits['request_seconds']), MVC_SESSION_TIMEOUT_SECONDS=str(limits['session_seconds']))
    harness = Harness(plan_path, run_dir, repo)
    if journal_sha:
        manifest = json.loads((run_dir / 'manifest.json').read_text())
        runtime = harness.check_runtime()
        require(all(runtime[key] == manifest[key] for key in runtime), 'The agent differs from the run manifest.')
        harness.resume(approval['reason'])
    else:
        harness.start(approval)
    agents.run_cli = harness.native
    connect_product(harness)
    asyncio.run(watch(harness))


def control(args, timeout: float = 350) -> int:
    """Send one operator action and show only what the operator needs."""
    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '-' + args.action + '.json'
    partial = args.run_dir / 'inbox' / (name + '.part')
    with os.fdopen(os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as file:
        json.dump(json.loads(args.body), file, ensure_ascii=False, indent=2)
    partial.replace(partial.with_suffix(''))
    reply = args.run_dir / 'outbox' / name
    deadline = time.monotonic() + timeout
    while not reply.exists():
        if time.monotonic() > deadline:
            print(json.dumps({'error': 'No reply yet; the request stays queued. Check that the server is running, and do not resend it.'}))
            return 1
        time.sleep(0.25)
    value = json.loads(reply.read_text())
    if 'job' in value:
        response = value.get('response') or {}
        assessment = value.get('assessment') or response.get('developer_view') or {}
        value = {k: value.get(k) for k in ('job', 'calls', 'questions_counted', 'closed', 'failure')} | {
            'question': value.get('question') or response.get('question'), 'disposition': assessment.get('disposition')}
    print(json.dumps(value, ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    run = commands.add_parser('serve')
    run.add_argument('--plan', type=Path, required=True)
    run.add_argument('--run-dir', type=Path, required=True)
    run.add_argument('--approval', type=Path, required=True)
    operate = commands.add_parser('control')
    operate.add_argument('--run-dir', type=Path, required=True)
    operate.add_argument('action', choices=ACTIONS)
    operate.add_argument('body', nargs='?', default='{}')
    args = parser.parse_args(argv)
    if args.command == 'serve':
        serve(args)
        return 0
    return control(args)


if __name__ == '__main__':
    raise SystemExit(main())
