// Deterministic browser-controller checks with DOM/HTTP doubles, not model evaluations.
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const {test} = require('node:test');
const vm = require('node:vm');
const {webcrypto} = require('node:crypto');

const staticDir = join(__dirname, '../src/meta_vibe_coding/static');
const script = readFileSync(join(staticDir, 'app.js'), 'utf8');
const ids = [...readFileSync(join(staticDir, 'index.html'), 'utf8').matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);

class Element {
  constructor() {
    this.value = '';
    this.hidden = false;
    this.disabled = false;
    this.children = [];
    this.handlers = new Map();
    this.text = '';
  }
  set textContent(value) { this.text = value; this.children = []; }
  get textContent() { return this.text + this.children.map((child) => child.textContent).join(' '); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.text = ''; this.children = children; }
  addEventListener(type, handler) { this.handlers.set(type, handler); }
  async fire(type) {
    if (type === 'click' && this.disabled) return false;
    await this.handlers.get(type)?.({preventDefault() {}});
    return true;
  }
}

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return {promise, resolve, reject};
}

const settle = () => new Promise((resolve) => setImmediate(resolve));
const response = (body, ok = true) => ({ok, json: async () => structuredClone(body)});

function assessed(payload, summary, question = null) {
  const state = structuredClone(payload.state);
  state.agent_calls += 1;
  state.revision += 1;
  if (payload.answer !== null) {
    const id = `t${state.turns.length + 1}`;
    state.turns.push({id, text: payload.answer});
    state.revision += 1;
    if (payload.question_id) state.questions.find((q) => q.id === payload.question_id).answer_turn_id = id;
    if (payload.declares_unknown) {
      const key = state.questions.find((q) => q.id === payload.question_id).topic;
      state.facts[key] = {value: null, status: 'unknown', source_turn_ids: [id], reason: 'The owner does not know yet.'};
      state.owner_unknowns = {...state.owner_unknowns, [key]: {source_turn_id: id, quote: payload.answer}};
    }
  }
  state.facts.goal = {value: state.raw_intent, status: 'confirmed', source_turn_ids: ['t0'], reason: ''};
  for (const prior of state.questions) if (!prior.answer_turn_id) prior.retired = true;
  state.assessment = {based_on_revision: state.revision,
    disposition: question ? 'provisional' : 'ready',
    risk: {level: 'unknown', reasons: ['Fictional test-double result.']}, hidden_requirements: [],
    recommendation: {kind: 'local_utility', summary, rationale: ['Fictional rationale.'],
      alternatives: [], owner_responsibilities: ['Check the fictional result.']},
    acceptance_criteria: ['Fictional acceptance check.'], open_questions: [], limitations: ['Test double.']};
  if (question) {
    state.facts.usage ??= {value: null, status: 'unknown', source_turn_ids: []};
    state.questions.push({id: `q${state.questions.length + 1}`, topic: 'usage', text: question,
      decision: 'Changes the fictional recommendation.', answer_turn_id: null, retired: false});
  }
  state.assessed_turn_count = state.turns.length;
  state.previous_assessment = null;
  return {request_id: payload.request_id, state,
    usage: {agent: 'test-double', model: 'fictional', elapsed_seconds: 0.01}, error: null};
}

function failed(payload) {
  const state = structuredClone(payload.state);
  state.previous_assessment = state.assessment ?? state.previous_assessment ?? null;
  state.assessment = null;
  state.agent_calls += 1;
  return {request_id: payload.request_id, state, usage: null,
    error: {code: 'timeout', message: 'Fictional test timeout.'}};
}

async function page(configOverrides = {}, initialTurns = []) {
  const elements = new Map(ids.map((id) => [id, new Element()]));
  const advances = [];
  const exports = [];
  const calls = [];
  const downloads = [];
  const fetch = async (path, options) => {
    if (path === '/api/config') return response({agent: 'test-double', requested_model: 'fictional', enabled: true,
      destination: 'test-double', data_notice: 'Fictional coding agent.', allowance_notice: 'No agent inference.', ...configOverrides});
    const body = JSON.parse(options.body);
    calls.push({path, body});
    if (path === '/api/start') return response({schema_version: 1, revision: 1, raw_intent: body.idea,
      turns: initialTurns, facts: {}, questions: [], assessment: null, agent_calls: 0, started_at: 1, assessed_turn_count: 0});
    if (path === '/api/advance') {
      assert.ok(advances.length, 'Every inference response must be an explicit test double');
      return response(await advances.shift()(body));
    }
    if (path === '/api/export') {
      if (exports.length) return exports.shift()(body);
      return response({revision: body.revision, raw_intent: body.raw_intent,
        recommendation: body.assessment.recommendation.summary});
    }
    throw new Error(`Unexpected path: ${path}`);
  };
  const context = {structuredClone, crypto: webcrypto, fetch, confirm: () => true, Blob,
    setTimeout, URL: {createObjectURL: (blob) => { downloads.push(blob); return 'blob:test'; }, revokeObjectURL() {}},
    document: {getElementById: (id) => elements.get(id), createElement: () => {
      const element = new Element(); element.click = () => {}; return element;
    }}};
  vm.runInNewContext(script, context, {filename: 'app.js'});
  await settle();
  const el = (id) => elements.get(id);
  return {el, advances, exports, calls, downloads,
    async start(idea) { el('idea').value = idea; await el('idea-form').fire('submit'); },
    async correct(text) { el('correction').value = text; await el('correction-form').fire('submit'); }};
}

