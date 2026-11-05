"""Closed native response schemas and explicit decoding into canonical state."""

from typing import Literal

from pydantic import Field, field_validator

from .models import (Assessment, AssessmentChange, Candidate, Fact, FactKey, Model, ProposedQuestion,
                     Scalar, State, UnknownEvidence, quoted_in)


class NativeFactUpdate(Model):
    key: FactKey
    value: Scalar | list[Scalar] | None
    status: Literal['confirmed', 'assumed', 'unknown', 'not_applicable']
    reason: str
    evidence: list[UnknownEvidence] = Field(max_length=100)
    owner_unknown: bool


class NativeResponse(Model):
    contract_version: Literal[3]
    fact_updates: list[NativeFactUpdate] = Field(max_length=100)
    remove_fact_keys: list[FactKey] = Field(max_length=100)
    assessment: Assessment
    question: ProposedQuestion | None
    assessment_changes: list[AssessmentChange] = Field(max_length=500)

    @field_validator('contract_version', mode='before')
    @classmethod
    def integer_version(cls, value):
        if type(value) is not int:
            raise ValueError('Native contract version must be an integer')
        return value

    def candidate(self, state: State) -> Candidate:
        # Keep the original state intact for adoption's confirmation/revision guards.
        facts = {key: fact.model_copy(deep=True) for key, fact in state.facts.items()}
        keys = [row.key for row in self.fact_updates]
        if len(set(keys)) != len(keys) or len(set(self.remove_fact_keys)) != len(self.remove_fact_keys):
            raise ValueError('Duplicate native operation key')
        if set(keys).intersection(self.remove_fact_keys):
            raise ValueError('A fact cannot be updated and removed together')
        for key in self.remove_fact_keys:
            if key not in state.facts:
                raise ValueError('Cannot remove a missing fact')
            if state.facts[key].status == 'confirmed' or key in state.owner_unknowns:
                raise ValueError('Cannot remove a confirmed fact or retained owner unknown')
            del facts[key]
        sources = {'t0': state.raw_intent, **{turn.id: turn.text for turn in state.turns}}
        unknowns = {}
        for row in self.fact_updates:
            for evidence in row.evidence:
                if evidence.source_turn_id not in sources or not quoted_in(evidence.quote, sources[evidence.source_turn_id]):
                    raise ValueError('Evidence must quote the owner\'s own words')
            source_ids = list(dict.fromkeys(e.source_turn_id for e in row.evidence))
            fact = Fact(value=row.value, status=row.status, source_turn_ids=source_ids, reason=row.reason)
            if row.owner_unknown:
                if row.status != 'unknown' or len(row.evidence) != 1:
                    raise ValueError('An owner unknown needs unknown/null and exactly one evidence record')
                unknowns[row.key] = row.evidence[0]
            retained = state.owner_unknowns.get(row.key)
            if (retained and fact.status == 'unknown' and not row.owner_unknown
                    and retained.source_turn_id not in source_ids):
                raise ValueError('A retained owner unknown must keep its cited source')
            facts[row.key] = fact
        if len(facts) > 100:
            raise ValueError('Too many native facts')
        if 'goal' not in facts:
            raise ValueError('The resulting facts need a goal')
        if self.question and self.question.topic not in facts:
            raise ValueError('Question target must reference a resulting fact')
        return Candidate(facts=facts, assessment=self.assessment, question=self.question,
                         owner_unknowns=unknowns, assessment_changes=self.assessment_changes)


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
