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

FIXED_UTC_NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="a6-red",
        text=text,
    )


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
    result = _runtime().enrich(
        owner="Carlos",
        session_id="a5-red",
        text=text,
        request=LLMRequest(prompt=text),
        now=FIXED_UTC_NOW,
    )
    return result.activated_stages


def test_a5_reasoning_only_selects_reasoning() -> None:
    assert _stages(
        "Analizá cognitivamente si estas dos alternativas son equivalentes."
    ) == ("reasoning",)


def test_a5_planning_only_selects_planning() -> None:
    assert _stages(
        "Planificá cómo estudiar este problema sin ejecutar ninguna acción."
    ) == ("planning",)


def test_a5_reflection_only_selects_reflection() -> None:
    assert _stages(
        "Reflexioná sobre por qué esta explicación podría estar incompleta."
    ) == ("reflection",)


def test_a5_coordination_only_selects_executive() -> None:
    assert _stages("Coordiná cognitivamente estas partes sin ejecutar acciones.") == (
        "executive",
    )


def test_a5_reasoning_plus_planning_selects_only_both() -> None:
    assert _stages(
        "Analizá cognitivamente las opciones y planificá cómo compararlas."
    ) == ("reasoning", "planning")


def test_a5_non_cognitive_turn_still_selects_no_stages() -> None:
    assert _stages("Hola, contame algo breve.") == ()


def test_a6_novel_request_is_not_a_historical_scenario() -> None:
    text = (
        "Evaluá mi restricción anterior junto con el clima actual y proponé "
        "cómo debería decidir, sin ejecutar nada."
    )
    assert UnifiedCognitiveCoordinator._detect_scenario(text) is None


def test_a6_novel_request_produces_advisory_composition() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    text = (
        "Evaluá mi restricción anterior junto con el clima actual y proponé "
        "cómo debería decidir, sin ejecutar nada."
    )
    advice = coordinator.compose_advisory(_request(text))
    assert advice is not None
    assert advice.execution_authorized is False
    assert "memory" in advice.needs
    assert "weather" in advice.needs
    assert "decision" in advice.needs


def test_a6_advisory_composition_requires_no_explicit_clause_separator() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    text = (
        "Considerá lo que recordamos de mi restricción y el clima actual "
        "para evaluar qué conviene hacer."
    )
    assert ";" not in text
    advice = coordinator.compose_advisory(_request(text))
    assert advice is not None
    assert set(advice.needs) >= {"memory", "weather"}


def test_a6_changed_conditions_change_advisory_composition() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    first = coordinator.compose_advisory(
        _request("Considerá lo que recordamos de mi restricción y el clima actual "
        "para evaluar qué conviene hacer.")
    )
    second = coordinator.compose_advisory(
        _request("Considerá lo que recordamos de mi restricción; el clima ya no es "
        "relevante para esta decisión.")
    )
    assert first is not None and second is not None
    assert first.needs != second.needs
    assert "weather" in first.needs
    assert "weather" not in second.needs


def test_a6_advisory_never_executes_capabilities() -> None:
    class Registry:
        def __init__(self) -> None:
            self.executions = 0

        @property
        def registrations(self):
            return ()

        def execute_registration(self, *args, **kwargs):
            self.executions += 1
            raise AssertionError("advisory composition must not execute capabilities")

    registry = Registry()
    coordinator = UnifiedCognitiveCoordinator(registry)
    advice = coordinator.compose_advisory(
        _request(
            "Evaluá mi restricción anterior junto con el clima actual y proponé "
        "cómo debería decidir, sin ejecutar nada.")
    )
    assert advice is not None
    assert registry.executions == 0
