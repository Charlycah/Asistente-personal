from __future__ import annotations

from dataclasses import fields, replace

import pytest

from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
)
from core.governed_reasoning.hypothesis_epistemic_delta import (
    GovernedHypothesisEpistemicDeltaReport,
    GovernedHypothesisEpistemicDeltaStatus,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsReport,
    GovernedHypothesisUpdateSemanticsStatus,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    GovernedMultiHypothesisDiscriminationReport,
    MultiHypothesisDiscriminationStatus,
)
from core.governed_reasoning.reasoning_method_provenance import (
    GovernedReasoningMethodOperationKind,
    GovernedReasoningMethodProvenance,
    GovernedReasoningMethodProvenanceFoundationV1,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
    GovernedReasoningQualityStatus,
)

FOUNDATION = GovernedReasoningMethodProvenanceFoundationV1()


def _deepening(
    suffix: str = "one",
    *,
    source_kind: HypothesisDeepeningSourceKind = (
        HypothesisDeepeningSourceKind.SCENARIO_SIMULATION
    ),
) -> GovernedHypothesisDeepeningReport:
    return GovernedHypothesisDeepeningReport(
        report_id=f"hypothesis-deepening-{suffix:0<16}"[:37],
        status=HypothesisDeepeningStatus.COMPLETE,
        source_kind=source_kind,
        source_reference="scenario-123",
        world_snapshot_id=f"world-{suffix}",
        assessments=(),
        epistemic_gaps=(),
        evidence_codes=(f"world_snapshot:world-{suffix}",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint=f"deepening-fingerprint-{suffix}",
    )


def _discrimination(
    deepening: GovernedHypothesisDeepeningReport,
) -> GovernedMultiHypothesisDiscriminationReport:
    return GovernedMultiHypothesisDiscriminationReport(
        report_id="multi-hypothesis-discrimination-1234567890abcdef",
        status=MultiHypothesisDiscriminationStatus.COMPLETE,
        source_reference=deepening.source_reference,
        world_snapshot_id=deepening.world_snapshot_id,
        comparisons=(),
        discrimination_requirements=(),
        evidence_codes=("comparison:explicit",),
        risk_codes=("not_truth_promotion",),
        source_fingerprint="discrimination-fingerprint",
    )


def _delta(
    deepening: GovernedHypothesisDeepeningReport,
) -> GovernedHypothesisEpistemicDeltaReport:
    return GovernedHypothesisEpistemicDeltaReport(
        report_id="hypothesis-epistemic-delta-1234567890abcdef",
        status=GovernedHypothesisEpistemicDeltaStatus.COMPLETE,
        before_report_id="hypothesis-deepening-before0000000",
        after_report_id=deepening.report_id,
        trigger_id="hypothesis-delta-trigger-evidence-1234567890",
        source_reference=deepening.source_reference,
        before_world_snapshot_id="world-before",
        after_world_snapshot_id=deepening.world_snapshot_id,
        triggering_evidence_references=("evidence-e1",),
        deltas=(),
        rationale_codes=("delta:explicit",),
        source_fingerprint="delta-fingerprint",
    )


def _update(
    deepening: GovernedHypothesisDeepeningReport,
    delta: GovernedHypothesisEpistemicDeltaReport,
) -> GovernedHypothesisUpdateSemanticsReport:
    return GovernedHypothesisUpdateSemanticsReport(
        report_id="hypothesis-update-semantics-1234567890abcdef",
        status=GovernedHypothesisUpdateSemanticsStatus.COMPLETE,
        source_delta_report_id=delta.report_id,
        source_reference=deepening.source_reference,
        before_world_snapshot_id=delta.before_world_snapshot_id,
        after_world_snapshot_id=deepening.world_snapshot_id,
        triggering_evidence_references=("evidence-e1",),
        updates=(),
        rationale_codes=("update:explicit",),
        source_fingerprint="update-fingerprint",
    )


def _sufficiency(
    deepening: GovernedHypothesisDeepeningReport,
    *,
    discrimination: GovernedMultiHypothesisDiscriminationReport | None = None,
    update: GovernedHypothesisUpdateSemanticsReport | None = None,
) -> GovernedEpistemicSufficiencyAssessment:
    return GovernedEpistemicSufficiencyAssessment(
        assessment_id="epistemic-sufficiency-1234567890abcdef123456",
        status=EpistemicSufficiencyStatus.SUFFICIENT,
        source_hypothesis_deepening_report_id=deepening.report_id,
        source_multi_hypothesis_discrimination_report_id=(
            discrimination.report_id if discrimination else None
        ),
        source_hypothesis_update_semantics_report_id=(
            update.report_id if update else None
        ),
        source_reference=deepening.source_reference,
        world_snapshot_id=deepening.world_snapshot_id,
        hypothesis_ids=(),
        unresolved_hypothesis_ids=(),
        epistemic_gap_ids=(),
        discrimination_requirement_ids=(),
        rationale_codes=("sufficiency:explicit",),
        source_fingerprint="sufficiency-fingerprint",
    )


def _quality(
    deepening: GovernedHypothesisDeepeningReport,
    sufficiency: GovernedEpistemicSufficiencyAssessment,
    *,
    discrimination: GovernedMultiHypothesisDiscriminationReport | None = None,
    update: GovernedHypothesisUpdateSemanticsReport | None = None,
) -> GovernedReasoningQualityAssessment:
    return GovernedReasoningQualityAssessment(
        assessment_id="reasoning-quality-1234567890abcdef123456",
        status=GovernedReasoningQualityStatus.ADEQUATE,
        source_hypothesis_deepening_report_id=deepening.report_id,
        source_epistemic_sufficiency_assessment_id=sufficiency.assessment_id,
        source_hypothesis_update_semantics_report_id=(
            update.report_id if update else None
        ),
        source_multi_hypothesis_discrimination_report_id=(
            discrimination.report_id if discrimination else None
        ),
        source_reference=deepening.source_reference,
        world_snapshot_id=deepening.world_snapshot_id,
        rationale_codes=("quality:explicit",),
        source_fingerprint="quality-fingerprint",
    )


def test_deepening_only_is_a_valid_minimal_method() -> None:
    result = FOUNDATION.derive(_deepening())

    assert result.operation_kinds == (
        GovernedReasoningMethodOperationKind.HYPOTHESIS_DEEPENING,
    )
    assert result.source_kind is HypothesisDeepeningSourceKind.SCENARIO_SIMULATION
    assert result.source_epistemic_sufficiency_assessment_id is None
    assert result.source_reasoning_quality_assessment_id is None


def test_explicit_artifacts_derive_canonical_operation_order() -> None:
    deepening = _deepening()
    discrimination = _discrimination(deepening)
    delta = _delta(deepening)
    update = _update(deepening, delta)

    result = FOUNDATION.derive(
        deepening,
        discrimination=discrimination,
        epistemic_delta=delta,
        update_semantics=update,
    )

    assert result.operation_kinds == (
        GovernedReasoningMethodOperationKind.HYPOTHESIS_DEEPENING,
        GovernedReasoningMethodOperationKind.MULTI_HYPOTHESIS_DISCRIMINATION,
        GovernedReasoningMethodOperationKind.EPISTEMIC_DELTA,
        GovernedReasoningMethodOperationKind.HYPOTHESIS_UPDATE_SEMANTICS,
    )


def test_source_kind_is_not_collapsed_into_operation_kind() -> None:
    result = FOUNDATION.derive(
        _deepening(source_kind=HypothesisDeepeningSourceKind.CAUSAL_PREDICTION)
    )

    assert result.source_kind is HypothesisDeepeningSourceKind.CAUSAL_PREDICTION
    assert tuple(item.value for item in result.operation_kinds) == (
        "hypothesis_deepening",
    )


def test_assessment_lineage_does_not_change_method_fingerprint() -> None:
    deepening = _deepening()
    bare = FOUNDATION.derive(deepening)
    sufficiency = _sufficiency(deepening)
    quality = _quality(deepening, sufficiency)
    assessed = FOUNDATION.derive(
        deepening,
        sufficiency=sufficiency,
        quality=quality,
    )

    assert assessed.method_fingerprint == bare.method_fingerprint
    assert assessed.source_fingerprint != bare.source_fingerprint
    assert (
        assessed.source_epistemic_sufficiency_assessment_id
        == sufficiency.assessment_id
    )
    assert assessed.source_reasoning_quality_assessment_id == quality.assessment_id


def test_same_structure_across_episodes_has_same_method_not_same_provenance() -> None:
    first = FOUNDATION.derive(_deepening("one"))
    second = FOUNDATION.derive(_deepening("two"))

    assert first.method_fingerprint == second.method_fingerprint
    assert first.provenance_id != second.provenance_id
    assert first.source_fingerprint != second.source_fingerprint


def test_method_fingerprint_changes_when_operation_composition_changes() -> None:
    deepening = _deepening()
    bare = FOUNDATION.derive(deepening)
    compared = FOUNDATION.derive(
        deepening,
        discrimination=_discrimination(deepening),
    )

    assert bare.method_fingerprint != compared.method_fingerprint


def test_discrimination_lineage_mismatch_fails_closed() -> None:
    deepening = _deepening()
    discrimination = replace(_discrimination(deepening), source_reference="other")

    with pytest.raises(ValueError, match="discrimination source lineage mismatch"):
        FOUNDATION.derive(deepening, discrimination=discrimination)


def test_delta_must_end_at_the_supplied_deepening() -> None:
    deepening = _deepening()
    delta = replace(_delta(deepening), after_report_id="different-deepening")

    with pytest.raises(ValueError, match="delta after-report lineage mismatch"):
        FOUNDATION.derive(deepening, epistemic_delta=delta)


def test_update_must_reference_supplied_delta_when_both_are_present() -> None:
    deepening = _deepening()
    delta = _delta(deepening)
    update = replace(_update(deepening, delta), source_delta_report_id="other-delta")

    with pytest.raises(ValueError, match="update delta lineage mismatch"):
        FOUNDATION.derive(
            deepening,
            epistemic_delta=delta,
            update_semantics=update,
        )


def test_quality_requires_explicit_matching_sufficiency_lineage() -> None:
    deepening = _deepening()
    sufficiency = _sufficiency(deepening)
    quality = _quality(deepening, sufficiency)

    with pytest.raises(
        ValueError, match="quality lineage requires supplied sufficiency"
    ):
        FOUNDATION.derive(deepening, quality=quality)


def test_sufficiency_cannot_claim_unsupplied_method_operations() -> None:
    deepening = _deepening()
    discrimination = _discrimination(deepening)
    sufficiency = _sufficiency(deepening, discrimination=discrimination)

    with pytest.raises(ValueError, match="sufficiency discrimination lineage mismatch"):
        FOUNDATION.derive(deepening, sufficiency=sufficiency)


def test_output_is_read_only_observational_and_non_adaptive() -> None:
    defaults = {
        field.name: field.default for field in fields(GovernedReasoningMethodProvenance)
    }
    assert defaults["canonical_authority"] == "governed_reasoning"
    assert defaults["read_only"] is True
    assert defaults["derivational"] is True
    assert defaults["consultative"] is True
    for name in (
        "evaluates_effectiveness",
        "ranks_methods",
        "selects_method",
        "recommends_method",
        "establishes_causality",
        "establishes_truth",
        "assigns_probability",
        "modifies_reasoning",
        "reruns_reasoning",
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
