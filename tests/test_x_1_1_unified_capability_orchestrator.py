from datetime import datetime, timezone

from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from app.unified_capability_orchestrator import UnifiedCapabilityOrchestrator
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


class StubInterceptor:
    def __init__(self, trigger: str, response: str) -> None:
        self.trigger = trigger
        self.response = response
        self.calls: list[str] = []

    def intercept(self, request, *, now):
        del now
        self.calls.append(request.text)
        if self.trigger not in request.text.casefold():
            return None
        return GovernedOperationalInterception(
            response_text=self.response,
            rationale=f"{self.trigger}_completed",
        )


def request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="household-main",
        text=text,
    )


def test_orchestrator_combines_two_safe_capabilities():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("clima", "Hace 14 grados.")
    reminders = StubInterceptor("recordame", "Recordatorio creado.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.register(
        name="resident.reminders",
        description="Recordatorios",
        interceptor=reminders,
    )
    orchestrator = UnifiedCapabilityOrchestrator(registry)

    result = orchestrator.intercept(
        request("Decime el clima y despues recordame llevar paraguas"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert "Hace 14 grados." in result.response_text
    assert "Recordatorio creado." in result.response_text
    assert orchestrator.snapshot.composed_turns == 1
    assert orchestrator.snapshot.last_capabilities == (
        "weather.household",
        "resident.reminders",
    )


def test_orchestrator_does_not_implicitly_execute_confirmed_capability():
    registry = OfficialRuntimeCapabilityRegistry()
    device = StubInterceptor("camara", "Camara activada.")
    registry.register(
        name="device.runtime",
        description="Dispositivo",
        interceptor=device,
        risk="high",
        permission_scope="device",
        requires_confirmation=True,
    )
    orchestrator = UnifiedCapabilityOrchestrator(registry)

    result = orchestrator.intercept(
        request("Mostrame el clima y despues activa la camara"),
        now=datetime.now(timezone.utc),
    )

    assert result is None
    assert device.calls == []


def test_registry_uses_orchestrator_before_normal_sequential_dispatch():
    registry = OfficialRuntimeCapabilityRegistry()
    first = StubInterceptor("proyecto", "Proyecto revisado.")
    second = StubInterceptor("objetivo", "Objetivo revisado.")
    registry.register(
        name="household.projects",
        description="Proyectos",
        interceptor=first,
    )
    registry.register(
        name="household.goals",
        description="Objetivos",
        interceptor=second,
    )
    registry.set_orchestrator(UnifiedCapabilityOrchestrator(registry))

    result = registry.intercept(
        request("Revisa el proyecto y ademas revisa el objetivo"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.rationale == "unified_capability_orchestration_completed"
    assert "Proyecto revisado." in result.response_text
    assert "Objetivo revisado." in result.response_text


def test_single_intent_is_left_to_existing_registry_dispatch():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("clima", "Hace frio.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.set_orchestrator(UnifiedCapabilityOrchestrator(registry))

    result = registry.intercept(
        request("Como esta el clima"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "Hace frio."
    assert result.rationale == "clima_completed"
