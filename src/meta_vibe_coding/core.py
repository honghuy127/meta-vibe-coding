"""Pure transitions; inference candidates never edit canonical input directly."""

import json
import time

from .models import (IDEA_ASSESSMENTS, AdvanceRequest, Assessment, Candidate, OpenQuestion, Review,
                     State, Turn, normalized_topic)
from .settings import Limits, load_limits

# What the owner can do next, by failure code. Messages say what happened.
NEXT_ACTIONS = {
    "invalid_output": "Nothing was changed. Press Retry to ask the agent again.",
    "invalid_input": "Check your entry and send it again.",
    "timeout": "Press Retry to ask the agent again.",
    "busy": "Wait for the running request to finish, then press Retry. This did not use an assessment.",
    "limit": "Retry cannot help. Start a new idea to continue; the last result stays on this page until then.",
    "server_limit": "Retry and a new idea cannot help. Whoever runs this app must restart it to allow more agent calls.",
    "disabled": "Whoever runs this app must connect the coding agent first.",
    "unavailable": "Check the agent's installation and account, then press Retry.",
    "free_limit": "Wait, or check the agent's workspace settings, then press Retry.",
    "usage_limit": "Wait until the agent account's usage limit resets, then press Retry.",
    "agent_request": "Check the agent's model settings, then press Retry.",
}
NO_RETRY = {"limit", "server_limit", "disabled", "invalid_input"}


class FlowError(Exception):
    # False when no agent process was started, so the idea is not charged an assessment.
    # None leaves the decision to the failure code.
    invoked: bool | None = None

    def __init__(self, code: str, message: str):
        self.code, self.message = code, message
        super().__init__(message)

    def payload(self) -> dict:
        return {"code": self.code, "message": self.message,
                "next_action": NEXT_ACTIONS.get(self.code, "Press Retry."), "retry": self.code not in NO_RETRY}

    def charged(self) -> bool:
        return self.invoked if self.invoked is not None else self.code not in {"busy", "disabled", "limit", "server_limit"}


def same_json(left, right) -> bool:
    # Python equality merges booleans and numbers, including inside lists/maps.
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


ADVICE_LABELS = {
    "risk.reasons": "Risk", "hidden_requirements": "Hidden requirement",
    "recommendation.rationale": "Reason", "recommendation.alternatives": "Alternative",
    "recommendation.owner_responsibilities": "Your responsibility",
    "acceptance_criteria": "Acceptance check", "open_questions": "Open decision", "limitations": "Limit",
}


def advice_lines(assessment: Assessment | None) -> list[str]:
    """One readable line per piece of advice, so two results can be compared by the owner."""
    if assessment is None:
        return []
    data = assessment.model_dump()
    lines = [f"Risk level: {data['risk']['level']}",
             f"Recommendation ({data['recommendation']['kind'].replace('_', ' ')}): {data['recommendation']['summary']}"]
    for field, label in ADVICE_LABELS.items():
        rows = data
        for part in field.split("."):
            rows = rows[part]
        for row in rows:
            text = row if isinstance(row, str) else f"{row['text']} — {row['reason']}"
            lines.append(f"{label}: {text}"[:8000])
    return list(dict.fromkeys(lines))


def advice_changes(previous: Assessment | None, current: Assessment) -> tuple[list[str], list[str]]:
    """Exact comparison only. It shows what changed; it cannot judge whether meaning was kept."""
    before, after = advice_lines(previous), advice_lines(current)
    if not before:
        return [], []
    return [line for line in before if line not in after], [line for line in after if line not in before]


def substantive(text: str) -> bool:
    # English phrases only: a bare unknown in another language is not recognized here.
    return text.strip().lower().rstrip(".! ") not in {
        "continue", "go on", "proceed", "next", "i don't know", "i don’t know", "i do not know"}


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
            if request.declares_unknown:
                key = question["topic"]
                if key not in state["facts"]:
                    raise FlowError("invalid_input", "This question is from an older session. Start a new idea to continue.")
                if state["facts"][key]["status"] not in {"unknown", "assumed"}:
                    raise FlowError("invalid_input", "This question no longer matches an unresolved detail. Use a correction instead.")
                state["facts"][key] = {"value": None, "status": "unknown", "source_turn_ids": [turn_id],
                    "reason": "The owner does not know yet."}
                state["owner_unknowns"][key] = {"source_turn_id": turn_id, "quote": request.answer}
        state["revision"] += 1
        # Facts may still describe earlier answers until reassessment. They cannot
        # be exported with an old recommendation while this input is pending.
    elif request.question_id:
        raise FlowError("invalid_input", "A question ID requires an answer.")
    if state["assessment"] is not None:
        state["previous_assessment"] = state["assessment"]
    state["assessment"] = None
    state["review"] = None
    return State.model_validate(state)


