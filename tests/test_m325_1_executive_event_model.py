from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from core.executive_event_model import (
    AmbientObservationEvent,
    BatteryLowEvent,
    DeliveryRequirement,
    EventKind,
    EventPriority,
    EventSource,
    GenericTextEvent,
    ImportantEmailEvent,
    PrivacyLevel,
    ReminderDueEvent,
    VerifiedNewsEvent,
    VisualCaptureResultEvent,
    event_from_dict,
    event_to_dict,
    text_to_executive_event,
)


def test_m325_1_builds_typed_battery_event_with_common_metadata() -> None:
    occurred_at = datetime(2026, 7, 25, 18, 0, tzinfo=timezone.utc)
    event = BatteryLowEvent(
        battery_percent=12,
        occurred_at=occurred_at,
        expires_at=occurred_at + timedelta(minutes=10),
        priority=EventPriority.HIGH,
        privacy_level=PrivacyLevel.PERSONAL,
        delivery_requirement=DeliveryRequirement.PRESENTATION_REQUIRED,
        entity_id="device:battery",
        correlation_id="battery-episode-1",
        payload={"power_source": "battery", "samples": [15, 13, 12]},
    )

    assert event.kind is EventKind.BATTERY_LOW
    assert event.source is EventSource.BATTERY
    assert event.priority is EventPriority.HIGH
    assert event.payload["samples"] == (15, 13, 12)
    assert event.event_id


def test_m325_1_event_and_nested_payload_are_immutable() -> None:
    event = GenericTextEvent(text="Mensaje", payload={"context": {"mode": "desktop"}})

    with pytest.raises(FrozenInstanceError):
        event.text = "Otro"  # type: ignore[misc]
    with pytest.raises(TypeError):
        event.payload["new"] = "value"  # type: ignore[index]
    nested = event.payload["context"]
    assert isinstance(nested, dict) is False
    with pytest.raises(TypeError):
        nested["mode"] = "console"  # type: ignore[index]


def test_m325_1_serialization_round_trip_preserves_concrete_type() -> None:
    occurred_at = datetime(2026, 7, 25, 18, 0, tzinfo=timezone.utc)
    event = ReminderDueEvent(
        reminder_id="reminder-42",
        title="Consulta médica",
        occurred_at=occurred_at,
        priority=75,
        payload={"advance_stage": "due"},
    )

    serialized = event_to_dict(event)
    restored = event_from_dict(serialized)

    assert serialized["schema_version"] == 1
    assert serialized["event_type"] == "ReminderDueEvent"
    assert restored == event
    assert isinstance(restored, ReminderDueEvent)


def test_m325_1_text_adapter_keeps_current_string_channel_compatible() -> None:
    event = text_to_executive_event(
        "Tenés un recordatorio pendiente.",
        source=EventSource.REMINDERS,
        correlation_id="legacy-notification-1",
    )

    assert isinstance(event, GenericTextEvent)
    assert event.text == "Tenés un recordatorio pendiente."
    assert event.source is EventSource.REMINDERS
    assert event.kind is EventKind.GENERIC_TEXT


def test_m325_1_expiry_is_evaluated_without_discarding_the_event() -> None:
    occurred_at = datetime(2026, 7, 25, 18, 0, tzinfo=timezone.utc)
    event = VerifiedNewsEvent(
        headline="Noticia verificada",
        publisher="Fuente",
        occurred_at=occurred_at,
        expires_at=occurred_at + timedelta(minutes=30),
    )

    assert not event.is_expired(occurred_at + timedelta(minutes=29))
    assert event.is_expired(occurred_at + timedelta(minutes=30))


@pytest.mark.parametrize(
    "event",
    [
        AmbientObservationEvent(observation="Se detectó movimiento", confidence=0.8),
        ImportantEmailEvent(
            message_reference="gmail:abc",
            subject="Turno confirmado",
            sender="Clínica",
        ),
        VisualCaptureResultEvent(
            description="La puerta está cerrada",
            capture_reference="capture:123",
            privacy_level=PrivacyLevel.SENSITIVE,
        ),
    ],
)
def test_m325_1_initial_event_catalog_serializes(event: object) -> None:
    serialized = event_to_dict(event)  # type: ignore[arg-type]
    assert event_from_dict(serialized) == event


def test_m325_1_rejects_invalid_common_and_specific_values() -> None:
    naive = datetime(2026, 7, 25, 18, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        GenericTextEvent(text="Mensaje", occurred_at=naive)
    with pytest.raises(ValueError, match="between 0 and 100"):
        BatteryLowEvent(battery_percent=101)
    with pytest.raises(ValueError, match="confidence"):
        AmbientObservationEvent(observation="Ruido", confidence=1.1)
    with pytest.raises(TypeError, match="non-JSON-compatible"):
        GenericTextEvent(text="Mensaje", payload={"bad": object()})


def test_m325_1_rejects_unknown_schema_and_event_types() -> None:
    event = event_to_dict(GenericTextEvent(text="Mensaje"))
    event["schema_version"] = 2
    with pytest.raises(ValueError, match="schema version"):
        event_from_dict(event)

    event["schema_version"] = 1
    event["event_type"] = "UnknownEvent"
    with pytest.raises(ValueError, match="unknown executive event type"):
        event_from_dict(event)
