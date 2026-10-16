from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from enum import Enum
from typing import Protocol
from uuid import uuid4


class GoalStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class HouseholdGoal:
    name: str
    description: str = ""
    status: GoalStatus | str = GoalStatus.ACTIVE
    progress_percent: int = 0
    target_date: date | None = None
    linked_project: str = ""
    linked_routine: str = ""
    next_step: str = ""
    notes: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    goal_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("goal name must not be empty")
        GoalStatus(self.status)
        if not 0 <= self.progress_percent <= 100:
            raise ValueError("goal progress must be between 0 and 100")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("goal timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("goal update cannot precede creation")

    @property
    def normalized_status(self) -> GoalStatus:
        return GoalStatus(self.status)


class HouseholdGoalRepository(Protocol):
    def save(self, goal: HouseholdGoal) -> HouseholdGoal: ...

    def get(self, goal_id: str) -> HouseholdGoal | None: ...

    def list_all(self) -> tuple[HouseholdGoal, ...]: ...


class HouseholdGoalManager:
    def __init__(self, repository: HouseholdGoalRepository) -> None:
        self.repository = repository

    def create(
        self,
        name: str,
        *,
        description: str,
        now: datetime,
        target_date: date | None = None,
    ) -> HouseholdGoal:
        return self.repository.save(
            HouseholdGoal(
                name=name.strip(),
                description=description.strip(),
                target_date=target_date,
                created_at=now,
                updated_at=now,
            )
        )

    def list(self, *, include_archived: bool = False) -> tuple[HouseholdGoal, ...]:
        goals = self.repository.list_all()
        if include_archived:
            return goals
        return tuple(g for g in goals if g.normalized_status is not GoalStatus.ARCHIVED)

    def find(self, query: str) -> HouseholdGoal | None:
        folded = query.strip().casefold()
        matches = [
            goal
            for goal in self.repository.list_all()
            if folded in goal.name.casefold() or folded in goal.description.casefold()
        ]
        return matches[-1] if matches else None

    def set_progress(
        self, goal_id: str, progress_percent: int, *, now: datetime
    ) -> HouseholdGoal:
        status = GoalStatus.COMPLETED if progress_percent == 100 else None
        changes: dict[str, object] = {"progress_percent": progress_percent}
        if status is not None:
            changes["status"] = status
        return self._update(goal_id, now=now, **changes)

    def set_next_step(self, goal_id: str, step: str, *, now: datetime) -> HouseholdGoal:
        return self._update(goal_id, now=now, next_step=step.strip())

    def link_project(
        self, goal_id: str, project_name: str, *, now: datetime
    ) -> HouseholdGoal:
        return self._update(goal_id, now=now, linked_project=project_name.strip())

    def link_routine(
        self, goal_id: str, routine_name: str, *, now: datetime
    ) -> HouseholdGoal:
        return self._update(goal_id, now=now, linked_routine=routine_name.strip())

    def add_note(self, goal_id: str, note: str, *, now: datetime) -> HouseholdGoal:
        current = self._require(goal_id)
        return self._update(goal_id, now=now, notes=(*current.notes, note.strip()))

    def change_status(
        self, goal_id: str, status: GoalStatus, *, now: datetime
    ) -> HouseholdGoal:
        progress = (
            100
            if status is GoalStatus.COMPLETED
            else self._require(goal_id).progress_percent
        )
        return self._update(goal_id, now=now, status=status, progress_percent=progress)

    def _update(self, goal_id: str, *, now: datetime, **changes) -> HouseholdGoal:
        current = self._require(goal_id)
        updated = replace(current, updated_at=now, **changes)
        return self.repository.save(updated)

    def _require(self, goal_id: str) -> HouseholdGoal:
        goal = self.repository.get(goal_id)
        if goal is None:
            raise KeyError(goal_id)
        return goal
