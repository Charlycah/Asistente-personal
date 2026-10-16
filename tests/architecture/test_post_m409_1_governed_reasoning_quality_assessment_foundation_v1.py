from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessmentFoundationV1,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEpistemicGap,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.hypothesis_epistemic_delta import (
    GovernedHypothesisDeltaTrigger,
    GovernedHypothesisEpistemicDeltaFoundationV1,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsFoundationV1,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    GovernedMultiHypothesisDiscriminator,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
    GovernedReasoningQualityAssessmentFoundationV1,
    GovernedReasoningQualityStatus,
)

QUALITY = GovernedReasoningQualityAssessmentFoundationV1()
SUFFICIENCY = GovernedEpistemicSufficiencyAssessmentFoundationV1()


def _assessment(
    hypothesis_id: str,
    relation: HypothesisEvidenceRelation,
    evidence: tuple[str, ...] = ("fact-a",),
) -> HypothesisEvidenceAssessment:
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=f"proposition {hypothesis_id}",
        relation=relation,
        evidence_references=evidence,
        rationale_codes=(f"assessment:{hypothesis_id}",),
    )


def _gap(hypothesis_id: str, *, snapshot: str = "world-2") -> HypothesisEpistemicGap:
    return HypothesisEpistemicGap(
        gap_id=f"hypothesis-gap-{hypothesis_id:0<16}"[:31],
        hypothesis_id=hypothesis_id,
        subject=f"proposition {hypothesis_id}",
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-123",
        known_elements=("fact-a",),
        unknown_element=f"evidence needed for {hypothesis_id}",
        evidence_codes=(f"world_snapshot:{snapshot}",),
        hypothesis=f"proposition {hypothesis_id}",
        epistemic_level=EpistemicLevel.UNKNOWN,
    )


def _report(
    assessments: tuple[HypothesisEvidenceAssessment, ...],
    *,
    snapshot: str = "world-2",
    gaps: tuple[HypothesisEpistemicGap, ...] = (),
    status: HypothesisDeepeningStatus = HypothesisDeepeningStatus.COMPLETE,
    suffix: str = "after",
) -> GovernedHypothesisDeepeningReport:
    return GovernedHypothesisDeepeningReport(
        report_id=f"hypothesis-deepening-{suffix:0<16}"[:37],
        status=status,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-123",
        world_snapshot_id=snapshot,
        assessments=assessments,
        epistemic_gaps=gaps,
        evidence_codes=(f"world_snapshot:{snapshot}",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint=f"fingerprint-{suffix}",
    )


def _semantics(
    before_relation: HypothesisEvidenceRelation,
    after_relation: HypothesisEvidenceRelation,
):
    before = _report(
        (_assessment("h1", before_relation),),
        snapshot="world-1",
        suffix="before",
    )
    after = _report(
        (_assessment("h1", after_relation),),
        snapshot="world-2",
        suffix="after",
    )
    trigger = GovernedHypothesisDeltaTrigger(
        trigger_id="hypothesis-delta-trigger-evidence-1234567890",
        evidence_references=("evidence-e1",),
        source_reference="scenario-123",
        world_snapshot_id="world-2",
        rationale_codes=("trigger:level2_acquired_evidence",),
    )
    delta = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before,
        trigger,
        after,
    )
    return GovernedHypothesisUpdateSemanticsFoundationV1().classify(delta)


def test_sufficient_coherent_episode_is_adequate() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))
    sufficiency = SUFFICIENCY.assess(deepening)

    result = QUALITY.assess(deepening, sufficiency)

    assert sufficiency.status is EpistemicSufficiencyStatus.SUFFICIENT
    assert result.status is GovernedReasoningQualityStatus.ADEQUATE
    assert "reasoning_quality:adequate_not_truth_or_correctness" in (
        result.rationale_codes
    )
    assert result.source_hypothesis_deepening_report_id == deepening.report_id
    assert result.source_epistemic_sufficiency_assessment_id == (
        sufficiency.assessment_id
    )


def test_insufficient_episode_is_limited_not_failed() -> None:
    deepening = _report(
        (_assessment("h1", HypothesisEvidenceRelation.UNRESOLVED),),
        gaps=(_gap("h1"),),
        status=HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT,
    )
    sufficiency = SUFFICIENCY.assess(deepening)

    result = QUALITY.assess(deepening, sufficiency)

    assert sufficiency.status is EpistemicSufficiencyStatus.INSUFFICIENT
    assert result.status is GovernedReasoningQualityStatus.LIMITED
    assert "reasoning_quality:insufficiency_is_not_reasoning_failure" in (
        result.rationale_codes
    )


