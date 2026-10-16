from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.cognitive_confidence import ConfidenceLevel
from core.cognitive_focus import Focus
from core.cognitive_goals import CognitiveGoal, GoalCollection

from .models import PriorityDecision, PriorityReason


@runtime_checkable
class PriorityPolicy(Protocol):
    def decide(
        self,
        goals: GoalCollection,
        *,
        focus: Focus | None,
        confidence_level: ConfidenceLevel,
    ) -> PriorityDecision: ...


class DeterministicPriorityPolicy:
    """Prioritize active goals without inference, learning, or side effects."""

    def decide(
        self,
        goals: GoalCollection,
        *,
        focus: Focus | None,
        confidence_level: ConfidenceLevel,
    ) -> PriorityDecision:
        if not isinstance(goals, GoalCollection):
            raise TypeError("goals must be a GoalCollection")
        if focus is not None and not isinstance(focus, Focus):
            raise TypeError("focus must be a Focus or None")
        if not isinstance(confidence_level, ConfidenceLevel):
            raise TypeError("confidence_level must be a ConfidenceLevel")

        active = goals.active_goals()
        considered = tuple(goal.identifier for goal in active)
        if not active:
            return PriorityDecision(None, None, confidence_level, considered)

        highest = max(goal.priority.value for goal in active)
        candidates = tuple(goal for goal in active if goal.priority.value == highest)
        if len(candidates) == 1:
            return self._decision(
                candidates[0],
                PriorityReason.GOAL_PRIORITY,
                confidence_level,
                considered,
                focus,
            )

        focused = self._focused_candidate(candidates, focus)
        if focused is not None:
            return PriorityDecision(
                focused,
                PriorityReason.FOCUS_ALIGNMENT,
                confidence_level,
                considered,
                focus_aligned=True,
            )

        oldest_time = min(goal.created_at for goal in candidates)
        oldest = tuple(goal for goal in candidates if goal.created_at == oldest_time)
        if len(oldest) == 1:
            return PriorityDecision(
                oldest[0],
                PriorityReason.OLDEST_GOAL,
                confidence_level,
                considered,
            )

        selected = min(oldest, key=lambda goal: goal.identifier)
        return PriorityDecision(
            selected,
            PriorityReason.STABLE_IDENTIFIER,
            confidence_level,
            considered,
        )

    @staticmethod
    def _focused_candidate(
        candidates: tuple[CognitiveGoal, ...],
        focus: Focus | None,
    ) -> CognitiveGoal | None:
        if focus is None:
            return None
        matches = tuple(
            goal
            for goal in candidates
            if goal.identifier == focus.identifier or goal.title == focus.title
        )
        if not matches:
            return None
        return min(matches, key=lambda goal: (goal.created_at, goal.identifier))

    @staticmethod
    def _decision(
        goal: CognitiveGoal,
        reason: PriorityReason,
        confidence_level: ConfidenceLevel,
        considered: tuple[str, ...],
        focus: Focus | None,
    ) -> PriorityDecision:
        aligned = focus is not None and (
            goal.identifier == focus.identifier or goal.title == focus.title
        )
        return PriorityDecision(
            goal,
            reason,
            confidence_level,
            considered,
            focus_aligned=aligned,
        )
