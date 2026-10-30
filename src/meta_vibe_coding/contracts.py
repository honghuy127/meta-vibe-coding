"""Closed native response schemas and explicit decoding into canonical state."""

import json
from typing import Literal

from pydantic import Field, field_validator

from .models import (Assessment, Candidate, Fact, FactKey, Model, ProposedQuestion,
                     Scalar, State, Text, UnknownEvidence)


class NativeFact(Model):
    key: FactKey
    value: Scalar | list[Scalar] | None
    status: Literal['confirmed', 'assumed', 'unknown', 'not_applicable']
    source_turn_ids: list[str]
    reason: str

    def fact(self) -> Fact:
        return Fact.model_validate(self.model_dump(exclude={'key'}))


class NativeQuestion(Model):
    fact: NativeFact
    text: Text
    decision: Text
    conflict_turn_id: str | None


class NativeUnknown(Model):
    key: FactKey
    source_turn_id: Text
    quote: str = Field(min_length=1, max_length=500)


class Grounding(UnknownEvidence):
    fact_keys: list[FactKey] = Field(min_length=1, max_length=100)


class NativeResponse(Model):
    contract_version: Literal[1]
    facts: list[NativeFact] = Field(max_length=100)
    assessment: Assessment
    question: NativeQuestion | None
    owner_unknowns: list[NativeUnknown] = Field(max_length=100)
    grounding: list[Grounding] = Field(max_length=100)

    @field_validator('contract_version', mode='before')
    @classmethod
    def integer_version(cls, value):
        if type(value) is not int:
            raise ValueError('Native contract version must be an integer')
        return value

    def candidate(self, state: State) -> Candidate:
        facts = {}
        for row in self.facts:
            if row.key in facts:
                raise ValueError('Duplicate native fact key')
            facts[row.key] = row.fact()
        question = None
        if self.question:
            row = self.question.fact
            fact = row.fact()
            if row.key in facts and json.dumps(facts[row.key].model_dump(), sort_keys=True) != json.dumps(fact.model_dump(), sort_keys=True):
                raise ValueError('Question target conflicts with native fact')
            facts[row.key] = fact
            question = ProposedQuestion(topic=row.key, **self.question.model_dump(exclude={'fact'}))
        if len(facts) > 100:
            raise ValueError('Too many native facts')
        unknowns = {}
        for row in self.owner_unknowns:
            if row.key in unknowns:
                raise ValueError('Duplicate native unknown key')
            unknowns[row.key] = UnknownEvidence.model_validate(row.model_dump(exclude={'key'}))
        candidate = Candidate(facts=facts, assessment=self.assessment, question=question, owner_unknowns=unknowns)
        validate_grounding(state, candidate, self.grounding)
        return candidate


def validate_grounding(state: State, candidate: Candidate, grounding: list[Grounding]) -> None:
    """Quotes establish source presence/linkage, not semantic support or completeness."""
    sources = {'t0': state.raw_intent, **{turn.id: turn.text for turn in state.turns}}
    links = set()
    for entry in grounding:
        if not entry.quote.strip() or entry.source_turn_id not in sources or entry.quote not in sources[entry.source_turn_id]:
            raise ValueError('Grounding needs an exact nonempty owner quote')
        if len(set(entry.fact_keys)) != len(entry.fact_keys):
            raise ValueError('Duplicate grounded fact key')
        for key in entry.fact_keys:
            fact = candidate.facts.get(key)
            if fact is None or entry.source_turn_id not in fact.source_turn_ids:
                raise ValueError('Grounding must link an existing fact and its cited source')
            links.add((key, entry.source_turn_id))
    for key, fact in candidate.facts.items():
        previous = state.facts.get(key)
        unchanged = (previous is not None and previous.status == fact.status
            and json.dumps(previous.value, sort_keys=True) == json.dumps(fact.value, sort_keys=True)
            and set(previous.source_turn_ids) == set(fact.source_turn_ids))
        if fact.status == 'confirmed' and not unchanged:
            if any((key, source) not in links for source in fact.source_turn_ids):
                raise ValueError('New or changed confirmed facts need quoted grounding for each source')


def native_schema(model: type[Model]) -> dict:
    """Use a conservative schema subset; retain all semantic/bound checks locally."""
    def compile_node(node):
        if any(key in node for key in ('oneOf', 'allOf', 'not', 'if', 'then', 'else', 'prefixItems', 'patternProperties')):
            raise ValueError('Unsupported structural native schema keyword')
        result = {}
        for key in ('$ref', 'type', 'enum', 'description'):
            if key in node:
                result[key] = node[key]
        if 'const' in node:
            result['enum'] = [node['const']]
        if '$defs' in node:
            result['$defs'] = {key: compile_node(value) for key, value in node['$defs'].items()}
        if 'anyOf' in node:
            result['anyOf'] = [compile_node(value) for value in node['anyOf']]
        if 'items' in node:
            result['items'] = compile_node(node['items'])
        if node.get('type') == 'object':
            if node.get('additionalProperties') is not False:
                raise ValueError('Native responses require closed objects, not arbitrary maps')
            result['properties'] = {key: compile_node(value) for key, value in node.get('properties', {}).items()}
            result['required'] = list(result['properties'])
            result['additionalProperties'] = False
        return result
    return compile_node(model.model_json_schema())
