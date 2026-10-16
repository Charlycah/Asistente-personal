from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping, Sequence

from .exceptions import DomainError


class GovernedObjectiveState(StrEnum):
    """Canonical lifecycle for an objective remembered by the cognitive core."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass(frozen=True)
class GovernedObjective:
    """Immutable objective context; it grants no planning or execution authority."""

    objective_id: str
    owner: str
    description: str
    state: GovernedObjectiveState
    created_at: datetime
    updated_at: datetime
    plan_ids: tuple[str, ...] = ()
    context: tuple[str, ...] = ()
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        for field_name in ("objective_id", "owner", "description"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        if not isinstance(self.state, GovernedObjectiveState):
            raise DomainError("state must be a GovernedObjectiveState")
        for field_name in ("created_at", "updated_at"):
            value = getattr(self, field_name)
            if not isinstance(value, datetime) or value.tzinfo is None:
                raise DomainError(f"{field_name} must be timezone-aware")
        if self.updated_at < self.created_at:
            raise DomainError("updated_at cannot precede created_at")
        object.__setattr__(
            self,
            "plan_ids",
            _normalized_strings("plan_ids", self.plan_ids),
        )
        object.__setattr__(
            self,
            "context",
            _normalized_strings("context", self.context),
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


@dataclass(frozen=True)
class GovernedObjectiveMemorySnapshot:
    schema_version: str
    authority: str
    persistence_enabled: bool
    execution_enabled: bool
    autonomous_detection_enabled: bool
    conversation_authority: bool
    remembered_objectives: int
    active_objectives: int
    states: tuple[GovernedObjectiveState, ...]


class GovernedObjectiveMemory:
    """Gateway-owned continuity memory for explicit governed objectives."""

    SCHEMA_VERSION = "m346.7"
    AUTHORITY = (
        "domain.governed_objective_memory:GovernedObjectiveMemory"
    )

    def __init__(self) -> None:
        self._objectives: dict[str, GovernedObjective] = {}

    @property
    def snapshot(self) -> GovernedObjectiveMemorySnapshot:
        return GovernedObjectiveMemorySnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            persistence_enabled=False,
            execution_enabled=False,
            autonomous_detection_enabled=False,
            conversation_authority=False,
            remembered_objectives=len(self._objectives),
            active_objectives=sum(
                objective.state is GovernedObjectiveState.ACTIVE
                for objective in self._objectives.values()
            ),
            states=tuple(GovernedObjectiveState),
        )

    def remember(
        self,
        *,
        objective_id: str,
        owner: str,
        description: str,
        observed_at: datetime | None = None,
        plan_ids: Sequence[str] = (),
        context: Sequence[str] = (),
        metadata: Mapping[str, str] | None = None,
    ) -> GovernedObjective:
        if objective_id in self._objectives:
            raise DomainError(f"objective_id already remembered: {objective_id}")
        timestamp = _observed_at(observed_at)
        objective = GovernedObjective(
            objective_id=objective_id,
            owner=owner,
            description=description,
            state=GovernedObjectiveState.ACTIVE,
            created_at=timestamp,
            updated_at=timestamp,
            plan_ids=tuple(plan_ids),
            context=tuple(context),
            metadata=metadata,
        )
        self._objectives[objective.objective_id] = objective
        return objective

    def find(self, objective_id: str) -> GovernedObjective | None:
        return self._objectives.get(objective_id)

    def list_all(self) -> tuple[GovernedObjective, ...]:
        return tuple(self._objectives.values())

    def active(self, *, owner: str | None = None) -> tuple[GovernedObjective, ...]:
        return tuple(
            objective
            for objective in self._objectives.values()
            if objective.state is GovernedObjectiveState.ACTIVE
            and (owner is None or objective.owner == owner)
        )

    def set_state(
        self,
        objective_id: str,
        state: GovernedObjectiveState,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedObjective:
        if not isinstance(state, GovernedObjectiveState):
            raise DomainError("state must be a GovernedObjectiveState")
        current = self._require(objective_id)
        updated = replace(
            current,
            state=state,
            updated_at=_observed_at(observed_at),
        )
        self._objectives[objective_id] = updated
        return updated

    def link_plan(
        self,
        objective_id: str,
        plan_id: str,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedObjective:
        current = self._require(objective_id)
        if not isinstance(plan_id, str) or not plan_id.strip():
            raise DomainError("plan_id must be a non-empty string")
        if plan_id in current.plan_ids:
            return current
        updated = replace(
            current,
            plan_ids=(*current.plan_ids, plan_id),
            updated_at=_observed_at(observed_at),
        )
        self._objectives[objective_id] = updated
        return updated

    def _require(self, objective_id: str) -> GovernedObjective:
        objective = self.find(objective_id)
        if objective is None:
            raise DomainError(f"unknown objective_id: {objective_id}")
        return objective


def _observed_at(value: datetime | None) -> datetime:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise DomainError("observed_at must be timezone-aware")
    return timestamp


def _normalized_strings(field_name: str, values: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(values)
    if not all(isinstance(value, str) and value.strip() for value in normalized):
        raise DomainError(f"{field_name} must contain only non-empty strings")
    if len(normalized) != len(set(normalized)):
        raise DomainError(f"{field_name} cannot contain duplicates")
    return normalized
