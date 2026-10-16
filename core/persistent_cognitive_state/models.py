from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class PersistentCognitiveState:
    """Minimal cognitive state that can survive process restarts."""

    active_objective: str | None = None
    current_focus: str | None = None
    confidence: float = 0.0
    last_decision: str | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        objective = self._clean(self.active_objective)
        focus = self._clean(self.current_focus)
        decision = self._clean(self.last_decision)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("cognitive state confidence must be between 0 and 1")
        if self.updated_at is not None and self.updated_at.tzinfo is None:
            raise ValueError("cognitive state timestamp must be timezone-aware")
        object.__setattr__(self, "active_objective", objective)
        object.__setattr__(self, "current_focus", focus)
        object.__setattr__(self, "last_decision", decision)

    @classmethod
    def empty(cls) -> PersistentCognitiveState:
        return cls()

    def with_updates(
        self,
        *,
        active_objective: str | None = None,
        current_focus: str | None = None,
        confidence: float | None = None,
        last_decision: str | None = None,
        updated_at: datetime | None = None,
    ) -> PersistentCognitiveState:
        timestamp = updated_at or datetime.now(timezone.utc)
        return replace(
            self,
            active_objective=(
                self.active_objective
                if active_objective is None
                else active_objective
            ),
            current_focus=(
                self.current_focus if current_focus is None else current_focus
            ),
            confidence=self.confidence if confidence is None else confidence,
            last_decision=(
                self.last_decision if last_decision is None else last_decision
            ),
            updated_at=timestamp,
        )

    @staticmethod
    def _clean(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None
