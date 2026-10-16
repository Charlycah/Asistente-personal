from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Protocol, runtime_checkable
from uuid import uuid4


class GoalStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class PersistentGoal:
    goal_id: str
    title: str
    description: str
    priority: float
    status: GoalStatus
    created_at: datetime
    updated_at: datetime
    review_at: datetime | None = None
    source: str = "runtime"
    progress_summary: str = "Goal created"

    def __post_init__(self) -> None:
        if not self.goal_id.strip():
            raise ValueError("goal id must not be blank")
        if not self.title.strip():
            raise ValueError("goal title must not be blank")
        if not self.description.strip():
            raise ValueError("goal description must not be blank")
        if not 0.0 <= self.priority <= 1.0:
            raise ValueError("goal priority must be between 0 and 1")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("goal timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("goal update cannot predate creation")
        if self.review_at is not None and self.review_at.tzinfo is None:
            raise ValueError("goal review timestamp must be timezone-aware")
        if not self.source.strip():
            raise ValueError("goal source must not be blank")
        if not self.progress_summary.strip():
            raise ValueError("goal progress summary must not be blank")


@dataclass(frozen=True, slots=True)
class PersistentGoalSnapshot:
    goals: tuple[PersistentGoal, ...]
    observed_at: datetime | None = None

    @property
    def active_count(self) -> int:
        return sum(goal.status is GoalStatus.ACTIVE for goal in self.goals)

    @property
    def due_for_review_count(self) -> int:
        if self.observed_at is None:
            return 0
        return sum(
            goal.status is GoalStatus.ACTIVE
            and goal.review_at is not None
            and goal.review_at <= self.observed_at
            for goal in self.goals
        )


@runtime_checkable
class PersistentGoalStore(Protocol):
    def create(
        self,
        *,
        title: str,
        description: str,
        priority: float,
        created_at: datetime,
        review_at: datetime | None = None,
        source: str = "runtime",
    ) -> PersistentGoal: ...

    def update(
        self,
        goal_id: str,
        *,
        updated_at: datetime,
        status: GoalStatus | str | None = None,
        priority: float | None = None,
        review_at: datetime | None = None,
        progress_summary: str | None = None,
    ) -> PersistentGoal: ...

    def snapshot(self, *, now: datetime | None = None) -> PersistentGoalSnapshot: ...


class JsonPersistentGoalStore:
    """Durable, atomic store for long-lived runtime goals."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._goals = self._load()

    def create(
        self,
        *,
        title: str,
        description: str,
        priority: float,
        created_at: datetime,
        review_at: datetime | None = None,
        source: str = "runtime",
    ) -> PersistentGoal:
        goal = PersistentGoal(
            goal_id=uuid4().hex,
            title=title,
            description=description,
            priority=priority,
            status=GoalStatus.ACTIVE,
            created_at=created_at,
            updated_at=created_at,
            review_at=review_at,
            source=source,
        )
        with self._lock:
            updated = dict(self._goals)
            updated[goal.goal_id] = goal
            self._persist(updated)
            self._goals = updated
        return goal

    def update(
        self,
        goal_id: str,
        *,
        updated_at: datetime,
        status: GoalStatus | str | None = None,
        priority: float | None = None,
        review_at: datetime | None = None,
        progress_summary: str | None = None,
    ) -> PersistentGoal:
        with self._lock:
            previous = self._goals.get(goal_id)
            if previous is None:
                raise KeyError(f"unknown persistent goal: {goal_id}")
            resolved_status = previous.status if status is None else GoalStatus(status)
            goal = PersistentGoal(
                goal_id=previous.goal_id,
                title=previous.title,
                description=previous.description,
                priority=previous.priority if priority is None else priority,
                status=resolved_status,
                created_at=previous.created_at,
                updated_at=updated_at,
                review_at=review_at,
                source=previous.source,
                progress_summary=(
                    previous.progress_summary
                    if progress_summary is None
                    else progress_summary
                ),
            )
            updated = dict(self._goals)
            updated[goal_id] = goal
            self._persist(updated)
            self._goals = updated
            return goal

    def snapshot(self, *, now: datetime | None = None) -> PersistentGoalSnapshot:
        with self._lock:
            goals = tuple(
                sorted(
                    self._goals.values(),
                    key=lambda goal: (-goal.priority, goal.created_at, goal.goal_id),
                )
            )
        if now is None:
            return PersistentGoalSnapshot(goals)
        due = tuple(
            goal
            for goal in goals
            if goal.status is GoalStatus.ACTIVE
            and goal.review_at is not None
            and goal.review_at <= now
        )
        not_due = tuple(goal for goal in goals if goal not in due)
        return PersistentGoalSnapshot(due + not_due, observed_at=now)

    def _persist(self, goals: dict[str, PersistentGoal]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": 1,
            "goals": [_goal_to_payload(goal) for goal in goals.values()],
        }
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                payload,
                stream,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)

    def _load(self) -> dict[str, PersistentGoal]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload["schema_version"] != 1:
                raise ValueError("unsupported persistent goal schema version")
            goals = tuple(_goal_from_payload(item) for item in payload["goals"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("invalid persistent goal file") from exc
        keyed = {goal.goal_id: goal for goal in goals}
        if len(keyed) != len(goals):
            raise ValueError("persistent goal file contains duplicate ids")
        return keyed


def _goal_to_payload(goal: PersistentGoal) -> dict[str, object]:
    return {
        "goal_id": goal.goal_id,
        "title": goal.title,
        "description": goal.description,
        "priority": goal.priority,
        "status": goal.status.value,
        "created_at": goal.created_at.isoformat(),
        "updated_at": goal.updated_at.isoformat(),
        "review_at": goal.review_at.isoformat() if goal.review_at else None,
        "source": goal.source,
        "progress_summary": goal.progress_summary,
    }


def _goal_from_payload(payload: dict[str, object]) -> PersistentGoal:
    review_at = payload["review_at"]
    return PersistentGoal(
        goal_id=str(payload["goal_id"]),
        title=str(payload["title"]),
        description=str(payload["description"]),
        priority=float(payload["priority"]),
        status=GoalStatus(str(payload["status"])),
        created_at=datetime.fromisoformat(str(payload["created_at"])),
        updated_at=datetime.fromisoformat(str(payload["updated_at"])),
        review_at=(datetime.fromisoformat(str(review_at)) if review_at else None),
        source=str(payload["source"]),
        progress_summary=str(payload["progress_summary"]),
    )


__all__ = [
    "GoalStatus",
    "JsonPersistentGoalStore",
    "PersistentGoal",
    "PersistentGoalSnapshot",
    "PersistentGoalStore",
]
