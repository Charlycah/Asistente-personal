from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path

import pytest

from core.governed_complex_decision_reasoning import (
    ComplexDecisionCriterionOutcome,
    ComplexDecisionOptionStatus,
    ComplexDecisionReasoningStatus,
    GovernedComplexDecisionReasoningFoundationV1,
    GovernedDecisionCriterion,
    GovernedOptionCriterionAssessment,
)
from core.governed_decision_advisory import GovernedDecisionOption

FOUNDATION = GovernedComplexDecisionReasoningFoundationV1()


def _option(option_id: str) -> GovernedDecisionOption:
    return GovernedDecisionOption(option_id=option_id, title=f"Option {option_id}")


def _criterion(
    criterion_id: str,
    *,
    required: bool = False,
    importance: float | None = None,
) -> GovernedDecisionCriterion:
    return GovernedDecisionCriterion(
        criterion_id=criterion_id,
        title=f"Criterion {criterion_id}",
        required=required,
        explicit_importance=importance,
        provenance_codes=(f"criterion_source:{criterion_id}",),
    )


def _evidence(
    option_id: str,
    criterion_id: str,
    outcome: ComplexDecisionCriterionOutcome,
    *,
    value: float | None = None,
) -> GovernedOptionCriterionAssessment:
    return GovernedOptionCriterionAssessment(
        option_id=option_id,
        criterion_id=criterion_id,
        outcome=outcome,
        explicit_value=value,
        evidence_codes=(f"evidence:{option_id}:{criterion_id}",),
        source_fingerprint=f"fingerprint-{option_id}-{criterion_id}",
    )


def test_foundation_requires_explicit_options_and_criteria() -> None:
    criterion = _criterion("safety")
    option = _option("a")
    evidence = _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE)

    with pytest.raises(ValueError, match="explicit options"):
        FOUNDATION.assess((), (criterion,), ())
    with pytest.raises(ValueError, match="explicit criteria"):
        FOUNDATION.assess((option,), (), ())
    report = FOUNDATION.assess((option,), (criterion,), (evidence,))
    assert report.source_option_ids == ("a",)


def test_duplicate_option_or_criterion_ids_fail_closed() -> None:
    option = _option("a")
    criterion = _criterion("safety")
    evidence = _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE)

    with pytest.raises(ValueError, match="option ids must be unique"):
        FOUNDATION.assess((option, option), (criterion,), (evidence,))
    with pytest.raises(ValueError, match="criterion ids must be unique"):
        FOUNDATION.assess((option,), (criterion, criterion), (evidence,))


def test_unknown_option_or_criterion_reference_fails_closed() -> None:
    option = _option("a")
    criterion = _criterion("safety")

    with pytest.raises(ValueError, match="unknown option"):
        FOUNDATION.assess(
            (option,),
            (criterion,),
            (_evidence("b", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),),
        )
    with pytest.raises(ValueError, match="unknown criterion"):
        FOUNDATION.assess(
            (option,),
            (criterion,),
            (_evidence("a", "cost", ComplexDecisionCriterionOutcome.FAVORABLE),),
        )


def test_duplicate_or_missing_option_criterion_pair_fails_closed() -> None:
    options = (_option("a"), _option("b"))
    criterion = _criterion("safety")
    first = _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE)

    with pytest.raises(ValueError, match="pairs must be unique"):
        FOUNDATION.assess(options, (criterion,), (first, first))
    with pytest.raises(ValueError, match="complete option criterion evidence"):
        FOUNDATION.assess(options, (criterion,), (first,))


def test_explicit_importance_and_value_are_bounded_and_never_inferred() -> None:
    with pytest.raises(ValueError, match="importance"):
        _criterion("safety", importance=1.1)
    with pytest.raises(ValueError, match="criterion value"):
        _evidence(
            "a",
            "safety",
            ComplexDecisionCriterionOutcome.FAVORABLE,
            value=-0.1,
        )

    criterion = _criterion("safety")
    assert criterion.explicit_importance is None


def test_required_unfavorable_criterion_blocks_option() -> None:
    options = (_option("a"), _option("b"))
    criterion = _criterion("safety", required=True)
    report = FOUNDATION.assess(
        options,
        (criterion,),
        (
            _evidence("a", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE),
            _evidence("b", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),
        ),
    )

    by_id = {item.option_id: item for item in report.option_assessments}
    assert by_id["a"].status is ComplexDecisionOptionStatus.BLOCKED
    assert by_id["a"].blocking_criterion_ids == ("safety",)
    assert report.recommended_option_id == "b"
    assert report.status is ComplexDecisionReasoningStatus.COMPLETE


def test_insufficient_evidence_requires_review_and_withholds_recommendation() -> None:
    options = (_option("a"), _option("b"))
    criterion = _criterion("cost")
    report = FOUNDATION.assess(
        options,
        (criterion,),
        (
            _evidence("a", "cost", ComplexDecisionCriterionOutcome.INSUFFICIENT),
            _evidence("b", "cost", ComplexDecisionCriterionOutcome.FAVORABLE),
        ),
    )

    assert report.status is ComplexDecisionReasoningStatus.INSUFFICIENT_EVIDENCE
    assert report.recommended_option_id is None
    assert "complex_decision:insufficient_evidence_preserved" in report.rationale_codes
    assert (
        "complex_decision:recommendation_withheld_for_incomplete_evidence"
        in report.rationale_codes
    )


