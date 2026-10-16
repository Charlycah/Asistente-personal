from __future__ import annotations

from dataclasses import fields, replace

import pytest

from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)
from core.governed_reasoning.hypothesis_deepening import (
    HypothesisDeepeningSourceKind,
)
from core.governed_reasoning.reasoning_method_outcome_association import (
    GovernedReasoningMethodOutcomeAssociation,
    GovernedReasoningMethodOutcomeAssociationFoundationV1,
    GovernedReasoningMethodOutcomeAssociationStatus,
    GovernedReasoningMethodOutcomeObservation,
)
from core.governed_reasoning.reasoning_method_provenance import (
    GovernedReasoningMethodOperationKind,
    GovernedReasoningMethodProvenance,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
    GovernedReasoningQualityStatus,
)

FOUNDATION = GovernedReasoningMethodOutcomeAssociationFoundationV1()


def _artifacts(
    suffix: str,
    quality_status: GovernedReasoningQualityStatus,
    sufficiency_status: EpistemicSufficiencyStatus,
    *,
    source_reference: str = "scenario-123",
    method_fingerprint: str = "method-fingerprint-shared",
):
    deepening_id = f"hypothesis-deepening-{suffix:0<16}"[:37]
    snapshot = f"world-{suffix}"
    sufficiency = GovernedEpistemicSufficiencyAssessment(
        assessment_id=f"epistemic-sufficiency-{suffix:0<24}"[:47],
        status=sufficiency_status,
        source_hypothesis_deepening_report_id=deepening_id,
        source_multi_hypothesis_discrimination_report_id=None,
        source_hypothesis_update_semantics_report_id=None,
        source_reference=source_reference,
        world_snapshot_id=snapshot,
        hypothesis_ids=(f"hypothesis-{suffix}",),
        unresolved_hypothesis_ids=(),
        epistemic_gap_ids=(),
        discrimination_requirement_ids=(),
        rationale_codes=(f"sufficiency:{suffix}",),
        source_fingerprint=f"sufficiency-fingerprint-{suffix}",
    )
    quality = GovernedReasoningQualityAssessment(
        assessment_id=f"reasoning-quality-{suffix:0<24}"[:42],
        status=quality_status,
        source_hypothesis_deepening_report_id=deepening_id,
        source_epistemic_sufficiency_assessment_id=sufficiency.assessment_id,
        source_hypothesis_update_semantics_report_id=None,
        source_multi_hypothesis_discrimination_report_id=None,
        source_reference=source_reference,
        world_snapshot_id=snapshot,
        rationale_codes=(f"quality:{suffix}",),
        source_fingerprint=f"quality-fingerprint-{suffix}",
    )
    provenance = GovernedReasoningMethodProvenance(
        provenance_id=f"reasoning-method-provenance-{suffix:0<24}"[:52],
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference=source_reference,
        world_snapshot_id=snapshot,
        operation_kinds=(GovernedReasoningMethodOperationKind.HYPOTHESIS_DEEPENING,),
        source_hypothesis_deepening_report_id=deepening_id,
        source_multi_hypothesis_discrimination_report_id=None,
        source_hypothesis_epistemic_delta_report_id=None,
        source_hypothesis_update_semantics_report_id=None,
        source_epistemic_sufficiency_assessment_id=sufficiency.assessment_id,
        source_reasoning_quality_assessment_id=quality.assessment_id,
        method_fingerprint=method_fingerprint,
        source_fingerprint=f"method-source-fingerprint-{suffix}",
    )
    return provenance, quality, sufficiency


def _observation(
    suffix: str,
    quality_status: GovernedReasoningQualityStatus,
    sufficiency_status: EpistemicSufficiencyStatus,
    *,
    source_reference: str = "scenario-123",
    method_fingerprint: str = "method-fingerprint-shared",
) -> GovernedReasoningMethodOutcomeObservation:
    return GovernedReasoningMethodOutcomeObservation.from_artifacts(
        *_artifacts(
            suffix,
            quality_status,
            sufficiency_status,
            source_reference=source_reference,
            method_fingerprint=method_fingerprint,
        )
    )


def test_observation_requires_exact_certified_episode_lineage() -> None:
    provenance, quality, sufficiency = _artifacts(
        "one",
        GovernedReasoningQualityStatus.ADEQUATE,
        EpistemicSufficiencyStatus.SUFFICIENT,
    )

    result = GovernedReasoningMethodOutcomeObservation.from_artifacts(
        provenance,
        quality,
        sufficiency,
    )

    assert result.method_provenance_id == provenance.provenance_id
    assert result.quality_assessment_id == quality.assessment_id
    assert result.sufficiency_assessment_id == sufficiency.assessment_id
    assert result.method_fingerprint == provenance.method_fingerprint


def test_quality_sufficiency_mismatch_fails_closed() -> None:
    provenance, quality, sufficiency = _artifacts(
        "one",
        GovernedReasoningQualityStatus.ADEQUATE,
        EpistemicSufficiencyStatus.SUFFICIENT,
    )
    quality = replace(
        quality,
        source_epistemic_sufficiency_assessment_id="epistemic-sufficiency-other",
    )

    with pytest.raises(ValueError, match="quality/sufficiency lineage mismatch"):
        GovernedReasoningMethodOutcomeObservation.from_artifacts(
            provenance,
            quality,
            sufficiency,
        )


