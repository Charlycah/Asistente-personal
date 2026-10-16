from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace

import pytest

from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)
from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedLongitudinalReasoningAssessmentFoundationV1,
    GovernedLongitudinalReasoningStatus,
    GovernedReasoningAssessmentObservation,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
    GovernedReasoningQualityStatus,
)

FOUNDATION = GovernedLongitudinalReasoningAssessmentFoundationV1()


def _sufficiency(
    suffix: str,
    status: EpistemicSufficiencyStatus,
    *,
    source_reference: str = "scenario-123",
    snapshot: str | None = None,
) -> GovernedEpistemicSufficiencyAssessment:
    snapshot_id = snapshot or f"world-{suffix}"
    return GovernedEpistemicSufficiencyAssessment(
        assessment_id=f"epistemic-sufficiency-{suffix:0<24}"[:47],
        status=status,
        source_hypothesis_deepening_report_id=f"deepening-{suffix}",
        source_multi_hypothesis_discrimination_report_id=None,
        source_hypothesis_update_semantics_report_id=None,
        source_reference=source_reference,
        world_snapshot_id=snapshot_id,
        hypothesis_ids=(f"hypothesis-{suffix}",),
        unresolved_hypothesis_ids=(),
        epistemic_gap_ids=(),
        discrimination_requirement_ids=(),
        rationale_codes=(f"sufficiency:{suffix}",),
        source_fingerprint=f"sufficiency-fingerprint-{suffix}",
    )


def _assessments(
    suffix: str,
    quality_status: GovernedReasoningQualityStatus,
    sufficiency_status: EpistemicSufficiencyStatus,
    *,
    source_reference: str = "scenario-123",
) -> tuple[GovernedReasoningQualityAssessment, GovernedEpistemicSufficiencyAssessment]:
    sufficiency = _sufficiency(
        suffix,
        sufficiency_status,
        source_reference=source_reference,
    )
    quality = GovernedReasoningQualityAssessment(
        assessment_id=f"reasoning-quality-{suffix:0<24}"[:42],
        status=quality_status,
        source_hypothesis_deepening_report_id=f"deepening-{suffix}",
        source_epistemic_sufficiency_assessment_id=sufficiency.assessment_id,
        source_hypothesis_update_semantics_report_id=None,
        source_multi_hypothesis_discrimination_report_id=None,
        source_reference=source_reference,
        world_snapshot_id=sufficiency.world_snapshot_id,
        rationale_codes=(f"quality:{suffix}",),
        source_fingerprint=f"quality-fingerprint-{suffix}",
    )
    return quality, sufficiency


def _observation(
    suffix: str,
    quality_status: GovernedReasoningQualityStatus,
    sufficiency_status: EpistemicSufficiencyStatus,
    *,
    source_reference: str = "scenario-123",
) -> GovernedReasoningAssessmentObservation:
    quality, sufficiency = _assessments(
        suffix,
        quality_status,
        sufficiency_status,
        source_reference=source_reference,
    )
    return GovernedReasoningAssessmentObservation.from_assessments(
        quality,
        sufficiency,
    )


def test_single_episode_is_insufficient_history_without_inventing_pattern() -> None:
    result = FOUNDATION.assess(
        (
            _observation(
                "one",
                GovernedReasoningQualityStatus.ADEQUATE,
                EpistemicSufficiencyStatus.SUFFICIENT,
            ),
        )
    )

    assert result.status is GovernedLongitudinalReasoningStatus.INSUFFICIENT_HISTORY
    assert result.adequate_count == 1
    assert result.sufficient_count == 1
    assert "longitudinal:not_temporal_trend" in result.rationale_codes


def test_two_adequate_episodes_are_consistently_adequate_not_truth_claim() -> None:
    result = FOUNDATION.assess(
        tuple(
            _observation(
                suffix,
                GovernedReasoningQualityStatus.ADEQUATE,
                EpistemicSufficiencyStatus.SUFFICIENT,
            )
            for suffix in ("one", "two")
        )
    )

    assert result.status is GovernedLongitudinalReasoningStatus.CONSISTENTLY_ADEQUATE
    assert result.adequate_count == 2
    assert result.sufficient_count == 2
    assert "longitudinal:not_truth_promotion" in result.rationale_codes
    assert "longitudinal:not_correctness_claim" in result.rationale_codes


def test_repeated_limited_is_recurrent_limitation_not_reasoning_failure() -> None:
    result = FOUNDATION.assess(
        tuple(
            _observation(
                suffix,
                GovernedReasoningQualityStatus.LIMITED,
                EpistemicSufficiencyStatus.INSUFFICIENT,
            )
            for suffix in ("one", "two")
        )
    )

    assert result.status is GovernedLongitudinalReasoningStatus.RECURRENT_LIMITATION
    assert result.limited_count == 2
    assert result.insufficient_count == 2
    assert "longitudinal:limitation_is_not_reasoning_failure" in result.rationale_codes


