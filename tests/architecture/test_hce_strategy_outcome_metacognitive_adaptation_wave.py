from __future__ import annotations

from dataclasses import replace

import pytest

from app.unified_cognitive_coordination import (
    GovernedStrategyMetacognitiveAdaptationV1,
    GovernedStrategyOutcomeObservation,
    StrategyMetacognitiveAdaptationStatus,
    StrategyOutcomePatternStatus,
)
from core.cognitive_runtime_orchestration import (
    CognitiveStrategyApplicationEvidence,
    CognitiveStrategyApplicationOutcomeStatus,
)
from core.governed_reasoning.epistemic_sufficiency import EpistemicSufficiencyStatus
from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeObservation,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityStatus,
)


def _application(
    strategy: str,
    *,
    status: str = "applied",
    owner: str = "Carlos",
    scope: str = "scope-a",
    ref: str = "reasoning-ref",
) -> CognitiveStrategyApplicationEvidence:
    return CognitiveStrategyApplicationEvidence(
        strategy_fingerprint=strategy,
        owner=owner,
        scope=scope,
        status=status,
        requested_stage_sequence=("reasoning", "planning"),
        applied_stage_sequence=("reasoning", "planning"),
        skipped_stages=(),
        failed_stages=(),
        unmet_requirements=(),
        contribution_reference_ids=(ref,),
        rationale_codes=("strategy_application:test",),
        source_fingerprint=f"application-{strategy}-{scope}",
    )


def _method_outcome(
    *,
    quality: GovernedReasoningQualityStatus,
    sufficiency: EpistemicSufficiencyStatus,
    source_reference: str = "reasoning-ref",
    snapshot: str = "world-1",
) -> GovernedReasoningMethodOutcomeObservation:
    return GovernedReasoningMethodOutcomeObservation(
        observation_id=f"reasoning-method-outcome-observation-{quality}-{sufficiency}",
        method_provenance_id="reasoning-method-provenance-test",
        method_fingerprint="method-a",
        quality_assessment_id=f"quality-{quality}",
        quality_status=quality,
        sufficiency_assessment_id=f"sufficiency-{sufficiency}",
        sufficiency_status=sufficiency,
        source_reference=source_reference,
        world_snapshot_id=snapshot,
        method_source_fingerprint="method-source",
        quality_source_fingerprint=f"quality-source-{quality}",
        sufficiency_source_fingerprint=f"sufficiency-source-{sufficiency}",
        source_fingerprint=f"outcome-{quality}-{sufficiency}",
    )


def _observation(
    strategy: str,
    *,
    quality: GovernedReasoningQualityStatus,
    sufficiency: EpistemicSufficiencyStatus,
    scope: str = "scope-a",
    snapshot: str = "world-1",
) -> GovernedStrategyOutcomeObservation:
    return GovernedStrategyOutcomeObservation.from_artifacts(
        _application(strategy, scope=scope),
        _method_outcome(
            quality=quality,
            sufficiency=sufficiency,
            snapshot=snapshot,
        ),
        evaluation_scope=scope,
    )


def test_strategy_outcome_requires_actual_full_application():
    partial = replace(
        _application("strategy-a"),
        status=CognitiveStrategyApplicationOutcomeStatus.PARTIALLY_APPLIED,
    )
    with pytest.raises(ValueError, match="fully applied"):
        GovernedStrategyOutcomeObservation.from_artifacts(
            partial,
            _method_outcome(
                quality=GovernedReasoningQualityStatus.ADEQUATE,
                sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            ),
            evaluation_scope="scope-a",
        )


def test_strategy_outcome_requires_exact_reasoning_reference_lineage():
    with pytest.raises(ValueError, match="reference lineage"):
        GovernedStrategyOutcomeObservation.from_artifacts(
            _application("strategy-a", ref="other-ref"),
            _method_outcome(
                quality=GovernedReasoningQualityStatus.ADEQUATE,
                sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            ),
            evaluation_scope="scope-a",
        )


def test_strategy_outcome_preserves_strategy_and_method_identity():
    observation = _observation(
        "strategy-a",
        quality=GovernedReasoningQualityStatus.ADEQUATE,
        sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
    )
    assert observation.strategy_fingerprint == "strategy-a"
    assert observation.reasoning_method_fingerprint == "method-a"
    assert observation.application_fingerprint == "application-strategy-a-scope-a"
    assert observation.pattern_status is StrategyOutcomePatternStatus.SUPPORTIVE
    assert observation.read_only is True
    assert observation.establishes_causality is False


def test_limited_or_insufficient_outcome_is_limiting_not_supportive():
    observation = _observation(
        "strategy-a",
        quality=GovernedReasoningQualityStatus.LIMITED,
        sufficiency=EpistemicSufficiencyStatus.INSUFFICIENT,
    )
    assert observation.pattern_status is StrategyOutcomePatternStatus.LIMITING


def test_review_required_outcome_forces_review_pattern():
    observation = _observation(
        "strategy-a",
        quality=GovernedReasoningQualityStatus.REVIEW_REQUIRED,
        sufficiency=EpistemicSufficiencyStatus.INDETERMINATE,
    )
    assert observation.pattern_status is StrategyOutcomePatternStatus.REVIEW_REQUIRED


