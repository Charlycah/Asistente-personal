from __future__ import annotations

from datetime import datetime, timezone

from app.cognitive_runtime_sources import OperationalCognitiveSource
from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.cognitive_runtime_orchestration import CognitiveRuntimeOrchestrator
from core.executive_cognitive_runtime import ExecutiveCognitiveRuntimeContributor
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.llm_provider import LLMRequest
from core.planning_runtime_integration import PlanningRuntimeContributor
from core.reasoning_runtime_integration import ReasoningRuntimeContributor
from core.reflection_runtime_integration import ReflectionRuntimeContributor

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


def _runtime() -> CognitiveRuntimeOrchestrator:
    source = OperationalCognitiveSource()
    return CognitiveRuntimeOrchestrator(
        (
            ReasoningRuntimeContributor(source.reasoning),
            PlanningRuntimeContributor(source.planning),
            ReflectionRuntimeContributor(source.reflection),
            ExecutiveCognitiveRuntimeContributor(source.coordination),
        )
    )


def _stages(text: str) -> tuple[str, ...]:
    return _runtime().enrich(
        owner="Carlos",
        session_id="l3-inhibition-red",
        text=text,
        request=LLMRequest(prompt=text),
        now=NOW,
    ).activated_stages


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="l3-inhibition-red",
        text=text,
    )


def test_negated_reflection_is_inhibited() -> None:
    assert _stages(
        "Planificá los pasos sin reflexionar todavía sobre resultados previos."
    ) == ("planning",)


def test_negated_planning_is_inhibited() -> None:
    assert _stages(
        "Analizá estas opciones, pero no planifiques todavía."
    ) == ("reasoning",)


def test_negated_reasoning_is_inhibited() -> None:
    assert _stages(
        "Planificá los pasos, pero no analices todavía las alternativas."
    ) == ("planning",)


def test_negated_coordination_is_inhibited() -> None:
    assert _stages(
        "Reflexioná sobre la respuesta sin coordinar todavía las partes."
    ) == ("reflection",)


def test_quoted_cognitive_commands_are_not_selected() -> None:
    assert _stages(
        'Explicame qué significa la frase "planificá y reflexioná" sin hacerlo.'
    ) == ()


def test_positive_unquoted_request_remains_selected() -> None:
    assert _stages(
        "Planificá los pasos y reflexioná sobre los riesgos."
    ) == ("planning", "reflection")


def test_mixed_asserted_and_quoted_needs_selects_only_asserted() -> None:
    assert _stages(
        'Analizá la opción y explicame la frase "planificá y reflexioná".'
    ) == ("reasoning",)


def test_mixed_asserted_and_negated_needs_selects_only_asserted() -> None:
    assert _stages(
        "Analizá las opciones sin planificar ni reflexionar todavía."
    ) == ("reasoning",)


def test_a6_changed_condition_weather_exclusion_stays_green() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    advice = coordinator.compose_advisory(
        _request(
            "Considerá lo que recordamos de mi restricción; el clima ya no "
            "es relevante para esta decisión."
        )
    )
    assert advice is not None
    assert "weather" not in advice.needs
    assert "memory" in advice.needs
    assert "decision" in advice.needs


def test_a6_identity_and_provenance_stay_green() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    advice = coordinator.compose_advisory(
        _request(
            "Considerá lo que recordamos de mi restricción y el clima actual "
            "para decidir qué conviene."
        )
    )
    assert advice is not None
    assert advice.owner == "Carlos"
    assert advice.scope == "l3-inhibition-red"
    assert advice.provenance == (
        "cognitive_planning:required_tools",
        "cognitive_planning:cognitive_needs",
        "decision:unified_cognitive_coordination",
    )


def test_inhibition_work_does_not_authorize_execution() -> None:
    class Registry:
        registrations = ()

        def __init__(self) -> None:
            self.executions = 0

        def execute_registration(self, *args, **kwargs):
            self.executions += 1
            raise AssertionError("advisory path must not execute")

    registry = Registry()
    advice = UnifiedCognitiveCoordinator(registry).compose_advisory(
        _request(
            "Considerá lo que recordamos de mi restricción y el clima actual "
            "para decidir qué conviene."
        )
    )
    assert advice is not None
    assert advice.execution_authorized is False
    assert registry.executions == 0
