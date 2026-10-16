from dataclasses import fields

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.causal_prediction import (
    CausalAssessment,
    CausalAssessmentKind,
    CausalHypothesis,
    CausalPredictionStatus,
    GovernedCausalPredictionReport,
    PredictiveOutcome,
    PredictiveOutcomeKind,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepener,
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.scenario_simulation import (
    GovernedScenarioSimulationReport,
    ScenarioHypothesis,
    ScenarioOutcome,
    ScenarioOutcomeKind,
    ScenarioSimulationStatus,
)


def test_deepening_reuses_m391_3_without_promoting_hypotheses() -> None:
    source = GovernedScenarioSimulationReport(
        simulation_id="scenario-simulation-1234567890abcdef",
        status=ScenarioSimulationStatus.COMPLETE,
        world_snapshot_id="world-1",
        hypotheses=(
            ScenarioHypothesis(
                hypothesis_id="h-1",
                proposition="The kitchen window is open",
                world_domain="home",
                fact_key="kitchen_window",
                assumed_value="open",
            ),
            ScenarioHypothesis(
                hypothesis_id="h-2",
                proposition="The garage door is open",
                world_domain="home",
                fact_key="garage_door",
                assumed_value="open",
            ),
        ),
        outcomes=(
            ScenarioOutcome(
                hypothesis_id="h-1",
                kind=ScenarioOutcomeKind.CONSISTENT,
                matched_fact_ids=("fact-window",),
                rationale_codes=("scenario:consistent_with_persistent_fact",),
            ),
            ScenarioOutcome(
                hypothesis_id="h-2",
                kind=ScenarioOutcomeKind.UNRESOLVED,
                matched_fact_ids=(),
                rationale_codes=("scenario:no_persistent_fact",),
            ),
        ),
        evidence_codes=("world_snapshot:world-1",),
        risk_codes=("scenario_unresolved",),
        source_fingerprint="scenario-source-fingerprint",
    )

    report = GovernedHypothesisDeepener().deepen_scenarios(source)

    assert report.canonical_authority == "governed_reasoning"
    assert report.source_kind is HypothesisDeepeningSourceKind.SCENARIO_SIMULATION
    assert report.source_reference == source.simulation_id
    assert report.status is HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT
    assert tuple(item.relation for item in report.assessments) == (
        HypothesisEvidenceRelation.COMPATIBLE,
        HypothesisEvidenceRelation.UNRESOLVED,
    )
    assert all(
        item.epistemic_level is EpistemicLevel.HYPOTHESIS for item in report.assessments
    )
    assert len(report.epistemic_gaps) == 1
    gap = report.epistemic_gaps[0]
    assert gap.hypothesis_id == "h-2"
    assert gap.source_reference == source.simulation_id
    assert gap.epistemic_level is EpistemicLevel.UNKNOWN
    assert not gap.creates_question
    assert not gap.creates_learning_candidate
    assert not gap.modifies_memory


def test_deepening_reuses_m391_4_without_proving_causality() -> None:
    source = GovernedCausalPredictionReport(
        analysis_id="causal-prediction-1234567890abcdef",
        status=CausalPredictionStatus.INSUFFICIENT_EVIDENCE,
        world_snapshot_id="world-1",
        hypotheses=(
            CausalHypothesis(
                relation_id="c-1",
                proposition="Opening the window cools the room",
                cause_domain="home",
                cause_key="window",
                cause_value="open",
                effect_domain="home",
                effect_key="temperature",
                effect_value="cooler",
            ),
        ),
        assessments=(
            CausalAssessment(
                relation_id="c-1",
                kind=CausalAssessmentKind.UNRESOLVED,
                cause_fact_ids=("fact-window",),
                effect_fact_ids=(),
                rationale_codes=("causal:insufficient_explicit_evidence",),
            ),
        ),
        predictions=(
            PredictiveOutcome(
                relation_id="c-1",
                kind=PredictiveOutcomeKind.UNRESOLVED,
                predicted_domain="home",
                predicted_key="temperature",
                predicted_value="cooler",
                rationale_codes=("prediction:insufficient_explicit_evidence",),
            ),
        ),
        evidence_codes=("world_snapshot:world-1",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint="causal-source-fingerprint",
    )

    report = GovernedHypothesisDeepener().deepen_causal_predictions(source)

    assert report.canonical_authority == "governed_reasoning"
    assert report.source_kind is HypothesisDeepeningSourceKind.CAUSAL_PREDICTION
    assert report.status is HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT
    assert report.assessments[0].relation is HypothesisEvidenceRelation.UNRESOLVED
    assert not report.assessments[0].establishes_fact
    assert not report.assessments[0].establishes_causality
    assert "causality_not_established" in report.risk_codes
    assert report.epistemic_gaps[0].known_elements == ("fact-window",)


def test_deepening_is_read_only_and_cannot_bypass_curiosity_or_learning() -> None:
    defaults = {
        field.name: field.default for field in fields(GovernedHypothesisDeepeningReport)
    }

    for field_name in (
        "persists_results",
        "creates_facts",
        "creates_questions",
        "creates_learning_candidates",
        "modifies_world_model",
        "modifies_memory",
        "modifies_learning",
        "modifies_planning",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[field_name] is False
