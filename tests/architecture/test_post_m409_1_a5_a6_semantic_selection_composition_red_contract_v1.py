from __future__ import annotations

from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.cognitive_planning.models import CognitiveNeed, ToolRequirement
from core.cognitive_planning.planner import CognitivePlanner
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _needs(text: str) -> tuple[CognitiveNeed, ...]:
    return CognitivePlanner().assess_cognitive_needs(text)


def _tools(text: str) -> tuple[ToolRequirement, ...]:
    return CognitivePlanner().plan(text).required_tools


def _advice_needs(text: str) -> tuple[str, ...]:
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="a5-a6-semantic-red",
        text=text,
    )
    advice = UnifiedCognitiveCoordinator(registry=object()).compose_advisory(
        request
    )
    assert advice is not None
    return advice.needs


def test_red_a5_reasoning_known_tradeoff_paraphrase() -> None:
    assert _needs(
        "Sopesá los pros y los contras de estas dos alternativas."
    ) == (CognitiveNeed.REASONING,)


def test_red_a5_planning_known_sequence_paraphrase() -> None:
    assert _needs(
        "Armame una secuencia de pasos para abordar este problema."
    ) == (CognitiveNeed.PLANNING,)


def test_red_a5_reflection_known_reconsider_paraphrase() -> None:
    assert _needs(
        "Pensá de nuevo en la respuesta y detectá qué quedó flojo."
    ) == (CognitiveNeed.REFLECTION,)


def test_red_a5_coordination_known_coherence_paraphrase() -> None:
    assert _needs(
        "Hacé que estas partes trabajen juntas de forma coherente."
    ) == (CognitiveNeed.COORDINATION,)


def test_red_a5_reasoning_unseen_tradeoff_paraphrase() -> None:
    assert _needs(
        "Poné en la balanza las ventajas y desventajas antes de responder."
    ) == (CognitiveNeed.REASONING,)


def test_red_a5_planning_unseen_ordered_steps_paraphrase() -> None:
    assert _needs(
        "Ordená qué tendría que hacer primero, después y al final."
    ) == (CognitiveNeed.PLANNING,)


def test_red_a5_reflection_unseen_weakness_review_paraphrase() -> None:
    assert _needs(
        "Volvé sobre lo que respondiste y buscá puntos débiles u omisiones."
    ) == (CognitiveNeed.REFLECTION,)


def test_red_a5_coordination_unseen_integration_paraphrase() -> None:
    assert _needs(
        "Lográ que todos estos componentes funcionen como un conjunto coherente."
    ) == (CognitiveNeed.COORDINATION,)


def test_red_a6_weather_adjectival_family_without_legacy_trigger() -> None:
    tools = _tools("Revisá las condiciones meteorológicas previstas para mañana.")
    assert ToolRequirement.WEATHER in tools
    assert ToolRequirement.CURRENT_AFFAIRS not in tools


def test_red_a6_decision_choice_family_without_legacy_trigger() -> None:
    assert _needs(
        "Elegí entre las alternativas la que resulte más adecuada."
    ) == (CognitiveNeed.DECISION,)


def test_red_a6_known_memory_weather_decision_composition() -> None:
    assert _advice_needs(
        "Tomá en cuenta lo que habíamos acordado y las condiciones "
        "meteorológicas de hoy para elegir la opción más conveniente."
    ) == ("memory", "weather", "decision")


def test_red_a6_unseen_memory_weather_decision_composition() -> None:
    assert _advice_needs(
        "Usá lo que acordamos antes, considerá el panorama meteorológico "
        "actual y seleccioná la alternativa más adecuada."
    ) == ("memory", "weather", "decision")


def test_red_a6_specific_weather_beats_generic_today_fallback() -> None:
    tools = _tools(
        "Necesito las condiciones meteorológicas de hoy para organizarme."
    )
    assert ToolRequirement.WEATHER in tools
    assert ToolRequirement.CURRENT_AFFAIRS not in tools


def test_red_a6_remove_weather_semantics_removes_weather_only() -> None:
    needs = _advice_needs(
        "Tomá en cuenta lo que habíamos acordado para elegir la opción "
        "más conveniente."
    )
    assert needs == ("memory", "decision")


def test_red_a6_remove_decision_semantics_removes_decision_only() -> None:
    needs = _advice_needs(
        "Tomá en cuenta lo que habíamos acordado y las condiciones "
        "meteorológicas de hoy."
    )
    assert needs == ("memory", "weather")


def test_red_a6_remove_memory_semantics_removes_memory_only() -> None:
    needs = _advice_needs(
        "Considerá las condiciones meteorológicas de hoy para elegir "
        "la opción más conveniente."
    )
    assert needs == ("weather", "decision")


def test_guard_legacy_reasoning_trigger_remains_selected() -> None:
    assert _needs("Analizá estas dos alternativas.") == (
        CognitiveNeed.REASONING,
    )


def test_guard_legacy_multi_need_selection_remains_ordered() -> None:
    assert _needs(
        "Analizá las opciones, planificá los pasos y reflexioná sobre riesgos."
    ) == (
        CognitiveNeed.REASONING,
        CognitiveNeed.PLANNING,
        CognitiveNeed.REFLECTION,
    )


def test_guard_negated_legacy_planning_remains_excluded() -> None:
    assert _needs(
        "Analizá estas opciones, pero no planifiques todavía."
    ) == (CognitiveNeed.REASONING,)


def test_guard_quoted_commands_remain_excluded() -> None:
    assert _needs(
        'Explicame la frase "planificá y reflexioná" sin hacerlo.'
    ) == ()


def test_guard_weather_irrelevant_remains_excluded() -> None:
    tools = _tools(
        "Recordá lo anterior; el clima no es relevante para esta decisión."
    )
    assert ToolRequirement.WEATHER not in tools
    assert ToolRequirement.MEMORY in tools


def test_guard_genuine_current_affairs_remains_current_affairs() -> None:
    tools = _tools("¿Qué noticias hay hoy sobre las elecciones?")
    assert ToolRequirement.CURRENT_AFFAIRS in tools
    assert ToolRequirement.WEATHER not in tools


def test_guard_advisory_identity_and_provenance_remain_preserved() -> None:
    request = GovernedConversationPipelineRequest(
        owner="Cristina",
        session_id="a5-a6-identity",
        text=(
            "Considerá lo que recordamos de mi restricción y el clima actual "
            "para decidir qué conviene."
        ),
    )
    advice = UnifiedCognitiveCoordinator(registry=object()).compose_advisory(
        request
    )
    assert advice is not None
    assert advice.owner == "Cristina"
    assert advice.scope == "a5-a6-identity"
    assert advice.provenance == (
        "cognitive_planning:required_tools",
        "cognitive_planning:cognitive_needs",
        "decision:unified_cognitive_coordination",
    )
