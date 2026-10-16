from datetime import datetime, timezone

import pytest

from core.executive_coordinator import ExecutiveCoordinator
from core.executive_event_model import (
    EventPriority,
    GenericTextEvent,
    ReminderDueEvent,
)
from core.executive_notification_broker import (
    BrokerSubmissionStatus,
    DeliveryState,
    ExecutiveNotificationBroker,
)


def _utc(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 7, 25, hour, minute, tzinfo=timezone.utc)


def _coordinated(*events: GenericTextEvent | ReminderDueEvent):
    coordinator = ExecutiveCoordinator()
    coordinator.start(now=_utc(18))
    results = [coordinator.publish(event, accepted_at=_utc(18)) for event in events]
    return tuple(result.coordinated_event for result in results)


def test_m325_3_broker_orders_by_priority_then_sequence() -> None:
    low = GenericTextEvent(text="Primero", priority=EventPriority.LOW)
    critical = GenericTextEvent(text="Segundo", priority=EventPriority.CRITICAL)
    normal = GenericTextEvent(text="Tercero", priority=EventPriority.NORMAL)
    coordinated = _coordinated(low, critical, normal)
    broker = ExecutiveNotificationBroker()
    for item in coordinated:
        assert item is not None
        broker.submit(item, evaluated_at=_utc(18))

    dispatched = broker.dispatch_pending(now=_utc(18))

    assert [item.event for item in dispatched] == [critical, normal, low]
    assert all(item.state is DeliveryState.DISPATCHED for item in dispatched)


def test_m325_3_equal_priorities_remain_fifo() -> None:
    first = GenericTextEvent(text="Primero")
    second = GenericTextEvent(text="Segundo")
    coordinated = _coordinated(first, second)
    broker = ExecutiveNotificationBroker()
    for item in coordinated:
        assert item is not None
        broker.submit(item, evaluated_at=_utc(18))

    dispatched = broker.dispatch_pending(now=_utc(18))

    assert [item.event for item in dispatched] == [first, second]


def test_m325_3_expired_event_is_discarded_on_admission() -> None:
    event = GenericTextEvent(
        text="Vencido",
        occurred_at=_utc(17),
        expires_at=_utc(18),
    )
    coordinated = _coordinated(event)[0]
    assert coordinated is not None
    broker = ExecutiveNotificationBroker()

    result = broker.submit(coordinated, evaluated_at=_utc(19))

    assert result.status is BrokerSubmissionStatus.EXPIRED
    assert result.brokered_event.state is DeliveryState.EXPIRED
    assert broker.snapshot.expired_count == 1
    assert broker.snapshot.pending_count == 0


def test_m325_3_event_can_expire_while_waiting() -> None:
    event = GenericTextEvent(
        text="Pronto vencido",
        occurred_at=_utc(17),
        expires_at=_utc(19),
    )
    coordinated = _coordinated(event)[0]
    assert coordinated is not None
    broker = ExecutiveNotificationBroker()
    broker.submit(coordinated, evaluated_at=_utc(18))

    assert broker.peek_next(now=_utc(19)) is None
    assert broker.snapshot.expired_count == 1
    assert broker.snapshot.pending_count == 0


def test_m325_3_semantic_deduplication_uses_explicit_entity_identity() -> None:
    first = ReminderDueEvent(
        reminder_id="rem-1",
        title="Consulta",
        entity_id="appointment-42",
    )
    duplicate = ReminderDueEvent(
        reminder_id="rem-2",
        title="Consulta actualizada",
        entity_id="appointment-42",
    )
    coordinated = _coordinated(first, duplicate)
    broker = ExecutiveNotificationBroker()
    first_coordinated, duplicate_coordinated = coordinated
    assert first_coordinated is not None
    assert duplicate_coordinated is not None
    first_result = broker.submit(first_coordinated, evaluated_at=_utc(18))
    duplicate_result = broker.submit(
        duplicate_coordinated,
        evaluated_at=_utc(18),
    )

    assert first_result.accepted
    assert duplicate_result.status is BrokerSubmissionStatus.DUPLICATE
    assert duplicate_result.brokered_event.state is DeliveryState.DUPLICATE
    assert broker.snapshot.duplicate_count == 1
    assert broker.snapshot.pending_count == 1


