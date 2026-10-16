from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from core.executive_event_model import ExecutiveEvent


class CoordinatorState(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"


class SubmissionStatus(str, Enum):
    ACCEPTED = "accepted"
    DUPLICATE = "duplicate"


@dataclass(frozen=True, slots=True)
class CoordinatedEvent:
    sequence: int
    accepted_at: datetime
    event: ExecutiveEvent

    def __post_init__(self) -> None:
        if self.sequence <= 0:
            raise ValueError("coordinated event sequence must be positive")
        if self.accepted_at.tzinfo is None:
            raise ValueError("accepted_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    status: SubmissionStatus | str
    coordinated_event: CoordinatedEvent | None = None

    def __post_init__(self) -> None:
        status = SubmissionStatus(self.status)
        if status is SubmissionStatus.ACCEPTED and self.coordinated_event is None:
            raise ValueError("accepted submissions require a coordinated event")
        if status is SubmissionStatus.DUPLICATE and self.coordinated_event is not None:
            raise ValueError("duplicate submissions cannot create a coordinated event")
        object.__setattr__(self, "status", status)

    @property
    def accepted(self) -> bool:
        return self.status is SubmissionStatus.ACCEPTED


@dataclass(frozen=True, slots=True)
class ExecutiveCoordinatorSnapshot:
    state: CoordinatorState | str
    pending_count: int
    accepted_count: int
    dispatched_count: int
    duplicate_count: int
    next_sequence: int
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    last_accepted_at: datetime | None = None
    last_dispatched_at: datetime | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        state = CoordinatorState(self.state)
        counters = (
            self.pending_count,
            self.accepted_count,
            self.dispatched_count,
            self.duplicate_count,
        )
        if min(counters) < 0:
            raise ValueError("coordinator counters must not be negative")
        if self.next_sequence <= 0:
            raise ValueError("next_sequence must be positive")
        if self.dispatched_count > self.accepted_count:
            raise ValueError("dispatched_count cannot exceed accepted_count")
        if self.pending_count != self.accepted_count - self.dispatched_count:
            raise ValueError("pending_count must match accepted minus dispatched")
        for value in (
            self.started_at,
            self.stopped_at,
            self.last_accepted_at,
            self.last_dispatched_at,
            self.updated_at,
        ):
            if value is not None and value.tzinfo is None:
                raise ValueError("coordinator times must be timezone-aware")
        object.__setattr__(self, "state", state)
