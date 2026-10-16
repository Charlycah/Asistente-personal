from __future__ import annotations

from dataclasses import fields

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEpistemicGap,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    GovernedMultiHypothesisDiscriminationReport,
    GovernedMultiHypothesisDiscriminator,
    HypothesisPairRelation,
    MultiHypothesisDiscriminationStatus,
)


def _assessment(
    hypothesis_id: str,
    relation: HypothesisEvidenceRelation,
    evidence: tuple[str, ...],
) -> HypothesisEvidenceAssessment:
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=f"proposition {hypothesis_id}",
        relation=relation,
        evidence_references=evidence,
        rationale_codes=(f"reason:{hypothesis_id}",),
    )


def _gap(hypothesis_id: str) -> HypothesisEpistemicGap:
    return HypothesisEpistemicGap(
        gap_id=f"hypothesis-gap-{hypothesis_id:0<16}"[:31],
        hypothesis_id=hypothesis_id,
        subject=f"proposition {hypothesis_id}",
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-123",
        known_elements=("fact-shared",),
        unknown_element=f"evidence needed to discriminate {hypothesis_id}",
        evidence_codes=("source:scenario-123",),
        hypothesis=f"proposition {hypothesis_id}",
        epistemic_level=EpistemicLevel.UNKNOWN,
    )


def _report(
    assessments: tuple[HypothesisEvidenceAssessment, ...],
    *,
    gaps: tuple[HypothesisEpistemicGap, ...] = (),
    status: HypothesisDeepeningStatus = HypothesisDeepeningStatus.COMPLETE,
) -> GovernedHypothesisDeepeningReport:
    return GovernedHypothesisDeepeningReport(
        report_id="hypothesis-deepening-1234567890abcdef",
        status=status,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        assessments=assessments,
        epistemic_gaps=gaps,
        evidence_codes=("world_snapshot:world-1",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint="source-fingerprint",
    )


def test_same_evidence_keeps_hypotheses_indistinguishable() -> None:
    h1 = _assessment(
        "h1",
        HypothesisEvidenceRelation.UNRESOLVED,
        ("fact-shared",),
    )
    h2 = _assessment(
        "h2",
        HypothesisEvidenceRelation.UNRESOLVED,
        ("fact-shared",),
    )
    result = GovernedMultiHypothesisDiscriminator().compare(
        _report((h1, h2), gaps=(_gap("h1"), _gap("h2")))
    )

    assert (
        result.status
        is MultiHypothesisDiscriminationStatus.DISCRIMINATION_REQUIREMENTS_PRESENT
    )
    assert result.comparisons[0].relation is HypothesisPairRelation.INDISTINGUISHABLE
    assert result.comparisons[0].shared_evidence_references == ("fact-shared",)
    assert len(result.discrimination_requirements) == 1
    requirement = result.discrimination_requirements[0]
    assert requirement.hypothesis_ids == ("h1", "h2")
    assert requirement.source_reference == "scenario-123"
    assert requirement.world_snapshot_id == "world-1"
    assert not requirement.creates_acquisition_plan
    assert not requirement.acquires_evidence


def test_differential_evidence_is_visible_without_declaring_winner() -> None:
    h1 = _assessment(
        "h1",
        HypothesisEvidenceRelation.COMPATIBLE,
        ("fact-shared", "fact-left"),
    )
    h2 = _assessment(
        "h2",
        HypothesisEvidenceRelation.COMPATIBLE,
        ("fact-shared",),
    )
    result = GovernedMultiHypothesisDiscriminator().compare(_report((h1, h2)))

    comparison = result.comparisons[0]
    assert result.status is MultiHypothesisDiscriminationStatus.COMPLETE
    assert comparison.relation is HypothesisPairRelation.PARTIALLY_DISCRIMINATED
    assert comparison.left_only_evidence_references == ("fact-left",)
    assert not comparison.establishes_truth
    assert not comparison.establishes_falsity
    assert result.discrimination_requirements == ()


def test_relation_difference_is_comparative_not_truth_promotion() -> None:
    h1 = _assessment("h1", HypothesisEvidenceRelation.COMPATIBLE, ("fact-a",))
    h2 = _assessment("h2", HypothesisEvidenceRelation.CONTRADICTED, ("fact-a",))
    result = GovernedMultiHypothesisDiscriminator().compare(_report((h1, h2)))

    comparison = result.comparisons[0]
    assert comparison.relation is HypothesisPairRelation.PARTIALLY_DISCRIMINATED
    assert "comparison:epistemic_relation_differs" in comparison.rationale_codes
    assert not comparison.establishes_truth
    assert not comparison.establishes_falsity


def test_single_hypothesis_fails_closed() -> None:
    h1 = _assessment("h1", HypothesisEvidenceRelation.UNRESOLVED, ())
    result = GovernedMultiHypothesisDiscriminator().compare(_report((h1,)))

    assert result.status is MultiHypothesisDiscriminationStatus.INSUFFICIENT_HYPOTHESES
    assert result.comparisons == ()
    assert result.discrimination_requirements == ()


def test_source_review_required_does_not_fabricate_discrimination() -> None:
    h1 = _assessment("h1", HypothesisEvidenceRelation.UNRESOLVED, ())
    h2 = _assessment("h2", HypothesisEvidenceRelation.UNRESOLVED, ())
    result = GovernedMultiHypothesisDiscriminator().compare(
        _report(
            (h1, h2),
            status=HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED,
        )
    )

    assert result.status is MultiHypothesisDiscriminationStatus.SOURCE_REVIEW_REQUIRED
    assert result.comparisons == ()
    assert result.discrimination_requirements == ()


def test_multi_hypothesis_foundation_is_read_only_and_advisory() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedMultiHypothesisDiscriminationReport)
    }
    for field_name in (
        "persists_results",
        "creates_facts",
        "creates_questions",
        "creates_acquisition_plans",
        "acquires_evidence",
        "modifies_memory",
        "modifies_planning",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[field_name] is False
    assert defaults["canonical_authority"] == "governed_reasoning"
    assert defaults["read_only"] is True
    assert defaults["consultative"] is True
