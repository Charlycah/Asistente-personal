from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import CognitiveGoal, GoalCollection


@runtime_checkable
class GoalResolver(Protocol):
    def resolve(self, goals: GoalCollection) -> CognitiveGoal | None: ...


class PriorityGoalResolver:
    """Select the highest-priority active goal, then the oldest one."""

    def resolve(self, goals: GoalCollection) -> CognitiveGoal | None:
        if not isinstance(goals, GoalCollection):
            raise TypeError("goals must be a GoalCollection")
        active = goals.active_goals()
        if not active:
            return None
        return min(
            active,
            key=lambda goal: (
                -goal.priority.value,
                goal.created_at,
                goal.identifier,
            ),
        )
