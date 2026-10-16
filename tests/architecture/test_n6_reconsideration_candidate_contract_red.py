from __future__ import annotations

from dataclasses import fields

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.hypothesis_epistemic_delta import (
    GovernedHypothesisDeltaTrigger,
    GovernedHypothesisEpistemicDeltaFoundationV1,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsFoundationV1,
    GovernedReconsiderationCandidateProjector,
    GovernedReconsiderationCandidateStatus,
    HypothesisUpdateSemantic,
)


def _assessment(
    relation: HypothesisEvidenceRelation,
    evidence: tuple[str, ...] = ("fact-a",),
) -> HypothesisEvidenceAssessment:
    return HypothesisEvidenceAssessment(
        hypothesis_id="h1",
        proposition="prior conclusion h1",
        relation=relation,
        evidence_references=evidence,
        rationale_codes=("assessment:h1",),
        epistemic_level=EpistemicLevel.HYPOTHESIS,
    )


def _report(
    suffix: str,
    relation: HypothesisEvidenceRelation,
    *,
    snapshot: str,
    evidence: tuple[str, ...] = ("fact-a",),
) -> GovernedHypothesisDeepeningReport:
    return GovernedHypothesisDeepeningReport(
        report_id=f"hypothesis-deepening-{suffix:0<16}"[:37],
        status=HypothesisDeepeningStatus.COMPLETE,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-n6",
        world_snapshot_id=snapshot,
        assessments=(_assessment(relation, evidence),),
        epistemic_gaps=(),
        evidence_codes=(f"world_snapshot:{snapshot}",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint=f"fingerprint-{suffix}",
    )


def _semantic_report(
    before_relation: HypothesisEvidenceRelation,
    after_relation: HypothesisEvidenceRelation,
    *,
    evidence: tuple[str, ...] = ("fact-a", "evidence-n6"),
):
    before = _report("before", before_relation, snapshot="world-before")
    after = _report(
        "after",
        after_relation,
        snapshot="world-after",
        evidence=evidence,
    )
    trigger = GovernedHypothesisDeltaTrigger(
        trigger_id="hypothesis-delta-trigger-n6-1234567890",
        evidence_references=("evidence-n6",),
        source_reference="scenario-n6",
        world_snapshot_id="world-after",
        rationale_codes=("trigger:n6_new_governed_evidence",),
    )
    delta = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before,
        trigger,
        after,
    )
    return GovernedHypothesisUpdateSemanticsFoundationV1().classify(delta)


def _project(semantic_report):
    return GovernedReconsiderationCandidateProjector().project(semantic_report)


def test_n6_weakened_prior_assessment_proposes_reconsideration() -> None:
    semantic = _semantic_report(
        HypothesisEvidenceRelation.COMPATIBLE,
        HypothesisEvidenceRelation.CONTRADICTED,
    )

    result = _project(semantic)

    assert semantic.updates[0].semantic is HypothesisUpdateSemantic.WEAKENED
    assert result.status is GovernedReconsiderationCandidateStatus.REVIEW_REQUIRED
    assert result.affected_hypothesis_ids == ("h1",)


def test_n6_preserves_prior_and_triggering_evidence_lineage() -> None:
    semantic = _semantic_report(
        HypothesisEvidenceRelation.UNRESOLVED,
        HypothesisEvidenceRelation.CONTRADICTED,
    )

    result = _project(semantic)

    assert result.source_semantics_report_id == semantic.report_id
    assert result.source_delta_report_id == semantic.source_delta_report_id
    assert result.source_reference == semantic.source_reference
    assert result.before_world_snapshot_id == semantic.before_world_snapshot_id
    assert result.after_world_snapshot_id == semantic.after_world_snapshot_id
    assert result.triggering_evidence_references == ("evidence-n6",)


def test_n6_does_not_reconsider_unchanged_prior_assessment() -> None:
    semantic = _semantic_report(
        HypothesisEvidenceRelation.COMPATIBLE,
        HypothesisEvidenceRelation.COMPATIBLE,
        evidence=("fact-a",),
    )

    result = _project(semantic)

    assert result.status is GovernedReconsiderationCandidateStatus.NOT_REQUIRED
    assert result.affected_hypothesis_ids == ()


def test_n6_evidence_change_alone_does_not_force_reconsideration() -> None:
    semantic = _semantic_report(
        HypothesisEvidenceRelation.COMPATIBLE,
        HypothesisEvidenceRelation.COMPATIBLE,
    )

    result = _project(semantic)

    assert semantic.updates[0].semantic is HypothesisUpdateSemantic.INDETERMINATE
    assert result.status is GovernedReconsiderationCandidateStatus.NOT_REQUIRED
    assert result.affected_hypothesis_ids == ()


def test_n6_structural_review_requirement_proposes_reconsideration() -> None:
    before = _report(
        "before",
        HypothesisEvidenceRelation.COMPATIBLE,
        snapshot="world-before",
    )
    after = GovernedHypothesisDeepeningReport(
        report_id="hypothesis-deepening-after00000000000",
        status=HypothesisDeepeningStatus.COMPLETE,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-n6",
        world_snapshot_id="world-after",
        assessments=(),
        epistemic_gaps=(),
        evidence_codes=("world_snapshot:world-after",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint="fingerprint-after",
    )
    trigger = GovernedHypothesisDeltaTrigger(
        trigger_id="hypothesis-delta-trigger-n6-structural-1234",
        evidence_references=("evidence-n6",),
        source_reference="scenario-n6",
        world_snapshot_id="world-after",
        rationale_codes=("trigger:n6_new_governed_evidence",),
    )
    delta = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before,
        trigger,
        after,
    )
    semantic = GovernedHypothesisUpdateSemanticsFoundationV1().classify(delta)

    result = _project(semantic)

    assert semantic.updates[0].semantic is HypothesisUpdateSemantic.REVIEW_REQUIRED
    assert result.status is GovernedReconsiderationCandidateStatus.REVIEW_REQUIRED
    assert result.affected_hypothesis_ids == ("h1",)


def test_n6_candidate_remains_read_only_and_non_operational() -> None:
    result = _project(
        _semantic_report(
            HypothesisEvidenceRelation.COMPATIBLE,
            HypothesisEvidenceRelation.CONTRADICTED,
        )
    )

    names = {item.name for item in fields(result)}
    forbidden = {
        "writes_memory",
        "modifies_knowledge",
        "modifies_hypotheses",
        "modifies_world_model",
        "invokes_planning",
        "grants_authority",
        "executes_actions",
        "persists_results",
    }

    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only
    assert result.consultative
    assert not forbidden.intersection(names)