for (const networkFailure of [false, true]) {
  test(`Retry preserves provisional intent after ${networkFailure ? 'network rejection' : 'agent timeout'}`, async () => {
    const ui = await page();
    ui.advances.push((body) => assessed(body, 'Initial conditional result.', 'Where is it used?'));
    await ui.start('Fictional idea');
    let previous;
    ui.advances.push((body) => {
      previous = body.state.assessment;
      if (networkFailure) throw new Error('Fictional connection failure.');
      return failed(body);
    });
    await ui.el('provisional').fire('click');
    assert.equal(ui.el('retry').hidden, false);
    assert.match(ui.el('disposition').textContent, /Outdated/);
    assert.equal(ui.el('download').disabled, true);
    ui.advances.push((body) => {
      assert.equal(body.state.assessment, null);
      assert.deepEqual(body.state.previous_assessment, previous);
      assert.equal(body.state.previous_assessment.based_on_revision, body.state.revision,
        'No-answer provisional requests may retain equal snapshot revisions');
      return assessed(body, 'Retried conditional result.');
    });
    await ui.el('retry').fire('click');
    const requests = ui.calls.filter((call) => call.path === '/api/advance');
    assert.deepEqual(requests.map((call) => call.body.provisional), [false, true, true]);
    assert.equal(requests[2].body.answer, null, 'Retry must not duplicate a submitted reply');
    assert.match(ui.el('owner').textContent, /Retried conditional result/);
  });
}

test('An unknown declaration survives a lost response and retry without becoming false', async () => {
  const ui = await page();
  ui.advances.push((body) => assessed(body, 'Initial conditional result.', 'Who owns updates?'));
  await ui.start('Fictional idea');
  ui.advances.push(() => { throw new Error('Fictional lost response.'); });
  await ui.el('unknown').fire('click');
  assert.equal(ui.el('retry').hidden, false);
  ui.advances.push((body) => {
    assert.equal(body.answer, null);
    assert.equal(body.declares_unknown, false);
    assert.equal(body.state.turns.length, 1);
    assert.equal(body.state.questions[0].answer_turn_id, 't1');
    assert.equal(body.state.facts.usage.value, null);
    assert.equal(body.state.facts.usage.status, 'unknown');
    assert.deepEqual(body.state.owner_unknowns.usage, {source_turn_id: 't1', quote: "I don't know."});
    return assessed(body, 'Conditional result with uncertainty.');
  });
  await ui.el('retry').fire('click');
  const calls = ui.calls.filter((call) => call.path === '/api/advance');
  assert.equal(calls[1].body.declares_unknown, true);
  assert.match(ui.el('owner').textContent, /usage: unknown/);
});

test('A suppressed unknown question still leaves the provisional action reachable', async () => {
  const ui = await page();
  ui.advances.push((body) => assessed(body, 'Initial question.', 'Who owns updates?'));
  await ui.start('Fictional idea');
  ui.advances.push((body) => {
    const result = assessed(body, 'A decision is still needed.');
    result.state.assessment.disposition = 'needs_answer';
    return result;
  });
  await ui.el('unknown').fire('click');
  assert.equal(ui.el('clarification').hidden, true);
  assert.equal(ui.el('provisional').hidden, false);
  assert.equal(ui.el('provisional').disabled, false);
  assert.equal(ui.el('download').disabled, true);
  ui.advances.push((body) => {
    assert.equal(body.provisional, true);
    const result = assessed(body, 'A conditional option with the unknown preserved.');
    result.state.assessment.disposition = 'provisional';
    return result;
  });
  await ui.el('provisional').fire('click');
  assert.equal(ui.el('provisional').hidden, true);
  assert.equal(ui.el('download').disabled, false);
});

