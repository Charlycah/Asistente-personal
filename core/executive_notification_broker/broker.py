from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timezone
from threading import RLock

from core.executive_coordinator import CoordinatedEvent
from core.executive_event_model import ExecutiveEvent
from core.executive_presence_attention import (
    AttentionDecision,
    AttentionDisposition,
)

from .models import (
    BrokeredEvent,
    BrokerSubmissionResult,
    BrokerSubmissionStatus,
    DeliveryState,
    ExecutiveNotificationBrokerSnapshot,
)

BrokeredEventHandler = Callable[[BrokeredEvent], None]
DeduplicationKeyFactory = Callable[[ExecutiveEvent], str | None]
AttentionDecider = Callable[[ExecutiveEvent, datetime], AttentionDecision]


class ExecutiveNotificationBroker:
    """Applies deterministic delivery policy to coordinated events.

    M325.3 introduces priority ordering, active expiry, semantic deduplication,
    and explicit in-memory delivery states. It does not persist broker state,
    confirm user presentation, coalesce related events, or replace Queue[str].
    """

    def __init__(
        self,
        *,
        deduplication_key_factory: DeduplicationKeyFactory | None = None,
        attention_decider: AttentionDecider | None = None,
    ) -> None:
        self._lock = RLock()
        self._pending: list[BrokeredEvent] = []
        self._deduplication_keys: set[str] = set()
        self._handlers: list[BrokeredEventHandler] = []
        self._key_factory = deduplication_key_factory or semantic_event_key
        self._attention_decider = attention_decider
        self._accepted_count = 0
        self._dispatched_count = 0
        self._duplicate_count = 0
        self._expired_count = 0
        self._expired_after_admission_count = 0
        self._deferred_decision_count = 0
        self._silenced_count = 0
        self._last_admitted_at: datetime | None = None
        self._last_dispatched_at: datetime | None = None
        self._dispatching = False

    @property
    def snapshot(self) -> ExecutiveNotificationBrokerSnapshot:
        with self._lock:
            return ExecutiveNotificationBrokerSnapshot(
                pending_count=len(self._pending),
                accepted_count=self._accepted_count,
                dispatched_count=self._dispatched_count,
                duplicate_count=self._duplicate_count,
                expired_count=self._expired_count,
                expired_after_admission_count=(
                    self._expired_after_admission_count
                ),
                deferred_decision_count=self._deferred_decision_count,
                silenced_count=self._silenced_count,
                last_admitted_at=self._last_admitted_at,
                last_dispatched_at=self._last_dispatched_at,
            )

    def subscribe(self, handler: BrokeredEventHandler) -> None:
        if not callable(handler):
            raise TypeError("broker handler must be callable")
        with self._lock:
            if handler not in self._handlers:
                self._handlers.append(handler)

    def unsubscribe(self, handler: BrokeredEventHandler) -> None:
        with self._lock:
            if handler in self._handlers:
                self._handlers.remove(handler)

    def submit(
        self,
        coordinated_event: CoordinatedEvent,
        *,
        evaluated_at: datetime | None = None,
    ) -> BrokerSubmissionResult:
        if not isinstance(coordinated_event, CoordinatedEvent):
            raise TypeError("broker accepts CoordinatedEvent instances only")
        timestamp = self._timestamp(evaluated_at)
        event = coordinated_event.event
        deduplication_key = self._key_factory(event)
        with self._lock:
            self._last_admitted_at = timestamp
            if event.is_expired(timestamp):
                self._expired_count += 1
                discarded = BrokeredEvent(
                    coordinated_event=coordinated_event,
                    admitted_at=timestamp,
                    deduplication_key=deduplication_key,
                    state=DeliveryState.EXPIRED,
                    discarded_at=timestamp,
                )
                return BrokerSubmissionResult(
                    status=BrokerSubmissionStatus.EXPIRED,
                    brokered_event=discarded,
                )
            if (
                deduplication_key is not None
                and deduplication_key in self._deduplication_keys
            ):
                self._duplicate_count += 1
                duplicate = BrokeredEvent(
                    coordinated_event=coordinated_event,
                    admitted_at=timestamp,
                    deduplication_key=deduplication_key,
                    state=DeliveryState.DUPLICATE,
                    discarded_at=timestamp,
                )
                return BrokerSubmissionResult(
                    status=BrokerSubmissionStatus.DUPLICATE,
                    brokered_event=duplicate,
                )
            brokered = BrokeredEvent(
                coordinated_event=coordinated_event,
                admitted_at=timestamp,
                deduplication_key=deduplication_key,
            )
            self._accepted_count += 1
            if deduplication_key is not None:
                self._deduplication_keys.add(deduplication_key)
            self._pending.append(brokered)
            return BrokerSubmissionResult(
                status=BrokerSubmissionStatus.ACCEPTED,
                brokered_event=brokered,
            )

    def coordinator_handler(self, coordinated_event: CoordinatedEvent) -> None:
        self.submit(coordinated_event)

    def peek_next(
        self,
        *,
        now: datetime | None = None,
    ) -> BrokeredEvent | None:
        timestamp = self._timestamp(now)
        with self._lock:
            self._discard_expired_locked(timestamp)
            return self._select_next_locked()

    def dispatch_next(
        self,
        *,
        now: datetime | None = None,
    ) -> BrokeredEvent | None:
        timestamp = self._timestamp(now)
        with self._lock:
            if self._dispatching:
                raise RuntimeError(
                    "executive notification broker is already dispatching"
                )
            self._discard_expired_locked(timestamp)
            queued = self._select_deliverable_locked(timestamp)
            if queued is None:
                return None
            index = self._pending.index(queued)
            selected = replace(
                queued,
                state=DeliveryState.DISPATCHING,
                selected_at=timestamp,
            )
            self._pending[index] = selected
            handlers = tuple(self._handlers)
            self._dispatching = True

        try:
            for handler in handlers:
                handler(selected)
        except Exception:
            with self._lock:
                current_index = self._pending.index(selected)
                self._pending[current_index] = replace(
                    selected,
                    state=DeliveryState.QUEUED,
                    selected_at=None,
                )
            raise
        finally:
            with self._lock:
                self._dispatching = False

        with self._lock:
            if selected not in self._pending:
                raise RuntimeError("broker pending set changed during dispatch")
            self._pending.remove(selected)
            dispatched = replace(
                selected,
                state=DeliveryState.DISPATCHED,
                dispatched_at=timestamp,
            )
            self._dispatched_count += 1
            self._last_dispatched_at = timestamp
            return dispatched

    def dispatch_pending(
        self,
        *,
        limit: int | None = None,
        now: datetime | None = None,
    ) -> tuple[BrokeredEvent, ...]:
        if limit is not None and limit <= 0:
            raise ValueError("dispatch limit must be positive")
        dispatched: list[BrokeredEvent] = []
        while limit is None or len(dispatched) < limit:
            brokered = self.dispatch_next(now=now)
            if brokered is None:
                break
            dispatched.append(brokered)
        return tuple(dispatched)

    def pending_events(
        self,
        *,
        now: datetime | None = None,
    ) -> tuple[BrokeredEvent, ...]:
        timestamp = self._timestamp(now)
        with self._lock:
            self._discard_expired_locked(timestamp)
            return tuple(sorted(self._pending, key=self._selection_key))

    def _discard_expired_locked(self, timestamp: datetime) -> None:
        active: list[BrokeredEvent] = []
        for brokered in self._pending:
            if brokered.event.is_expired(timestamp):
                self._expired_count += 1
                self._expired_after_admission_count += 1
                continue
            active.append(brokered)
        self._pending = active

    def _select_next_locked(self) -> BrokeredEvent | None:
        if not self._pending:
            return None
        return min(self._pending, key=self._selection_key)

    def _select_deliverable_locked(
        self,
        timestamp: datetime,
    ) -> BrokeredEvent | None:
        for brokered in sorted(self._pending, key=self._selection_key):
            if self._attention_decider is None:
                return brokered
            decision = self._attention_decider(brokered.event, timestamp)
            if decision.event is not brokered.event:
                raise ValueError("attention decision must reference evaluated event")
            if decision.disposition is AttentionDisposition.DELIVER:
                return brokered
            if decision.disposition is AttentionDisposition.DEFER:
                self._deferred_decision_count += 1
                continue
            self._pending.remove(brokered)
            self._silenced_count += 1
        return None

    @staticmethod
    def _selection_key(brokered: BrokeredEvent) -> tuple[int, int]:
        return (
            -int(brokered.event.priority),
            brokered.coordinated_event.sequence,
        )

    @staticmethod
    def _timestamp(value: datetime | None) -> datetime:
        timestamp = value or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("broker time must be timezone-aware")
        return timestamp


def semantic_event_key(event: ExecutiveEvent) -> str | None:
    """Return a conservative semantic identity for safe deduplication.

    Only explicit cross-event identities are used. Events without entity or
    correlation identity remain independent and are never deduplicated by text.
    """

    identity = event.entity_id or event.correlation_id
    if identity is None:
        return None
    return f"{event.kind.value}:{identity.strip()}"