def test_required_failure_precedes_other_insufficient_evidence_on_same_option() -> None:
    option = _option("a")
    criteria = (_criterion("safety", required=True), _criterion("cost"))
    report = FOUNDATION.assess(
        (option,),
        criteria,
        (
            _evidence("a", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE),
            _evidence("a", "cost", ComplexDecisionCriterionOutcome.INSUFFICIENT),
        ),
    )

    assessment = report.option_assessments[0]
    assert assessment.status is ComplexDecisionOptionStatus.BLOCKED
    assert assessment.blocking_criterion_ids == ("safety",)
    assert assessment.review_criterion_ids == ("cost",)


def test_pareto_dominance_recommends_without_utility_score() -> None:
    options = (_option("a"), _option("b"))
    criteria = (_criterion("safety"), _criterion("cost"))
    report = FOUNDATION.assess(
        options,
        criteria,
        (
            _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),
            _evidence("a", "cost", ComplexDecisionCriterionOutcome.FAVORABLE),
            _evidence("b", "safety", ComplexDecisionCriterionOutcome.NEUTRAL),
            _evidence("b", "cost", ComplexDecisionCriterionOutcome.FAVORABLE),
        ),
    )

    assert report.recommended_option_id == "a"
    assert "complex_decision:pareto_dominance" in report.rationale_codes
    assert report.tradeoff_codes == ()


def test_explicit_value_refines_comparison_without_replacing_outcome_semantics(
) -> None:
    options = (_option("a"), _option("b"))
    criterion = _criterion("cost")
    report = FOUNDATION.assess(
        options,
        (criterion,),
        (
            _evidence(
                "a",
                "cost",
                ComplexDecisionCriterionOutcome.FAVORABLE,
                value=0.8,
            ),
            _evidence(
                "b",
                "cost",
                ComplexDecisionCriterionOutcome.FAVORABLE,
                value=0.6,
            ),
        ),
    )

    assert report.recommended_option_id == "a"


def test_tradeoff_without_explicit_importance_remains_review_required() -> None:
    options = (_option("a"), _option("b"))
    criteria = (_criterion("safety"), _criterion("cost"))
    report = FOUNDATION.assess(
        options,
        criteria,
        (
            _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),
            _evidence("a", "cost", ComplexDecisionCriterionOutcome.UNFAVORABLE),
            _evidence("b", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE),
            _evidence("b", "cost", ComplexDecisionCriterionOutcome.FAVORABLE),
        ),
    )

    assert report.recommended_option_id is None
    assert report.status is ComplexDecisionReasoningStatus.REVIEW_REQUIRED
    assert report.tradeoff_codes
    assert "complex_decision:non_dominated_review_required" in report.rationale_codes


def test_higher_explicit_importance_can_resolve_tradeoff_lexicographically() -> None:
    options = (_option("a"), _option("b"))
    criteria = (
        _criterion("safety", importance=1.0),
        _criterion("cost", importance=0.5),
    )
    report = FOUNDATION.assess(
        options,
        criteria,
        (
            _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),
            _evidence("a", "cost", ComplexDecisionCriterionOutcome.UNFAVORABLE),
            _evidence("b", "safety", ComplexDecisionCriterionOutcome.NEUTRAL),
            _evidence("b", "cost", ComplexDecisionCriterionOutcome.FAVORABLE),
        ),
    )

    assert report.recommended_option_id == "a"
    assert report.tradeoff_codes
    assert (
        "complex_decision:explicit_importance_resolved_tradeoff"
        in report.rationale_codes
    )


def test_equal_importance_conflict_does_not_create_arbitrary_winner() -> None:
    options = (_option("a"), _option("b"))
    criteria = (
        _criterion("safety", importance=1.0),
        _criterion("cost", importance=1.0),
    )
    report = FOUNDATION.assess(
        options,
        criteria,
        (
            _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),
            _evidence("a", "cost", ComplexDecisionCriterionOutcome.UNFAVORABLE),
            _evidence("b", "safety", ComplexDecisionCriterionOutcome.UNFAVORABLE),
            _evidence("b", "cost", ComplexDecisionCriterionOutcome.FAVORABLE),
        ),
    )

    assert report.recommended_option_id is None
    assert report.status is ComplexDecisionReasoningStatus.REVIEW_REQUIRED


def test_single_complete_option_is_advisable_but_not_action_authorized() -> None:
    report = FOUNDATION.assess(
        (_option("a"),),
        (_criterion("safety"),),
        (_evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),),
    )

    assert report.recommended_option_id == "a"
    assert report.status is ComplexDecisionReasoningStatus.COMPLETE
    assert report.option_assessments[0].action_authorized is False
    assert report.executes_actions is False