test('A lost reply response retains owner evidence once when retrying', async () => {
  const ui = await page();
  ui.advances.push((body) => assessed(body, 'Initial result.', 'Where will you use it?'));
  await ui.start('Fictional idea');
  ui.el('answer').value = 'On my phone and laptop.';
  let previous;
  ui.advances.push((body) => { previous = body.state.assessment; throw new Error('Fictional lost response.'); });
  await ui.el('reply-form').fire('submit');
  assert.equal(ui.el('retry').hidden, false);
  ui.advances.push((body) => {
    assert.equal(body.state.assessment, null);
    assert.deepEqual(body.state.previous_assessment, previous);
    assert.ok(body.state.previous_assessment.based_on_revision < body.state.revision);
    return assessed(body, 'Current result.');
  });
  await ui.el('retry').fire('click');
  const requests = ui.calls.filter((call) => call.path === '/api/advance');
  const retry = requests[2].body;
  assert.equal(retry.answer, null);
  assert.equal(retry.state.turns.length, 1);
  assert.equal(retry.state.turns[0].text, 'On my phone and laptop.');
  assert.equal(retry.state.questions[0].answer_turn_id, retry.state.turns[0].id);
  assert.notEqual(retry.request_id, requests[1].body.request_id);
  assert.equal(ui.el('download').disabled, false);
});

test('New idea clears drafts, prior outputs, usage, and export', async () => {
  const ui = await page();
  ui.advances.push((body) => assessed(body, 'Old recommendation.'));
  await ui.start('Old fictional idea');
  assert.equal(ui.el('download').disabled, false);
  assert.match(ui.el('usage').textContent, /test-double/);
  ui.el('answer').value = 'Old answer draft';
  ui.el('correction').value = 'Old correction draft';
  await ui.el('reset').fire('click');
  for (const id of ['idea', 'answer', 'correction']) assert.equal(ui.el(id).value, '', id);
  for (const id of ['original', 'owner', 'brief', 'question', 'why', 'usage', 'disposition', 'status']) {
    assert.equal(ui.el(id).textContent, '', id);
  }
  assert.equal(ui.el('workspace').hidden, true);
  assert.equal(ui.el('entry').hidden, false);
  assert.equal(ui.el('download').disabled, true);
  ui.advances.push((body) => assessed(body, 'New conditional result.', 'New question?'));
  await ui.start('New fictional idea');
  assert.equal(ui.el('answer').value, '');
  assert.equal(ui.el('correction').value, '');
  assert.equal(ui.el('original').textContent, 'New fictional idea');
  assert.doesNotMatch(ui.el('owner').textContent, /Old recommendation/);
});

test('A late agent response cannot replace a new idea', async () => {
  const ui = await page();
  const oldReply = deferred();
  let oldPayload;
  ui.advances.push((body) => { oldPayload = body; return oldReply.promise; });
  const oldStart = ui.start('Old fictional idea');
  await settle();
  assert.ok(oldPayload);
  await ui.el('reset').fire('click');
  ui.advances.push((body) => assessed(body, 'Current recommendation.'));
  await ui.start('Current fictional idea');
  oldReply.resolve(assessed(oldPayload, 'Obsolete recommendation.'));
  await oldStart;
  assert.equal(ui.el('original').textContent, 'Current fictional idea');
  assert.match(ui.el('owner').textContent, /Current recommendation/);
  assert.doesNotMatch(ui.el('owner').textContent, /Obsolete recommendation/);
  assert.match(ui.el('brief').textContent, /Current fictional idea/);
  assert.equal(ui.el('download').disabled, false);
});

test('Export stays disabled while revising, and late old exports are ignored', async () => {
  const ui = await page();
  const oldExport = deferred();
  ui.exports.push(() => oldExport.promise);
  ui.advances.push((body) => assessed(body, 'Original recommendation.'));
  const first = ui.start('Fictional idea');
  await settle();
  const nextReply = deferred();
  let correctionPayload;
  ui.advances.push((body) => { correctionPayload = body; return nextReply.promise; });
  const revision = ui.correct('Use filename dates instead.');
  await settle();
  assert.ok(correctionPayload);
  assert.equal(ui.el('download').disabled, true);
  assert.match(ui.el('disposition').textContent, /Outdated/);
  assert.equal(await ui.el('download').fire('click'), false);
  assert.equal(ui.downloads.length, 0);
  oldExport.resolve(response({raw_intent: 'Obsolete export', revision: 0}));
  await first;
  assert.equal(ui.el('download').disabled, true);
  assert.doesNotMatch(ui.el('brief').textContent, /Obsolete export/);
  nextReply.resolve(assessed(correctionPayload, 'Corrected recommendation.'));
  await revision;
  assert.equal(ui.el('download').disabled, false);
  assert.match(ui.el('brief').textContent, /Corrected recommendation/);
});

