from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class CognitiveState:
    """Minimal persistible view of Roby's current cognitive state."""

    active_objective: str | None
    current_focus: str | None
    confidence: float
    last_decision: str | None
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.updated_at.tzinfo is None:
            raise ValueError("cognitive state timestamp must be timezone-aware")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("cognitive state confidence must be between zero and one")
        for field_name in ("active_objective", "current_focus", "last_decision"):
            value = getattr(self, field_name)
            if value is not None:
                normalized = value.strip()
                if not normalized:
                    raise ValueError(
                        f"cognitive state {field_name} must not be blank"
                    )
                object.__setattr__(self, field_name, normalized)

    @classmethod
    def empty(cls, *, updated_at: datetime) -> CognitiveState:
        return cls(
            active_objective=None,
            current_focus=None,
            confidence=0.0,
            last_decision=None,
            updated_at=updated_at,
        )

    @property
    def is_empty(self) -> bool:
        return (
            self.active_objective is None
            and self.current_focus is None
            and self.last_decision is None
            and self.confidence == 0.0
        )


@runtime_checkable
class CognitiveStateReader(Protocol):
    """Read-only boundary for future cognitive-state providers."""

    def snapshot(self) -> CognitiveState: ...
