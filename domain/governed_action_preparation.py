from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping, Sequence

from .exceptions import DomainError
from .governed_objective_memory import GovernedObjective, GovernedObjectiveState
from .governed_plan import GovernedPlan, GovernedPlanStep


class GovernedActionKind(StrEnum):
    """Descriptive action families; none grants execution authority."""

    COMMUNICATION = "communication"
    CALENDAR = "calendar"
    DOCUMENT = "document"
    INFORMATION = "information"
    OTHER = "other"


@dataclass(frozen=True)
class GovernedActionCandidate:
    """Immutable preparation record awaiting an explicit future authorization."""

    action_id: str
    objective_id: str
    plan_id: str
    plan_revision: int
    step_id: str
    description: str
    kind: GovernedActionKind
    required_authorizations: tuple[str, ...]
    parameters: Mapping[str, str] | None = None
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "action_id",
            "objective_id",
            "plan_id",
            "step_id",
            "description",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        if (
            not isinstance(self.plan_revision, int)
            or isinstance(self.plan_revision, bool)
            or self.plan_revision < 1
        ):
            raise DomainError("plan_revision must be a positive integer")
        if not isinstance(self.kind, GovernedActionKind):
            raise DomainError("kind must be a GovernedActionKind")
        authorizations = _normalized_strings(
            "required_authorizations", self.required_authorizations
        )
        if not authorizations:
            raise DomainError("an action candidate must require authorization")
        object.__setattr__(self, "required_authorizations", authorizations)
        object.__setattr__(
            self,
            "parameters",
            _immutable_mapping("parameters", self.parameters),
        )
        object.__setattr__(
            self,
            "metadata",
            _immutable_mapping("metadata", self.metadata),
        )


@dataclass(frozen=True)
class GovernedActionPreparationSnapshot:
    schema_version: str
    authority: str
    persistence_enabled: bool
    execution_enabled: bool
    authorization_enabled: bool
    autonomous_preparation_enabled: bool
    conversation_authority: bool
    prepared_candidates: int
    kinds: tuple[GovernedActionKind, ...]


class GovernedActionPreparation:
    """Gateway-owned authority for non-executing action candidates."""

    SCHEMA_VERSION = "m346.9"
    AUTHORITY = (
        "domain.governed_action_preparation:GovernedActionPreparation"
    )

    def __init__(self) -> None:
        self._candidates: dict[str, GovernedActionCandidate] = {}

    @property
    def snapshot(self) -> GovernedActionPreparationSnapshot:
        return GovernedActionPreparationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            persistence_enabled=False,
            execution_enabled=False,
            authorization_enabled=False,
            autonomous_preparation_enabled=False,
            conversation_authority=False,
            prepared_candidates=len(self._candidates),
            kinds=tuple(GovernedActionKind),
        )

    def prepare(
        self,
        objective: GovernedObjective,
        plan: GovernedPlan,
        *,
        action_id: str,
        step_id: str,
        description: str,
        kind: GovernedActionKind,
        required_authorizations: Sequence[str] = (),
        parameters: Mapping[str, str] | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> GovernedActionCandidate:
        if objective.state is GovernedObjectiveState.COMPLETED:
            raise DomainError("completed objectives cannot prepare actions")
        if plan.plan_id not in objective.plan_ids:
            raise DomainError("objective must link the plan before action preparation")
        if action_id in self._candidates:
            raise DomainError(f"action_id already prepared: {action_id}")
        step = _require_step(plan, step_id)
        authorizations = tuple(required_authorizations)
        if not authorizations:
            authorizations = plan.required_authorizations
        if not authorizations and step.requires_authorization:
            authorizations = ("explicit_user_authorization",)
        if not authorizations:
            raise DomainError("action preparation requires explicit authorization")
        candidate = GovernedActionCandidate(
            action_id=action_id,
            objective_id=objective.objective_id,
            plan_id=plan.plan_id,
            plan_revision=plan.revision,
            step_id=step.step_id,
            description=description,
            kind=kind,
            required_authorizations=authorizations,
            parameters=parameters,
            metadata=metadata,
        )
        self._candidates[action_id] = candidate
        return candidate

    def find(self, action_id: str) -> GovernedActionCandidate | None:
        return self._candidates.get(action_id)

    def for_plan(
        self, objective_id: str, plan_id: str
    ) -> tuple[GovernedActionCandidate, ...]:
        return tuple(
            candidate
            for candidate in self._candidates.values()
            if candidate.objective_id == objective_id
            and candidate.plan_id == plan_id
        )


def _require_step(plan: GovernedPlan, step_id: str) -> GovernedPlanStep:
    if not isinstance(step_id, str) or not step_id.strip():
        raise DomainError("step_id must be a non-empty string")
    for step in plan.steps:
        if step.step_id == step_id:
            return step
    raise DomainError("step_id must reference a current plan step")


def _normalized_strings(field_name: str, values: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(values)
    if not all(isinstance(value, str) and value.strip() for value in normalized):
        raise DomainError(f"{field_name} must contain only non-empty strings")
    if len(normalized) != len(set(normalized)):
        raise DomainError(f"{field_name} cannot contain duplicates")
    return normalized


def _immutable_mapping(
    field_name: str, values: Mapping[str, str] | None
) -> Mapping[str, str]:
    normalized = dict(values or {})
    if not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in normalized.items()
    ):
        raise DomainError(
            f"{field_name} must contain non-empty string keys and values"
        )
    return MappingProxyType(normalized)
