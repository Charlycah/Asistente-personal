from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping, Sequence

from .exceptions import DomainError
from .governed_objective_memory import GovernedObjective, GovernedObjectiveState
from .governed_permanent_knowledge import (
    GovernedKnowledgeFact,
    GovernedKnowledgeState,
)


class GovernedJudgmentOutcome(StrEnum):
    """Advisory outcomes that never grant decision or execution authority."""

    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"
    CONFLICTED = "conflicted"
    DEFER = "defer"


@dataclass(frozen=True)
class GovernedCognitiveJudgment:
    """Immutable and explainable assessment of a governed situation."""

    judgment_id: str
    subject: str
    objective_ids: tuple[str, ...]
    knowledge_fact_ids: tuple[str, ...]
    evidence: tuple[str, ...]
    missing_information: tuple[str, ...]
    conflicts: tuple[str, ...]
    risks: tuple[str, ...]
    prioritized_objective_ids: tuple[str, ...]
    outcome: GovernedJudgmentOutcome
    rationale: str
    confidence: float
    clarification_questions: tuple[str, ...] = ()
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        for field_name in ("judgment_id", "subject", "rationale"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        for field_name in (
            "objective_ids",
            "knowledge_fact_ids",
            "evidence",
            "missing_information",
            "conflicts",
            "risks",
            "prioritized_objective_ids",
            "clarification_questions",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalized_strings(field_name, getattr(self, field_name)),
            )
        if not self.objective_ids:
            raise DomainError("cognitive judgment requires at least one objective")
        if not isinstance(self.outcome, GovernedJudgmentOutcome):
            raise DomainError("outcome must be a GovernedJudgmentOutcome")
        if (
            not isinstance(self.confidence, (int, float))
            or isinstance(self.confidence, bool)
            or not 0.0 <= float(self.confidence) <= 1.0
        ):
            raise DomainError("confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", float(self.confidence))
        unknown_priorities = set(self.prioritized_objective_ids) - set(
            self.objective_ids
        )
        if unknown_priorities:
            raise DomainError("prioritized objectives must belong to the judgment")
        if self.outcome is GovernedJudgmentOutcome.NEEDS_CLARIFICATION:
            if not self.missing_information:
                raise DomainError(
                    "clarification outcome requires missing information"
                )
            if not self.clarification_questions:
                raise DomainError(
                    "clarification outcome requires explicit questions"
                )
        if self.outcome is GovernedJudgmentOutcome.CONFLICTED and not self.conflicts:
            raise DomainError("conflicted outcome requires explicit conflicts")
        if self.outcome is GovernedJudgmentOutcome.READY:
            if self.missing_information or self.conflicts:
                raise DomainError(
                    "ready judgment cannot retain missing information or conflicts"
                )
            if not self.prioritized_objective_ids:
                raise DomainError("ready judgment requires a reasoned priority")
        object.__setattr__(self, "metadata", _immutable_mapping(self.metadata))


@dataclass(frozen=True)
class GovernedCognitiveJudgmentSnapshot:
    schema_version: str
    authority: str
    persistence_enabled: bool
    autonomous_judgment_enabled: bool
    decision_authority: bool
    execution_authority: bool
    conversation_authority: bool
    recorded_judgments: int
    outcomes: tuple[GovernedJudgmentOutcome, ...]


class GovernedCognitiveJudgmentAuthority:
    """Gateway-owned advisory authority for explicit cognitive judgments."""

    SCHEMA_VERSION = "m347.1"
    AUTHORITY = (
        "domain.governed_cognitive_judgment:"
        "GovernedCognitiveJudgmentAuthority"
    )

    def __init__(self) -> None:
        self._judgments: dict[str, GovernedCognitiveJudgment] = {}

    @property
    def snapshot(self) -> GovernedCognitiveJudgmentSnapshot:
        return GovernedCognitiveJudgmentSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            persistence_enabled=False,
            autonomous_judgment_enabled=False,
            decision_authority=False,
            execution_authority=False,
            conversation_authority=False,
            recorded_judgments=len(self._judgments),
            outcomes=tuple(GovernedJudgmentOutcome),
        )

    def assess(
        self,
        objectives: Sequence[GovernedObjective],
        knowledge_facts: Sequence[GovernedKnowledgeFact] = (),
        **judgment_fields,
    ) -> GovernedCognitiveJudgment:
        judgment_id = judgment_fields.get("judgment_id")
        if judgment_id in self._judgments:
            raise DomainError(f"judgment_id already exists: {judgment_id}")
        objective_tuple = tuple(objectives)
        if not objective_tuple:
            raise DomainError("cognitive judgment requires governed objectives")
        if any(
            objective.state is GovernedObjectiveState.COMPLETED
            for objective in objective_tuple
        ):
            raise DomainError("completed objectives cannot receive new judgment")
        fact_tuple = tuple(knowledge_facts)
        if any(
            fact.state is GovernedKnowledgeState.RETRACTED for fact in fact_tuple
        ):
            raise DomainError("retracted knowledge cannot support judgment")
        supplied_objective_ids = tuple(
            judgment_fields.pop("objective_ids", ())
        )
        supplied_fact_ids = tuple(
            judgment_fields.pop("knowledge_fact_ids", ())
        )
        objective_ids = tuple(
            objective.objective_id for objective in objective_tuple
        )
        fact_ids = tuple(fact.fact_id for fact in fact_tuple)
        if supplied_objective_ids and supplied_objective_ids != objective_ids:
            raise DomainError("objective_ids must match governed objectives")
        if supplied_fact_ids and supplied_fact_ids != fact_ids:
            raise DomainError("knowledge_fact_ids must match governed facts")
        judgment = GovernedCognitiveJudgment(
            objective_ids=objective_ids,
            knowledge_fact_ids=fact_ids,
            **judgment_fields,
        )
        self._judgments[judgment.judgment_id] = judgment
        return judgment

    def find(self, judgment_id: str) -> GovernedCognitiveJudgment | None:
        return self._judgments.get(judgment_id)

    def for_objective(
        self, objective_id: str
    ) -> tuple[GovernedCognitiveJudgment, ...]:
        return tuple(
            judgment
            for judgment in self._judgments.values()
            if objective_id in judgment.objective_ids
        )


def _normalized_strings(
    field_name: str, values: Sequence[str]
) -> tuple[str, ...]:
    normalized = tuple(values)
    if not all(isinstance(value, str) and value.strip() for value in normalized):
        raise DomainError(f"{field_name} must contain only non-empty strings")
    if len(normalized) != len(set(normalized)):
        raise DomainError(f"{field_name} cannot contain duplicates")
    return normalized


def _immutable_mapping(values: Mapping[str, str] | None) -> Mapping[str, str]:
    normalized = dict(values or {})
    if not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in normalized.items()
    ):
        raise DomainError("metadata must contain non-empty string keys and values")
    return MappingProxyType(normalized)
