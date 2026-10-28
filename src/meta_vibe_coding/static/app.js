const $ = (id) => document.getElementById(id);
let state = null;
let brief = null;
let currentRequest = null;
let pending = false;
let previousResult = null;
let configured = false;
let lastProvisional = false;
let requestSeconds = 300;

async function api(path, data) {
  const response = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'The request failed. Your answers are still on this page.');
  return result;
}
function status(text) { $('status').textContent = text; }
function factLabel(key) {
  const labels = {'goal': 'Your goal', 'users.primary': 'Who will use it',
    'users.secondary': 'Other people using it', 'usage.environment': 'Where it will be used',
    'data.persistent': 'Whether information must be saved', 'data.personal': 'Personal information',
    'data.sensitive': 'Sensitive information', 'access.public': 'Who can access it',
    'access.accounts': 'Whether people need accounts', 'content.updates': 'How content is updated',
    'operations.budget': 'Your budget'};
  return labels[key] || key.replaceAll('.', ' ').replaceAll('_', ' ');
}
function section(title, items) {
  if (!items.length) return;
  const heading = document.createElement('h3'); heading.textContent = title;
  const list = document.createElement('ul');
  for (const value of items) { const item = document.createElement('li'); item.textContent = value; list.append(item); }
  $('owner').append(heading, list);
}
function setPending(value) {
  pending = value;
  for (const id of ['reply', 'unknown', 'provisional', 'revise', 'retry', 'start']) $(id).disabled = value;
  $('start').disabled = value || !configured;
  $('download').disabled = value || !brief;
}
async function render() {
  $('workspace').hidden = !state;
  $('entry').hidden = !!state;
  if (!state) return;
  $('original').textContent = state.raw_intent;
  const viewState = state.assessment ? state : previousResult;
  const assessment = viewState?.assessment;
  $('result').hidden = !assessment;
  $('clarification').hidden = true;
  brief = null;
  $('brief').textContent = '';
  $('owner').replaceChildren();
  if (assessment) {
    $('disposition').textContent = state.assessment ? assessment.disposition.replaceAll('_', ' ') : 'Outdated · awaiting a new result';
    const goal = viewState.facts.goal;
    section('Understood goal', [typeof goal?.value === 'string' && goal.value.trim()
      ? `${goal.value} (${goal.status})` : 'Your goal still needs clarification.']);
    section('Recommended approach', [assessment.recommendation.summary, ...assessment.recommendation.rationale]);
    section('Alternatives', assessment.recommendation.alternatives);
    section('Risk and hidden requirements', [`Risk: ${assessment.risk.level}`, ...assessment.risk.reasons,
      ...assessment.hidden_requirements.map((r) => `${r.text} — ${r.reason}`)]);
    section('Your responsibilities', assessment.recommendation.owner_responsibilities);
    section('Assumptions and unknowns', Object.entries(viewState.facts).filter(([, f]) => f.status !== 'confirmed')
      .map(([key, f]) => `${factLabel(key)}: ${f.status.replaceAll('_', ' ')}${f.value !== null ? ` (${JSON.stringify(f.value)})` : ''}${f.reason ? ` — ${f.reason}` : ''}`));
    section('Open decisions and limits', [...assessment.open_questions.map((q) => `${q.text} — ${q.reason}`), ...assessment.limitations]);
    section('What a solution should satisfy', assessment.acceptance_criteria);
    const question = [...state.questions].reverse().find((q) => !q.answer_turn_id && !q.retired);
    if (question && state.assessment) {
      $('clarification').hidden = false;
      $('question').textContent = question.text;
      $('why').textContent = `Why this matters: ${question.decision}`;
    }
    if (state.assessment && assessment.disposition !== 'needs_answer') {
      const snapshot = state;
      try {
        const exported = await api('/api/export', snapshot);
        if (state !== snapshot || pending) return;
        brief = exported;
        $('brief').textContent = JSON.stringify(brief, null, 2);
      } catch (error) { if (state === snapshot && !pending) status(error.message); }
    } else $('brief').textContent = state.assessment ? JSON.stringify(state, null, 2) : 'Outdated result. Export is disabled until the current input is assessed.';
  }
  $('download').disabled = pending || !brief;
}
async function advance(answer = null, questionId = null, provisional = false) {
  if (!state || pending) return;
  lastProvisional = provisional;
  const requestId = crypto.randomUUID();
  currentRequest = requestId;
  const payload = {state, request_id: requestId, answer, question_id: questionId, provisional};
  if (state.assessment) previousResult = structuredClone(state);
  // Keep a local copy of the submitted reply even if the HTTP request is lost.
  if (answer !== null) {
    let next = state.turns.length + 1;
    const existing = new Set(state.turns.map((turn) => turn.id));
    while (existing.has(`t${next}`)) next += 1;
    const turnId = `t${next}`;
    state = structuredClone(state);
    state.turns.push({id: turnId, text: answer});
    if (questionId) state.questions.find((q) => q.id === questionId).answer_turn_id = turnId;
    state.revision += 1;
  }
  state = {...state, assessment: null, agent_calls: Math.min(7, state.agent_calls + 1)};
  brief = null;
  $('result').hidden = !previousResult;
  if (previousResult) $('disposition').textContent = 'Outdated · updating';
  $('clarification').hidden = true;
  $('retry').hidden = true;
  setPending(true);
  status(`Considering the goal, consequences, and simplest useful option… This can take up to ${Math.ceil(requestSeconds / 60)} minutes.`);
  try {
    const result = await api('/api/advance', payload);
    if (currentRequest !== requestId || result.request_id !== requestId) return;
    state = result.state;
    setPending(false);
    status(result.error ? result.error.message : 'Updated. Check the interpretation and any open decisions.');
    $('retry').hidden = !result.error;
    $('usage').textContent = result.usage ? `${result.usage.agent} · ${result.usage.model || 'model not reported'} · ${result.usage.elapsed_seconds.toFixed(1)}s · agent request ${state.agent_calls}/7` : '';
    await render();
  } catch (error) {
    if (currentRequest !== requestId) return;
    setPending(false);
    status(error.message);
    $('retry').hidden = false;
    await render();
  }
}
$('idea-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  if (pending || !configured) return;
  const startId = crypto.randomUUID(); currentRequest = startId; setPending(true);
  try {
    const started = await api('/api/start', {idea: $('idea').value.trim()});
    if (currentRequest !== startId) return;
    state = started; previousResult = null; setPending(false); await render(); await advance();
  } catch (error) { if (currentRequest === startId) { setPending(false); status(error.message); } }
});
$('reply-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = [...state.questions].reverse().find((q) => !q.answer_turn_id && !q.retired);
  const value = $('answer').value.trim();
  if (!value || !question) return;
  $('answer').value = '';
  await advance(value, question.id);
});
$('unknown').addEventListener('click', async () => {
  const question = [...state.questions].reverse().find((q) => !q.answer_turn_id && !q.retired);
  if (question) await advance("I don't know.", question.id);
});
$('provisional').addEventListener('click', () => advance(null, null, true));
$('retry').addEventListener('click', () => advance(null, null, lastProvisional));
$('correction-form').addEventListener('submit', async (event) => {
  event.preventDefault(); const value = $('correction').value.trim();
  if (!value) return; $('correction').value = ''; await advance(value);
});
$('reset').addEventListener('click', () => {
  if (!confirm('Start a new idea? This clears the current session from the page.')) return;
  currentRequest = null; state = null; previousResult = null; brief = null; setPending(false);
  lastProvisional = false;
  for (const id of ['idea', 'answer', 'correction']) $(id).value = '';
  for (const id of ['original', 'owner', 'brief', 'question', 'why', 'usage', 'disposition']) $(id).textContent = '';
  $('retry').hidden = true; status(''); render();
});
$('download').addEventListener('click', () => {
  if (!brief || pending) return;
  const url = URL.createObjectURL(new Blob([JSON.stringify(brief, null, 2)], {type: 'application/json'}));
  const link = document.createElement('a'); link.href = url; link.download = 'engineering-brief.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
fetch('/api/config').then((r) => { if (!r.ok) throw new Error('Backend unavailable'); return r.json(); }).then((config) => {
  $('agent').textContent = `${config.agent} · ${config.requested_model || 'model selected by the agent'}`;
  $('data-notice').textContent = config.data_notice;
  $('allowance-notice').textContent = config.allowance_notice;
  requestSeconds = config.limits?.request_seconds || 300;
  configured = config.enabled === true;
  $('start').disabled = pending || !configured;
  if (!configured) status('The coding agent is not connected yet. Configure it before exploring an idea.');
}).catch(() => { $('agent').textContent = 'Agent unavailable'; $('start').disabled = true; });