def check_allowance(state: State, limits: Limits | None = None) -> None:
    limits = limits or load_limits()
    if state.agent_calls >= IDEA_ASSESSMENTS:
        raise FlowError("limit", f"This idea has used all {IDEA_ASSESSMENTS} of its assessments. Your answers are retained.")
    if time.time() - state.started_at >= limits.session_seconds:
        raise FlowError("limit", "This idea reached its time limit. Your answers are retained.")


def charge(state: State) -> State:
    """Count one assessment against the idea. Call only once an agent process was started."""
    return state.model_copy(update={"agent_calls": min(IDEA_ASSESSMENTS, state.agent_calls + 1)})


def reserve_call(state: State, limits: Limits | None = None) -> State:
    check_allowance(state, limits)
    return charge(state)


def adopt(state: State, candidate: Candidate, *, allow_question: bool = True) -> State:
    """Refuse a result only when adopting it would break the state. Anything that can be
    weakened instead is weakened and reported to the owner in `review` (D022)."""
    if candidate.assessment.based_on_revision != state.revision:
        raise FlowError("invalid_output", "The agent returned an outdated revision.")
    goal = candidate.facts.get("goal")
    if goal is None or (goal.value is not None and (not isinstance(goal.value, str) or not goal.value.strip())):
        raise FlowError("invalid_output", "The agent did not provide a usable goal. Your answers are retained.")
    # Retaining unsupported confirmed assertions is not a way to remove a fact.
    removed = {k for k, f in state.facts.items() if f.status == "confirmed"} - candidate.facts.keys()
    if removed:
        raise FlowError("invalid_output", "The agent dropped confirmed facts.")
    if state.owner_unknowns.keys() - candidate.facts.keys():
        raise FlowError("invalid_output", "The agent lost a detail you said was unknown. Your answers are retained.")
    notices = list(candidate.notices)
    latest_turn = state.turns[-1].id if state.turns else "t0"
    fresh_reply = len(state.turns) > state.assessed_turn_count
    substantive_reply = fresh_reply and substantive(state.turns[-1].text)
    turn_ids = ["t0"] + [turn.id for turn in state.turns]
    unknowns = state.owner_unknowns.copy()
    facts = dict(candidate.facts)
    kept = set()
    # After the first result, a new confirmed fact needs the owner's latest substantive reply.
    # Otherwise renaming a key could turn the agent's reading of old text into a confirmation.
    first_result = state.assessment is None and state.previous_assessment is None
    for key, fact in candidate.facts.items():
        previous = state.facts.get(key)
        if previous is None:
            if (fact.status == "confirmed" and not first_result
                    and not (substantive_reply and latest_turn in fact.source_turn_ids)):
                reason = "Not confirmed: no new answer from you supports this yet."
                facts[key] = fact.model_copy(update={"status": "assumed",
                    "reason": (fact.reason.strip() + " " + reason).strip()})
                notices.append(f"Recorded “{key}” as an assumption: it is new and your latest reply does not support it.")
            continue
        problem = None
        meaning_changed = not same_json(fact.value, previous.value) or fact.status != previous.status
        evidence = state.owner_unknowns.get(key)
        if previous.status != "confirmed" and fact.status == "confirmed" and (
                not substantive_reply or latest_turn not in fact.source_turn_ids):
            problem = "it was marked confirmed without a new answer from you"
        elif meaning_changed and previous.status == "confirmed" and (
                not fresh_reply or latest_turn not in fact.source_turn_ids or latest_turn in previous.source_turn_ids):
            problem = "it changed something you confirmed without a new reply from you"
        elif evidence and fact.status != "unknown" and (
                fact.status not in {"confirmed", "not_applicable"} or not substantive_reply
                or latest_turn not in fact.source_turn_ids
                or turn_ids.index(latest_turn) <= turn_ids.index(evidence.source_turn_id)):
            problem = "you said you do not know this, and nothing newer settles it"
        if problem:
            facts[key] = previous
            kept.add(key)
            notices.append(f"Kept the earlier record for “{key}”: {problem}.")
        elif evidence and fact.status != "unknown":
            unknowns.pop(key)
    question = candidate.question
    for key, evidence in candidate.owner_unknowns.items():
        previous = unknowns.get(key)
        if key in kept or facts[key].status != "unknown":
            continue
        if previous and evidence != previous and (evidence.source_turn_id not in turn_ids
                or turn_ids.index(evidence.source_turn_id) <= turn_ids.index(previous.source_turn_id)):
            continue  # Keep the earlier declaration; an older or equal source cannot replace it.
        unknowns[key] = evidence
    for key, evidence in unknowns.items():
        if evidence.source_turn_id not in facts[key].source_turn_ids:
            facts[key] = facts[key].model_copy(update={
                "source_turn_ids": [*facts[key].source_turn_ids, evidence.source_turn_id]})
    if question and candidate.assessment.disposition == "ready":
        raise FlowError("invalid_output", "A ready result cannot ask another clarification question.")

    def leave_out(reason: str) -> None:
        notices.append(f"Left out the agent's follow-up question “{question.text}”: {reason}.")

    if question and (question.topic not in facts or facts[question.topic].status not in {"unknown", "assumed"}):
        leave_out("it asks about a detail that is already settled")
        question = None
    # An explicit request for a result ends clarification; open decisions remain
    # in the assessment without creating another question for the owner.
    ask_question = allow_question and question is not None and question.topic not in unknowns
    assessment = candidate.assessment
    if question and not ask_question:
        if question.topic in unknowns:
            leave_out("you said you do not know this, so it stays an open decision")
        if not any(normalized_topic(q.topic) == normalized_topic(question.topic) for q in assessment.open_questions):
            # Keep the unasked decision visible rather than discarding the whole result.
            assessment = assessment.model_copy(deep=True)
            assessment.open_questions.append(OpenQuestion(topic=question.topic, text=question.text,
                blocks_recommendation=False, reason=question.decision))
            notices.append(f"Added “{question.text}” to the open decisions: the agent asked it but did not list it.")
        question = None
    if question:
        answered = [q for q in state.questions if q.topic == question.topic and q.answer_turn_id is not None]
        conflict = question.conflict_turn_id
        if len(state.questions) >= 5:
            leave_out("five questions have already been asked")
            question = None
        elif answered and (conflict != latest_turn or not all(
                turn_ids.index(conflict) > turn_ids.index(q.answer_turn_id) for q in answered)):
            leave_out("you already answered it and nothing newer conflicts")
            question = None
        elif conflict is not None and (not answered or conflict != latest_turn):
            leave_out("it claims a conflict that your replies do not show")
            question = None
    data = state.model_dump()
    new_facts = {key: fact.model_dump() for key, fact in facts.items()}
    if not same_json(new_facts, data["facts"]):
        data["revision"] += 1
    data["facts"] = new_facts
    data["owner_unknowns"] = {key: value.model_dump() for key, value in unknowns.items()}
    data["assessment"] = assessment.model_dump()
    data["previous_assessment"] = None
    data["assessment"]["based_on_revision"] = data["revision"]
    data["assessed_turn_count"] = len(state.turns)
    removed_advice, added_advice = advice_changes(state.previous_assessment or state.assessment, assessment)
    data["review"] = Review(downgrades=[note[:8000] for note in notices], removed_advice=removed_advice,
                            added_advice=added_advice).model_dump()
    for row in data["questions"]:
        if row["answer_turn_id"] is None:
            row["retired"] = True
    if question:
        data["questions"].append({"id": allocate_id("q", [q["id"] for q in data["questions"]]),
                                  **question.model_dump(), "answer_turn_id": None})
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
    # `review` is the wrapper's note to the owner, not context for the agent.
    return json.dumps({"state": state.model_dump(exclude={"review"}), "request_provisional": provisional}, ensure_ascii=False)
