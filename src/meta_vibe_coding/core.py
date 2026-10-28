"""Pure transitions; inference candidates never edit canonical input directly."""

import json
import time

from .models import AdvanceRequest, Candidate, State, Turn
from .settings import Limits, load_limits


class FlowError(Exception):
    def __init__(self, code: str, message: str):
        self.code, self.message = code, message
        super().__init__(message)


def same_json(left, right) -> bool:
    # Python equality merges booleans and numbers, including inside lists/maps.
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def allocate_id(prefix: str, existing: list[str]) -> str:
    number = len(existing) + 1
    while f"{prefix}{number}" in existing:
        number += 1
    return f"{prefix}{number}"


def prepare(request: AdvanceRequest) -> State:
    state = request.state.model_dump()
    if request.answer is not None:
        if not request.answer.strip():
            raise FlowError("invalid_input", "Enter an answer or correction.")
        turn_id = allocate_id("t", [turn["id"] for turn in state["turns"]])
        state["turns"].append(Turn(id=turn_id, text=request.answer).model_dump())
        if request.question_id:
            question = next((q for q in state["questions"] if q["id"] == request.question_id), None)
            if not question or question["retired"] or question["answer_turn_id"] is not None:
                raise FlowError("invalid_input", "That question is missing, retired, or already answered.")
            question["answer_turn_id"] = turn_id
        state["revision"] += 1
        # Facts may still describe earlier answers until reassessment. They cannot
        # be exported with an old recommendation while this input is pending.
    elif request.question_id:
        raise FlowError("invalid_input", "A question ID requires an answer.")
    state["assessment"] = None
    return State.model_validate(state)


def reserve_call(state: State, limits: Limits | None = None) -> State:
    limits = limits or load_limits()
    if state.agent_calls >= 7 or time.time() - state.started_at >= limits.session_seconds:
        raise FlowError("limit", "This session reached its request or time limit. Your answers are retained; start a new idea to continue.")
    return state.model_copy(update={"agent_calls": state.agent_calls + 1})


def adopt(state: State, candidate: Candidate) -> State:
    if candidate.assessment.based_on_revision != state.revision:
        raise FlowError("invalid_output", "The agent returned an outdated revision.")
    # Retaining unsupported confirmed assertions is not a way to remove a fact.
    removed = {k for k, f in state.facts.items() if f.status == "confirmed"} - candidate.facts.keys()
    if removed:
        raise FlowError("invalid_output", "The agent dropped confirmed facts.")
    latest_turn = state.turns[-1].id if state.turns else "t0"
    fresh_reply = len(state.turns) > state.assessed_turn_count
    for key, fact in candidate.facts.items():
        previous = state.facts.get(key)
        if previous and previous.status != "confirmed" and fact.status == "confirmed":
            latest_text = state.turns[-1].text.strip().lower().rstrip(".! ") if state.turns else ""
            if not fresh_reply or latest_turn not in fact.source_turn_ids or latest_text in {"continue", "go on", "proceed", "next"}:
                raise FlowError("invalid_output", "An assumption requires a substantive owner confirmation.")
        meaning_changed = previous is not None and (not same_json(fact.value, previous.value) or fact.status != previous.status)
        if meaning_changed and previous.status == "confirmed":
            if not fresh_reply or latest_turn not in fact.source_turn_ids or latest_turn in previous.source_turn_ids:
                raise FlowError("invalid_output", "A changed confirmed fact needs a new owner reply as evidence.")
    data = state.model_dump()
    facts = {key: fact.model_dump() for key, fact in candidate.facts.items()}
    if not same_json(facts, data["facts"]):
        data["revision"] += 1
    data["facts"] = facts
    data["assessment"] = candidate.assessment.model_dump()
    data["assessment"]["based_on_revision"] = data["revision"]
    data["assessed_turn_count"] = len(state.turns)
    for question in data["questions"]:
        if question["answer_turn_id"] is None:
            question["retired"] = True
    if candidate.question:
        if len(data["questions"]) >= 5:
            raise FlowError("limit", "The agent requested more than five clarification questions.")
        answered = [q for q in state.questions if q.topic == candidate.question.topic and q.answer_turn_id is not None]
        conflict = candidate.question.conflict_turn_id
        turn_ids = ["t0"] + [turn.id for turn in state.turns]
        if answered and (conflict != latest_turn or not all(turn_ids.index(conflict) > turn_ids.index(q.answer_turn_id) for q in answered)):
            raise FlowError("invalid_output", "A repeated question must cite newer owner input that creates a conflict.")
        if conflict is not None and (not answered or conflict != latest_turn):
            raise FlowError("invalid_output", "A conflict must reopen an answered topic using the latest owner reply.")
        if candidate.assessment.disposition == "ready":
            raise FlowError("invalid_output", "A ready result cannot ask another clarification question.")
        data["questions"].append({"id": allocate_id("q", [q["id"] for q in data["questions"]]),
                                  **candidate.question.model_dump(), "answer_turn_id": None})
    # Revalidation enforces revision, provenance, enum, and readiness invariants.
    return State.model_validate(data)


def export_brief(state: State) -> dict:
    if not state.assessment or state.assessment.disposition == "needs_answer":
        raise FlowError("not_ready", "There is no current recommendation to export.")
    data = state.assessment.model_dump(exclude={"based_on_revision"})
    data.update(schema_version=state.schema_version, revision=state.revision,
                raw_intent=state.raw_intent,
                facts={key: fact.model_dump() for key, fact in state.facts.items()})
    needed = {source for fact in state.facts.values() for source in fact.source_turn_ids}
    sources = {"t0": state.raw_intent, **{turn.id: turn.text for turn in state.turns}}
    data["sources"] = [{"id": key, "text": text} for key, text in sources.items() if key in needed]
    return data


def model_input(state: State, provisional: bool) -> str:
    return json.dumps({"state": state.model_dump(), "request_provisional": provisional}, ensure_ascii=False)
