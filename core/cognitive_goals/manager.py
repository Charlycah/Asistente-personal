from __future__ import annotations

from datetime import datetime
from typing import Callable, Protocol, runtime_checkable

from core.cognitive_state_contract import CognitiveStateUpdate, CognitiveStateUpdater

from .models import CognitiveGoal, GoalCollection, GoalStatus
from .resolver import GoalResolver


@runtime_checkable
class GoalController(Protocol):
    def collection(self) -> GoalCollection: ...

    def primary_goal(self) -> CognitiveGoal | None: ...

    def add(self, goal: CognitiveGoal) -> CognitiveGoal: ...

    def remove(self, identifier: str) -> CognitiveGoal: ...


class GoalManager:
    """Manage explicit goals and mirror only the primary title to cognitive state."""

    def __init__(
        self,
        state_updater: CognitiveStateUpdater,
        resolver: GoalResolver,
        *,
        clock: Callable[[], datetime],
    ) -> None:
        self._state_updater = state_updater
        self._resolver = resolver
        self._clock = clock
        self._collection = GoalCollection()

    def collection(self) -> GoalCollection:
        return self._collection

    def all_goals(self) -> tuple[CognitiveGoal, ...]:
        return self._collection.all_goals()

    def active_goals(self) -> tuple[CognitiveGoal, ...]:
        return self._collection.active_goals()

    def primary_goal(self) -> CognitiveGoal | None:
        return self._resolver.resolve(self._collection)

    def add(self, goal: CognitiveGoal) -> CognitiveGoal:
        candidate = self._collection.add(goal)
        self._commit(candidate)
        return goal

    def remove(self, identifier: str) -> CognitiveGoal:
        goal = self._required(identifier)
        candidate = self._collection.remove(identifier)
        self._commit(candidate)
        return goal

    def pause(self, identifier: str) -> CognitiveGoal:
        return self._change_status(identifier, GoalStatus.PAUSED)

    def resume(self, identifier: str) -> CognitiveGoal:
        return self._change_status(identifier, GoalStatus.ACTIVE)

    def complete(self, identifier: str) -> CognitiveGoal:
        return self._change_status(identifier, GoalStatus.COMPLETED)

    def cancel(self, identifier: str) -> CognitiveGoal:
        return self._change_status(identifier, GoalStatus.CANCELLED)

    def _change_status(self, identifier: str, status: GoalStatus) -> CognitiveGoal:
        current = self._required(identifier)
        if current.status is status:
            return current
        updated = current.with_status(status, updated_at=self._now())
        candidate = self._collection.replace(updated)
        self._commit(candidate)
        return updated

    def _required(self, identifier: str) -> CognitiveGoal:
        goal = self._collection.get(identifier)
        if goal is None:
            missing = (
                identifier.strip() if isinstance(identifier, str) else identifier
            )
            raise KeyError(missing)
        return goal

    def _commit(self, candidate: GoalCollection) -> None:
        before = self._resolver.resolve(self._collection)
        after = self._resolver.resolve(candidate)
        before_title = None if before is None else before.title
        after_title = None if after is None else after.title
        if before_title != after_title:
            self._state_updater.update(
                CognitiveStateUpdate(active_objective=after_title)
            )
        self._collection = candidate

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime):
            raise TypeError("clock must return a datetime")
        if value.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value
