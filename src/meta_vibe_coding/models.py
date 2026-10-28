"""State shared by the interface, inference adapters, and exported brief."""

import re
import time
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

Text = Annotated[str, Field(min_length=1, max_length=8000)]
Scalar = str | bool | int | float


class Model(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)


class Fact(Model):
    value: Scalar | list[Scalar] | None
    status: Literal["confirmed", "assumed", "unknown", "not_applicable"]
    source_turn_ids: list[str]
    reason: str = ""

    @model_validator(mode="after")
    def check_meaning(self) -> Self:
        if (self.status in {"unknown", "not_applicable"}) != (self.value is None):
            raise ValueError("Only unknown/not_applicable facts have null values")
        if self.status == "confirmed" and not self.source_turn_ids:
            raise ValueError("Confirmed facts require owner sources")
        if self.status in {"assumed", "not_applicable"} and not self.reason.strip():
            raise ValueError("Assumed/not_applicable facts require a reason")
        return self


class Turn(Model):
    id: Text
    text: Text


class Question(Model):
    id: Text
    topic: Text
    text: Text
    decision: Text
    answer_turn_id: str | None = None
    retired: bool = False
    conflict_turn_id: str | None = None


class ProposedQuestion(Model):
    topic: Text
    text: Text
    decision: Text
    conflict_turn_id: str | None = None


class OpenQuestion(Model):
    topic: Text
    text: Text
    blocks_recommendation: bool
    reason: Text


class HiddenRequirement(Model):
    text: Text
    reason: Text


class Risk(Model):
    level: Literal["low", "medium", "high", "unknown"]
    reasons: list[Text] = Field(min_length=1)


class Recommendation(Model):
    kind: Literal["existing_tool", "manual_workflow", "local_utility", "static_site",
                  "application", "do_not_build", "undecided"]
    summary: Text
    rationale: list[Text] = Field(min_length=1)
    alternatives: list[Text]
    owner_responsibilities: list[Text]


class Assessment(Model):
    based_on_revision: int = Field(ge=1)
    disposition: Literal["needs_answer", "provisional", "ready"]
    risk: Risk
    hidden_requirements: list[HiddenRequirement]
    recommendation: Recommendation
    acceptance_criteria: list[Text]
    open_questions: list[OpenQuestion]
    limitations: list[Text]


class State(Model):
    schema_version: Literal[1] = 1
    revision: int = Field(default=1, ge=1)
    raw_intent: Text
    turns: list[Turn] = Field(default_factory=list, max_length=30)
    facts: dict[str, Fact] = Field(default_factory=dict, max_length=100)
    questions: list[Question] = Field(default_factory=list, max_length=5)
    assessment: Assessment | None = None
    agent_calls: int = Field(default=0, ge=0, le=7)
    started_at: float = Field(default_factory=time.time, gt=0)
    assessed_turn_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def check_consistency(self) -> Self:
        turn_ids = ["t0"] + [turn.id for turn in self.turns]
        question_ids = [question.id for question in self.questions]
        if len(turn_ids) != len(set(turn_ids)) or len(question_ids) != len(set(question_ids)):
            raise ValueError("Turn and question IDs must be unique")
        if self.assessed_turn_count > len(self.turns):
            raise ValueError("Assessed turn count cannot exceed owner reply count")
        for key, fact in self.facts.items():
            if not re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*", key):
                raise ValueError("Fact keys must be lower-case semantic keys")
            if not set(fact.source_turn_ids).issubset(turn_ids):
                raise ValueError("Fact refers to an unknown owner source")
        for question in self.questions:
            if question.answer_turn_id is not None and question.answer_turn_id not in turn_ids:
                raise ValueError("Question answer refers to an unknown owner source")
            if question.conflict_turn_id is not None and question.conflict_turn_id not in turn_ids:
                raise ValueError("Question conflict refers to an unknown owner source")
        if self.assessment:
            if self.assessed_turn_count != len(self.turns):
                raise ValueError("Assessment does not cover the current owner replies")
            if self.assessment.based_on_revision != self.revision:
                raise ValueError("Assessment belongs to an outdated revision")
            if self.assessment.disposition == "ready":
                goal = self.facts.get("goal")
                if not goal or goal.status != "confirmed":
                    raise ValueError("Ready results require a confirmed goal")
                if not isinstance(goal.value, str) or not goal.value.strip():
                    raise ValueError("A ready goal must be nonempty text")
                if self.assessment.recommendation.kind == "undecided":
                    raise ValueError("Ready results require a decided recommendation")
                if not self.assessment.acceptance_criteria:
                    raise ValueError("Ready results require acceptance criteria")
                if any(q.blocks_recommendation for q in self.assessment.open_questions):
                    raise ValueError("Blocking questions prevent a ready result")
        return self


class Candidate(Model):
    # A complete fact map makes removals of dependent assumptions explicit.
    facts: dict[str, Fact]
    assessment: Assessment
    question: ProposedQuestion | None


class AdvanceRequest(Model):
    state: State
    request_id: Text
    answer: Text | None = None
    question_id: str | None = None
    provisional: bool = False


class Usage(Model):
    agent: str
    agent_version: str | None = None
    model: str | None = None
    elapsed_seconds: float = Field(ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0)
