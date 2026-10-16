from __future__ import annotations

from app.governed_explanatory_model_productive_consumption import (
    GovernedExplanatoryModelProductiveConsumptionV1,
)
from core.governed_reasoning.explanatory_model_composition import (
    ExplanatoryModelCompositionStatus,
    GovernedExplanatoryModelComposer,
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
    GovernedMultiHypothesisDiscriminator,
)


def _assessment(hypothesis_id: str, evidence: tuple[str, ...]):
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=f"explanation {hypothesis_id}",
        relation=HypothesisEvidenceRelation.UNRESOLVED,
        evidence_references=evidence,
        rationale_codes=(f"reason:{hypothesis_id}",),
    )


def _gap(hypothesis_id: str):
    return HypothesisEpistemicGap(
        gap_id=f"hypothesis-gap-{hypothesis_id}-0001",
        hypothesis_id=hypothesis_id,
        subject=f"explanation {hypothesis_id}",
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-explanatory-1",
        known_elements=("fact-shared",),
        unknown_element=f"evidence for {hypothesis_id}",
        evidence_codes=("evidence:bounded",),
        hypothesis=f"explanation {hypothesis_id}",
    )


def _report(*, single=False, status=HypothesisDeepeningStatus.COMPLETE):
    assessments = (_assessment("h1", ("fact-shared", "fact-h1")),)
    gaps = (_gap("h1"),)
    if not single:
        assessments += (_assessment("h2", ("fact-shared",)),)
        gaps += (_gap("h2"),)
    return GovernedHypothesisDeepeningReport(
        report_id="hypothesis-deepening-explanatory-0001",
        status=status,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-explanatory-1",
        world_snapshot_id="world-explanatory-1",
        assessments=assessments,
        epistemic_gaps=gaps,
        evidence_codes=("world:bounded",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint="explanatory-source-fingerprint",
    )


def test_multiple_hypotheses_compose_one_governed_explanatory_model():
    source = _report()
    discrimination = GovernedMultiHypothesisDiscriminator().compare(source)
    model = GovernedExplanatoryModelComposer().compose(source, discrimination)

    assert model.status is ExplanatoryModelCompositionStatus.MODEL_CANDIDATE
    assert tuple(item.hypothesis_id for item in model.components) == ("h1", "h2")
    assert len(model.relations) == 1
    assert model.source_report_id == source.report_id
    assert model.world_snapshot_id == source.world_snapshot_id


def test_component_local_gaps_and_evidence_are_preserved():
    source = _report()
    model = GovernedExplanatoryModelComposer().compose(
        source,
        GovernedMultiHypothesisDiscriminator().compare(source),
    )
    by_id = {item.hypothesis_id: item for item in model.components}
    assert by_id["h1"].evidence_references == ("fact-h1", "fact-shared")
    assert by_id["h1"].unresolved_gap_ids == ("hypothesis-gap-h1-0001",)
    assert by_id["h2"].unresolved_gap_ids == ("hypothesis-gap-h2-0001",)


def test_single_hypothesis_fails_closed_without_model_components():
    source = _report(single=True)
    model = GovernedExplanatoryModelComposer().compose(
        source,
        GovernedMultiHypothesisDiscriminator().compare(source),
    )
    assert model.status is ExplanatoryModelCompositionStatus.INSUFFICIENT_HYPOTHESES
    assert model.components == ()
    assert model.relations == ()


def test_source_review_required_does_not_become_explanatory_model():
    source = _report(status=HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED)
    model = GovernedExplanatoryModelComposer().compose(
        source,
        GovernedMultiHypothesisDiscriminator().compare(source),
    )
    assert model.status is ExplanatoryModelCompositionStatus.SOURCE_REVIEW_REQUIRED
    assert model.components == ()


def test_productive_consumption_reuses_existing_discrimination_chain():
    result = GovernedExplanatoryModelProductiveConsumptionV1().consume(_report())
    assert result.model.status is ExplanatoryModelCompositionStatus.MODEL_CANDIDATE
    assert result.model.discrimination_report_id == (
        result.discrimination.discrimination_report.report_id
    )
    assert result.model.source_reference == result.discrimination.source_reference


def test_productive_context_is_explicitly_consultative_and_revisable():
    result = GovernedExplanatoryModelProductiveConsumptionV1().consume(_report())
    lines = result.context_lines()
    assert "Modelo explicativo gobernado disponible" in lines[0]
    assert "no establece verdad ni causalidad" in lines[1]
    assert "no autoriza aprendizaje, transferencia o acción" in lines[1]


def test_model_preserves_strict_non_authoritative_boundaries():
    result = GovernedExplanatoryModelProductiveConsumptionV1().consume(_report())
    model = result.model
    assert model.read_only is True
    assert model.consultative is True
    assert model.persists_results is False
    assert model.creates_facts is False
    assert model.establishes_truth is False
    assert model.establishes_causality is False
    assert model.creates_questions is False
    assert model.creates_learning is False
    assert model.modifies_memory is False
    assert model.modifies_world_model is False
    assert model.executes_transfer is False
    assert model.executes_actions is False
    assert model.grants_authority is False
