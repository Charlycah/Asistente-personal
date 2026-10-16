from datetime import datetime, timezone

from app.executive_cognitive_director import ExecutiveCognitiveDirector
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
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


def test_director_infers_weather_and_briefing_for_early_departure():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("pronostico", "Manana: 8 grados y lluvia.")
    briefing = StubInterceptor("que tengo hoy", "Tenes una reunion a las 8.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.register(
        name="household.daily_briefing",
        description="Resumen",
        interceptor=briefing,
    )
    director = ExecutiveCognitiveDirector(registry)

    result = director.intercept(
        request("Manana tengo que salir temprano"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert "salida temprana" in result.response_text
    assert "8 grados" in result.response_text
    assert "reunion" in result.response_text
    assert director.snapshot.executed_requests == 2


def test_director_does_not_take_over_explicit_questions():
    registry = OfficialRuntimeCapabilityRegistry()
    director = ExecutiveCognitiveDirector(registry)

    result = director.intercept(
        request("Como esta el clima manana?"),
        now=datetime.now(timezone.utc),
    )

    assert result is None
    assert director.snapshot.directed_turns == 0


def test_director_does_not_execute_sensitive_capabilities():
    registry = OfficialRuntimeCapabilityRegistry()
    camera = StubInterceptor("pronostico", "Camara activada.")
    registry.register(
        name="device.camera",
        description="Camara",
        interceptor=camera,
        risk="high",
        requires_confirmation=True,
    )
    director = ExecutiveCognitiveDirector(registry)

    result = director.intercept(
        request("Manana tengo que salir temprano"),
        now=datetime.now(timezone.utc),
    )

    assert result is None
    assert camera.calls == []


def test_registry_runs_director_before_planner_and_orchestrator():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("pronostico", "Pronostico disponible.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.set_director(ExecutiveCognitiveDirector(registry))

    result = registry.intercept(
        request("Manana tengo que salir temprano"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.rationale == "executive_cognitive_direction_completed"
