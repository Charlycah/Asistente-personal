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


def _run(text: str):
    return _runtime().enrich(
        owner="Carlos",
        session_id="l3-inhibition-causal",
        text=text,
        request=LLMRequest(prompt=text),
        now=NOW,
    )


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="l3-inhibition-causal",
        text=text,
    )


def test_negation_is_causal_for_reflection_selection() -> None:
    asserted = _run("Planificá los pasos y reflexioná sobre resultados previos.")
    inhibited = _run(
        "Planificá los pasos sin reflexionar todavía sobre resultados previos."
    )

    assert asserted.activated_stages == ("planning", "reflection")
    assert inhibited.activated_stages == ("planning",)
    assert asserted.request.metadata["cognitive_stages"] == "planning,reflection"
    assert inhibited.request.metadata["cognitive_stages"] == "planning"


def test_negation_is_causal_for_coordination_selection() -> None:
    asserted = _run("Reflexioná sobre la respuesta y coordiná las partes.")
    inhibited = _run(
        "Reflexioná sobre la respuesta sin coordinar todavía las partes."
    )

    assert asserted.activated_stages == ("reflection", "executive")
    assert inhibited.activated_stages == ("reflection",)


def test_negation_is_causal_for_planning_and_reasoning_selection() -> None:
    planning_asserted = _run("Analizá estas opciones y planificá los próximos pasos.")
    planning_inhibited = _run(
        "Analizá estas opciones, pero no planifiques todavía."
    )
    reasoning_asserted = _run("Planificá los pasos y analizá las alternativas.")
    reasoning_inhibited = _run(
        "Planificá los pasos, pero no analices todavía las alternativas."
    )

    assert planning_asserted.activated_stages == ("reasoning", "planning")
    assert planning_inhibited.activated_stages == ("reasoning",)
    assert reasoning_asserted.activated_stages == ("reasoning", "planning")
    assert reasoning_inhibited.activated_stages == ("planning",)


def test_quotation_is_causal_for_cognitive_selection() -> None:
    asserted = _run("Planificá y reflexioná sobre este problema.")
    mentioned = _run(
        'Explicame qué significa la frase "planificá y reflexioná" sin hacerlo.'
    )

    assert asserted.activated_stages == ("planning", "reflection")
    assert mentioned.activated_stages == ()


def test_quoted_distractors_do_not_change_asserted_reasoning() -> None:
    control = _run("Analizá la opción.")
    distracted = _run(
        'Analizá la opción y explicame la frase "planificá y reflexioná".'
    )

    assert control.activated_stages == ("reasoning",)
    assert distracted.activated_stages == ("reasoning",)
    assert control.request.metadata["cognitive_stages"] == "reasoning"
    assert distracted.request.metadata["cognitive_stages"] == "reasoning"


def test_negated_distractors_do_not_change_asserted_reasoning() -> None:
    control = _run("Analizá las opciones.")
    distracted = _run(
        "Analizá las opciones sin planificar ni reflexionar todavía."
    )

    assert control.activated_stages == ("reasoning",)
    assert distracted.activated_stages == ("reasoning",)


def test_inhibition_changes_applied_vs_skipped_status_causally() -> None:
    result = _run(
        "Planificá los pasos sin reflexionar todavía sobre resultados previos."
    )
    states = {item.stage: item.status.value for item in result.contributions}

    assert states["planning"] == "applied"
    assert states["reflection"] == "skipped"
    assert states["reasoning"] == "skipped"
    assert states["executive"] == "skipped"


def test_a6_changed_condition_and_identity_provenance_remain_preserved() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    first = coordinator.compose_advisory(
        _request(
            "Considerá lo que recordamos de mi restricción y el clima actual "
            "para decidir qué conviene."
        )
    )
    second = coordinator.compose_advisory(
        _request(
            "Considerá lo que recordamos de mi restricción; el clima ya no "
            "es relevante para esta decisión."
        )
    )

    assert first is not None and second is not None
    assert "weather" in first.needs
    assert "weather" not in second.needs
    assert first.owner == second.owner == "Carlos"
    assert first.scope == second.scope == "l3-inhibition-causal"
    assert first.provenance == second.provenance


def test_inhibition_certification_does_not_authorize_execution() -> None:
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
