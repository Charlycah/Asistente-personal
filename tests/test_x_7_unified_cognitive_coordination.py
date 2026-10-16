from datetime import datetime, timezone

from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


class Interceptor:
    def __init__(self, trigger: str, response: str) -> None:
        self.trigger = trigger
        self.response = response
        self.calls = 0

    def intercept(self, request, *, now):
        del now
        if self.trigger not in request.text.casefold():
            return None
        self.calls += 1
        return GovernedOperationalInterception(
            response_text=self.response,
            rationale="test_completed",
        )


def request(text: str):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="household-main",
        text=text,
    )


def registry():
    item = OfficialRuntimeCapabilityRegistry()
    item.register(
        name="weather.household",
        description="Weather",
        interceptor=Interceptor("clima", "Manana llueve."),
    )
    item.register(
        name="household.daily_briefing",
        description="Briefing",
        interceptor=Interceptor("resumen", "Tenes una reunion a las 9."),
    )
    item.register(
        name="resident.reminders",
        description="Reminders",
        interceptor=Interceptor("recordatorios", "No hay recordatorios."),
    )
    return item


def test_coordinates_an_outing_with_multiple_capabilities():
    coordinator = UnifiedCognitiveCoordinator(registry())
    result = coordinator.intercept(request("organizame la salida"), now=NOW)
    assert result is not None
    assert "Plan coordinado" in result.response_text
    assert "Manana llueve" in result.response_text
    assert "reunion" in result.response_text
    assert coordinator.snapshot.coordinated_turns == 1


def test_ordinary_requests_are_left_to_the_existing_runtime():
    coordinator = UnifiedCognitiveCoordinator(registry())
    assert coordinator.intercept(request("como esta el clima"), now=NOW) is None


def test_high_risk_capabilities_are_not_executed_implicitly():
    item = registry()
    camera = Interceptor("camara", "Foto tomada")
    item.register(
        name="camera.capture_runtime",
        description="Camera",
        interceptor=camera,
        risk="high",
        requires_confirmation=True,
    )
    coordinator = UnifiedCognitiveCoordinator(item)
    result = coordinator.intercept(request("organizame la salida"), now=NOW)
    assert result is not None
    assert camera.calls == 0


def test_coordination_snapshot_exposes_executed_capabilities():
    coordinator = UnifiedCognitiveCoordinator(registry())
    coordinator.intercept(request("organizame el dia"), now=NOW)
    assert coordinator.snapshot.executed_capabilities == (
        "household.daily_briefing",
        "weather.household",
        "resident.reminders",
    )
