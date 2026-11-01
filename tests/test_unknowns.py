"""Source-backed uncertainty and fact-bound questions; no native inference."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from meta_vibe_coding.app import create_app
from meta_vibe_coding.core import FlowError, adopt, export_brief, prepare
from meta_vibe_coding.models import AdvanceRequest, Candidate, Fact, Question, State, Usage
from test_flow import result


def declared_state():
    return State(raw_intent="I want a tool. I don't know the budget.", facts={
        "goal": Fact(value="I want a tool.", status="confirmed", source_turn_ids=["t0"]),
        "operations.budget": Fact(value=None, status="unknown", source_turn_ids=["t0"])},
        owner_unknowns={"operations.budget": {"source_turn_id": "t0", "quote": "I don't know the budget."}})


def questioning(state, key="operations.budget"):
    candidate = result(state, facts=state.facts.copy(), disposition="provisional",
        question={"topic": key, "text": "What is the decision?", "decision": "Changes suitable options."})
    body = candidate.model_dump()
    body["assessment"]["open_questions"] = [{"topic": key, "text": "This decision is still open.",
        "blocks_recommendation": False, "reason": "Check it before choosing."}]
    return Candidate.model_validate(body)


def test_sourced_owner_unknown_suppresses_only_its_bound_question_and_is_not_exported():
    state = declared_state()
    updated = adopt(state, questioning(state))
    assert updated.questions == [] and updated.owner_unknowns == state.owner_unknowns
    brief = export_brief(updated)
    assert brief["facts"]["operations.budget"]["value"] is None
    assert brief["open_questions"][0]["topic"] == "operations.budget"
    assert brief["schema_version"] == 1 and "owner_unknowns" not in brief
    other = adopt(state, questioning(state, "operations.maintainer"))
    assert other.questions[-1].topic == "operations.maintainer"


def test_agent_can_annotate_a_verbatim_explicit_unknown_from_the_initial_idea():
    known = declared_state()
    state = State(raw_intent=known.raw_intent)
    candidate = questioning(known)
    candidate.owner_unknowns = known.owner_unknowns.copy()
    updated = adopt(state, candidate)
    assert updated.owner_unknowns == known.owner_unknowns and updated.questions == []


@pytest.mark.parametrize("change", ["source", "quote", "whitespace", "status", "missing_fact", "fact_source"])
def test_unknown_evidence_must_reference_its_unknown_fact_and_exact_owner_text(change):
    body = declared_state().model_dump()
    evidence = body["owner_unknowns"]["operations.budget"]
    if change == "source": evidence["source_turn_id"] = "t99"
    if change == "quote": evidence["quote"] = "A fabricated owner statement."
    if change == "whitespace": evidence["quote"] = " "
    if change == "status": body["facts"]["operations.budget"].update(value=20, status="confirmed")
    if change == "missing_fact": body["facts"].pop("operations.budget")
    if change == "fact_source": body["facts"]["operations.budget"]["source_turn_ids"] = []
    with pytest.raises(ValidationError): State.model_validate(body)


def test_unknown_button_survives_agent_failure_and_retry_without_duplicate_reply():
    class RecoveringAgent:
        calls = 0
        async def assess(self, state, provisional):
            self.calls += 1
            assert state.facts["operations.budget"].status == "unknown"
            assert state.owner_unknowns["operations.budget"].source_turn_id == "t1"
            if self.calls == 1: raise FlowError("timeout", "Fictional timeout.")
            return questioning(state), Usage(agent="test-double", elapsed_seconds=0)
    state = declared_state().model_copy(update={"raw_intent": "I want a tool.", "owner_unknowns": {},
        "facts": {"goal": Fact(value="I want a tool.", status="confirmed", source_turn_ids=["t0"]),
            "operations.budget": Fact(value=20, status="assumed", source_turn_ids=[], reason="Not confirmed.")},
        "questions": [Question(id="q1", topic="operations.budget", text="What is the budget?", decision="Changes options.")]})
    agent = RecoveringAgent()
    with TestClient(create_app(agent)) as client:
        failed = client.post('/api/advance', json={"state": state.model_dump(), "request_id": "unknown",
            "answer": "I don't know.", "question_id": "q1", "declares_unknown": True}).json()
        assert failed["error"]["code"] == "timeout"
        retained = failed["state"]
        assert retained["facts"]["operations.budget"]["value"] is None
        assert retained["owner_unknowns"]["operations.budget"]["quote"] == "I don't know."
        assert client.post('/api/export', json=retained).status_code == 409
        retried = client.post('/api/advance', json={"state": retained, "request_id": "retry"}).json()
        assert retried["error"] is None and len(retried["state"]["turns"]) == 1
        assert retried["state"]["questions"][0]["answer_turn_id"] == "t1"
        assert len(retried["state"]["questions"]) == 1 and agent.calls == 2


def test_unknown_cannot_be_resolved_by_its_own_unassessed_declaration():
    base = State(raw_intent="A tool", facts={"goal": Fact(value="A tool", status="confirmed", source_turn_ids=["t0"]),
        "operations.budget": Fact(value=None, status="unknown", source_turn_ids=[])},
        questions=[Question(id="q1", topic="operations.budget", text="Budget?", decision="Changes options.")])
    state = prepare(AdvanceRequest(state=base, request_id="unknown", answer="I don't know.",
        question_id="q1", declares_unknown=True))
    candidate = result(state, facts={**state.facts,
        "operations.budget": Fact(value=20, status="confirmed", source_turn_ids=["t1"])})
    with pytest.raises(FlowError): adopt(state, candidate)


@pytest.mark.parametrize("reply", [None, "Continue.", "I don't know.", "The budget is 20 per month."])
def test_only_a_later_substantive_answer_can_resolve_a_retained_unknown(reply):
    state = declared_state()
    if reply: state = prepare(AdvanceRequest(state=state, request_id="later", answer=reply))
    candidate = result(state, facts={**state.facts,
        "operations.budget": Fact(value=20, status="confirmed", source_turn_ids=["t1" if reply else "t0"])})
    if reply == "The budget is 20 per month.":
        resolved = adopt(state, candidate)
        assert resolved.owner_unknowns == {} and resolved.facts["operations.budget"].value == 20
    else:
        with pytest.raises(FlowError): adopt(state, candidate)


def test_later_not_applicable_answer_resolves_uncertainty_but_a_model_guess_does_not():
    state = prepare(AdvanceRequest(state=declared_state(), request_id="not-applicable",
        answer="Ongoing service costs do not apply because we will not use a hosted service."))
    candidate = result(state, facts={**state.facts, "operations.budget": Fact(value=None,
        status="not_applicable", source_turn_ids=["t1"], reason="The owner ruled out ongoing services.")},
        disposition="provisional")
    assert adopt(state, candidate).owner_unknowns == {}
    candidate.facts["operations.budget"] = Fact(value=20, status="assumed", source_turn_ids=["t1"],
        reason="A model estimate, not an owner answer.")
    with pytest.raises(FlowError): adopt(state, candidate)


def test_declared_unknown_cannot_be_dropped_or_reanchored_and_suppression_keeps_open_decision():
    state = declared_state()
    dropped = result(state)
    with pytest.raises(FlowError): adopt(state, dropped)
    body = questioning(state).model_dump()
    body["owner_unknowns"] = {"operations.budget": {"source_turn_id": "t0", "quote": "budget"}}
    reanchored = Candidate.model_validate(body)
    with pytest.raises(FlowError): adopt(state, reanchored)
    omitted_decision = questioning(state)
    omitted_decision.assessment.open_questions = []
    with pytest.raises(FlowError): adopt(state, omitted_decision)


def test_goal_and_question_binding_are_canonical_and_legacy_marker_default_is_empty():
    state = State(raw_intent="A tool")
    assert state.owner_unknowns == {}
    assert Candidate.model_json_schema()["properties"]["facts"]["required"] == ["goal"]
    alias = result(state)
    alias.facts["project.goal"] = alias.facts.pop("goal")
    with pytest.raises(FlowError): adopt(state, alias)
    candidate = questioning(declared_state())
    candidate.facts.pop("operations.budget")
    with pytest.raises(FlowError): adopt(state, candidate)
    with pytest.raises(ValidationError):
        AdvanceRequest(state=state, request_id="bad-action", declares_unknown=True)


@pytest.mark.parametrize("status", ["confirmed", "not_applicable"])
@pytest.mark.parametrize("allow_question", [True, False])
def test_settled_question_targets_fail_even_when_the_question_would_be_suppressed(status, allow_question):
    state = State(raw_intent="Editors may request changes.", facts={
        "goal": Fact(value="Track editorial requests.", status="confirmed", source_turn_ids=["t0"]),
        "workflow.requests": Fact(value=True if status == "confirmed" else None, status=status,
            source_turn_ids=["t0"], reason="Scripted applicability decision.")})
    before = state.model_dump()
    with pytest.raises(FlowError, match="settled detail"):
        adopt(state, questioning(state, "workflow.requests"), allow_question=allow_question)
    assert state.model_dump() == before


@pytest.mark.parametrize("status", ["confirmed", "not_applicable"])
def test_unknown_action_on_a_legacy_settled_target_cannot_erase_it_or_call_an_agent(status):
    class ForbiddenAgent:
        async def assess(self, state, provisional): raise AssertionError("Reject before inference")
    state = State(raw_intent="A fictional editorial workflow.", facts={
        "goal": Fact(value="Track requests.", status="confirmed", source_turn_ids=["t0"]),
        "workflow.requests": Fact(value=True if status == "confirmed" else None, status=status,
            source_turn_ids=["t0"], reason="Scripted applicability decision.")},
        questions=[Question(id="q1", topic="workflow.requests", text="Who approves requests?",
            decision="This older question mistakenly targets the request capability.")])
    before = state.model_dump()
    request = AdvanceRequest(state=state, request_id="mismatched-unknown", question_id="q1",
        answer="I don't know.", declares_unknown=True)
    with pytest.raises(FlowError, match="unresolved detail"): prepare(request)
    with TestClient(create_app(ForbiddenAgent())) as client:
        response = client.post('/api/advance', json=request.model_dump())
        assert response.status_code == 422 and response.json()["code"] == "invalid_input"
    assert state.model_dump() == before
    assert state.turns == [] and state.owner_unknowns == {} and state.agent_calls == 0


def test_a_confirmed_fact_can_reopen_only_after_a_later_sourced_conflict_makes_it_unresolved():
    base = State(raw_intent="Share fictional design sketches.")
    question = {"topic": "access.visibility", "text": "Who should see the sketches?",
        "decision": "Changes access requirements."}
    state = adopt(base, result(base, question=question, disposition="provisional"))
    answered = prepare(AdvanceRequest(state=state, request_id="private", question_id="q1", answer="Only me."))
    state = adopt(answered, result(answered, facts={**answered.facts, "access.visibility": Fact(
        value="Only the owner.", status="confirmed", source_turn_ids=["t1"])}, disposition="provisional"))
    assert state.facts["access.visibility"].status == "confirmed"
    repeated = {**question, "conflict_turn_id": "t1"}
    unresolved = Fact(value=None, status="unknown", source_turn_ids=["t1"], reason="Conflicting access needs.")
    with pytest.raises(FlowError, match="new owner reply"):
        adopt(state, result(state, facts={**state.facts, "access.visibility": unresolved},
            question=repeated, disposition="provisional"))

    changed = prepare(AdvanceRequest(state=state, request_id="mixed", answer="Let reviewers see part, but keep the rest private."))
    repeated.update(conflict_turn_id="t2", decision="Your later mixed-access request needs a boundary for public and private sketches.")
    with pytest.raises(FlowError, match="new owner reply"):
        adopt(changed, result(changed, facts={**changed.facts, "access.visibility": unresolved},
            question=repeated, disposition="provisional"))
    unresolved.source_turn_ids = ["t2"]
    updated = adopt(changed, result(changed, facts={**changed.facts, "access.visibility": unresolved},
        question=repeated, disposition="provisional"))
    assert updated.questions[-1].topic == "access.visibility"
    assert updated.questions[-1].conflict_turn_id == "t2"
    assert updated.facts["access.visibility"].status == "unknown"
    assert state.facts["access.visibility"].status == "confirmed"
