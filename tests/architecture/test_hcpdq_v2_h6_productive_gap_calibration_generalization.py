from __future__ import annotations

from core.governed_complex_decision_reasoning import (
    ComplexDecisionCriterionOutcome,
    ComplexDecisionOptionStatus,
    ComplexDecisionReasoningStatus,
    GovernedComplexDecisionReasoningFoundationV1,
    GovernedDecisionCriterion,
    GovernedOptionCriterionAssessment,
)
from core.governed_decision_advisory import GovernedDecisionOption


def _option(option_id: str):
    return GovernedDecisionOption(option_id=option_id, title=option_id.title())


def _criterion(criterion_id: str, *, required: bool = False):
    return GovernedDecisionCriterion(
        criterion_id=criterion_id,
        title=criterion_id.title(),
        required=required,
        provenance_codes=(f"calibration:{criterion_id}",),
    )


def _assessment(option_id, criterion_id, outcome):
    return GovernedOptionCriterionAssessment(
        option_id=option_id,
        criterion_id=criterion_id,
        outcome=outcome,
        evidence_codes=(f"calibration:{option_id}:{criterion_id}",),
    )


def _assess(options, criteria, assessments):
    return GovernedComplexDecisionReasoningFoundationV1().assess(
        tuple(options),
        tuple(criteria),
        tuple(assessments),
    )


def test_generalizes_to_three_options_and_two_required_constraints():
    options = [_option("alpha"), _option("beta"), _option("gamma")]
    criteria = [
        _criterion("legal", required=True),
        _criterion("safety", required=True),
        _criterion("cost"),
    ]
    assessments = [
        _assessment(
            "alpha", "legal", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "alpha", "safety", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "alpha", "cost", ComplexDecisionCriterionOutcome.INSUFFICIENT
        ),
        _assessment(
            "beta", "legal", ComplexDecisionCriterionOutcome.UNFAVORABLE
        ),
        _assessment(
            "beta", "safety", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "beta", "cost", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "gamma", "legal", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "gamma", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE
        ),
        _assessment(
            "gamma", "cost", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
    ]
    report = _assess(options, criteria, assessments)
    assert report.recommended_option_id == "alpha"
    assert report.status is ComplexDecisionReasoningStatus.COMPLETE
    alpha = next(
        item for item in report.option_assessments if item.option_id == "alpha"
    )
    assert alpha.review_criterion_ids == ("cost",)


def test_multiple_required_constraint_survivors_do_not_trigger_exception():
    options = [_option("alpha"), _option("beta"), _option("gamma")]
    criteria = [
        _criterion("safety", required=True),
        _criterion("cost"),
    ]
    assessments = [
        _assessment(
            "alpha", "safety", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "alpha", "cost", ComplexDecisionCriterionOutcome.INSUFFICIENT
        ),
        _assessment(
            "beta", "safety", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "beta", "cost", ComplexDecisionCriterionOutcome.INSUFFICIENT
        ),
        _assessment(
            "gamma", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE
        ),
        _assessment(
            "gamma", "cost", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
    ]
    report = _assess(options, criteria, assessments)
    assert report.recommended_option_id is None
    assert report.status is ComplexDecisionReasoningStatus.INSUFFICIENT_EVIDENCE


def test_required_insufficient_evidence_does_not_count_as_survival():
    options = [_option("alpha"), _option("beta")]
    criteria = [
        _criterion("safety", required=True),
        _criterion("cost"),
    ]
    assessments = [
        _assessment(
            "alpha", "safety", ComplexDecisionCriterionOutcome.INSUFFICIENT
        ),
        _assessment(
            "alpha", "cost", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "beta", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE
        ),
        _assessment(
            "beta", "cost", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
    ]
    report = _assess(options, criteria, assessments)
    assert report.recommended_option_id is None
    assert report.status is ComplexDecisionReasoningStatus.INSUFFICIENT_EVIDENCE


def test_no_required_criterion_does_not_activate_survivor_exception():
    options = [_option("alpha"), _option("beta")]
    criteria = [_criterion("safety"), _criterion("cost")]
    assessments = [
        _assessment(
            "alpha", "safety", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "alpha", "cost", ComplexDecisionCriterionOutcome.INSUFFICIENT
        ),
        _assessment(
            "beta", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE
        ),
        _assessment(
            "beta", "cost", ComplexDecisionCriterionOutcome.INSUFFICIENT
        ),
    ]
    report = _assess(options, criteria, assessments)
    assert report.recommended_option_id is None
    assert report.status is ComplexDecisionReasoningStatus.INSUFFICIENT_EVIDENCE


def test_unblocked_competitor_prevents_required_survivor_exception():
    options = [_option("alpha"), _option("beta")]
    criteria = [
        _criterion("safety", required=True),
        _criterion("cost"),
    ]
    assessments = [
        _assessment(
            "alpha", "safety", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "alpha", "cost", ComplexDecisionCriterionOutcome.INSUFFICIENT
        ),
        _assessment(
            "beta", "safety", ComplexDecisionCriterionOutcome.INSUFFICIENT
        ),
        _assessment(
            "beta", "cost", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
    ]
    report = _assess(options, criteria, assessments)
    assert report.recommended_option_id is None
    assert report.status is ComplexDecisionReasoningStatus.INSUFFICIENT_EVIDENCE


def test_blocked_option_never_becomes_recommended():
    options = [_option("alpha"), _option("beta")]
    criteria = [_criterion("safety", required=True)]
    assessments = [
        _assessment(
            "alpha", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE
        ),
        _assessment(
            "beta", "safety", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
    ]
    report = _assess(options, criteria, assessments)
    alpha = next(
        item for item in report.option_assessments if item.option_id == "alpha"
    )
    assert alpha.status is ComplexDecisionOptionStatus.BLOCKED
    assert report.recommended_option_id == "beta"


def test_required_survivor_result_is_order_invariant():
    options = [_option("alpha"), _option("beta")]
    criteria = [
        _criterion("safety", required=True),
        _criterion("cost"),
    ]
    assessments = [
        _assessment(
            "alpha", "safety", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
        _assessment(
            "alpha", "cost", ComplexDecisionCriterionOutcome.INSUFFICIENT
        ),
        _assessment(
            "beta", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE
        ),
        _assessment(
            "beta", "cost", ComplexDecisionCriterionOutcome.FAVORABLE
        ),
    ]
    forward = _assess(options, criteria, assessments)
    reverse = _assess(
        list(reversed(options)),
        criteria,
        list(reversed(assessments)),
    )
    assert forward.recommended_option_id == "alpha"
    assert reverse.recommended_option_id == "alpha"
