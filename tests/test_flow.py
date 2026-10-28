"""Deterministic contract checks using explicit test doubles, not product evaluations."""

import asyncio
import json
import time

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from meta_vibe_coding.app import create_app
from meta_vibe_coding.core import FlowError, adopt, export_brief, prepare, reserve_call
from meta_vibe_coding.models import AdvanceRequest, Candidate, Fact, Question, State, Turn, Usage


def result(state, *, question=None, facts=None, disposition="ready"):
    """Fictional response from a agent test double, never an evaluation result."""
    return Candidate.model_validate({
        "facts": facts if facts is not None else {
            "goal": {"value": state.raw_intent, "status": "confirmed", "source_turn_ids": ["t0"]}},
        "assessment": {"based_on_revision": state.revision, "disposition": disposition,
            "risk": {"level": "unknown", "reasons": ["A fictional test result, not a risk review."]},
            "hidden_requirements": [],
            "recommendation": {"kind": "local_utility", "summary": "Consider a local utility.",
                "rationale": ["Files stay on the laptop."], "alternatives": ["Existing utility"],
                "owner_responsibilities": ["Preview changes and retain originals."]},
            "acceptance_criteria": ["A dry run shows proposed names."], "open_questions": [],
            "limitations": ["Test-double output."]}, "question": question})


def test_false_unknown_empty_and_strict_types():
    for value, status in [(False, "confirmed"), ([], "confirmed"), (None, "unknown")]:
        fact = Fact(value=value, status=status, source_turn_ids=["t0"])
        assert fact.value == value and type(fact.value) is type(value)
    for data in [{"value": False, "status": "unknown", "source_turn_ids": []},
                 {"value": None, "status": "confirmed", "source_turn_ids": ["t0"]},
                 {"value": "A guess", "status": "assumed", "source_turn_ids": []},
                 {"value": "Fact", "status": "confirmed", "source_turn_ids": []}]:
        with pytest.raises(ValidationError):
            Fact.model_validate(data)
    with pytest.raises(ValidationError):
        State.model_validate({"raw_intent": "Idea", "revision": "1"})


@pytest.mark.parametrize("mutation", ["source", "turn", "version", "revision", "blocking", "goal"])
def test_invalid_state_cannot_be_exported(mutation):
    state = adopt(State(raw_intent="Rename files"), result(State(raw_intent="Rename files")))
    data = state.model_dump()
    if mutation == "source": data["facts"]["goal"]["source_turn_ids"] = ["missing"]
    if mutation == "turn": data["turns"] = [{"id": "t0", "text": "Duplicate"}]
    if mutation == "version": data["schema_version"] = 2
    if mutation == "revision": data["assessment"]["based_on_revision"] -= 1
    if mutation == "blocking": data["assessment"]["open_questions"] = [{"topic": "data", "text": "Private?", "blocks_recommendation": True, "reason": "Changes fit"}]
    if mutation == "goal": data["facts"]["goal"].update(status="assumed", reason="Not confirmed")
    with pytest.raises(ValidationError): State.model_validate(data)


def test_correction_invalidates_export_and_requires_fresh_source():
    original = State(raw_intent="Rename photos by metadata date")
    state = adopt(original, result(original))
    revised = prepare(AdvanceRequest(state=state, request_id="r2", answer="Use filename dates instead."))
    assert revised.raw_intent == original.raw_intent
    assert revised.turns[-1].text == "Use filename dates instead."
    assert revised.assessment is None
    with pytest.raises(FlowError): export_brief(revised)
    bad = result(revised)
    bad.facts["goal"].value = "Rename by filename date"
    with pytest.raises(FlowError): adopt(revised, bad)
    bad.facts["goal"].source_turn_ids = ["t1"]
    updated = adopt(revised, bad)
    assert updated.revision > revised.revision
    assert updated.assessment.based_on_revision == updated.revision
    assert updated.turns[0].text == revised.turns[0].text


def test_cannot_drop_confirmed_fact_or_adopt_stale_assessment():
    base = State(raw_intent="Rename files")
    state = adopt(base, result(base))
    with pytest.raises(FlowError): adopt(state, result(state, facts={}))
    with pytest.raises(FlowError): adopt(state, result(base))


def test_unknown_answer_and_question_retirement():
    state = State(raw_intent="Inventory photos")
    question = {"topic": "data.sensitive", "text": "Do photos contain private details?", "decision": "Changes storage requirements"}
    state = adopt(state, result(state, question=question, disposition="provisional"))
    state = prepare(AdvanceRequest(state=state, request_id="r2", question_id="q1", answer="I don't know."))
    facts = {**state.facts, "data.sensitive": Fact(value=None, status="unknown", source_turn_ids=["t1"])}
    updated = adopt(state, result(state, facts=facts, disposition="provisional"))
    assert updated.facts["data.sensitive"].value is None
    assert updated.questions[0].answer_turn_id == "t1"
    with pytest.raises(FlowError): adopt(updated, result(updated, question=question, disposition="provisional"))
    pending = adopt(State(raw_intent="Files"), result(State(raw_intent="Files"), question=question, disposition="provisional"))
    final = adopt(pending, result(pending))
    assert final.questions[0].retired


