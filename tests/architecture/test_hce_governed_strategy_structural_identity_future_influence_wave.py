from __future__ import annotations

from dataclasses import replace

from app.unified_cognitive_coordination import (
    GovernedFutureStrategyInfluenceStatus,
    GovernedStrategyMetacognitiveAdaptation,
    StrategyMetacognitiveAdaptationStatus,
    UnifiedCognitiveCoordinator,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _request(text: str, scope: str = "decision-scope"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=scope,
        text=text,
    )


def _strategy(text: str, scope: str = "decision-scope"):
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    result = coordinator.synthesize_strategy_advisory(
        _request(text, scope)
    )
    assert result is not None
    return result


def _advisory(
    recommended_instance: str | None,
    *,
    scope: str = "decision-scope",
    status: StrategyMetacognitiveAdaptationStatus = (
        StrategyMetacognitiveAdaptationStatus.ADAPTATION_SUGGESTED
    ),
):
    candidates = (
        (recommended_instance,) if recommended_instance is not None else ("unused",)
    )
    source = "a" * 64
    return GovernedStrategyMetacognitiveAdaptation(
        advisory_id=f"strategy-metacognitive-adaptation-{source[:24]}",
        status=status,
        evaluation_scope=scope,
        candidate_strategy_fingerprints=candidates,
        recommended_strategy_fingerprint=recommended_instance,
        source_observation_ids=("obs-1", "obs-2"),
        world_snapshot_ids=("world-1", "world-2"),
        rationale_codes=("strategy_adaptation:test",),
        source_fingerprint=source,
    )


def test_semantic_paraphrases_share_structural_identity_but_not_instance_identity():
    one = _strategy(
        "Sopesá los pros y los contras y elegí la opción más conveniente."
    )
    two = _strategy(
        "Compará ventajas y desventajas y decidí cuál de las opciones conviene."
    )
    assert one.capabilities == two.capabilities == ("reasoning", "decision")
    assert one.structural_fingerprint == two.structural_fingerprint
    assert one.source_fingerprint != two.source_fingerprint


def test_different_topology_has_different_structural_identity():
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    request = _request(
        "Analizá las opciones, planificá los pasos y decidí cuál conviene."
    )
    eligible = coordinator.synthesize_eligible_strategy_advisories(request)
    assert len(eligible) >= 2
    identities = {item.structural_fingerprint for item in eligible}
    assert len(identities) == len(eligible)
    assert {
        tuple(step.capability for step in item.steps)
        for item in eligible
    } >= {
        ("reasoning", "planning", "decision"),
        ("reasoning", "decision", "planning"),
    }


def test_no_advisory_preserves_current_synthesis_exactly():
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    request = _request(
        "Analizá las opciones, planificá los pasos y decidí cuál conviene."
    )
    baseline = coordinator.synthesize_strategy_advisory(request)
    influenced = coordinator.synthesize_strategy_with_metacognitive_influence(
        request,
        advisory=None,
        historical_strategies=(),
    )
    assert influenced.strategy == baseline
    assert influenced.influence.status is (
        GovernedFutureStrategyInfluenceStatus.NO_INFLUENCE
    )


def test_historical_preference_can_select_current_eligible_structure():
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    current_request = _request(
        "Analizá las opciones, planificá los pasos y decidí cuál conviene."
    )
    current_eligible = coordinator.synthesize_eligible_strategy_advisories(
        current_request
    )
    preferred_current = next(
        item
        for item in current_eligible
        if tuple(step.capability for step in item.steps)
        == ("reasoning", "decision", "planning")
    )

    historical = replace(
        preferred_current,
        source_fingerprint="historical-instance-b",
    )
    advisory = _advisory(historical.source_fingerprint)

    result = coordinator.synthesize_strategy_with_metacognitive_influence(
        current_request,
        advisory=advisory,
        historical_strategies=(historical,),
    )
    assert result.influence.status is GovernedFutureStrategyInfluenceStatus.PREFER
    assert (
        result.influence.selected_structural_fingerprint
        == historical.structural_fingerprint
    )
    assert result.strategy.structural_fingerprint == historical.structural_fingerprint
    assert result.strategy.source_fingerprint != historical.source_fingerprint
    assert result.strategy.source_fingerprint != preferred_current.source_fingerprint
    assert (
        "metacognitive_influence:bounded_preference_applied"
        in result.strategy.rationale_codes
    )


def test_influence_cannot_change_current_planner_capability_needs():
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    historical = _strategy(
        "Recordá lo anterior, analizá las opciones y decidí cuál conviene."
    )
    advisory = _advisory(historical.source_fingerprint)

    current = _request("Analizá las opciones y decidí cuál conviene.")
    result = coordinator.synthesize_strategy_with_metacognitive_influence(
        current,
        advisory=advisory,
        historical_strategies=(historical,),
    )
    assert result.strategy.capabilities == ("reasoning", "decision")
    assert "memory" not in result.strategy.capabilities
    assert result.influence.status is GovernedFutureStrategyInfluenceStatus.NO_INFLUENCE


def test_incompatible_scope_produces_no_influence():
    historical = _strategy(
        "Analizá las opciones y decidí cuál conviene.",
        scope="other-scope",
    )
    result = UnifiedCognitiveCoordinator(
        registry=object()
    ).synthesize_strategy_with_metacognitive_influence(
        _request("Compará las opciones y decidí cuál conviene."),
        advisory=_advisory(
            historical.source_fingerprint,
            scope="other-scope",
        ),
        historical_strategies=(historical,),
    )
    assert result.influence.status is GovernedFutureStrategyInfluenceStatus.NO_INFLUENCE


def test_ambiguous_review_and_insufficient_history_fail_closed():
    coordinator = UnifiedCognitiveCoordinator(registry=object())
    request = _request("Analizá las opciones y decidí cuál conviene.")
    expected = {
        StrategyMetacognitiveAdaptationStatus.AMBIGUOUS:
            GovernedFutureStrategyInfluenceStatus.AMBIGUOUS,
        StrategyMetacognitiveAdaptationStatus.REVIEW_REQUIRED:
            GovernedFutureStrategyInfluenceStatus.REVIEW_REQUIRED,
        StrategyMetacognitiveAdaptationStatus.INSUFFICIENT_EVIDENCE:
            GovernedFutureStrategyInfluenceStatus.NO_INFLUENCE,
    }
    for status, influence_status in expected.items():
        result = coordinator.synthesize_strategy_with_metacognitive_influence(
            request,
            advisory=_advisory(None, status=status),
            historical_strategies=(),
        )
        assert result.influence.status is influence_status


def test_missing_recommended_historical_instance_fails_closed():
    current = _request("Analizá las opciones y decidí cuál conviene.")
    result = UnifiedCognitiveCoordinator(
        registry=object()
    ).synthesize_strategy_with_metacognitive_influence(
        current,
        advisory=_advisory("missing-instance"),
        historical_strategies=(),
    )
    assert result.influence.status is GovernedFutureStrategyInfluenceStatus.NO_INFLUENCE


def test_tampered_advisory_integrity_is_rejected():
    advisory = _advisory("historical-instance")
    from pytest import raises

    with raises(ValueError, match="identifier is inconsistent"):
        replace(advisory, advisory_id="strategy-metacognitive-adaptation-tampered")


def test_influence_is_read_only_non_learning_non_persistent():
    historical = _strategy("Analizá las opciones y decidí cuál conviene.")
    result = UnifiedCognitiveCoordinator(
        registry=object()
    ).synthesize_strategy_with_metacognitive_influence(
        _request("Compará las opciones y decidí cuál conviene."),
        advisory=_advisory(historical.source_fingerprint),
        historical_strategies=(historical,),
    )
    influence = result.influence
    assert influence.read_only is True
    assert influence.persists is False
    assert influence.creates_learning is False
    assert influence.creates_memory is False
    assert influence.modifies_planner is False
    assert influence.executes_actions is False
    assert influence.grants_authority is False
