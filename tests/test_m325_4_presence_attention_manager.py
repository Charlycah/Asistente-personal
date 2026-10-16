from datetime import datetime, timezone

import pytest

from core.executive_coordinator import ExecutiveCoordinator
from core.executive_event_model import (
    DeliveryRequirement,
    EventPriority,
    GenericTextEvent,
)
from core.executive_notification_broker import ExecutiveNotificationBroker
from core.executive_presence_attention import (
    AttentionDisposition,
    AttentionReason,
    AttentionState,
    PresenceAttentionManager,
    PresenceState,
)


def _utc(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 7, 25, hour, minute, tzinfo=timezone.utc)


def _coordinated(*events: GenericTextEvent):
    coordinator = ExecutiveCoordinator()
    coordinator.start(now=_utc(18))
    results = [coordinator.publish(event, accepted_at=_utc(18)) for event in events]
    return tuple(result.coordinated_event for result in results)


def test_m325_4_available_user_receives_event() -> None:
    manager = PresenceAttentionManager()
    manager.update(
        presence=PresenceState.PRESENT,
        attention=AttentionState.AVAILABLE,
        observed_at=_utc(18),
    )
    event = GenericTextEvent(text="Mensaje")

    decision = manager.assess(event, evaluated_at=_utc(18))

    assert decision.disposition is AttentionDisposition.DELIVER
    assert decision.reason is AttentionReason.AVAILABLE


@pytest.mark.parametrize(
    "attention",
    [AttentionState.USER_SPEAKING, AttentionState.USER_TYPING],
)
def test_m325_4_user_activity_defers_noncritical_event(
    attention: AttentionState,
) -> None:
    manager = PresenceAttentionManager()
    manager.update(
        presence=PresenceState.PRESENT,
        attention=attention,
        observed_at=_utc(18),
    )

    decision = manager.assess(
        GenericTextEvent(text="Mensaje"),
        evaluated_at=_utc(18),
    )

    assert decision.disposition is AttentionDisposition.DEFER
    assert decision.reason is AttentionReason.USER_BUSY


def test_m325_4_roby_response_defers_event() -> None:
    manager = PresenceAttentionManager()
    manager.update(
        attention=AttentionState.ROBY_RESPONDING,
        observed_at=_utc(18),
    )

    decision = manager.assess(
        GenericTextEvent(text="Mensaje"),
        evaluated_at=_utc(18),
    )

    assert decision.disposition is AttentionDisposition.DEFER
    assert decision.reason is AttentionReason.ROBY_BUSY


def test_m325_4_away_user_silences_best_effort_event() -> None:
    manager = PresenceAttentionManager()
    manager.update(presence=PresenceState.AWAY, observed_at=_utc(18))

    decision = manager.assess(
        GenericTextEvent(text="Mensaje"),
        evaluated_at=_utc(18),
    )

    assert decision.disposition is AttentionDisposition.SILENCE
    assert decision.reason is AttentionReason.BEST_EFFORT_WHILE_AWAY


def test_m325_4_away_user_defers_required_presentation() -> None:
    manager = PresenceAttentionManager()
    manager.update(presence=PresenceState.AWAY, observed_at=_utc(18))
    event = GenericTextEvent(
        text="Mensaje",
        delivery_requirement=DeliveryRequirement.PRESENTATION_REQUIRED,
    )

    decision = manager.assess(event, evaluated_at=_utc(18))

    assert decision.disposition is AttentionDisposition.DEFER
    assert decision.reason is AttentionReason.USER_AWAY


def test_m325_4_do_not_disturb_silences_noncritical_event() -> None:
    manager = PresenceAttentionManager()
    manager.update(
        presence=PresenceState.PRESENT,
        attention=AttentionState.DO_NOT_DISTURB,
        observed_at=_utc(18),
    )

    decision = manager.assess(
        GenericTextEvent(text="Mensaje", priority=EventPriority.HIGH),
        evaluated_at=_utc(18),
    )

    assert decision.disposition is AttentionDisposition.SILENCE
    assert decision.reason is AttentionReason.DO_NOT_DISTURB


