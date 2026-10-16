from __future__ import annotations

import importlib

from app.unified_cognitive_coordination import (
    GovernedStrategyMetacognitiveAdaptation,
    StrategyMetacognitiveAdaptationStatus,
)

MODULE = "app.governed_strategy_metacognitive_learning_bridge"


def _bridge_type():
    module = importlib.import_module(MODULE)
    return module.GovernedStrategyMetacognitiveLearningBridge


def _adaptation(
    *,
    status: StrategyMetacognitiveAdaptationStatus = (
        StrategyMetacognitiveAdaptationStatus.ADAPTATION_SUGGESTED
    ),
    recommendation: str | None = "strategy-a",
) -> GovernedStrategyMetacognitiveAdaptation:
    source = "a" * 64
    return GovernedStrategyMetacognitiveAdaptation(
        advisory_id=f"strategy-metacognitive-adaptation-{source[:24]}",
        status=status,
        evaluation_scope="scope-a",
        candidate_strategy_fingerprints=("strategy-a", "strategy-b"),
        recommended_strategy_fingerprint=recommendation,
        source_observation_ids=("observation-1", "observation-2"),
        world_snapshot_ids=("world-1", "world-2"),
        rationale_codes=(
            "strategy_adaptation:bounded_supportive_pattern_observed",
        ),
        source_fingerprint=source,
    )


def test_h4_projects_only_suggested_adaptation_into_canonical_learning() -> None:
    result = _bridge_type()().evaluate(_adaptation(), confidence=0.8)

    assert result.uses_existing_m369 is True
    assert result.source_candidate.subject.startswith("strategy_metacognition:")
    assert result.source_candidate.disposition.value == "review_required"
    assert result.source_candidate.accepted_as_knowledge is False
    assert result.source_candidate.persistence_authorized is False


def test_h4_preserves_metacognitive_lineage_in_learning_observations() -> None:
    bridge = _bridge_type()()
    result = bridge.evaluate(_adaptation(), confidence=0.8)

    candidate = result.source_candidate
    assert set(candidate.observation_ids) == {
        "strategy-metacognition:observation-1",
        "strategy-metacognition:observation-2",
    }
    assert "world-1" in candidate.proposed_value
    assert "world-2" in candidate.proposed_value


def test_h4_learning_statement_remains_bounded_to_evaluation_scope() -> None:
    result = _bridge_type()().evaluate(_adaptation(), confidence=0.8)

    value = result.source_candidate.proposed_value.casefold()
    assert "scope-a" in value
    assert "strategy-a" in value
    assert "always" not in value
    assert "superior" not in value
    assert "causes" not in value


def test_h4_insufficient_evidence_fails_closed() -> None:
    adaptation = _adaptation(
        status=StrategyMetacognitiveAdaptationStatus.INSUFFICIENT_EVIDENCE,
        recommendation=None,
    )
    result = _bridge_type()().evaluate(adaptation, confidence=0.8)

    assert result.status.value == "not_eligible"
    assert result.accepts_learning is False
    assert result.persists_results is False


def test_h4_ambiguous_adaptation_fails_closed() -> None:
    adaptation = _adaptation(
        status=StrategyMetacognitiveAdaptationStatus.AMBIGUOUS,
        recommendation=None,
    )
    result = _bridge_type()().evaluate(adaptation, confidence=0.8)

    assert result.status.value == "not_eligible"
    assert result.accepts_learning is False


def test_h4_review_required_adaptation_fails_closed() -> None:
    adaptation = _adaptation(
        status=StrategyMetacognitiveAdaptationStatus.REVIEW_REQUIRED,
        recommendation=None,
    )
    result = _bridge_type()().evaluate(adaptation, confidence=0.8)

    assert result.status.value == "not_eligible"
    assert result.accepts_learning is False


def test_h4_requires_explicit_bounded_confidence() -> None:
    bridge = _bridge_type()()

    for confidence in (-0.1, 1.1):
        result = bridge.evaluate(_adaptation(), confidence=confidence)
        assert result.status.value == "not_eligible"
        assert result.accepts_learning is False


def test_h4_bridge_never_writes_memory_or_knowledge() -> None:
    result = _bridge_type()().evaluate(_adaptation(), confidence=0.8)

    assert result.read_only is True
    assert result.accepts_learning is False
    assert result.persists_results is False
    assert result.writes_memory is False
    assert result.writes_knowledge is False


def test_h4_does_not_mutate_the_metacognitive_source_contract() -> None:
    adaptation = _adaptation()
    before = adaptation

    _bridge_type()().evaluate(adaptation, confidence=0.8)

    assert adaptation == before
    assert adaptation.application_authorized is False
    assert adaptation.modifies_planner is False
    assert adaptation.persists_preference is False
    assert adaptation.creates_learning is False
    assert adaptation.creates_memory is False
    assert adaptation.executes_actions is False
    assert adaptation.grants_authority is False
