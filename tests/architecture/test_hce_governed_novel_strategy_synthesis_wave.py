from __future__ import annotations

from app.unified_cognitive_coordination import UnifiedCognitiveCoordinator
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="strategy-audit",
        text=text,
    )


def _strategy(text: str, available: tuple[str, ...] | None = None):
    return UnifiedCognitiveCoordinator(registry=object()).synthesize_strategy_advisory(
        _request(text),
        available_capabilities=available,
    )


def test_novel_problem_produces_ordered_advisory_strategy_without_scenario():
    strategy = _strategy(
        "Tomá en cuenta lo que habíamos acordado, sopesá las alternativas, "
        "decidí cuál conviene y después revisá críticamente qué podría fallar."
    )
    assert strategy is not None
    assert strategy.status == "ready"
    assert strategy.capabilities == ("memory", "reasoning", "decision", "reflection")
    assert strategy.advisory_only is True
    assert strategy.execution_authorized is False
    assert strategy.persists is False
    assert strategy.learns is False
    assert strategy.grants_authority is False
    assert "scenario:" not in " ".join(strategy.rationale_codes)


def test_strategy_dependencies_follow_evidence_before_reasoning_before_decision():
    strategy = _strategy(
        "Recordá lo acordado, analizá las alternativas y elegí la más conveniente."
    )
    assert strategy is not None
    steps = {step.capability: step for step in strategy.steps}
    assert steps["memory"].depends_on == ()
    assert steps["reasoning"].depends_on == ("memory",)
    assert steps["decision"].depends_on == ("memory", "reasoning")


def test_changed_relevance_recomposes_strategy_without_weather():
    before = _strategy(
        "Recordá lo acordado, mirá el clima de hoy, analizá las opciones "
        "y decidí cuál conviene."
    )
    after = _strategy(
        "Recordá lo acordado; el clima ya no es relevante. Analizá las opciones "
        "y decidí cuál conviene."
    )
    assert before is not None and after is not None
    assert "weather" in before.capabilities
    assert "weather" not in after.capabilities
    assert before.source_fingerprint != after.source_fingerprint


def test_missing_required_capability_fails_closed():
    strategy = _strategy(
        "Recordá lo acordado, analizá las alternativas y decidí cuál conviene.",
        available=("memory", "reasoning"),
    )
    assert strategy is not None
    assert strategy.status == "blocked"
    assert strategy.missing_capabilities == ("decision",)
    assert strategy.steps == ()


def test_irrelevant_capabilities_are_not_added_just_because_available():
    strategy = _strategy(
        "Analizá estas alternativas y decidí cuál conviene.",
        available=(
            "memory",
            "weather",
            "calendar",
            "current_affairs",
            "reasoning",
            "planning",
            "reflection",
            "decision",
            "coordination",
        ),
    )
    assert strategy is not None
    assert strategy.capabilities == ("reasoning", "decision")


def test_reasonable_paraphrase_preserves_strategy_structure():
    one = _strategy(
        "Sopesá los pros y los contras y elegí la opción más conveniente."
    )
    two = _strategy(
        "Compará ventajas y desventajas y decidí cuál de las opciones conviene."
    )
    assert one is not None and two is not None
    assert one.capabilities == two.capabilities == ("reasoning", "decision")


def test_different_problem_produces_different_composition():
    decision = _strategy(
        "Analizá estas alternativas y elegí cuál conviene."
    )
    planning = _strategy(
        "Armame una secuencia de pasos y después revisá críticamente "
        "si quedó algo flojo."
    )
    assert decision is not None and planning is not None
    assert decision.capabilities == ("reasoning", "decision")
    assert planning.capabilities == ("planning", "reflection")
    assert decision.source_fingerprint != planning.source_fingerprint


def test_single_need_does_not_fake_multi_step_strategy():
    assert _strategy("Analizá este argumento.") is None


def test_strategy_preserves_owner_scope_and_provenance():
    strategy = _strategy(
        "Recordá lo anterior, analizá las opciones y decidí cuál conviene."
    )
    assert strategy is not None
    assert strategy.owner == "Carlos"
    assert strategy.scope == "strategy-audit"
    assert strategy.provenance == (
        "cognitive_planning:required_tools",
        "cognitive_planning:cognitive_needs",
        "decision:unified_cognitive_coordination",
    )
