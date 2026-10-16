from __future__ import annotations

from dataclasses import fields

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
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


def test_single_resolved_hypothesis_can_be_contextually_sufficient() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))

    result = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(deepening)

    assert result.status is EpistemicSufficiencyStatus.SUFFICIENT
    assert result.hypothesis_ids == ("h1",)
    assert result.unresolved_hypothesis_ids == ()
    assert result.epistemic_gap_ids == ()
    assert not result.establishes_truth
    assert not result.closes_reasoning
    assert not result.authorizes_stopping


def test_unresolved_hypothesis_is_insufficient() -> None:
    deepening = _report(
        (_assessment("h1", HypothesisEvidenceRelation.UNRESOLVED),),
        gaps=(_gap("h1"),),
    )

    result = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(deepening)

    assert result.status is EpistemicSufficiencyStatus.INSUFFICIENT
    assert result.unresolved_hypothesis_ids == ("h1",)
    assert result.epistemic_gap_ids


def test_multi_hypothesis_requires_existing_comparison() -> None:
    deepening = _report(
        (
            _assessment("h1", HypothesisEvidenceRelation.COMPATIBLE, ("fact-a",)),
            _assessment("h2", HypothesisEvidenceRelation.CONTRADICTED, ("fact-a",)),
        )
    )

    result = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(deepening)

    assert result.status is EpistemicSufficiencyStatus.INDETERMINATE
    assert result.rationale_codes == ("epistemic_sufficiency:comparison_not_supplied",)


def test_completed_existing_comparison_can_contribute_to_sufficiency() -> None:
    deepening = _report(
        (
            _assessment("h1", HypothesisEvidenceRelation.COMPATIBLE, ("fact-a",)),
            _assessment("h2", HypothesisEvidenceRelation.CONTRADICTED, ("fact-a",)),
        )
    )
    discrimination = GovernedMultiHypothesisDiscriminator().compare(deepening)

    result = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(
        deepening,
        discrimination=discrimination,
    )

    assert result.status is EpistemicSufficiencyStatus.SUFFICIENT
    assert result.source_multi_hypothesis_discrimination_report_id == (
        discrimination.report_id
    )
    assert not result.establishes_truth
    assert not result.establishes_falsity


def test_discrimination_requirement_is_insufficient_not_stop_authorization() -> None:
    deepening = _report(
        (
            _assessment("h1", HypothesisEvidenceRelation.UNRESOLVED, ("fact-a",)),
            _assessment("h2", HypothesisEvidenceRelation.UNRESOLVED, ("fact-a",)),
        ),
        gaps=(_gap("h1"), _gap("h2")),
    )
    discrimination = GovernedMultiHypothesisDiscriminator().compare(deepening)

    result = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(
        deepening,
        discrimination=discrimination,
    )

    assert result.status is EpistemicSufficiencyStatus.INSUFFICIENT
    assert result.discrimination_requirement_ids
    assert not result.authorizes_stopping


def test_source_review_is_indeterminate() -> None:
    deepening = _report(
        (_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),),
        status=HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED,
    )

    result = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(deepening)

    assert result.status is EpistemicSufficiencyStatus.INDETERMINATE


def test_resolved_unchanged_update_semantics_allows_sufficiency() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))
    semantics = _semantics(
        HypothesisEvidenceRelation.COMPATIBLE,
        HypothesisEvidenceRelation.COMPATIBLE,
    )

    result = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(
        deepening,
        update_semantics=semantics,
    )

    assert result.status is EpistemicSufficiencyStatus.SUFFICIENT


def test_unmapped_update_semantics_is_indeterminate() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.UNRESOLVED),))
    semantics = _semantics(
        HypothesisEvidenceRelation.COMPATIBLE,
        HypothesisEvidenceRelation.UNRESOLVED,
    )

    result = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(
        deepening,
        update_semantics=semantics,
    )

    assert result.status is EpistemicSufficiencyStatus.INDETERMINATE


def test_lineage_mismatch_fails_closed() -> None:
    deepening = _report((_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),))
    other = _report(
        (
            _assessment("h1", HypothesisEvidenceRelation.COMPATIBLE),
            _assessment("h2", HypothesisEvidenceRelation.CONTRADICTED),
        ),
        snapshot="world-other",
        suffix="other",
    )
    discrimination = GovernedMultiHypothesisDiscriminator().compare(other)

    try:
        GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(
            deepening,
            discrimination=discrimination,
        )
    except ValueError as error:
        assert "snapshot lineage mismatch" in str(error)
    else:
        raise AssertionError("lineage mismatch must fail closed")


def test_foundation_is_read_only_derived_and_non_authoritative() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedEpistemicSufficiencyAssessment)
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
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[field_name] is False
    assert defaults["canonical_authority"] == "governed_reasoning"
    assert defaults["read_only"] is True
    assert defaults["consultative"] is True
    assert defaults["derivational"] is True
    assert defaults["contextual"] is True
