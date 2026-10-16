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


def _options():
    return (
        GovernedDecisionOption(option_id="alpha", title="Alpha"),
        GovernedDecisionOption(option_id="beta", title="Beta"),
    )


def _criteria(*, required: bool):
    return (
        GovernedDecisionCriterion(
            criterion_id="safety",
            title="Safety",
            required=required,
            provenance_codes=("test:explicit:safety",),
        ),
        GovernedDecisionCriterion(
            criterion_id="cost",
            title="Cost",
            provenance_codes=("test:explicit:cost",),
        ),
    )


def _assessment(option_id, criterion_id, outcome):
    return GovernedOptionCriterionAssessment(
        option_id=option_id,
        criterion_id=criterion_id,
        outcome=outcome,
        evidence_codes=(f"test:{option_id}:{criterion_id}",),
    )


def _required_survivor_report():
    assessments = (
        _assessment(
            "alpha",
            "safety",
            ComplexDecisionCriterionOutcome.FAVORABLE,
        ),
        _assessment(
            "alpha",
            "cost",
            ComplexDecisionCriterionOutcome.INSUFFICIENT,
        ),
        _assessment(
            "beta",
            "safety",
            ComplexDecisionCriterionOutcome.UNFAVORABLE,
        ),
        _assessment(
            "beta",
            "cost",
            ComplexDecisionCriterionOutcome.INSUFFICIENT,
        ),
    )
    return GovernedComplexDecisionReasoningFoundationV1().assess(
        _options(),
        _criteria(required=True),
        assessments,
    )


def test_red_sole_required_constraint_survivor_is_recommended():
    report = _required_survivor_report()
    assert report.recommended_option_id == "alpha"
    assert report.status is ComplexDecisionReasoningStatus.COMPLETE


def test_red_survivor_keeps_unknown_secondary_evidence_visible():
    report = _required_survivor_report()
    alpha = next(
        item for item in report.option_assessments if item.option_id == "alpha"
    )
    assert alpha.review_criterion_ids == ("cost",)
    cost = next(
        item
        for item in alpha.criterion_assessments
        if item.criterion_id == "cost"
    )
    assert cost.outcome is ComplexDecisionCriterionOutcome.INSUFFICIENT


def test_red_failed_required_constraint_remains_blocking():
    report = _required_survivor_report()
    beta = next(
        item for item in report.option_assessments if item.option_id == "beta"
    )
    assert beta.status is ComplexDecisionOptionStatus.BLOCKED
    assert beta.blocking_criterion_ids == ("safety",)


def test_red_ambiguous_nonrequired_missing_evidence_still_abstains():
    assessments = (
        _assessment(
            "alpha",
            "safety",
            ComplexDecisionCriterionOutcome.FAVORABLE,
        ),
        _assessment(
            "alpha",
            "cost",
            ComplexDecisionCriterionOutcome.INSUFFICIENT,
        ),
        _assessment(
            "beta",
            "safety",
            ComplexDecisionCriterionOutcome.UNFAVORABLE,
        ),
        _assessment(
            "beta",
            "cost",
            ComplexDecisionCriterionOutcome.INSUFFICIENT,
        ),
    )
    report = GovernedComplexDecisionReasoningFoundationV1().assess(
        _options(),
        _criteria(required=False),
        assessments,
    )
    assert report.recommended_option_id is None
    assert report.status is ComplexDecisionReasoningStatus.INSUFFICIENT_EVIDENCE


def test_red_missing_evidence_is_never_rewritten_as_unfavorable():
    report = _required_survivor_report()
    outcomes = {
        (item.option_id, assessment.criterion_id): assessment.outcome
        for item in report.option_assessments
        for assessment in item.criterion_assessments
    }
    assert outcomes[("alpha", "cost")] is (
        ComplexDecisionCriterionOutcome.INSUFFICIENT
    )
    assert outcomes[("beta", "cost")] is (
        ComplexDecisionCriterionOutcome.INSUFFICIENT
    )


def test_red_report_preserves_governed_read_only_limits():
    report = _required_survivor_report()
    assert report.read_only is True
    assert report.advisory_only is True
    assert report.human_decision_preserved is True
    assert report.executes_actions is False
    assert report.modifies_memory is False
    assert report.modifies_learning is False
