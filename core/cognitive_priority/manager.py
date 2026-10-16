from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.cognitive_confidence import ConfidenceLevel
from core.cognitive_focus import Focus
from core.cognitive_goals import GoalCollection

from .models import PriorityDecision
from .policy import PriorityPolicy


@runtime_checkable
class PriorityResolver(Protocol):
    def resolve(
        self,
        goals: GoalCollection,
        *,
        focus: Focus | None,
        confidence_level: ConfidenceLevel,
    ) -> PriorityDecision: ...


class PriorityManager:
    """Evaluate cognitive priority explicitly and without mutating inputs."""

    def __init__(self, policy: PriorityPolicy) -> None:
        if not isinstance(policy, PriorityPolicy):
            raise TypeError("policy must implement PriorityPolicy")
        self._policy = policy

    def resolve(
        self,
        goals: GoalCollection,
        *,
        focus: Focus | None = None,
        confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM,
    ) -> PriorityDecision:
        return self._policy.decide(
            goals,
            focus=focus,
            confidence_level=confidence_level,
        )
