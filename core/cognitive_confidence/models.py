from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ConfidenceLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

    @property
    def score(self) -> float:
        return {
            ConfidenceLevel.VERY_LOW: 0.1,
            ConfidenceLevel.LOW: 0.3,
            ConfidenceLevel.MEDIUM: 0.5,
            ConfidenceLevel.HIGH: 0.75,
            ConfidenceLevel.VERY_HIGH: 0.95,
        }[self]

    @classmethod
    def from_score(cls, score: float) -> ConfidenceLevel:
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            raise TypeError("confidence score must be a number")
        value = float(score)
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence score must be between zero and one")
        return min(cls, key=lambda level: abs(level.score - value))


@dataclass(frozen=True, slots=True)
class Confidence:
    """Explicit confidence assessment with derived uncertainty."""

    level: ConfidenceLevel
    reason: str
    updated_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.level, ConfidenceLevel):
            raise TypeError("confidence level must be a ConfidenceLevel")
        reason = self.reason.strip()
        if not reason:
            raise ValueError("confidence reason must not be blank")
        object.__setattr__(self, "reason", reason)
        if not isinstance(self.updated_at, datetime):
            raise TypeError("confidence updated_at must be a datetime")
        if self.updated_at.tzinfo is None:
            raise ValueError("confidence updated_at must be timezone-aware")

    @property
    def score(self) -> float:
        return self.level.score

    @property
    def uncertainty(self) -> float:
        return round(1.0 - self.score, 10)
