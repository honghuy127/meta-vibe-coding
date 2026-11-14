"""Closed native response schemas and explicit decoding into canonical state."""

from typing import Literal

from pydantic import Field, field_validator

from .models import (Assessment, Candidate, Fact, FactKey, Model, ProposedQuestion,
                     Scalar, State, UnknownEvidence, quoted_in)

# English phrases only; a declaration in another language is recorded as an ordinary unknown.
NOT_KNOWING = ("don't know", "don’t know", "do not know", "dont know", "not sure", "unsure",
               "no idea", "haven't decided", "have not decided", "not decided", "can't say", "cannot say")


def declares_not_knowing(quote: str) -> bool:
    text = " ".join(quote.lower().split())
    return any(phrase in text for phrase in NOT_KNOWING)


class NativeFactUpdate(Model):
    key: FactKey
    value: Scalar | list[Scalar] | None
    status: Literal['confirmed', 'assumed', 'unknown', 'not_applicable']
    reason: str
    evidence: list[UnknownEvidence] = Field(max_length=100)


class NativeResponse(Model):
    contract_version: Literal[4]
    fact_updates: list[NativeFactUpdate] = Field(max_length=100)
    remove_fact_keys: list[FactKey] = Field(max_length=100)
    assessment: Assessment
    question: ProposedQuestion | None

    @field_validator('contract_version', mode='before')
    @classmethod
    def integer_version(cls, value):
        if type(value) is not int:
            raise ValueError('Native contract version must be an integer')
        return value

    def candidate(self, state: State) -> Candidate:
        """Decode against the original state. An update the owner's words do not support is
        weakened and reported, so one bad citation does not discard the whole result (D022)."""
        facts = {key: fact.model_copy(deep=True) for key, fact in state.facts.items()}
        keys = [row.key for row in self.fact_updates]
        if len(set(keys)) != len(keys) or set(keys).intersection(self.remove_fact_keys):
            raise ValueError('A fact key appears in more than one native operation')
        notices = []
        for key in dict.fromkeys(self.remove_fact_keys):
            if key not in state.facts:
                continue
            if state.facts[key].status == 'confirmed' or key in state.owner_unknowns:
                notices.append(f'Kept “{key}”: the agent tried to drop something you confirmed or said you do not know.')
                continue
            del facts[key]
        sources = {'t0': state.raw_intent, **{turn.id: turn.text for turn in state.turns}}
        unknowns = {}
        for row in self.fact_updates:
            evidence = [e for e in row.evidence
                        if e.source_turn_id in sources and quoted_in(e.quote, sources[e.source_turn_id])]
            status, reason = row.status, row.reason
            if status == 'confirmed' and (not evidence or len(evidence) != len(row.evidence)):
                # Every cited passage must be the owner's; otherwise this is the agent's reading.
                status = 'assumed'
                reason = (reason.strip() + ' ' if reason.strip() else '') + 'Not confirmed: the agent did not quote your words for this.'
                notices.append(f'Recorded “{row.key}” as an assumption: the agent did not quote your words for it.')
            source_ids = list(dict.fromkeys(e.source_turn_id for e in evidence))
            facts[row.key] = Fact(value=row.value, status=status, source_turn_ids=source_ids, reason=reason)
            declarations = [e for e in evidence if declares_not_knowing(e.quote)]
            if status == 'unknown' and declarations:
                # Only the owner's own words saying they do not know make a declaration (D022).
                # Other quotes on an unknown fact are context and suppress no later question.
                unknowns[row.key] = declarations[-1]
        if len(facts) > 100:
            raise ValueError('Too many native facts')
        if 'goal' not in facts:
            raise ValueError('The resulting facts need a goal')
        return Candidate(facts=facts, assessment=self.assessment, question=self.question,
                         owner_unknowns=unknowns, notices=notices)


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