def test_repeated_support_vs_repeated_limitation_produces_bounded_adaptation():
    observations = (
        _observation(
            "strategy-a",
            quality=GovernedReasoningQualityStatus.ADEQUATE,
            sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            snapshot="world-1",
        ),
        _observation(
            "strategy-a",
            quality=GovernedReasoningQualityStatus.ADEQUATE,
            sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            snapshot="world-2",
        ),
        _observation(
            "strategy-b",
            quality=GovernedReasoningQualityStatus.LIMITED,
            sufficiency=EpistemicSufficiencyStatus.INSUFFICIENT,
            snapshot="world-1",
        ),
        _observation(
            "strategy-b",
            quality=GovernedReasoningQualityStatus.LIMITED,
            sufficiency=EpistemicSufficiencyStatus.INSUFFICIENT,
            snapshot="world-2",
        ),
    )
    result = GovernedStrategyMetacognitiveAdaptationV1().advise(
        observations,
        evaluation_scope="scope-a",
        candidate_strategy_fingerprints=("strategy-a", "strategy-b"),
    )
    assert result.status is StrategyMetacognitiveAdaptationStatus.ADAPTATION_SUGGESTED
    assert result.recommended_strategy_fingerprint == "strategy-a"
    assert result.application_authorized is False
    assert result.modifies_planner is False
    assert result.persists_preference is False
    assert result.creates_learning is False
    assert result.executes_actions is False


def test_one_observation_is_insufficient_for_adaptation():
    result = GovernedStrategyMetacognitiveAdaptationV1().advise(
        (
            _observation(
                "strategy-a",
                quality=GovernedReasoningQualityStatus.ADEQUATE,
                sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            ),
        ),
        evaluation_scope="scope-a",
        candidate_strategy_fingerprints=("strategy-a", "strategy-b"),
    )
    assert result.status is StrategyMetacognitiveAdaptationStatus.INSUFFICIENT_EVIDENCE
    assert result.recommended_strategy_fingerprint is None


def test_ambiguous_support_does_not_choose_a_strategy():
    observations = tuple(
        _observation(
            strategy,
            quality=GovernedReasoningQualityStatus.ADEQUATE,
            sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            snapshot=f"world-{index}",
        )
        for strategy in ("strategy-a", "strategy-b")
        for index in (1, 2)
    )
    result = GovernedStrategyMetacognitiveAdaptationV1().advise(
        observations,
        evaluation_scope="scope-a",
        candidate_strategy_fingerprints=("strategy-a", "strategy-b"),
    )
    assert result.status is StrategyMetacognitiveAdaptationStatus.AMBIGUOUS
    assert result.recommended_strategy_fingerprint is None


def test_review_required_history_blocks_adaptation():
    observations = (
        _observation(
            "strategy-a",
            quality=GovernedReasoningQualityStatus.ADEQUATE,
            sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            snapshot="world-1",
        ),
        _observation(
            "strategy-a",
            quality=GovernedReasoningQualityStatus.REVIEW_REQUIRED,
            sufficiency=EpistemicSufficiencyStatus.INDETERMINATE,
            snapshot="world-2",
        ),
    )
    result = GovernedStrategyMetacognitiveAdaptationV1().advise(
        observations,
        evaluation_scope="scope-a",
        candidate_strategy_fingerprints=("strategy-a",),
    )
    assert result.status is StrategyMetacognitiveAdaptationStatus.REVIEW_REQUIRED
    assert result.recommended_strategy_fingerprint is None


def test_scope_isolation_prevents_cross_context_preference():
    observations = (
        _observation(
            "strategy-a",
            quality=GovernedReasoningQualityStatus.ADEQUATE,
            sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            scope="scope-b",
            snapshot="world-1",
        ),
        _observation(
            "strategy-a",
            quality=GovernedReasoningQualityStatus.ADEQUATE,
            sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            scope="scope-b",
            snapshot="world-2",
        ),
    )
    result = GovernedStrategyMetacognitiveAdaptationV1().advise(
        observations,
        evaluation_scope="scope-a",
        candidate_strategy_fingerprints=("strategy-a",),
    )
    assert result.status is StrategyMetacognitiveAdaptationStatus.INSUFFICIENT_EVIDENCE


def test_adaptation_is_deterministic_and_read_only():
    observations = (
        _observation(
            "strategy-a",
            quality=GovernedReasoningQualityStatus.ADEQUATE,
            sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            snapshot="world-1",
        ),
        _observation(
            "strategy-a",
            quality=GovernedReasoningQualityStatus.ADEQUATE,
            sufficiency=EpistemicSufficiencyStatus.SUFFICIENT,
            snapshot="world-2",
        ),
    )
    engine = GovernedStrategyMetacognitiveAdaptationV1()
    first = engine.advise(
        observations,
        evaluation_scope="scope-a",
        candidate_strategy_fingerprints=("strategy-a",),
    )
    second = engine.advise(
        tuple(reversed(observations)),
        evaluation_scope="scope-a",
        candidate_strategy_fingerprints=("strategy-a",),
    )
    assert first.source_fingerprint == second.source_fingerprint
    assert first.read_only is True
    assert first.recommends_strategy is True
    assert first.establishes_strategy_superiority is False
    assert first.grants_authority is False