def test_export_only_referenced_sources():
    state = State(raw_intent="Rename files", turns=[Turn(id="t1", text="Unreferenced private note")])
    state = adopt(state, result(state, disposition="provisional"))
    brief = export_brief(state)
    assert brief["disposition"] == "provisional"
    assert brief["sources"] == [{"id": "t0", "text": "Rename files"}]
    assert "Unreferenced private note" not in json.dumps(brief)
    assert "turns" not in brief and "agent_calls" not in brief


@pytest.mark.parametrize("state", [State(raw_intent="x", agent_calls=7), State(raw_intent="x", started_at=time.time()-1801)])
def test_session_limits(state):
    with pytest.raises(FlowError): reserve_call(state)


class FakeAgent:
    model = "explicit-test-double"
    def __init__(self, failure=False): self.failure = failure
    async def assess(self, state, provisional):
        if self.failure: raise FlowError("timeout", "Test timeout")
        return result(state), Usage(agent="test-double", model=self.model, elapsed_seconds=0.0)


def test_http_flow_and_failure_preserve_reply():
    for failure in [False, True]:
        with TestClient(create_app(FakeAgent(failure))) as client:
            state = client.post('/api/start', json={"idea": "Rename files"}).json()
            response = client.post('/api/advance', json={"state": state, "request_id": "r1", "answer": "Keep originals"}).json()
            assert response["request_id"] == "r1"
            assert response["state"]["turns"][0]["text"] == "Keep originals"
            assert response["state"]["agent_calls"] == 1
            if failure:
                assert response["error"]["code"] == "timeout"
                assert response["state"]["assessment"] is None
                assert client.post('/api/export', json=response["state"]).status_code == 409
            else:
                assert response["error"] is None
                assert client.post('/api/export', json=response["state"]).status_code == 200


def test_http_origin_host_and_invalid_state_do_not_echo_input():
    with TestClient(create_app(FakeAgent())) as client:
        assert client.post('/api/start', json={"idea": "private"}, headers={"Origin": "https://other.example"}).status_code == 403
        assert client.get('/api/config', headers={"Host": "attacker.example"}).status_code == 400
        response = client.post('/api/start', json={"idea": 123, "private": "do-not-echo"})
        assert response.status_code == 422
        assert "do-not-echo" not in response.text
        assert client.get('/').headers['cache-control'] == 'no-store'
        assert client.get('/app.js').status_code == 200


def test_bare_continue_does_not_confirm_assumptions():
    state = State(raw_intent="A tool", facts={"goal": Fact(value="Organize records", status="assumed", source_turn_ids=["t0"], reason="Inferred")})
    state = prepare(AdvanceRequest(state=state, request_id="next", answer="Continue."))
    candidate = result(state)
    candidate.facts["goal"] = Fact(value="Organize records", status="confirmed", source_turn_ids=["t1"])
    with pytest.raises(FlowError): adopt(state, candidate)


def test_ready_with_another_question_is_rejected():
    state = State(raw_intent="A tool")
    question = {"topic": "usage", "text": "Who uses it?", "decision": "Changes access"}
    with pytest.raises(FlowError): adopt(state, result(state, question=question))


def test_reassessment_cannot_rewrite_confirmed_fact_without_new_owner_input():
    base = State(raw_intent="Keep files local")
    state = adopt(base, result(base))
    candidate = result(state)
    candidate.facts["goal"].value = "Upload files to a server"
    with pytest.raises(FlowError): adopt(state, candidate)


@pytest.mark.parametrize("before,after", [(False, 0), ([False], [0]), (1, 1.0)])
def test_fact_type_change_requires_evidence_and_advances_revision(before, after):
    base = State(raw_intent="Keep records local")
    candidate = result(base)
    candidate.facts["data.example"] = Fact(value=before, status="confirmed", source_turn_ids=["t0"])
    state = adopt(base, candidate)
    changed = result(state, facts={**state.facts, "data.example": Fact(value=after, status="confirmed", source_turn_ids=["t0"])})
    with pytest.raises(FlowError): adopt(state, changed)
    revised = prepare(AdvanceRequest(state=state, request_id="type-change", answer="Use the revised value."))
    changed.assessment.based_on_revision = revised.revision
    changed.facts["data.example"].source_turn_ids = ["t1"]
    updated = adopt(revised, changed)
    assert updated.revision == revised.revision + 1
    assert type(updated.facts["data.example"].value) is type(after)


