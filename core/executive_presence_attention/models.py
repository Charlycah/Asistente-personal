from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from core.executive_event_model import ExecutiveEvent


class PresenceState(str, Enum):
    UNKNOWN = "unknown"
    PRESENT = "present"
    AWAY = "away"


class AttentionState(str, Enum):
    AVAILABLE = "available"
    USER_SPEAKING = "user_speaking"
    USER_TYPING = "user_typing"
    ROBY_RESPONDING = "roby_responding"
    DO_NOT_DISTURB = "do_not_disturb"


class AttentionDisposition(str, Enum):
    DELIVER = "deliver"
    DEFER = "defer"
    SILENCE = "silence"


class AttentionReason(str, Enum):
    AVAILABLE = "available"
    CRITICAL_OVERRIDE = "critical_override"
    USER_BUSY = "user_busy"
    ROBY_BUSY = "roby_busy"
    USER_AWAY = "user_away"
    DO_NOT_DISTURB = "do_not_disturb"
    BEST_EFFORT_WHILE_AWAY = "best_effort_while_away"


@dataclass(frozen=True, slots=True)
class PresenceAttentionContext:
    presence: PresenceState | str = PresenceState.UNKNOWN
    attention: AttentionState | str = AttentionState.AVAILABLE
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        presence = PresenceState(self.presence)
        attention = AttentionState(self.attention)
        if self.observed_at.tzinfo is None:
            raise ValueError("presence observation must be timezone-aware")
        object.__setattr__(self, "presence", presence)
        object.__setattr__(self, "attention", attention)


@dataclass(frozen=True, slots=True)
class AttentionDecision:
    event: ExecutiveEvent
    disposition: AttentionDisposition | str
    reason: AttentionReason | str
    evaluated_at: datetime
    context: PresenceAttentionContext

    def __post_init__(self) -> None:
        disposition = AttentionDisposition(self.disposition)
        reason = AttentionReason(self.reason)
        if self.evaluated_at.tzinfo is None:
            raise ValueError("attention evaluation must be timezone-aware")
        object.__setattr__(self, "disposition", disposition)
        object.__setattr__(self, "reason", reason)


@dataclass(frozen=True, slots=True)
class PresenceAttentionSnapshot:
    context: PresenceAttentionContext
    update_count: int
    decision_count: int
    delivered_count: int
    deferred_count: int
    silenced_count: int
    last_decision_at: datetime | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        counters = (
            self.update_count,
            self.decision_count,
            self.delivered_count,
            self.deferred_count,
            self.silenced_count,
        )
        if min(counters) < 0:
            raise ValueError("attention counters must not be negative")
        if self.decision_count != sum(counters[2:]):
            raise ValueError("attention decisions must match disposition counters")
        for timestamp in (self.last_decision_at, self.updated_at):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError("attention timestamps must be timezone-aware")
