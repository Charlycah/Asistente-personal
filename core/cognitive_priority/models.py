from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.cognitive_confidence import ConfidenceLevel
from core.cognitive_goals import CognitiveGoal


class PriorityReason(str, Enum):
    GOAL_PRIORITY = "goal_priority"
    FOCUS_ALIGNMENT = "focus_alignment"
    OLDEST_GOAL = "oldest_goal"
    STABLE_IDENTIFIER = "stable_identifier"


@dataclass(frozen=True, slots=True)
class PriorityDecision:
    """Deterministic and explainable cognitive priority result."""

    goal: CognitiveGoal | None
    reason: PriorityReason | None
    confidence_level: ConfidenceLevel
    considered_goal_ids: tuple[str, ...]
    focus_aligned: bool = False

    def __post_init__(self) -> None:
        if self.goal is not None and not isinstance(self.goal, CognitiveGoal):
            raise TypeError("priority goal must be a CognitiveGoal or None")
        if self.reason is not None and not isinstance(self.reason, PriorityReason):
            raise TypeError("priority reason must be a PriorityReason or None")
        if not isinstance(self.confidence_level, ConfidenceLevel):
            raise TypeError("confidence_level must be a ConfidenceLevel")
        if not isinstance(self.considered_goal_ids, tuple):
            raise TypeError("considered_goal_ids must be a tuple")
        invalid_ids = any(
            not isinstance(item, str) or not item
            for item in self.considered_goal_ids
        )
        if invalid_ids:
            raise ValueError("considered goal identifiers must be non-empty strings")
        if not isinstance(self.focus_aligned, bool):
            raise TypeError("focus_aligned must be a bool")
        if self.goal is None:
            if self.reason is not None or self.focus_aligned:
                raise ValueError(
                    "empty decisions cannot have a reason or focus alignment"
                )
        elif self.reason is None:
            raise ValueError("non-empty decisions require a reason")

    @property
    def selected_goal_id(self) -> str | None:
        return None if self.goal is None else self.goal.identifier
