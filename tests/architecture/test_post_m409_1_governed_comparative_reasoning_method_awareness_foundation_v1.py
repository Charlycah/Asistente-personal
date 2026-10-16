from __future__ import annotations

from dataclasses import fields

import pytest

from core.governed_reasoning.comparative_reasoning_method_awareness import (
    GovernedComparativeReasoningMethodAwareness,
    GovernedComparativeReasoningMethodAwarenessFoundationV1,
    GovernedComparativeReasoningMethodAwarenessStatus,
)
from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeAssociation,
    GovernedReasoningMethodOutcomeAssociationStatus,
)

FOUNDATION = GovernedComparativeReasoningMethodAwarenessFoundationV1()


def _association(
    suffix: str,
    status: GovernedReasoningMethodOutcomeAssociationStatus,
    *,
    source_reference: str = "scenario-123",
    method_fingerprint: str | None = None,
    observation_count: int = 2,
) -> GovernedReasoningMethodOutcomeAssociation:
    method = method_fingerprint or f"method-{suffix}"
    adequate = observation_count if status is (
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE
    ) else 0
    limited = observation_count if status is (
        GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION
    ) else 0
    review = observation_count if status is (
        GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_REVIEW_REQUIRED
    ) else 0
    sufficient = adequate
    insufficient = limited
    indeterminate = review
    if status is GovernedReasoningMethodOutcomeAssociationStatus.MIXED:
        adequate = 1
        sufficient = 1
        limited = max(0, observation_count - 1)
        insufficient = limited
    observation_ids = tuple(
        f"reasoning-method-outcome-observation-{suffix}-{index}"
        for index in range(observation_count)
    )
    return GovernedReasoningMethodOutcomeAssociation(
        association_id=f"reasoning-method-outcome-association-{suffix}",
        status=status,
        method_fingerprint=method,
        source_reference=source_reference,
        observation_ids=observation_ids,
        method_provenance_ids=tuple(
            f"reasoning-method-provenance-{suffix}-{index}"
            for index in range(observation_count)
        ),
        quality_assessment_ids=tuple(
            f"reasoning-quality-{suffix}-{index}"
            for index in range(observation_count)
        ),
        sufficiency_assessment_ids=tuple(
            f"epistemic-sufficiency-{suffix}-{index}"
            for index in range(observation_count)
        ),
        world_snapshot_ids=tuple(
            f"world-{suffix}-{index}" for index in range(observation_count)
        ),
        observation_count=observation_count,
        adequate_count=adequate,
        limited_count=limited,
        review_required_count=review,
        sufficient_count=sufficient,
        insufficient_count=insufficient,
        indeterminate_count=indeterminate,
        rationale_codes=(f"method_outcome:{status.value}",),
        source_fingerprint=f"source-fingerprint-{suffix}",
    )


def test_distinct_methods_with_same_pattern_are_described_only() -> None:
    result = FOUNDATION.assess(
        (
            _association(
                "a",
                GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
            ),
            _association(
                "b",
                GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
            ),
        )
    )

    assert result.status is (
        GovernedComparativeReasoningMethodAwarenessStatus.SAME_PATTERN
    )
    assert result.compares_methods is True
    assert result.establishes_method_superiority is False
    assert (
        "comparative_method:sameness_is_not_equivalence_claim"
        in result.rationale_codes
    )


def test_distinct_patterns_are_not_superiority_or_causality_claims() -> None:
    result = FOUNDATION.assess(
        (
            _association(
                "a",
                GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
            ),
            _association(
                "b",
                GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
            ),
        )
    )

    assert result.status is (
        GovernedComparativeReasoningMethodAwarenessStatus.DIFFERENT_PATTERN
    )
    assert result.establishes_causality is False
    assert result.evaluates_effectiveness is False
    assert result.ranks_methods is False
    assert (
        "comparative_method:difference_is_not_superiority_claim"
        in result.rationale_codes
    )


def test_insufficient_association_blocks_difference_inference() -> None:
    result = FOUNDATION.assess(
        (
            _association(
                "a",
                GovernedReasoningMethodOutcomeAssociationStatus.INSUFFICIENT_EVIDENCE,
                observation_count=1,
            ),
            _association(
                "b",
                GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
            ),
        )
    )

    assert result.status is (
        GovernedComparativeReasoningMethodAwarenessStatus
        .INSUFFICIENT_COMPARATIVE_EVIDENCE
    )
    assert "comparative_method:no_difference_inference" in result.rationale_codes


def test_same_method_is_rejected_as_not_cross_method_comparison() -> None:
    associations = (
        _association(
            "a",
            GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
            method_fingerprint="method-shared",
        ),
        _association(
            "b",
            GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
            method_fingerprint="method-shared",
        ),
    )

    with pytest.raises(ValueError, match="distinct methods"):
        FOUNDATION.assess(associations)


def test_cross_source_comparison_fails_closed() -> None:
    associations = (
        _association(
            "a",
            GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
            source_reference="scenario-a",
        ),
        _association(
            "b",
            GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
            source_reference="scenario-b",
        ),
    )

    with pytest.raises(ValueError, match="shared source reference"):
        FOUNDATION.assess(associations)


def test_different_snapshot_series_remain_admissible_and_preserved() -> None:
    first = _association(
        "a",
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
    )
    second = _association(
        "b",
        GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
        observation_count=3,
    )

    result = FOUNDATION.assess((first, second))

    assert result.observation_counts == (
        first.observation_count,
        second.observation_count,
    )
    assert result.world_snapshot_ids == (
        first.world_snapshot_ids,
        second.world_snapshot_ids,
    )


def test_comparison_identity_is_input_order_independent() -> None:
    first = _association(
        "a",
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
    )
    second = _association(
        "b",
        GovernedReasoningMethodOutcomeAssociationStatus.MIXED,
    )

    forward = FOUNDATION.assess((first, second))
    reverse = FOUNDATION.assess((second, first))

    assert forward == reverse


def test_foundation_requires_exactly_two_associations() -> None:
    association = _association(
        "a",
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
    )

    with pytest.raises(ValueError, match="exactly two associations"):
        FOUNDATION.assess((association,))  # type: ignore[arg-type]


def test_input_associations_preserve_governed_reasoning_authority() -> None:
    first = _association(
        "a",
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
    )
    second = _association(
        "b",
        GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
    )

    assert first.canonical_authority == "governed_reasoning"
    assert second.canonical_authority == "governed_reasoning"

    awareness = FOUNDATION.assess((first, second))

    assert awareness.canonical_authority == "governed_reasoning"


def test_awareness_contract_is_read_only_and_non_authoritative() -> None:
    names = {
        field.name
        for field in fields(GovernedComparativeReasoningMethodAwareness)
    }
    forbidden_true = {
        "establishes_truth",
        "establishes_falsity",
        "establishes_causality",
        "assigns_probability",
        "evaluates_effectiveness",
        "establishes_method_superiority",
        "ranks_methods",
        "selects_method",
        "recommends_method",
        "modifies_reasoning",
        "reruns_reasoning",
        "changes_reasoning_method",
        "invokes_adaptive_reasoning",
        "creates_learning_candidate",
        "persists_results",
        "creates_memory",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    }

    assert forbidden_true <= names
    result = FOUNDATION.assess(
        (
            _association(
                "a",
                GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE,
            ),
            _association(
                "b",
                GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION,
            ),
        )
    )
    assert result.read_only is True
    assert result.derivational is True
    assert result.consultative is True
    assert all(getattr(result, name) is False for name in forbidden_true)
