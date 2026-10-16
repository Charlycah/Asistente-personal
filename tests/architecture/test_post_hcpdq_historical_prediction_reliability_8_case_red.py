from __future__ import annotations

from dataclasses import replace
from enum import StrEnum

import pytest

from core.governed_reasoning.prediction_outcome_evaluation import (
    PredictionOutcomeDisposition,
    PredictionOutcomeEvaluation,
)


class ExpectedHistoricalReliability(StrEnum):
    SUPPORTED = "supported"
    MIXED = "mixed"
    LIMITED = "limited"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


def _outcome(
    index: int,
    disposition: PredictionOutcomeDisposition,
    *,
    scope: str = "transport.arrival",
) -> PredictionOutcomeEvaluation:
    observed = None if disposition is PredictionOutcomeDisposition.UNRESOLVED else (
        f"observation-{scope}-{index}"
    )
    return PredictionOutcomeEvaluation(
        evaluation_id=f"prediction-outcome-{scope.replace('.', '-')}-{index:02d}",
        prediction_id=f"prediction-{scope}-{index}",
        observation_id=observed,
        disposition=disposition,
        predicted_value="viable",
        observed_value=(
            None
            if disposition is PredictionOutcomeDisposition.UNRESOLVED
            else "viable"
            if disposition is PredictionOutcomeDisposition.MATCH
            else "blocked"
        ),
        evidence_codes=(
            f"prediction:prediction-{scope}-{index}",
            *(() if observed is None else (f"observation:{observed}",)),
        ),
        rationale_codes=(f"prediction_outcome:{disposition.value}",),
    )


def _history(
    *,
    matches: int = 0,
    mismatches: int = 0,
    unresolved: int = 0,
    review: int = 0,
    scope: str = "transport.arrival",
) -> tuple[PredictionOutcomeEvaluation, ...]:
    dispositions = (
        (PredictionOutcomeDisposition.MATCH,) * matches
        + (PredictionOutcomeDisposition.MISMATCH,) * mismatches
        + (PredictionOutcomeDisposition.UNRESOLVED,) * unresolved
        + (PredictionOutcomeDisposition.REVIEW,) * review
    )
    return tuple(
        _outcome(index, disposition, scope=scope)
        for index, disposition in enumerate(dispositions, start=1)
    )


def _evaluate(
    history: tuple[PredictionOutcomeEvaluation, ...],
    *,
    scope: str = "transport.arrival",
):
    from core.governed_reasoning.historical_prediction_reliability import (
        GovernedHistoricalPredictionReliabilityEvaluator,
    )

    return GovernedHistoricalPredictionReliabilityEvaluator().evaluate(
        scope=scope,
        outcomes=history,
    )


def _assert_governed_limits(result) -> None:
    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.establishes_truth is False
    assert result.calibrates_probability is False
    assert result.modifies_response_confidence is False
    assert result.modifies_prediction is False
    assert result.modifies_world_model is False
    assert result.modifies_memory is False
    assert result.modifies_learning is False
    assert result.persists_results is False
    assert result.executes_actions is False


def test_hr1_predominantly_matching_history_is_supported():
    result = _evaluate(_history(matches=8, mismatches=2))
    assert result.disposition.value == ExpectedHistoricalReliability.SUPPORTED
    assert result.total_count == 10
    assert result.evaluable_count == 10
    assert result.match_count == 8
    assert result.mismatch_count == 2
    _assert_governed_limits(result)


def test_hr2_predominantly_mismatching_history_is_not_supported():
    result = _evaluate(_history(matches=2, mismatches=8))
    assert result.disposition.value == ExpectedHistoricalReliability.MIXED
    assert result.match_count == 2
    assert result.mismatch_count == 8
    _assert_governed_limits(result)


def test_hr3_balanced_history_is_mixed():
    result = _evaluate(_history(matches=5, mismatches=5))
    assert result.disposition.value == ExpectedHistoricalReliability.MIXED
    assert result.evaluable_count == 10
    _assert_governed_limits(result)


def test_hr4_small_evaluable_sample_is_limited():
    result = _evaluate(_history(matches=2, mismatches=1))
    assert result.disposition.value == ExpectedHistoricalReliability.LIMITED
    assert result.evaluable_count == 3
    _assert_governed_limits(result)


def test_hr5_unresolved_heavy_history_exposes_limited_coverage():
    result = _evaluate(_history(matches=4, mismatches=1, unresolved=15))
    assert result.disposition.value == ExpectedHistoricalReliability.LIMITED
    assert result.total_count == 20
    assert result.evaluable_count == 5
    assert result.unresolved_count == 15
    assert result.coverage == pytest.approx(0.25)
    _assert_governed_limits(result)


def test_hr6_review_or_cross_scope_lineage_requires_review():
    history = _history(matches=6, mismatches=1, review=1)
    foreign = _outcome(
        99,
        PredictionOutcomeDisposition.MATCH,
        scope="weather.rain",
    )
    result = _evaluate((*history, foreign))
    assert result.disposition.value == ExpectedHistoricalReliability.REVIEW_REQUIRED
    assert result.review_count >= 1
    _assert_governed_limits(result)


def test_hr7_duplicate_outcomes_do_not_inflate_reliability():
    base = _history(matches=4, mismatches=2)
    duplicated = (*base, replace(base[0]), replace(base[1]))
    result = _evaluate(duplicated)
    assert result.unique_count == 6
    assert result.duplicate_count == 2
    assert result.evaluable_count == 6
    assert result.disposition.value != ExpectedHistoricalReliability.SUPPORTED
    _assert_governed_limits(result)


def test_hr8_historical_ratio_never_becomes_future_probability_or_confidence():
    result = _evaluate(_history(matches=8, mismatches=2))
    assert result.match_ratio == pytest.approx(0.8)
    assert result.match_ratio_is_descriptive is True
    assert result.future_probability is None
    assert result.response_confidence_update is None
    assert result.establishes_truth is False
    assert result.calibrates_probability is False
    assert result.modifies_response_confidence is False
    _assert_governed_limits(result)
