from __future__ import annotations

from collections import deque
from collections.abc import Callable
from datetime import datetime, timezone
from threading import RLock
from typing import Protocol

from core.executive_event_model import ExecutiveEvent

from .models import (
    CoordinatedEvent,
    CoordinatorState,
    ExecutiveCoordinatorSnapshot,
    SubmissionResult,
    SubmissionStatus,
)


class ExecutiveEventPublisher(Protocol):
    def publish(
        self,
        event: ExecutiveEvent,
        *,
        accepted_at: datetime | None = None,
    ) -> SubmissionResult: ...


CoordinatedEventHandler = Callable[[CoordinatedEvent], None]


class ExecutiveCoordinator:
    """Owns typed-event intake and deterministic FIFO dispatch.

    M325.2 intentionally contains no priority, expiry, deduplication-by-content,
    persistence, or recovery policy. It only establishes one authority for event
    admission, sequencing, lifecycle, and dispatch.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._pending: deque[CoordinatedEvent] = deque()
        self._seen_event_ids: set[str] = set()
        self._handlers: list[CoordinatedEventHandler] = []
        self._state = CoordinatorState.STOPPED
        self._accepted_count = 0
        self._dispatched_count = 0
        self._duplicate_count = 0
        self._next_sequence = 1
        self._started_at: datetime | None = None
        self._stopped_at: datetime | None = None
        self._last_accepted_at: datetime | None = None
        self._last_dispatched_at: datetime | None = None
        self._dispatching = False

    @property
    def snapshot(self) -> ExecutiveCoordinatorSnapshot:
        with self._lock:
            return ExecutiveCoordinatorSnapshot(
                state=self._state,
                pending_count=len(self._pending),
                accepted_count=self._accepted_count,
                dispatched_count=self._dispatched_count,
                duplicate_count=self._duplicate_count,
                next_sequence=self._next_sequence,
                started_at=self._started_at,
                stopped_at=self._stopped_at,
                last_accepted_at=self._last_accepted_at,
                last_dispatched_at=self._last_dispatched_at,
            )

    def start(self, *, now: datetime | None = None) -> ExecutiveCoordinatorSnapshot:
        timestamp = self._timestamp(now)
        with self._lock:
            if self._state is CoordinatorState.RUNNING:
                return self.snapshot
            self._state = CoordinatorState.RUNNING
            self._started_at = timestamp
            self._stopped_at = None
            return self.snapshot

    def stop(self, *, now: datetime | None = None) -> ExecutiveCoordinatorSnapshot:
        timestamp = self._timestamp(now)
        with self._lock:
            if self._state is CoordinatorState.STOPPED:
                return self.snapshot
            self._state = CoordinatorState.STOPPED
            self._stopped_at = timestamp
            return self.snapshot

    def subscribe(self, handler: CoordinatedEventHandler) -> None:
        if not callable(handler):
            raise TypeError("coordinator handler must be callable")
        with self._lock:
            if handler not in self._handlers:
                self._handlers.append(handler)

    def unsubscribe(self, handler: CoordinatedEventHandler) -> None:
        with self._lock:
            if handler in self._handlers:
                self._handlers.remove(handler)

    def publish(
        self,
        event: ExecutiveEvent,
        *,
        accepted_at: datetime | None = None,
    ) -> SubmissionResult:
        if not isinstance(event, ExecutiveEvent):
            raise TypeError("coordinator accepts ExecutiveEvent instances only")
        timestamp = self._timestamp(accepted_at)
        with self._lock:
            self._require_running()
            if event.event_id in self._seen_event_ids:
                self._duplicate_count += 1
                return SubmissionResult(status=SubmissionStatus.DUPLICATE)
            coordinated = CoordinatedEvent(
                sequence=self._next_sequence,
                accepted_at=timestamp,
                event=event,
            )
            self._next_sequence += 1
            self._accepted_count += 1
            self._last_accepted_at = timestamp
            self._seen_event_ids.add(event.event_id)
            self._pending.append(coordinated)
            return SubmissionResult(
                status=SubmissionStatus.ACCEPTED,
                coordinated_event=coordinated,
            )

    def peek_next(self) -> CoordinatedEvent | None:
        with self._lock:
            return self._pending[0] if self._pending else None

    def dispatch_next(self, *, now: datetime | None = None) -> CoordinatedEvent | None:
        timestamp = self._timestamp(now)
        with self._lock:
            self._require_running()
            if self._dispatching:
                raise RuntimeError("executive coordinator is already dispatching")
            if not self._pending:
                return None
            coordinated = self._pending[0]
            handlers = tuple(self._handlers)
            self._dispatching = True

        try:
            for handler in handlers:
                handler(coordinated)
        finally:
            with self._lock:
                self._dispatching = False

        with self._lock:
            if not self._pending or self._pending[0] is not coordinated:
                raise RuntimeError("coordinator pending order changed during dispatch")
            self._pending.popleft()
            self._dispatched_count += 1
            self._last_dispatched_at = timestamp
            return coordinated

    def dispatch_pending(
        self,
        *,
        limit: int | None = None,
        now: datetime | None = None,
    ) -> tuple[CoordinatedEvent, ...]:
        if limit is not None and limit <= 0:
            raise ValueError("dispatch limit must be positive")
        dispatched: list[CoordinatedEvent] = []
        while limit is None or len(dispatched) < limit:
            coordinated = self.dispatch_next(now=now)
            if coordinated is None:
                break
            dispatched.append(coordinated)
        return tuple(dispatched)

    def pending_events(self) -> tuple[CoordinatedEvent, ...]:
        with self._lock:
            return tuple(self._pending)

    def _require_running(self) -> None:
        if self._state is not CoordinatorState.RUNNING:
            raise RuntimeError("executive coordinator is not running")

    @staticmethod
    def _timestamp(value: datetime | None) -> datetime:
        timestamp = value or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("coordinator time must be timezone-aware")
        return timestamp
