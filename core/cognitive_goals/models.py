from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum


class GoalStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GoalPriority(int, Enum):
    LOW = 10
    MEDIUM = 20
    HIGH = 30
    CRITICAL = 40


@dataclass(frozen=True, slots=True)
class CognitiveGoal:
    """One explicit cognitive objective managed without autonomous execution."""

    identifier: str
    title: str
    description: str | None
    priority: GoalPriority
    status: GoalStatus
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        for field_name in ("identifier", "title"):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"goal {field_name} must be a string")
            normalized = value.strip()
            if not normalized:
                raise ValueError(f"goal {field_name} must not be blank")
            object.__setattr__(self, field_name, normalized)
        if self.description is not None:
            if not isinstance(self.description, str):
                raise TypeError("goal description must be a string or None")
            description = self.description.strip()
            if not description:
                raise ValueError("goal description must not be blank")
            object.__setattr__(self, "description", description)
        if not isinstance(self.priority, GoalPriority):
            raise TypeError("goal priority must be a GoalPriority")
        if not isinstance(self.status, GoalStatus):
            raise TypeError("goal status must be a GoalStatus")
        for field_name in ("created_at", "updated_at"):
            value = getattr(self, field_name)
            if not isinstance(value, datetime):
                raise TypeError(f"goal {field_name} must be a datetime")
            if value.tzinfo is None:
                raise ValueError(f"goal {field_name} must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("goal updated_at must not precede created_at")

    @property
    def is_selectable(self) -> bool:
        return self.status is GoalStatus.ACTIVE

    def with_status(self, status: GoalStatus, *, updated_at: datetime) -> CognitiveGoal:
        if not isinstance(status, GoalStatus):
            raise TypeError("status must be a GoalStatus")
        return replace(self, status=status, updated_at=updated_at)


@dataclass(frozen=True, slots=True)
class GoalCollection:
    """Immutable collection of cognitive goals with unique identifiers."""

    goals: tuple[CognitiveGoal, ...] = ()

    def __post_init__(self) -> None:
        identifiers: set[str] = set()
        for goal in self.goals:
            if not isinstance(goal, CognitiveGoal):
                raise TypeError("goal collection items must be CognitiveGoal values")
            if goal.identifier in identifiers:
                raise ValueError("goal identifiers must be unique")
            identifiers.add(goal.identifier)

    def all_goals(self) -> tuple[CognitiveGoal, ...]:
        return self.goals

    def active_goals(self) -> tuple[CognitiveGoal, ...]:
        return tuple(goal for goal in self.goals if goal.is_selectable)

    def get(self, identifier: str) -> CognitiveGoal | None:
        normalized = _normalized_identifier(identifier)
        return next(
            (goal for goal in self.goals if goal.identifier == normalized),
            None,
        )

    def add(self, goal: CognitiveGoal) -> GoalCollection:
        if not isinstance(goal, CognitiveGoal):
            raise TypeError("goal must be a CognitiveGoal")
        if self.get(goal.identifier) is not None:
            raise ValueError(f"goal {goal.identifier!r} already exists")
        return GoalCollection((*self.goals, goal))

    def remove(self, identifier: str) -> GoalCollection:
        normalized = _normalized_identifier(identifier)
        if self.get(normalized) is None:
            raise KeyError(normalized)
        return GoalCollection(
            tuple(goal for goal in self.goals if goal.identifier != normalized)
        )

    def replace(self, goal: CognitiveGoal) -> GoalCollection:
        if not isinstance(goal, CognitiveGoal):
            raise TypeError("goal must be a CognitiveGoal")
        if self.get(goal.identifier) is None:
            raise KeyError(goal.identifier)
        return GoalCollection(
            tuple(
                goal if current.identifier == goal.identifier else current
                for current in self.goals
            )
        )


def _normalized_identifier(identifier: str) -> str:
    if not isinstance(identifier, str):
        raise TypeError("goal identifier must be a string")
    normalized = identifier.strip()
    if not normalized:
        raise ValueError("goal identifier must not be blank")
    return normalized
