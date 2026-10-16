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
        session_id="l3-adversarial",
        text=text,
        request=LLMRequest(prompt=text),
        now=NOW,
    ).activated_stages


def _request(
    text: str,
    *,
    owner: str = "Carlos",
    session_id: str = "l3-adversarial",
) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner=owner,
        session_id=session_id,
        text=text,
    )


def test_a5_paraphrased_reasoning_without_trigger_word_is_selected() -> None:
    assert _stages(
        "Sopesá los pros y los contras de estas dos alternativas."
    ) == ("reasoning",)


def test_a5_paraphrased_planning_without_trigger_word_is_selected() -> None:
    assert _stages(
        "Armame una secuencia de pasos para abordar este problema."
    ) == ("planning",)


def test_a5_paraphrased_reflection_without_trigger_word_is_selected() -> None:
    assert _stages(
        "Pensá de nuevo en la respuesta y detectá qué quedó flojo."
    ) == ("reflection",)


def test_a5_paraphrased_coordination_without_trigger_word_is_selected() -> None:
    assert _stages(
        "Hacé que estas partes trabajen juntas de forma coherente."
    ) == ("executive",)


def test_a5_negated_planning_is_not_overselected() -> None:
    assert _stages(
        "Analizá estas opciones, pero no planifiques todavía."
    ) == ("reasoning",)


def test_a5_negated_reflection_is_not_overselected() -> None:
    assert _stages(
        "Planificá los pasos sin reflexionar todavía sobre resultados previos."
    ) == ("planning",)


def test_a5_irrelevant_cognitive_words_in_quoted_context_do_not_overselect() -> None:
    assert _stages(
        'Explicame qué significa la frase "planificá y reflexioná" sin hacerlo.'
    ) == ()


def test_a6_novel_paraphrase_composes_memory_weather_decision() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    advice = coordinator.compose_advisory(
        _request(
            "Tomá en cuenta lo que habíamos acordado y las condiciones "
            "meteorológicas de hoy para elegir la opción más conveniente."
        )
    )
    assert advice is not None
    assert advice.needs == ("memory", "weather", "decision")


def test_a6_negated_weather_is_excluded_from_novel_composition() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    advice = coordinator.compose_advisory(
        _request(
            "Considerá lo que recordamos de mi restricción; el clima no importa "
            "para decidir qué conviene."
        )
    )
    assert advice is not None
    assert "memory" in advice.needs
    assert "decision" in advice.needs
    assert "weather" not in advice.needs


def test_a6_distractor_calendar_is_not_added_without_relevance() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    advice = coordinator.compose_advisory(
        _request(
            "Considerá lo que recordamos de mi restricción y el clima actual "
            "para decidir. La palabra calendario aparece sólo como ejemplo."
        )
    )
    assert advice is not None
    assert "calendar" not in advice.needs


def test_a6_owner_scope_and_provenance_survive_adversarial_paraphrase() -> None:
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    advice = coordinator.compose_advisory(
        _request(
            "Tomá en cuenta lo que habíamos acordado y el clima de hoy para "
            "elegir qué conviene.",
            owner="Cristina",
            session_id="scope-novel",
        )
    )
    assert advice is not None
    assert advice.owner == "Cristina"
    assert advice.scope == "scope-novel"
    assert advice.provenance == (
        "cognitive_planning:required_tools",
        "cognitive_planning:cognitive_needs",
        "decision:unified_cognitive_coordination",
    )


def test_a6_adversarial_path_never_executes_capabilities() -> None:
    class Registry:
        registrations = ()

        def __init__(self) -> None:
            self.executions = 0

        def execute_registration(self, *args, **kwargs):
            self.executions += 1
            raise AssertionError("advisory path must not execute capabilities")

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