def test_repeated_review_required_is_observed_without_authorizing_review() -> None:
    result = FOUNDATION.assess(
        tuple(
            _observation(
                suffix,
                GovernedReasoningQualityStatus.REVIEW_REQUIRED,
                EpistemicSufficiencyStatus.INDETERMINATE,
            )
            for suffix in ("one", "two")
        )
    )

    assert result.status is (
        GovernedLongitudinalReasoningStatus.RECURRENT_REVIEW_REQUIRED
    )
    assert result.review_required_count == 2
    assert result.indeterminate_count == 2
    assert result.authorizes_review is False


def test_non_recurrent_mixed_history_remains_mixed() -> None:
    result = FOUNDATION.assess(
        (
            _observation(
                "one",
                GovernedReasoningQualityStatus.ADEQUATE,
                EpistemicSufficiencyStatus.SUFFICIENT,
            ),
            _observation(
                "two",
                GovernedReasoningQualityStatus.LIMITED,
                EpistemicSufficiencyStatus.INSUFFICIENT,
            ),
        )
    )

    assert result.status is GovernedLongitudinalReasoningStatus.MIXED
    assert result.adequate_count == 1
    assert result.limited_count == 1


def test_series_requires_same_explicit_source_reference() -> None:
    observations = (
        _observation(
            "one",
            GovernedReasoningQualityStatus.ADEQUATE,
            EpistemicSufficiencyStatus.SUFFICIENT,
            source_reference="scenario-a",
        ),
        _observation(
            "two",
            GovernedReasoningQualityStatus.ADEQUATE,
            EpistemicSufficiencyStatus.SUFFICIENT,
            source_reference="scenario-b",
        ),
    )

    with pytest.raises(ValueError, match="not comparable"):
        FOUNDATION.assess(observations)


def test_pair_lineage_mismatch_fails_closed() -> None:
    quality, _sufficiency_source = _assessments(
        "one",
        GovernedReasoningQualityStatus.ADEQUATE,
        EpistemicSufficiencyStatus.SUFFICIENT,
    )
    other = _sufficiency("other", EpistemicSufficiencyStatus.SUFFICIENT)

    with pytest.raises(ValueError, match="quality/sufficiency lineage mismatch"):
        GovernedReasoningAssessmentObservation.from_assessments(quality, other)


def test_duplicate_quality_or_sufficiency_ids_fail_closed() -> None:
    first = _observation(
        "one",
        GovernedReasoningQualityStatus.ADEQUATE,
        EpistemicSufficiencyStatus.SUFFICIENT,
    )
    second = _observation(
        "two",
        GovernedReasoningQualityStatus.ADEQUATE,
        EpistemicSufficiencyStatus.SUFFICIENT,
    )
    duplicate_quality = replace(
        second,
        quality_assessment_id=first.quality_assessment_id,
    )
    with pytest.raises(ValueError, match="repeats quality assessments"):
        FOUNDATION.assess((first, duplicate_quality))

    duplicate_sufficiency = replace(
        second,
        sufficiency_assessment_id=first.sufficiency_assessment_id,
    )
    with pytest.raises(ValueError, match="repeats sufficiency assessments"):
        FOUNDATION.assess((first, duplicate_sufficiency))


def test_input_order_does_not_change_identity_or_counts() -> None:
    first = _observation(
        "one",
        GovernedReasoningQualityStatus.ADEQUATE,
        EpistemicSufficiencyStatus.SUFFICIENT,
    )
    second = _observation(
        "two",
        GovernedReasoningQualityStatus.LIMITED,
        EpistemicSufficiencyStatus.INSUFFICIENT,
    )

    forward = FOUNDATION.assess((first, second))
    reverse = FOUNDATION.assess((second, first))

    assert forward == reverse
    assert forward.source_fingerprint == reverse.source_fingerprint


def test_assessment_is_immutable_and_has_no_power_surface() -> None:
    result = FOUNDATION.assess(
        (
            _observation(
                "one",
                GovernedReasoningQualityStatus.ADEQUATE,
                EpistemicSufficiencyStatus.SUFFICIENT,
            ),
        )
    )

    defaults = {field.name: field.default for field in fields(result)}
    assert defaults["canonical_authority"] == "governed_reasoning"
    assert defaults["read_only"] is True
    assert defaults["consultative"] is True
    assert defaults["derivational"] is True
    assert defaults["longitudinal"] is True
    for name in (
        "establishes_truth",
        "establishes_falsity",
        "assigns_probability",
        "changes_reasoning",
        "reruns_reasoning",
        "authorizes_review",
        "authorizes_stopping",
        "invokes_reflection",
        "invokes_learning",
        "persists_results",
        "creates_memory",
        "creates_learning_candidate",
        "modifies_hypotheses",
        "modifies_world_model",
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[name] is False

    with pytest.raises(FrozenInstanceError):
        result.status = GovernedLongitudinalReasoningStatus.MIXED  # type: ignore[misc]


def test_foundation_has_no_temporal_or_persistence_input_contract() -> None:
    annotations = GovernedReasoningAssessmentObservation.__annotations__
    forbidden = ("timestamp", "created_at", "sequence", "memory", "learning")
    assert all(name not in annotations for name in forbidden)
    assert "quality" not in annotations
    assert "sufficiency" not in annotations