def test_indeterminate_sufficiency_requires_review() -> None:
    deepening = _report(
        (_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),),
        status=HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED,
    )
    sufficiency = SUFFICIENCY.assess(deepening)

    result = QUALITY.assess(deepening, sufficiency)

    assert sufficiency.status is EpistemicSufficiencyStatus.INDETERMINATE
    assert result.status is GovernedReasoningQualityStatus.REVIEW_REQUIRED


def test_optional_update_semantics_preserves_exact_lineage() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))
    semantics = _semantics(
        HypothesisEvidenceRelation.COMPATIBLE,
        HypothesisEvidenceRelation.COMPATIBLE,
    )
    sufficiency = SUFFICIENCY.assess(deepening, update_semantics=semantics)

    result = QUALITY.assess(
        deepening,
        sufficiency,
        update_semantics=semantics,
    )

    assert result.status is GovernedReasoningQualityStatus.ADEQUATE
    assert result.source_hypothesis_update_semantics_report_id == semantics.report_id


def test_optional_discrimination_preserves_exact_lineage() -> None:
    deepening = _report(
        (
            _assessment("h1", HypothesisEvidenceRelation.COMPATIBLE, ("fact-a",)),
            _assessment("h2", HypothesisEvidenceRelation.CONTRADICTED, ("fact-a",)),
        )
    )
    discrimination = GovernedMultiHypothesisDiscriminator().compare(deepening)
    sufficiency = SUFFICIENCY.assess(
        deepening,
        discrimination=discrimination,
    )

    result = QUALITY.assess(
        deepening,
        sufficiency,
        discrimination=discrimination,
    )

    assert result.status is GovernedReasoningQualityStatus.ADEQUATE
    assert result.source_multi_hypothesis_discrimination_report_id == (
        discrimination.report_id
    )


def test_deepening_lineage_mismatch_fails_closed() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))
    other = _report(
        (_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),),
        snapshot="world-other",
        suffix="other",
    )
    sufficiency = SUFFICIENCY.assess(other)

    with pytest.raises(ValueError, match="deepening lineage mismatch"):
        QUALITY.assess(deepening, sufficiency)


def test_unexpected_update_semantics_fails_closed() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))
    sufficiency = SUFFICIENCY.assess(deepening)
    semantics = _semantics(
        HypothesisEvidenceRelation.COMPATIBLE,
        HypothesisEvidenceRelation.COMPATIBLE,
    )

    with pytest.raises(ValueError, match="unexpected update semantics lineage"):
        QUALITY.assess(deepening, sufficiency, update_semantics=semantics)


def test_unexpected_discrimination_fails_closed() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))
    sufficiency = SUFFICIENCY.assess(deepening)
    comparison_source = _report(
        (
            _assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),
            _assessment("h2", HypothesisEvidenceRelation.CONTRADICTED),
        )
    )
    discrimination = GovernedMultiHypothesisDiscriminator().compare(comparison_source)

    with pytest.raises(ValueError, match="unexpected discrimination lineage"):
        QUALITY.assess(deepening, sufficiency, discrimination=discrimination)


def test_same_input_is_deterministic() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))
    sufficiency = SUFFICIENCY.assess(deepening)

    first = QUALITY.assess(deepening, sufficiency)
    second = QUALITY.assess(deepening, sufficiency)

    assert first == second
    assert first.source_fingerprint == second.source_fingerprint


def test_assessment_is_frozen() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))
    sufficiency = SUFFICIENCY.assess(deepening)
    result = QUALITY.assess(deepening, sufficiency)

    with pytest.raises(FrozenInstanceError):
        result.status = GovernedReasoningQualityStatus.LIMITED


def test_foundation_is_read_only_derived_and_non_authoritative() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedReasoningQualityAssessment)
    }
    for field_name in (
        "establishes_truth",
        "establishes_falsity",
        "assigns_probability",
        "closes_reasoning",
        "authorizes_stopping",
        "invokes_reasoning",
        "invokes_comparison",
        "invokes_curiosity",
        "invokes_planning",
        "invokes_capabilities",
        "persists_results",
        "creates_memory",
        "creates_learning_candidate",
        "modifies_world_model",
        "modifies_hypotheses",
        "corrects_reasoning",
        "reruns_reasoning",
        "changes_conclusion",
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[field_name] is False
    assert defaults["canonical_authority"] == "governed_reasoning"
    assert defaults["read_only"] is True
    assert defaults["consultative"] is True
    assert defaults["derivational"] is True
    assert defaults["contextual"] is True
