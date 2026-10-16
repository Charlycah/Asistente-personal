from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping, Sequence

from .exceptions import DomainError


class GovernedPlanState(StrEnum):
    """Canonical non-executing lifecycle state for a cognitive plan."""

    DRAFT = "draft"
    PROPOSED = "proposed"


@dataclass(frozen=True)
class GovernedPlanStep:
    """One ordered, descriptive step; it never performs an action."""

    step_id: str
    order: int
    description: str
    depends_on: tuple[str, ...] = ()
    requires_authorization: bool = False

    def __post_init__(self) -> None:
        for field_name in ("step_id", "description"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        if (
            not isinstance(self.order, int)
            or isinstance(self.order, bool)
            or self.order < 1
        ):
            raise DomainError("order must be a positive integer")
        dependencies = _normalized_strings("depends_on", self.depends_on)
        if self.step_id in dependencies:
            raise DomainError("a plan step cannot depend on itself")
        object.__setattr__(self, "depends_on", dependencies)
        if not isinstance(self.requires_authorization, bool):
            raise DomainError("requires_authorization must be a bool")


@dataclass(frozen=True)
class GovernedPlan:
    """Immutable cognitive plan with no persistence or execution authority."""

    plan_id: str
    objective: str
    current_state: str
    steps: tuple[GovernedPlanStep, ...]
    expected_outcome: str
    confidence: int
    assumptions: tuple[str, ...] = ()
    missing_information: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    required_authorizations: tuple[str, ...] = ()
    state: GovernedPlanState = GovernedPlanState.DRAFT
    metadata: Mapping[str, str] | None = None
    revision: int = 1
    supersedes_revision: int | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "plan_id",
            "objective",
            "current_state",
            "expected_outcome",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        if not isinstance(self.state, GovernedPlanState):
            raise DomainError("state must be a GovernedPlanState")
        if not isinstance(self.confidence, int) or isinstance(self.confidence, bool):
            raise DomainError("confidence must be an integer")
        if not 0 <= self.confidence <= 100:
            raise DomainError("confidence must be between 0 and 100")
        if (
            not isinstance(self.revision, int)
            or isinstance(self.revision, bool)
            or self.revision < 1
        ):
            raise DomainError("revision must be a positive integer")
        if self.supersedes_revision is not None:
            if (
                not isinstance(self.supersedes_revision, int)
                or isinstance(self.supersedes_revision, bool)
                or self.supersedes_revision < 1
            ):
                raise DomainError("supersedes_revision must be a positive integer")
            if self.supersedes_revision >= self.revision:
                raise DomainError("supersedes_revision must precede revision")

        steps = tuple(self.steps)
        if not steps:
            raise DomainError("steps must contain at least one GovernedPlanStep")
        if not all(isinstance(step, GovernedPlanStep) for step in steps):
            raise DomainError("steps must contain only GovernedPlanStep values")
        step_ids = tuple(step.step_id for step in steps)
        if len(step_ids) != len(set(step_ids)):
            raise DomainError("plan step ids must be unique")
        orders = tuple(step.order for step in steps)
        if len(orders) != len(set(orders)):
            raise DomainError("plan step orders must be unique")
        if orders != tuple(sorted(orders)):
            raise DomainError("plan steps must be ordered by ascending order")
        known_ids = set(step_ids)
        for step in steps:
            unknown = set(step.depends_on) - known_ids
            if unknown:
                raise DomainError("plan step dependencies must reference known steps")
            dependency_orders = {
                candidate.step_id: candidate.order for candidate in steps
            }
            if any(dependency_orders[item] >= step.order for item in step.depends_on):
                raise DomainError("plan steps may depend only on earlier steps")
        object.__setattr__(self, "steps", steps)

        for field_name in (
            "assumptions",
            "missing_information",
            "dependencies",
            "risks",
            "required_authorizations",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalized_strings(field_name, getattr(self, field_name)),
            )
        metadata = dict(self.metadata or {})
        if not all(
            isinstance(key, str)
            and key.strip()
            and isinstance(value, str)
            and value.strip()
            for key, value in metadata.items()
        ):
            raise DomainError("metadata must contain non-empty string keys and values")
        object.__setattr__(self, "metadata", MappingProxyType(metadata))

    @property
    def requires_authorization(self) -> bool:
        return bool(self.required_authorizations) or any(
            step.requires_authorization for step in self.steps
        )


@dataclass(frozen=True)
class GovernedPlanModelSnapshot:
    schema_version: str
    authority: str
    persistence_enabled: bool
    execution_enabled: bool
    autonomous_planning_enabled: bool
    conversation_authority: bool
    states: tuple[GovernedPlanState, ...]


class GovernedPlanModel:
    """Single model authority for valid governed cognitive plans."""

    SCHEMA_VERSION = "m346.6"
    AUTHORITY = "domain.governed_plan:GovernedPlanModel"

    @property
    def snapshot(self) -> GovernedPlanModelSnapshot:
        return GovernedPlanModelSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            persistence_enabled=False,
            execution_enabled=False,
            autonomous_planning_enabled=False,
            conversation_authority=False,
            states=tuple(GovernedPlanState),
        )

    def create(
        self,
        *,
        plan_id: str,
        objective: str,
        current_state: str,
        steps: Sequence[GovernedPlanStep],
        expected_outcome: str,
        confidence: int,
        assumptions: Sequence[str] = (),
        missing_information: Sequence[str] = (),
        dependencies: Sequence[str] = (),
        risks: Sequence[str] = (),
        required_authorizations: Sequence[str] = (),
        state: GovernedPlanState = GovernedPlanState.DRAFT,
        metadata: Mapping[str, str] | None = None,
        revision: int = 1,
        supersedes_revision: int | None = None,
    ) -> GovernedPlan:
        return GovernedPlan(
            plan_id=plan_id,
            objective=objective,
            current_state=current_state,
            steps=tuple(steps),
            expected_outcome=expected_outcome,
            confidence=confidence,
            assumptions=tuple(assumptions),
            missing_information=tuple(missing_information),
            dependencies=tuple(dependencies),
            risks=tuple(risks),
            required_authorizations=tuple(required_authorizations),
            state=state,
            metadata=metadata,
            revision=revision,
            supersedes_revision=supersedes_revision,
        )


def _normalized_strings(field_name: str, values: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(values)
    if not all(isinstance(value, str) and value.strip() for value in normalized):
        raise DomainError(f"{field_name} must contain only non-empty strings")
    if len(normalized) != len(set(normalized)):
        raise DomainError(f"{field_name} cannot contain duplicates")
    return normalized
