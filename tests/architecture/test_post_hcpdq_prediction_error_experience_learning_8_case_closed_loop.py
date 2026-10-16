from __future__ import annotations

from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    ReflectionLearningEvidenceAdapter,
)
from core.governed_reasoning.governed_prediction import (
    GovernedPredictionAssessment,
    GovernedPredictionDisposition,
)
from core.governed_reasoning.prediction_outcome_evaluation import (
    GovernedPredictionOutcomeEvaluator,
    ObservedPredictionOutcome,
    PredictionOutcomeDisposition,
)


def _prediction(
    *,
    disposition: GovernedPredictionDisposition = (
        GovernedPredictionDisposition.CONDITIONALLY_SUPPORTED
    ),
) -> GovernedPredictionAssessment:
    return GovernedPredictionAssessment(
        prediction_id="prediction-trip-arrival",
        relation_id="relation-transport-arrival",
        horizon_code="next_observation_window",
        disposition=disposition,
        predicted_domain="environment",
        predicted_key="trip.arrival",
        predicted_value="viable",
        condition_codes=("condition:transport_available",),
        rationale_codes=("prediction:challenge_supported",),
    )


def _observation(**changes) -> ObservedPredictionOutcome:
    values = {
        "observation_id": "observation-trip-arrival",
        "domain": "environment",
        "key": "trip.arrival",
        "value": "viable",
        "horizon_code": "next_observation_window",
        "condition_codes": ("condition:transport_available",),
        "evidence_codes": ("observation:explicit",),
    }
    values.update(changes)
    return ObservedPredictionOutcome(**values)


def test_pe1_matching_outcome_is_explicit_without_learning_candidate():
    result = GovernedPredictionOutcomeEvaluator().evaluate(
        _prediction(),
        _observation(),
    )
    assert result.disposition is PredictionOutcomeDisposition.MATCH
    assert result.learning_candidate is None
    assert result.predicted_value == "viable"
    assert result.observed_value == "viable"


def test_pe2_valid_mismatch_creates_review_only_learning_candidate():
    result = GovernedPredictionOutcomeEvaluator().evaluate(
        _prediction(),
        _observation(value="blocked"),
    )
    assert result.disposition is PredictionOutcomeDisposition.MISMATCH
    candidate = result.learning_candidate
    assert candidate is not None
    assert candidate.disposition == "review_required"
    assert candidate.accepted_as_knowledge is False
    assert candidate.persistence_authorized is False


def test_pe3_prediction_error_reaches_existing_learning_evidence_node():
    result = GovernedPredictionOutcomeEvaluator().evaluate(
        _prediction(),
        _observation(value="blocked"),
    )
    records = []
    adapter = ReflectionLearningEvidenceAdapter()
    with adapter.capture(records.append):
        adapter.observe_learning_candidate(result.learning_candidate)
    assert len(records) == 1
    assert records[0].node_id == "learning_candidate"
    assert records[0].state is CognitiveCycleNodeState.PARTICIPATED
    assert records[0].evidence_codes == ("learning_candidate:review_required",)


def test_pe4_horizon_mismatch_requires_review_not_error_learning():
    result = GovernedPredictionOutcomeEvaluator().evaluate(
        _prediction(),
        _observation(horizon_code="later_window"),
    )
    assert result.disposition is PredictionOutcomeDisposition.REVIEW
    assert result.learning_candidate is None
    assert result.rationale_codes == ("prediction_outcome:horizon_mismatch",)


def test_pe5_condition_mismatch_requires_review_not_error_learning():
    result = GovernedPredictionOutcomeEvaluator().evaluate(
        _prediction(),
        _observation(condition_codes=("condition:transport_unavailable",)),
    )
    assert result.disposition is PredictionOutcomeDisposition.REVIEW
    assert result.learning_candidate is None
    assert result.rationale_codes == ("prediction_outcome:condition_mismatch",)


def test_pe6_unrelated_observation_cannot_be_claimed_as_prediction_error():
    result = GovernedPredictionOutcomeEvaluator().evaluate(
        _prediction(),
        _observation(key="weather.current", value="rain"),
    )
    assert result.disposition is PredictionOutcomeDisposition.REVIEW
    assert result.learning_candidate is None
    assert result.rationale_codes == (
        "prediction_outcome:observation_lineage_mismatch",
    )


def test_pe7_missing_or_unsupported_prediction_evidence_stays_unresolved():
    evaluator = GovernedPredictionOutcomeEvaluator()
    missing = evaluator.evaluate(_prediction(), None)
    unsupported = evaluator.evaluate(
        _prediction(disposition=GovernedPredictionDisposition.UNRESOLVED),
        _observation(value="blocked"),
    )
    assert missing.disposition is PredictionOutcomeDisposition.UNRESOLVED
    assert unsupported.disposition is PredictionOutcomeDisposition.UNRESOLVED
    assert missing.learning_candidate is None
    assert unsupported.learning_candidate is None


def test_pe8_outcome_evaluation_is_read_only_non_authoritative_and_lineaged():
    result = GovernedPredictionOutcomeEvaluator().evaluate(
        _prediction(),
        _observation(value="blocked"),
    )
    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.establishes_truth is False
    assert result.proves_causality is False
    assert result.calibrates_probability is False
    assert result.modifies_prediction is False
    assert result.modifies_world_model is False
    assert result.modifies_memory is False
    assert result.modifies_learning is False
    assert result.persists_results is False
    assert result.executes_actions is False
    assert "prediction:prediction-trip-arrival" in result.evidence_codes
    assert "observation:observation-trip-arrival" in result.evidence_codes
