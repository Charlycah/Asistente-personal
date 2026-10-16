from core.governed_reasoning.historical_method_advisory import (
    GovernedHistoricalReasoningMethodAdvisoryStatus,
    GovernedHistoricalReasoningMethodAdvisoryV1,
)
from core.governed_reasoning.reasoning_method_effectiveness_awareness import (
    GovernedReasoningMethodEffectivenessAwareness,
    GovernedReasoningMethodEffectivenessAwarenessStatus,
)
from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeAssociationStatus,
)

ADVISORY = GovernedHistoricalReasoningMethodAdvisoryV1()
AwarenessStatus = GovernedReasoningMethodEffectivenessAwarenessStatus
AssociationStatus = GovernedReasoningMethodOutcomeAssociationStatus
AdvisoryStatus = GovernedHistoricalReasoningMethodAdvisoryStatus


def _awareness(
    suffix: str,
    status: GovernedReasoningMethodEffectivenessAwarenessStatus,
    *,
    scope: str = "diagnostic-python",
    observations: int = 3,
) -> GovernedReasoningMethodEffectivenessAwareness:
    association_status = {
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD:
            AssociationStatus.CONSISTENTLY_ADEQUATE,
        AwarenessStatus.LIMITING_OBSERVED_RECORD:
            AssociationStatus.RECURRENT_LIMITATION,
        AwarenessStatus.REVIEW_REQUIRED_OBSERVED_RECORD:
            AssociationStatus.RECURRENT_REVIEW_REQUIRED,
        AwarenessStatus.MIXED_OBSERVED_RECORD:
            AssociationStatus.MIXED,
        AwarenessStatus.INSUFFICIENT_EVALUATIVE_EVIDENCE:
            AssociationStatus.INSUFFICIENT_EVIDENCE,
    }[status]
    return GovernedReasoningMethodEffectivenessAwareness(
        awareness_id=f"reasoning-method-effectiveness-awareness-{suffix}",
        status=status,
        method_fingerprint=f"method-{suffix}",
        evaluation_scope=scope,
        source_association_id=f"reasoning-method-outcome-association-{suffix}",
        source_association_status=association_status,
        observation_count=observations,
        adequate_count=observations if "SUPPORTIVE" in status.name else 0,
        limited_count=observations if "LIMITING" in status.name else 0,
        review_required_count=observations if "REVIEW" in status.name else 0,
        sufficient_count=observations if "SUPPORTIVE" in status.name else 0,
        insufficient_count=observations if "LIMITING" in status.name else 0,
        indeterminate_count=observations if "REVIEW" in status.name else 0,
        world_snapshot_ids=tuple(f"world-{suffix}-{i}" for i in range(observations)),
        rationale_codes=(f"awareness:{status.value}",),
        source_fingerprint=f"source-{suffix}",
    )


def _advise(*items, scope="diagnostic-python"):
    return ADVISORY.advise(
        tuple(items),
        evaluation_scope=scope,
        candidate_method_fingerprints=tuple(item.method_fingerprint for item in items),
    )


def test_unique_supportive_history_yields_bounded_preference() -> None:
    good = _awareness(
        "good",
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD,
    )
    limited = _awareness(
        "limited",
        AwarenessStatus.LIMITING_OBSERVED_RECORD,
    )
    result = _advise(good, limited)
    assert result.status is (
        AdvisoryStatus.METHOD_PREFERENCE_OBSERVED
    )
    assert result.recommended_method_fingerprint == good.method_fingerprint
    assert result.application_authorized is False


def test_single_supported_method_is_advisory_only() -> None:
    good = _awareness(
        "only",
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD,
    )
    result = _advise(good)
    assert result.status is (
        AdvisoryStatus.ONE_METHOD_SUPPORTED
    )
    assert result.selects_method is False
    assert result.modifies_reasoning is False
    assert result.reruns_reasoning is False


def test_incompatible_scope_is_not_generalized() -> None:
    good = _awareness(
        "other-scope",
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD,
        scope="python",
    )
    result = _advise(good, scope="personal-planning")
    assert result.status is (
        AdvisoryStatus.NO_APPLICABLE_HISTORY
    )
    assert result.recommended_method_fingerprint is None


def test_insufficient_history_does_not_recommend() -> None:
    good = _awareness(
        "thin",
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD,
        observations=1,
    )
    result = _advise(good)
    assert result.status is (
        AdvisoryStatus.NO_APPLICABLE_HISTORY
    )


def test_review_required_history_fails_closed() -> None:
    good = _awareness(
        "good-review",
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD,
    )
    review = _awareness(
        "review",
        AwarenessStatus.REVIEW_REQUIRED_OBSERVED_RECORD,
    )
    result = _advise(good, review)
    assert result.status is AdvisoryStatus.REVIEW_REQUIRED
    assert result.recommended_method_fingerprint is None


def test_multiple_supportive_methods_remain_ambiguous() -> None:
    first = _awareness(
        "first",
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD,
    )
    second = _awareness(
        "second",
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD,
    )
    result = _advise(first, second)
    assert result.status is AdvisoryStatus.AMBIGUOUS
    assert result.recommended_method_fingerprint is None


def test_provenance_and_scope_are_preserved() -> None:
    good = _awareness(
        "provenance",
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD,
    )
    result = _advise(good)
    assert result.evaluation_scope == good.evaluation_scope
    assert result.source_awareness_ids == (good.awareness_id,)
    assert result.source_association_ids == (good.source_association_id,)
    assert set(result.world_snapshot_ids) == set(good.world_snapshot_ids)
    assert result.source_fingerprint


def test_advisory_has_no_persistence_learning_execution_or_authority_power() -> None:
    good = _awareness(
        "bounded",
        AwarenessStatus.SUPPORTIVE_OBSERVED_RECORD,
    )
    result = _advise(good)
    assert result.canonical_authority == "governed_reasoning"
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.executes_actions is False
    assert result.grants_authority is False
