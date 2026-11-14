const $ = (id) => document.getElementById(id);
const STORE = 'meta-vibe-coding.session.v1';
let state = null;
let brief = null;
let currentRequest = null;
let pending = false;
let previousResult = null;
let configured = false;
let lastProvisional = false;
let requestSeconds = 300;
let ideaLimit = 7;
let serverCallsLeft = null;
// A submission the server has not acknowledged. The server owns every state change,
// so the page keeps the owner's input here and resends it unchanged on Retry.
let unsent = null;
let failure = null;

function save() {
  // This browser only; cleared by "New idea". Storage can be unavailable, and the page works without it.
  try {
    if (state) localStorage.setItem(STORE, JSON.stringify({state, previousResult, unsent, failure}));
    else localStorage.removeItem(STORE);
  } catch (error) { /* private window or blocked storage */ }
}
function restore() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE) || 'null');
    if (!saved?.state) return;
    ({state, previousResult = null, unsent = null, failure = null} = saved);
    if (unsent && !failure) failure = {message: 'The page was reloaded before a result arrived.',
      next_action: 'Press Retry to send your input again.', retry: true};
  } catch (error) { state = null; }
}
async function api(path, data) {
  const response = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'The request failed. Your answers are still on this page.');
  return result;
}
function status(text, kind = '') { $('status').textContent = text; $('status').className = kind; }
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
function showFailure() {
  $('retry').hidden = !failure || failure.retry === false;
  $('submitted').hidden = true;
  if (!failure) return;
  status(`Stopped, not running. ${failure.message} ${failure.next_action || ''}`.trim(), 'stopped');
  const waiting = state && state.turns.length > state.assessed_turn_count ? state.turns[state.turns.length - 1].text : null;
  const text = unsent?.answer ?? waiting;
  if (text) {
    $('submitted').hidden = false;
    $('submitted').textContent = `Your last input is kept and will be used on the next attempt: “${text}”`;
  }
}
function showUsage(usage = null) {
  if (!state) { $('usage').textContent = ''; return; }
  const parts = usage ? [usage.agent, usage.model || 'model not reported', `${usage.elapsed_seconds.toFixed(1)}s`] : [];
  parts.push(`Assessment ${state.agent_calls} of ${ideaLimit} for this idea`);
  if (serverCallsLeft !== null) parts.push(`${serverCallsLeft} agent call${serverCallsLeft === 1 ? '' : 's'} left on this server`);
  $('usage').textContent = parts.join(' · ');
}
async function render() {
  $('workspace').hidden = !state;
  $('entry').hidden = !!state;
  if (!state) return;
  $('original').textContent = state.raw_intent;
  // A result is current only when the server assessed everything the owner has sent.
  const current = !!state.assessment && !unsent;
  const viewState = state.assessment ? state : previousResult;
  const assessment = viewState?.assessment;
  $('result').hidden = !assessment;
  $('clarification').hidden = true;
  $('provisional').hidden = true;
  brief = null;
  $('brief').textContent = '';
  $('owner').replaceChildren();
  if (assessment) {
    $('disposition').textContent = current ? assessment.disposition.replaceAll('_', ' ') : 'Outdated · awaiting a new result';
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
    const review = viewState.review;
    if (review) {
      section('Check these: the agent\'s updates that were not accepted as given', review.downgrades);
      section('Changed since the last result: removed or reworded', review.removed_advice);
      section('Changed since the last result: added', review.added_advice);
    }
    const question = [...state.questions].reverse().find((q) => !q.answer_turn_id && !q.retired);
    if (question && current) {
      $('clarification').hidden = false;
      $('question').textContent = question.text;
      $('why').textContent = `Why this matters: ${question.decision}`;
      $('unknown').disabled = !['unknown', 'assumed'].includes(state.facts[question.topic]?.status);
      if ($('unknown').disabled) $('why').textContent += ' This question needs reassessment. Use the correction box or request a provisional result.';
    }
    $('provisional').hidden = !current || (!question && assessment.disposition !== 'needs_answer');
    if (current && assessment.disposition !== 'needs_answer') {
      const snapshot = state;
      try {
        const exported = await api('/api/export', snapshot);
        if (state !== snapshot || pending) return;
        brief = exported;
        $('brief').textContent = JSON.stringify(brief, null, 2);
      } catch (error) { if (state === snapshot && !pending) status(error.message, 'stopped'); }
    } else $('brief').textContent = current ? JSON.stringify(state, null, 2) : 'Outdated result. Export is disabled until the current input is assessed.';
  }
  $('download').disabled = pending || !brief;
}
async function advance(answer = null, questionId = null, provisional = false, declaresUnknown = false) {
  if (!state || pending) return;
  if (declaresUnknown) {
    const question = state.questions.find((q) => q.id === questionId);
    if (!['unknown', 'assumed'].includes(state.facts[question?.topic]?.status)) {
      status('This question no longer matches an unresolved detail. Use the correction box instead.', 'stopped');
      return;
    }
  }
  lastProvisional = provisional;
  const requestId = crypto.randomUUID();
  currentRequest = requestId;
  const payload = {state, request_id: requestId, answer, question_id: questionId, provisional,
    declares_unknown: declaresUnknown};
  if (state.assessment) previousResult = structuredClone(state);
  unsent = {answer, questionId, provisional, declaresUnknown};
  failure = null;
  save();
  brief = null;
  $('result').hidden = !previousResult;
  if (previousResult) $('disposition').textContent = 'Outdated · updating';
  $('clarification').hidden = true;
  $('retry').hidden = true;
  $('submitted').hidden = true;
  setPending(true);
  status(`Running: the agent is considering the goal, consequences, and simplest useful option. This can take up to ${Math.ceil(requestSeconds / 60)} minutes.`, 'running');
  try {
    const result = await api('/api/advance', payload);
    if (currentRequest !== requestId || result.request_id !== requestId) return;
    state = result.state;
    unsent = null;
    failure = result.error;
    if (result.server_calls_left !== undefined) serverCallsLeft = result.server_calls_left;
    setPending(false);
    if (!failure) status('Finished. Check the interpretation and any open decisions.', 'done');
    showFailure();
    showUsage(result.usage);
    save();
    await render();
  } catch (error) {
    if (currentRequest !== requestId) return;
    // No acknowledgement: the state is unchanged and `unsent` still holds the input.
    failure = {message: error.message, next_action: 'Press Retry to send your input again.', retry: true};
    setPending(false);
    showFailure();
    save();
    await render();
  }
}
function retry() {
  if (unsent) return advance(unsent.answer, unsent.questionId, unsent.provisional, unsent.declaresUnknown);
  return advance(null, null, lastProvisional);
}
$('idea-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  if (pending || !configured) return;
  const startId = crypto.randomUUID(); currentRequest = startId; setPending(true);
  try {
    const started = await api('/api/start', {idea: $('idea').value.trim()});
    if (currentRequest !== startId) return;
    state = started; previousResult = null; unsent = null; failure = null; setPending(false); await render(); await advance();
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
  if (question) await advance("I don't know.", question.id, false, true);
});
$('provisional').addEventListener('click', () => advance(null, null, true));
$('retry').addEventListener('click', () => retry());
$('correction-form').addEventListener('submit', async (event) => {
  event.preventDefault(); const value = $('correction').value.trim();
  if (!value) return; $('correction').value = ''; await advance(value);
});
$('reset').addEventListener('click', () => {
  if (!confirm('Start a new idea? This clears the current session from the page.')) return;
  currentRequest = null; state = null; previousResult = null; brief = null; unsent = null; failure = null; setPending(false);
  lastProvisional = false; save();
  for (const id of ['idea', 'answer', 'correction']) $(id).value = '';
  for (const id of ['original', 'owner', 'brief', 'question', 'why', 'usage', 'disposition']) $(id).textContent = '';
  $('retry').hidden = true; $('submitted').hidden = true; status(''); render();
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
  ideaLimit = config.limits?.idea_assessments || 7;
  configured = config.enabled === true;
  $('start').disabled = pending || !configured;
  if (!configured) status('The coding agent is not connected yet. Configure it before exploring an idea.');
  restore();
  if (state) { showFailure(); showUsage(); render(); }
}).catch(() => { $('agent').textContent = 'Agent unavailable'; $('start').disabled = true; });