def test_m325_3_events_without_explicit_identity_are_not_text_deduplicated() -> None:
    first = GenericTextEvent(text="Mismo texto")
    second = GenericTextEvent(text="Mismo texto")
    coordinated = _coordinated(first, second)
    broker = ExecutiveNotificationBroker()
    for item in coordinated:
        assert item is not None
        assert broker.submit(item, evaluated_at=_utc(18)).accepted

    assert broker.snapshot.pending_count == 2
    assert broker.snapshot.duplicate_count == 0


def test_m325_3_coordinator_can_feed_broker_without_runtime_rewiring() -> None:
    coordinator = ExecutiveCoordinator()
    broker = ExecutiveNotificationBroker()
    coordinator.subscribe(broker.coordinator_handler)
    coordinator.start(now=_utc(18))
    event = GenericTextEvent(text="Mensaje")
    coordinator.publish(event, accepted_at=_utc(18))

    coordinated = coordinator.dispatch_next(now=_utc(18))

    assert coordinated is not None
    assert broker.peek_next(now=_utc(18)) is not None
    assert broker.peek_next(now=_utc(18)).event is event  # type: ignore[union-attr]


def test_m325_3_failed_handler_restores_queued_state() -> None:
    event = GenericTextEvent(text="Mensaje")
    coordinated = _coordinated(event)[0]
    assert coordinated is not None
    broker = ExecutiveNotificationBroker()

    def fail(_event: object) -> None:
        raise RuntimeError("handler failed")

    broker.subscribe(fail)
    broker.submit(coordinated, evaluated_at=_utc(18))

    with pytest.raises(RuntimeError, match="handler failed"):
        broker.dispatch_next(now=_utc(18))

    pending = broker.peek_next(now=_utc(18))
    assert pending is not None
    assert pending.state is DeliveryState.QUEUED
    assert broker.snapshot.dispatched_count == 0


def test_m325_3_reentrant_dispatch_is_rejected_without_losing_event() -> None:
    event = GenericTextEvent(text="Mensaje")
    coordinated = _coordinated(event)[0]
    assert coordinated is not None
    broker = ExecutiveNotificationBroker()

    def reenter(_event: object) -> None:
        broker.dispatch_next(now=_utc(18))

    broker.subscribe(reenter)
    broker.submit(coordinated, evaluated_at=_utc(18))

    with pytest.raises(RuntimeError, match="already dispatching"):
        broker.dispatch_next(now=_utc(18))

    assert broker.snapshot.pending_count == 1
    assert broker.snapshot.dispatched_count == 0


def test_m325_3_broker_validates_inputs_and_limit() -> None:
    broker = ExecutiveNotificationBroker()

    with pytest.raises(TypeError, match="CoordinatedEvent"):
        broker.submit("message")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="positive"):
        broker.dispatch_pending(limit=0)
    with pytest.raises(ValueError, match="timezone-aware"):
        broker.peek_next(now=datetime(2026, 7, 25, 18, 0))


def test_m325_3_snapshot_tracks_policy_outcomes() -> None:
    active = GenericTextEvent(text="Activo", entity_id="entity-1")
    duplicate = GenericTextEvent(text="Duplicado", entity_id="entity-1")
    expired = GenericTextEvent(
        text="Vencido",
        occurred_at=_utc(17),
        expires_at=_utc(18),
    )
    coordinated = _coordinated(active, duplicate, expired)
    broker = ExecutiveNotificationBroker()
    for item in coordinated:
        assert item is not None
        broker.submit(item, evaluated_at=_utc(19))

    snapshot = broker.snapshot

    assert snapshot.accepted_count == 1
    assert snapshot.duplicate_count == 1
    assert snapshot.expired_count == 1
    assert snapshot.pending_count == 1