def test_provenance_must_explicitly_bind_quality_and_sufficiency() -> None:
    provenance, quality, sufficiency = _artifacts(
        "one",
        GovernedReasoningQualityStatus.ADEQUATE,
        EpistemicSufficiencyStatus.SUFFICIENT,
    )
    provenance = replace(
        provenance,
        source_epistemic_sufficiency_assessment_id=None,
        source_reasoning_quality_assessment_id=None,
    )

    with pytest.raises(ValueError, match="provenance/sufficiency lineage mismatch"):
        GovernedReasoningMethodOutcomeObservation.from_artifacts(
            provenance,
            quality,
            sufficiency,
        )


def test_single_episode_is_insufficient_evidence() -> None:
    result = FOUNDATION.assess(
        (
            _observation(
                "one",
                GovernedReasoningQualityStatus.ADEQUATE,
                EpistemicSufficiencyStatus.SUFFICIENT,
            ),
        )
    )

    assert result.status is (
        GovernedReasoningMethodOutcomeAssociationStatus.INSUFFICIENT_EVIDENCE
    )
    assert result.observation_count == 1


def test_two_adequate_outcomes_are_consistently_adequate() -> None:
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

    assert result.status is (
        GovernedReasoningMethodOutcomeAssociationStatus.CONSISTENTLY_ADEQUATE
    )
    assert result.adequate_count == 2
    assert result.sufficient_count == 2


def test_repeated_limited_outcomes_are_observed_not_method_failure() -> None:
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

    assert result.status is (
        GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_LIMITATION
    )
    assert result.limited_count == 2
    assert result.insufficient_count == 2
    assert "method_outcome:limitation_is_not_method_failure" in result.rationale_codes


def test_repeated_review_required_does_not_authorize_review() -> None:
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
        GovernedReasoningMethodOutcomeAssociationStatus.RECURRENT_REVIEW_REQUIRED
    )
    assert result.review_required_count == 2
    assert result.indeterminate_count == 2
    assert "method_outcome:does_not_authorize_review" in result.rationale_codes


def test_majority_does_not_create_predominance_in_v1() -> None:
    observations = tuple(
        _observation(
            suffix,
            GovernedReasoningQualityStatus.LIMITED,
            EpistemicSufficiencyStatus.INSUFFICIENT,
        )
        for suffix in ("one", "two", "three")
    ) + (
        _observation(
            "four",
            GovernedReasoningQualityStatus.ADEQUATE,
            EpistemicSufficiencyStatus.SUFFICIENT,
        ),
    )

    result = FOUNDATION.assess(observations)

    assert result.status is GovernedReasoningMethodOutcomeAssociationStatus.MIXED
    assert "method_outcome:no_majority_inference" in result.rationale_codes


def test_series_requires_one_explicit_method_fingerprint() -> None:
    observations = (
        _observation(
            "one",
            GovernedReasoningQualityStatus.ADEQUATE,
            EpistemicSufficiencyStatus.SUFFICIENT,
            method_fingerprint="method-a",
        ),
        _observation(
            "two",
            GovernedReasoningQualityStatus.ADEQUATE,
            EpistemicSufficiencyStatus.SUFFICIENT,
            method_fingerprint="method-b",
        ),
    )

    with pytest.raises(ValueError, match="one method"):
        FOUNDATION.assess(observations)


def test_cross_source_association_is_rejected_in_v1() -> None:
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

    with pytest.raises(ValueError, match="not source-comparable"):
        FOUNDATION.assess(observations)


def test_duplicate_episode_identities_fail_closed() -> None:
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
    duplicate = replace(second, method_provenance_id=first.method_provenance_id)

    with pytest.raises(ValueError, match="repeats method provenance ids"):
        FOUNDATION.assess((first, duplicate))


def test_input_order_does_not_change_association_identity_or_counts() -> None:
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
    assert forward.status is GovernedReasoningMethodOutcomeAssociationStatus.MIXED


def test_association_is_read_only_non_causal_non_adaptive_and_non_learning() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedReasoningMethodOutcomeAssociation)
    }
    assert defaults["canonical_authority"] == "governed_reasoning"
    assert defaults["read_only"] is True
    assert defaults["derivational"] is True
    assert defaults["consultative"] is True
    for name in (
        "establishes_truth",
        "establishes_falsity",
        "establishes_causality",
        "assigns_probability",
        "evaluates_effectiveness",
        "compares_methods",
        "ranks_methods",
        "selects_method",
        "recommends_method",
        "modifies_reasoning",
        "reruns_reasoning",
        "changes_reasoning_method",
        "invokes_adaptive_reasoning",
        "invokes_curiosity",
        "invokes_reflection",
        "creates_learning_candidate",
        "persists_results",
        "creates_memory",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[name] is False
