from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from core.executive_coordinator import CoordinatedEvent
from core.executive_event_model import ExecutiveEvent


class BrokerSubmissionStatus(str, Enum):
    ACCEPTED = "accepted"
    DUPLICATE = "duplicate"
    SILENCED = "silenced"
    EXPIRED = "expired"


class DeliveryState(str, Enum):
    QUEUED = "queued"
    DISPATCHING = "dispatching"
    DISPATCHED = "dispatched"
    EXPIRED = "expired"
    DUPLICATE = "duplicate"
    SILENCED = "silenced"


@dataclass(frozen=True, slots=True)
class BrokeredEvent:
    coordinated_event: CoordinatedEvent
    admitted_at: datetime
    deduplication_key: str | None
    state: DeliveryState | str = DeliveryState.QUEUED
    selected_at: datetime | None = None
    dispatched_at: datetime | None = None
    discarded_at: datetime | None = None

    def __post_init__(self) -> None:
        state = DeliveryState(self.state)
        timestamps = (
            self.admitted_at,
            self.selected_at,
            self.dispatched_at,
            self.discarded_at,
        )
        for timestamp in timestamps:
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError("broker timestamps must be timezone-aware")
        if self.deduplication_key is not None and not self.deduplication_key.strip():
            raise ValueError("deduplication_key must not be blank")
        object.__setattr__(self, "state", state)

    @property
    def event(self) -> ExecutiveEvent:
        return self.coordinated_event.event


@dataclass(frozen=True, slots=True)
class BrokerSubmissionResult:
    status: BrokerSubmissionStatus | str
    brokered_event: BrokeredEvent

    def __post_init__(self) -> None:
        status = BrokerSubmissionStatus(self.status)
        expected_state = {
            BrokerSubmissionStatus.ACCEPTED: DeliveryState.QUEUED,
            BrokerSubmissionStatus.DUPLICATE: DeliveryState.DUPLICATE,
            BrokerSubmissionStatus.EXPIRED: DeliveryState.EXPIRED,
        }[status]
        if self.brokered_event.state is not expected_state:
            raise ValueError("submission status must match brokered event state")
        object.__setattr__(self, "status", status)

    @property
    def accepted(self) -> bool:
        return self.status is BrokerSubmissionStatus.ACCEPTED


@dataclass(frozen=True, slots=True)
class ExecutiveNotificationBrokerSnapshot:
    pending_count: int
    accepted_count: int
    dispatched_count: int
    duplicate_count: int
    expired_count: int
    expired_after_admission_count: int
    deferred_decision_count: int = 0
    silenced_count: int = 0
    last_admitted_at: datetime | None = None
    last_dispatched_at: datetime | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        counters = (
            self.pending_count,
            self.accepted_count,
            self.dispatched_count,
            self.duplicate_count,
            self.expired_count,
            self.expired_after_admission_count,
            self.deferred_decision_count,
            self.silenced_count,
        )
        if min(counters) < 0:
            raise ValueError("broker counters must not be negative")
        expected_pending = (
            self.accepted_count
            - self.dispatched_count
            - self.expired_after_admission_count
            - self.silenced_count
        )
        if self.pending_count != expected_pending:
            raise ValueError("pending_count must match accepted terminal outcomes")
        if self.expired_after_admission_count > self.expired_count:
            raise ValueError("post-admission expiry cannot exceed total expiry")
        for timestamp in (
            self.last_admitted_at,
            self.last_dispatched_at,
            self.updated_at,
        ):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError("broker timestamps must be timezone-aware")
