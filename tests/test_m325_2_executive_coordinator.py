from datetime import datetime, timezone

import pytest

from core.executive_coordinator import (
    CoordinatorState,
    ExecutiveCoordinator,
    SubmissionStatus,
)
from core.executive_event_model import (
    BatteryLowEvent,
    EventPriority,
    GenericTextEvent,
    ReminderDueEvent,
)


def _utc(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 7, 25, hour, minute, tzinfo=timezone.utc)


def test_m325_2_coordinator_has_explicit_lifecycle() -> None:
    coordinator = ExecutiveCoordinator()

    assert coordinator.snapshot.state is CoordinatorState.STOPPED
    started = coordinator.start(now=_utc(18))
    stopped = coordinator.stop(now=_utc(19))

    assert started.state is CoordinatorState.RUNNING
    assert started.started_at == _utc(18)
    assert stopped.state is CoordinatorState.STOPPED
    assert stopped.stopped_at == _utc(19)


def test_m325_2_publish_requires_running_coordinator() -> None:
    coordinator = ExecutiveCoordinator()

    with pytest.raises(RuntimeError, match="not running"):
        coordinator.publish(GenericTextEvent(text="Mensaje"))


def test_m325_2_publish_assigns_monotonic_sequence() -> None:
    coordinator = ExecutiveCoordinator()
    coordinator.start(now=_utc(18))

    first = coordinator.publish(
        BatteryLowEvent(battery_percent=15),
        accepted_at=_utc(18, 1),
    )
    second = coordinator.publish(
        ReminderDueEvent(reminder_id="rem-1", title="Consulta"),
        accepted_at=_utc(18, 2),
    )

    assert first.accepted
    assert second.accepted
    assert first.coordinated_event is not None
    assert second.coordinated_event is not None
    assert first.coordinated_event.sequence == 1
    assert second.coordinated_event.sequence == 2
    assert coordinator.snapshot.next_sequence == 3


def test_m325_2_rejects_duplicate_event_id_without_resequencing() -> None:
    coordinator = ExecutiveCoordinator()
    coordinator.start()
    event = GenericTextEvent(text="Mensaje", event_id="event-1")

    accepted = coordinator.publish(event)
    duplicate = coordinator.publish(event)
    next_result = coordinator.publish(GenericTextEvent(text="Otro"))

    assert accepted.status is SubmissionStatus.ACCEPTED
    assert duplicate.status is SubmissionStatus.DUPLICATE
    assert next_result.coordinated_event is not None
    assert next_result.coordinated_event.sequence == 2
    assert coordinator.snapshot.duplicate_count == 1


def test_m325_2_dispatch_is_fifo_even_when_priorities_differ() -> None:
    coordinator = ExecutiveCoordinator()
    coordinator.start()
    low = GenericTextEvent(text="Primero", priority=EventPriority.LOW)
    critical = GenericTextEvent(text="Segundo", priority=EventPriority.CRITICAL)
    coordinator.publish(low)
    coordinator.publish(critical)

    dispatched = coordinator.dispatch_pending()

    assert [item.event for item in dispatched] == [low, critical]
    assert coordinator.snapshot.pending_count == 0
    assert coordinator.snapshot.dispatched_count == 2


def test_m325_2_subscribers_receive_coordinated_event() -> None:
    coordinator = ExecutiveCoordinator()
    received = []
    coordinator.subscribe(received.append)
    coordinator.start()
    event = GenericTextEvent(text="Mensaje")
    coordinator.publish(event)

    dispatched = coordinator.dispatch_next(now=_utc(18))

    assert dispatched is not None
    assert received == [dispatched]


def test_m325_2_failed_handler_keeps_event_pending() -> None:
    coordinator = ExecutiveCoordinator()

    def fail(_event: object) -> None:
        raise RuntimeError("handler failed")

    coordinator.subscribe(fail)
    coordinator.start()
    event = GenericTextEvent(text="Mensaje")
    coordinator.publish(event)

    with pytest.raises(RuntimeError, match="handler failed"):
        coordinator.dispatch_next()

    assert coordinator.peek_next() is not None
    assert coordinator.peek_next().event is event  # type: ignore[union-attr]
    assert coordinator.snapshot.dispatched_count == 0


def test_m325_2_expired_event_is_admitted_without_policy_decision() -> None:
    coordinator = ExecutiveCoordinator()
    coordinator.start()
    event = GenericTextEvent(
        text="Evento vencido",
        occurred_at=_utc(17),
        expires_at=_utc(18),
    )

    result = coordinator.publish(event, accepted_at=_utc(19))

    assert result.accepted
    assert coordinator.peek_next() is not None
    pending = coordinator.peek_next()
    assert pending is not None
    assert pending.event.is_expired(_utc(19))


def test_m325_2_stop_preserves_pending_events_for_same_instance() -> None:
    coordinator = ExecutiveCoordinator()
    coordinator.start()
    event = GenericTextEvent(text="Pendiente")
    coordinator.publish(event)

    coordinator.stop()
    coordinator.start()

    dispatched = coordinator.dispatch_next()
    assert dispatched is not None
    assert dispatched.event is event


def test_m325_2_validates_inputs_and_dispatch_limit() -> None:
    coordinator = ExecutiveCoordinator()
    coordinator.start()

    with pytest.raises(TypeError, match="ExecutiveEvent"):
        coordinator.publish("mensaje")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="positive"):
        coordinator.dispatch_pending(limit=0)
    with pytest.raises(ValueError, match="timezone-aware"):
        coordinator.publish(
            GenericTextEvent(text="Mensaje"),
            accepted_at=datetime(2026, 7, 25, 18, 0),
        )


def test_m325_2_reentrant_dispatch_is_rejected_without_losing_event() -> None:
    coordinator = ExecutiveCoordinator()

    def reenter(_event: object) -> None:
        coordinator.dispatch_next()

    coordinator.subscribe(reenter)
    coordinator.start()
    coordinator.publish(GenericTextEvent(text="Mensaje"))

    with pytest.raises(RuntimeError, match="already dispatching"):
        coordinator.dispatch_next()

    assert coordinator.snapshot.pending_count == 1
    assert coordinator.snapshot.dispatched_count == 0