def test_all_blocked_options_preserve_human_review_and_no_recommendation() -> None:
    options = (_option("a"), _option("b"))
    criterion = _criterion("safety", required=True)
    report = FOUNDATION.assess(
        options,
        (criterion,),
        tuple(
            _evidence(
                item.option_id,
                "safety",
                ComplexDecisionCriterionOutcome.UNFAVORABLE,
            )
            for item in options
        ),
    )

    assert report.recommended_option_id is None
    assert report.status is ComplexDecisionReasoningStatus.REVIEW_REQUIRED
    assert "complex_decision:no_eligible_option" in report.rationale_codes


def test_input_order_does_not_change_report_identity_or_selection() -> None:
    a = _option("a")
    b = _option("b")
    safety = _criterion("safety")
    cost = _criterion("cost")
    evidence = (
        _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),
        _evidence("a", "cost", ComplexDecisionCriterionOutcome.FAVORABLE),
        _evidence("b", "safety", ComplexDecisionCriterionOutcome.NEUTRAL),
        _evidence("b", "cost", ComplexDecisionCriterionOutcome.FAVORABLE),
    )

    forward = FOUNDATION.assess((a, b), (safety, cost), evidence)
    reverse = FOUNDATION.assess(
        (b, a),
        (cost, safety),
        tuple(reversed(evidence)),
    )

    assert reverse.report_id == forward.report_id
    assert reverse.source_fingerprint == forward.source_fingerprint
    assert reverse.recommended_option_id == forward.recommended_option_id == "a"


def test_fingerprint_changes_when_criterion_evidence_or_importance_changes() -> None:
    options = (_option("a"), _option("b"))
    criterion = _criterion("safety", importance=0.8)
    evidence = (
        _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),
        _evidence("b", "safety", ComplexDecisionCriterionOutcome.NEUTRAL),
    )
    base = FOUNDATION.assess(options, (criterion,), evidence)
    changed_importance = FOUNDATION.assess(
        options,
        (replace(criterion, explicit_importance=0.9),),
        evidence,
    )
    changed_evidence = FOUNDATION.assess(
        options,
        (criterion,),
        (
            replace(evidence[0], evidence_codes=("evidence:changed",)),
            evidence[1],
        ),
    )

    assert changed_importance.source_fingerprint != base.source_fingerprint
    assert changed_evidence.source_fingerprint != base.source_fingerprint


def test_provenance_is_preserved_end_to_end() -> None:
    option = _option("a")
    criterion = _criterion("safety")
    evidence = _evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE)
    report = FOUNDATION.assess((option,), (criterion,), (evidence,))

    assert report.source_option_ids == ("a",)
    assert report.criteria[0].provenance_codes == ("criterion_source:safety",)
    projected = report.option_assessments[0].criterion_assessments[0]
    assert projected.evidence_codes == ("evidence:a:safety",)
    assert projected.source_fingerprint == "fingerprint-a-safety"


def test_contracts_are_immutable_and_cannot_be_promoted_to_action() -> None:
    report = FOUNDATION.assess(
        (_option("a"),),
        (_criterion("safety"),),
        (_evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),),
    )

    with pytest.raises(FrozenInstanceError):
        report.read_only = False
    with pytest.raises(ValueError, match="authorize action"):
        replace(report.option_assessments[0], action_authorized=True)
    with pytest.raises(ValueError, match="facts or actions"):
        replace(
            report.option_assessments[0].criterion_assessments[0],
            action_authorized=True,
        )


def test_report_defaults_preserve_canonical_authority_and_non_power_contract() -> None:
    defaults = {field.name: field.default for field in fields(type(FONDATION_REPORT()))}

    assert defaults["canonical_authority"] == "unified_cognitive_coordination"
    assert defaults["canonical_facade"] == "CanonicalDecisionFacade"
    assert defaults["read_only"] is True
    assert defaults["advisory_only"] is True
    assert defaults["human_decision_preserved"] is True
    for name in (
        "establishes_truth",
        "assigns_probability",
        "creates_facts",
        "creates_plans",
        "creates_tasks",
        "persists_results",
        "modifies_memory",
        "modifies_learning",
        "modifies_world_model",
        "modifies_planning",
        "modifies_organization",
        "executes_actions",
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[name] is False


def FONDATION_REPORT():
    return FOUNDATION.assess(
        (_option("a"),),
        (_criterion("safety"),),
        (_evidence("a", "safety", ComplexDecisionCriterionOutcome.FAVORABLE),),
    )


def test_foundation_module_has_no_runtime_gateway_or_mutating_dependencies() -> None:
    source = Path("core/governed_complex_decision_reasoning.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "OfficialConversationGateway",
        "OfficialConversationIntelligenceRuntimeGateway",
        "memory_gateway",
        "learning_gateway",
        "from core.persistent_world_model",
        "from core.task_manager",
        "from core.agenda",
        "requests",
        "httpx",
        "subprocess",
    )

    for token in forbidden:
        assert token not in source


def test_historical_m391_6_option_contract_is_not_modified_by_foundation() -> None:
    option_field_names = tuple(field.name for field in fields(GovernedDecisionOption))

    assert option_field_names == (
        "option_id",
        "title",
        "organization_item_id",
        "scenario_hypothesis_id",
        "causal_relation_id",
        "explicit_preference",
    )