def test_m325_4_critical_event_overrides_attention_block() -> None:
    manager = PresenceAttentionManager()
    manager.update(
        presence=PresenceState.AWAY,
        attention=AttentionState.DO_NOT_DISTURB,
        observed_at=_utc(18),
    )
    event = GenericTextEvent(
        text="Alerta crítica",
        priority=EventPriority.CRITICAL,
    )

    decision = manager.assess(event, evaluated_at=_utc(18))

    assert decision.disposition is AttentionDisposition.DELIVER
    assert decision.reason is AttentionReason.CRITICAL_OVERRIDE


def test_m325_4_broker_skips_deferred_event_and_delivers_critical() -> None:
    manager = PresenceAttentionManager()
    manager.update(
        presence=PresenceState.PRESENT,
        attention=AttentionState.USER_SPEAKING,
        observed_at=_utc(18),
    )
    normal = GenericTextEvent(text="Normal", priority=EventPriority.NORMAL)
    critical = GenericTextEvent(text="Crítico", priority=EventPriority.CRITICAL)
    coordinated = _coordinated(normal, critical)
    broker = ExecutiveNotificationBroker(attention_decider=manager.broker_decider)
    for item in coordinated:
        assert item is not None
        broker.submit(item, evaluated_at=_utc(18))

    dispatched = broker.dispatch_next(now=_utc(18))

    assert dispatched is not None
    assert dispatched.event is critical
    assert broker.snapshot.pending_count == 1


def test_m325_4_deferred_event_remains_pending_until_available() -> None:
    manager = PresenceAttentionManager()
    manager.update(
        presence=PresenceState.PRESENT,
        attention=AttentionState.USER_TYPING,
        observed_at=_utc(18),
    )
    event = GenericTextEvent(text="Mensaje")
    coordinated = _coordinated(event)[0]
    assert coordinated is not None
    broker = ExecutiveNotificationBroker(attention_decider=manager.broker_decider)
    broker.submit(coordinated, evaluated_at=_utc(18))

    assert broker.dispatch_next(now=_utc(18)) is None
    assert broker.snapshot.pending_count == 1

    manager.update(attention=AttentionState.AVAILABLE, observed_at=_utc(19))
    dispatched = broker.dispatch_next(now=_utc(19))

    assert dispatched is not None
    assert dispatched.event is event
    assert broker.snapshot.pending_count == 0


def test_m325_4_silenced_event_is_removed_from_broker() -> None:
    manager = PresenceAttentionManager()
    manager.update(
        attention=AttentionState.DO_NOT_DISTURB,
        observed_at=_utc(18),
    )
    event = GenericTextEvent(text="Mensaje")
    coordinated = _coordinated(event)[0]
    assert coordinated is not None
    broker = ExecutiveNotificationBroker(attention_decider=manager.broker_decider)
    broker.submit(coordinated, evaluated_at=_utc(18))

    assert broker.dispatch_next(now=_utc(18)) is None

    snapshot = broker.snapshot
    assert snapshot.pending_count == 0
    assert snapshot.silenced_count == 1


def test_m325_4_manager_snapshot_tracks_decisions() -> None:
    manager = PresenceAttentionManager()
    manager.update(
        presence=PresenceState.PRESENT,
        attention=AttentionState.USER_TYPING,
        observed_at=_utc(18),
    )
    manager.assess(GenericTextEvent(text="Uno"), evaluated_at=_utc(18))
    manager.update(
        attention=AttentionState.AVAILABLE,
        observed_at=_utc(19),
    )
    manager.assess(GenericTextEvent(text="Dos"), evaluated_at=_utc(19))

    snapshot = manager.snapshot

    assert snapshot.update_count == 2
    assert snapshot.decision_count == 2
    assert snapshot.deferred_count == 1
    assert snapshot.delivered_count == 1
    assert snapshot.silenced_count == 0


def test_m325_4_validates_inputs_and_timestamps() -> None:
    manager = PresenceAttentionManager()

    with pytest.raises(TypeError, match="ExecutiveEvent"):
        manager.assess("mensaje")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="timezone-aware"):
        manager.update(observed_at=datetime(2026, 7, 25, 18, 0))