test('A late export failure cannot overwrite the current idea status', async () => {
  const ui = await page();
  const oldExport = deferred();
  ui.exports.push(() => oldExport.promise);
  ui.advances.push((body) => assessed(body, 'Old recommendation.'));
  const first = ui.start('Old fictional idea');
  await settle();
  await ui.el('reset').fire('click');
  ui.advances.push((body) => assessed(body, 'Current recommendation.'));
  await ui.start('Current fictional idea');
  const currentStatus = ui.el('status').textContent;
  oldExport.resolve(response({error: 'Obsolete export failure.'}, false));
  await first;
  assert.equal(ui.el('status').textContent, currentStatus);
  assert.match(ui.el('owner').textContent, /Current recommendation/);
  assert.equal(ui.el('download').disabled, false);
});

// A configured page must still respect the explicit execution gate.
test('Disabled agent keeps exploration unavailable and sends no idea', async () => {
  const ui = await page({enabled: false});
  assert.equal(ui.el('start').disabled, true);
  await ui.start('Fictional idea');
  assert.equal(ui.calls.length, 0);
  assert.match(ui.el('status').textContent, /not connected/);
});

test('A lost correction retains a unique source ID with nonsequential history', async () => {
  const ui = await page({}, [{id: 't2', text: 'Earlier owner reply.'}]);
  ui.advances.push((body) => assessed(body, 'Original result.'));
  await ui.start('Fictional idea');
  ui.advances.push(() => { throw new Error('Fictional lost response.'); });
  await ui.correct('Only the members should have access.');
  ui.advances.push((body) => assessed(body, 'Revised result.'));
  await ui.el('retry').fire('click');
  const retry = ui.calls.filter((call) => call.path === '/api/advance')[2].body;
  assert.deepEqual(retry.state.turns.map((turn) => turn.id), ['t2', 't3']);
  assert.equal(retry.state.turns[1].text, 'Only the members should have access.');
});

test('Unknown goals and inapplicable facts use readable owner-facing text', async () => {
  const ui = await page();
  ui.advances.push((body) => {
    const reply = assessed(body, 'Clarify the goal first.', 'What would you like to accomplish?');
    reply.state.facts.goal = {value: null, status: 'unknown', source_turn_ids: []};
    reply.state.facts['access.accounts'] = {value: null, status: 'not_applicable', source_turn_ids: [], reason: 'No application is selected.'};
    return reply;
  });
  await ui.start('I need something useful.');
  assert.match(ui.el('owner').textContent, /Your goal still needs clarification/);
  assert.match(ui.el('owner').textContent, /not applicable/);
  assert.doesNotMatch(ui.el('owner').textContent, /null \(unknown\)|not_applicable/);
});

for (const knownStatus of ['confirmed', 'not_applicable']) {
  test(`A legacy ${knownStatus} question target cannot be erased by the unknown action`, async () => {
    const ui = await page();
    ui.advances.push((body) => {
      // An older server could return a question bound to this different, settled property.
      const reply = assessed(body, 'Legacy result.', 'Who approves requests?');
      reply.state.facts.usage = {value: knownStatus === 'confirmed' ? true : null,
        status: knownStatus, source_turn_ids: ['t0'], reason: 'Scripted legacy state.'};
      return reply;
    });
    await ui.start('Fictional editorial requests.');
    assert.equal(ui.el('unknown').disabled, true);
    assert.match(ui.el('why').textContent, /needs reassessment/);
    const count = ui.calls.length;
    // Check the action boundary too, even if an old page/event bypasses disabled presentation.
    ui.el('unknown').disabled = false;
    await ui.el('unknown').fire('click');
    assert.equal(ui.calls.length, count, 'No HTTP request or optimistic edit is allowed');
    assert.match(ui.el('status').textContent, /correction box/);
    assert.equal(ui.el('download').disabled, false, 'The unchanged legacy snapshot stays available');
    ui.advances.push((body) => {
      assert.equal(body.state.facts.usage.status, knownStatus);
      assert.equal(body.state.turns.length, 0);
      assert.equal(body.state.agent_calls, 1);
      assert.equal(body.state.assessment.recommendation.summary, 'Legacy result.');
      assert.equal(Object.keys(body.state.owner_unknowns || {}).length, 0);
      return assessed(body, 'Fresh provisional result.');
    });
    await ui.el('provisional').fire('click');
    assert.equal(ui.el('download').disabled, false);
    assert.match(ui.el('owner').textContent, /Fresh provisional result/);
  });
}
