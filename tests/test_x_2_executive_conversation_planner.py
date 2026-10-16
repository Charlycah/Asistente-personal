from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from app.executive_conversation_planner import ExecutiveConversationPlanner
from app.runtime_capability_registry import (
    OfficialRuntimeCapabilityRegistry,
    PlanningCapabilityEvidence,
)
from core.capability_registry import CapabilityRisk
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


def test_planner_executes_action_when_condition_is_true():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("llover", "Manana puede llover. Lluvia 70%.")
    reminder = StubInterceptor("recordame", "Recordatorio creado.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.register(
        name="resident.reminders",
        description="Recordatorios",
        interceptor=reminder,
    )
    planner = ExecutiveConversationPlanner(registry)

    result = planner.intercept(
        request("Va a llover manana, si llueve, recordame llevar paraguas"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert "Lluvia 70%." in result.response_text
    assert "Recordatorio creado." in result.response_text
    assert planner.snapshot.executed_steps == 2


def test_planner_skips_action_when_condition_is_false():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("llover", "Manana sin lluvia. Lluvia 0%.")
    reminder = StubInterceptor("recordame", "Recordatorio creado.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.register(
        name="resident.reminders",
        description="Recordatorios",
        interceptor=reminder,
    )
    planner = ExecutiveConversationPlanner(registry)

    result = planner.intercept(
        request("Va a llover manana, si llueve, recordame llevar paraguas"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert "no se cumplio" in result.response_text
    assert reminder.calls == []
    assert planner.snapshot.skipped_steps == 1


def test_planner_does_not_execute_sensitive_action_implicitly():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("llover", "Lluvia 80%.")
    camera = StubInterceptor("camara", "Camara activada.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.register(
        name="device.camera",
        description="Camara",
        interceptor=camera,
        risk="high",
        requires_confirmation=True,
    )
    planner = ExecutiveConversationPlanner(registry)

    result = planner.intercept(
        request("Va a llover, si llueve, activa la camara"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert "capacidad oficial segura" in result.response_text
    assert camera.calls == []


def test_registry_runs_planner_before_orchestrator():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("llover", "Lluvia 60%.")
    reminder = StubInterceptor("recordame", "Recordatorio creado.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.register(
        name="resident.reminders",
        description="Recordatorios",
        interceptor=reminder,
    )
    registry.set_planner(ExecutiveConversationPlanner(registry))

    result = registry.intercept(
        request("Va a llover, si llueve, recordame el paraguas"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.rationale == "executive_conversation_plan_completed"


def test_planner_abstains_from_hypothetical_epistemic_question():
    registry = OfficialRuntimeCapabilityRegistry()
    planner = ExecutiveConversationPlanner(registry)

    result = planner.intercept(
        request(
            "Si el cielo estuvo despejado toda la noche, "
            "¿qué hipótesis sobre el origen del agua perdería fuerza?"
        ),
        now=datetime.now(timezone.utc),
    )

    assert result is None
    assert planner.snapshot.planned_turns == 0
    assert planner.snapshot.last_step_count == 0


def test_planner_abstains_from_hypothetical_capability_question():
    registry = OfficialRuntimeCapabilityRegistry()
    planner = ExecutiveConversationPlanner(registry)

    result = planner.intercept(
        request(
            "Si te preguntara quién era el propietario según la información inicial, "
            "¿podrías distinguirlo de la información actual?"
        ),
        now=datetime.now(timezone.utc),
    )

    assert result is None


def test_planner_admits_interrogative_performative_request():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("llueve", "Llueve. Lluvia 70%.")
    reminder = StubInterceptor("recordarme", "Recordatorio creado.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.register(
        name="resident.reminders",
        description="Recordatorios",
        interceptor=reminder,
    )
    planner = ExecutiveConversationPlanner(registry)

    result = planner.intercept(
        request("Si mañana llueve, ¿podés recordarme llevar paraguas?"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert "Recordatorio creado." in result.response_text
    assert planner.snapshot.executed_steps == 2


def test_planner_abstains_from_immediate_cognitive_imperative():
    registry = OfficialRuntimeCapabilityRegistry()
    planner = ExecutiveConversationPlanner(registry)

    result = planner.intercept(
        request("Si cambia la evidencia, analizá qué hipótesis queda."),
        now=datetime.now(timezone.utc),
    )

    assert result is None


def test_registry_projects_immutable_read_only_planning_capability_evidence():
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=StubInterceptor("llover", "Lluvia 70%."),
    )

    evidence = registry.planning_capability_evidence()

    assert evidence == (
        PlanningCapabilityEvidence(
            name="weather.household",
            enabled=True,
            requires_confirmation=False,
            risk=CapabilityRisk.LOW,
        ),
    )
    try:
        evidence[0].enabled = False
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("planning capability evidence must be immutable")


def test_planner_uses_read_only_capability_evidence_before_execution():
    registry = OfficialRuntimeCapabilityRegistry()
    weather = StubInterceptor("llover", "Lluvia 70%.")
    reminder = StubInterceptor("recordame", "Recordatorio creado.")
    registry.register(
        name="weather.household",
        description="Clima",
        interceptor=weather,
    )
    registry.register(
        name="resident.reminders",
        description="Recordatorios",
        interceptor=reminder,
    )
    registry.planning_capability_evidence = lambda: ()
    planner = ExecutiveConversationPlanner(registry)

    result = planner.intercept(
        request("Va a llover manana, si llueve, recordame llevar paraguas"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert "capacidad oficial segura" in result.response_text
    assert weather.calls == []
    assert reminder.calls == []