def test_question_can_reopen_only_with_new_owner_conflict_source():
    state = State(raw_intent="Publish event information")
    question = {"topic": "access.public", "text": "Who can see it?", "decision": "Changes sharing"}
    state = adopt(state, result(state, question=question, disposition="provisional"))
    state = prepare(AdvanceRequest(state=state, request_id="answer", question_id="q1", answer="Everyone can see it."))
    state = adopt(state, result(state, disposition="provisional"))
    repeated = {**question, "conflict_turn_id": "t1"}
    with pytest.raises(FlowError): adopt(state, result(state, question=repeated, disposition="provisional"))
    state = prepare(AdvanceRequest(state=state, request_id="correction", answer="Only part should be public; the linked content may be private."))
    repeated["conflict_turn_id"] = "t2"
    repeated["decision"] = "Your new mixed-access request conflicts with public-only sharing; clarify which content is private."
    updated = adopt(state, result(state, question=repeated, disposition="provisional"))
    assert updated.questions[-1].conflict_turn_id == "t2"
    assert updated.questions[-1].answer_turn_id is None
    with pytest.raises(FlowError):
        adopt(state, result(state, question={**repeated, "conflict_turn_id": "missing"}, disposition="provisional"))


@pytest.mark.parametrize("sources", [[], ["t0"]])
def test_retry_cannot_confirm_an_assumption_without_new_owner_input(sources):
    base = State(raw_intent="A tool for events")
    assumed = Fact(value="Organize events", status="assumed", source_turn_ids=sources, reason="Inferred goal")
    state = adopt(base, result(base, facts={"goal": assumed}, disposition="provisional"))
    retry = prepare(AdvanceRequest(state=state, request_id="retry"))
    confirmation = Fact(value="Organize events", status="confirmed", source_turn_ids=["t0"])
    with pytest.raises(FlowError): adopt(retry, result(retry, facts={"goal": confirmation}))
    answered = prepare(AdvanceRequest(state=state, request_id="answer", answer="Yes, I want to organize events."))
    # A failed request has no adopted assessment yet: retry may use the retained new reply.
    retry = prepare(AdvanceRequest(state=answered, request_id="retry-retained-reply"))
    confirmation.source_turn_ids = ["t1"]
    updated = adopt(retry, result(retry, facts={"goal": confirmation}))
    assert updated.assessed_turn_count == 1
    assert "assessed_turn_count" not in export_brief(updated)


def test_already_assessed_reply_cannot_reconfirm_or_rewrite_facts_on_retry():
    base = State(raw_intent="Organize events")
    state = prepare(AdvanceRequest(state=base, request_id="reply", answer="Use it on my phone."))
    assumed = Fact(value="One organizer", status="assumed", source_turn_ids=[], reason="Inferred usage")
    candidate = result(state)
    candidate.facts["users.primary"] = assumed
    state = adopt(state, candidate)
    retry = prepare(AdvanceRequest(state=state, request_id="retry"))
    candidate = result(retry, facts={**state.facts, "users.primary": Fact(value="One organizer", status="confirmed", source_turn_ids=["t1"])})
    with pytest.raises(FlowError): adopt(retry, candidate)
    candidate = result(retry, facts=state.facts.copy())
    candidate.facts["goal"] = Fact(value="Build a mobile app", status="confirmed", source_turn_ids=["t1"])
    with pytest.raises(FlowError): adopt(retry, candidate)


def test_retired_question_cannot_receive_a_late_answer():
    base = State(raw_intent="Organize events")
    question = {"topic": "usage", "text": "Who uses it?", "decision": "Changes access"}
    state = adopt(base, result(base, question=question, disposition="provisional"))
    state = adopt(state, result(state))
    assert state.questions[0].retired
    with pytest.raises(FlowError):
        prepare(AdvanceRequest(state=state, request_id="late", question_id="q1", answer="Three people"))


def test_valid_nonsequential_ids_do_not_collide_with_new_records():
    state = State(raw_intent="Organize events", turns=[Turn(id="t2", text="Phone access matters.")],
        questions=[Question(id="q2", topic="older", text="An older question?", decision="Changes access", retired=True)])
    state = prepare(AdvanceRequest(state=state, request_id="reply", answer="Only club members."))
    assert state.turns[-1].id == "t3"
    question = {"topic": "updates", "text": "How often are events updated?", "decision": "Changes owner workload"}
    state = adopt(state, result(state, question=question, disposition="provisional"))
    assert state.questions[-1].id == "q3"


@pytest.mark.parametrize("value", [False, 0, [], "", " "])
def test_ready_result_requires_a_textual_nonempty_goal(value):
    state = State(raw_intent="Organize events")
    candidate = result(state)
    candidate.facts["goal"] = Fact(value=value, status="confirmed", source_turn_ids=["t0"])
    with pytest.raises(ValidationError): adopt(state, candidate)


def test_assessed_reply_count_cannot_claim_future_or_unreviewed_input():
    with pytest.raises(ValidationError): State(raw_intent="Idea", assessed_turn_count=1)
    state = adopt(State(raw_intent="Idea"), result(State(raw_intent="Idea")))
    payload = state.model_dump()
    payload["turns"] = [{"id": "t1", "text": "New reply without reassessment"}]
    with pytest.raises(ValidationError): State.model_validate(payload)
