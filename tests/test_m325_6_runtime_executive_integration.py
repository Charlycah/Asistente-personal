from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.executive_event_model import (
    BatteryLowEvent,
    DeliveryRequirement,
    EventPriority,
)
from core.executive_presence_attention import AttentionState
from core.executive_runtime_integration import (
    RuntimeExecutiveIntegration,
    render_executive_event,
)

NOW = datetime(2026, 7, 25, 22, 0, tzinfo=timezone.utc)


def test_runtime_routes_legacy_text_through_executive_pipeline() -> None:
    runtime = RuntimeExecutiveIntegration()
    runtime.start(now=NOW)

    result = runtime.publish_text("Recordatorio de prueba")

    assert result.accepted
    assert runtime.drain_notifications() == ("Recordatorio de prueba",)
    snapshot = runtime.snapshot
    assert snapshot.published_count == 1
    assert snapshot.presented_count == 1
    assert snapshot.drained_count == 1
    assert snapshot.coordinator.dispatched_count == 1
    assert snapshot.broker.dispatched_count == 1


def test_runtime_defers_notification_while_roby_is_responding() -> None:
    runtime = RuntimeExecutiveIntegration()
    runtime.start(now=NOW)
    runtime.update_attention(AttentionState.ROBY_RESPONDING, observed_at=NOW)
    runtime.publish_text("No interrumpir")

    assert runtime.drain_notifications() == ()
    assert runtime.snapshot.broker.pending_count == 1

    runtime.update_attention(AttentionState.AVAILABLE, observed_at=NOW)
    assert runtime.drain_notifications() == ("No interrumpir",)


def test_runtime_critical_event_crosses_attention_block() -> None:
    runtime = RuntimeExecutiveIntegration()
    runtime.start(now=NOW)
    runtime.update_attention(AttentionState.DO_NOT_DISTURB, observed_at=NOW)
    runtime.publish(
        BatteryLowEvent(
            battery_percent=3,
            priority=EventPriority.CRITICAL,
            delivery_requirement=DeliveryRequirement.PRESENTATION_REQUIRED,
        )
    )

    assert runtime.drain_notifications() == ("Batería baja: 3% (sin cargar).",)


def test_runtime_lifecycle_is_idempotent_and_rejects_stopped_publish() -> None:
    runtime = RuntimeExecutiveIntegration()

    with pytest.raises(RuntimeError, match="not running"):
        runtime.publish_text("antes de iniciar")

    first = runtime.start(now=NOW)
    second = runtime.start(now=NOW)
    assert first.running is True
    assert second.running is True

    runtime.stop(now=NOW)
    runtime.stop(now=NOW)
    assert runtime.snapshot.running is False


def test_runtime_health_tracks_successful_pipeline() -> None:
    runtime = RuntimeExecutiveIntegration()
    runtime.start(now=NOW)
    runtime.publish_text("salud")
    runtime.drain_notifications()

    components = {
        item.component_id: item for item in runtime.snapshot.health.components
    }
    assert components["executive.coordinator"].total_successes >= 3
    assert components["executive.broker"].total_successes >= 2
    assert components["executive.presentation"].total_successes >= 2


def test_renderer_supports_typed_battery_event() -> None:
    event = BatteryLowEvent(battery_percent=12, charging=True)

    assert render_executive_event(event) == "Batería baja: 12% (cargando)."
