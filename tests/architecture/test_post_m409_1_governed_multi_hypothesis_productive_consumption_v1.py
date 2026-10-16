from __future__ import annotations

import ast
import inspect
from dataclasses import fields

from app.governed_multi_hypothesis_productive_consumption import (
    GovernedMultiHypothesisProductiveConsumption,
    GovernedMultiHypothesisProductiveConsumptionV1,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEpistemicGap,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    MultiHypothesisDiscriminationStatus,
)


def _assessment(
    hypothesis_id: str,
    evidence: tuple[str, ...],
) -> HypothesisEvidenceAssessment:
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=f"proposition {hypothesis_id}",
        relation=HypothesisEvidenceRelation.UNRESOLVED,
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


def test_productive_consumption_preserves_discrimination_requirement() -> None:
    h1 = _assessment("h1", ("fact-shared",))
    h2 = _assessment("h2", ("fact-shared",))
    source = _report((h1, h2), gaps=(_gap("h1"), _gap("h2")))

    result = GovernedMultiHypothesisProductiveConsumptionV1().consume(source)

    assert (
        result.discrimination_report.status
        is MultiHypothesisDiscriminationStatus.DISCRIMINATION_REQUIREMENTS_PRESENT
    )
    assert len(result.discrimination_requirements) == 1
    requirement = result.discrimination_requirements[0]
    assert requirement.source_reference == source.source_reference
    assert requirement.world_snapshot_id == source.world_snapshot_id
    assert not requirement.creates_acquisition_plan
    assert not requirement.acquires_evidence


def test_partial_discrimination_does_not_fabricate_requirement() -> None:
    h1 = _assessment("h1", ("fact-shared", "fact-left"))
    h2 = _assessment("h2", ("fact-shared",))

    result = GovernedMultiHypothesisProductiveConsumptionV1().consume(
        _report((h1, h2))
    )

    assert (
        result.discrimination_report.status
        is MultiHypothesisDiscriminationStatus.COMPLETE
    )
    assert result.discrimination_requirements == ()


def test_single_hypothesis_fails_closed_productively() -> None:
    result = GovernedMultiHypothesisProductiveConsumptionV1().consume(
        _report((_assessment("h1", ()),))
    )

    assert (
        result.discrimination_report.status
        is MultiHypothesisDiscriminationStatus.INSUFFICIENT_HYPOTHESES
    )
    assert result.discrimination_requirements == ()


def test_source_review_required_stays_non_operational() -> None:
    source = _report(
        (_assessment("h1", ()), _assessment("h2", ())),
        status=HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED,
    )

    result = GovernedMultiHypothesisProductiveConsumptionV1().consume(source)

    assert (
        result.discrimination_report.status
        is MultiHypothesisDiscriminationStatus.SOURCE_REVIEW_REQUIRED
    )
    assert result.discrimination_requirements == ()


def test_productive_consumption_preserves_exact_lineage() -> None:
    source = _report(
        (_assessment("h1", ("fact-shared",)), _assessment("h2", ("fact-shared",))),
        gaps=(_gap("h1"), _gap("h2")),
    )

    result = GovernedMultiHypothesisProductiveConsumptionV1().consume(source)

    assert result.source_report_id == source.report_id
    assert result.source_reference == source.source_reference
    assert result.world_snapshot_id == source.world_snapshot_id
    assert (
        result.discrimination_report.source_reference
        == source.source_reference
    )
    assert (
        result.discrimination_report.world_snapshot_id
        == source.world_snapshot_id
    )


def test_productive_consumption_is_read_only_and_has_no_operational_bypass() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedMultiHypothesisProductiveConsumption)
    }
    for field_name in (
        "persists_results",
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

    source = inspect.getsource(GovernedMultiHypothesisProductiveConsumptionV1)
    tree = ast.parse(source)
    assert "OfficialMemoryGateway" not in source
    assert "OfficialConversationGateway" not in source
    assert "Curiosity" not in source
    assert "requests." not in source
    assert "socket." not in source
    assert "subprocess." not in source
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name in {"remember", "persist", "learn", "emit", "acquire"}
        )
        for node in ast.walk(tree)
    )
