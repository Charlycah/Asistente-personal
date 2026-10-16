from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    ActionCandidate,
    DecisionSituation,
    DeterministicRiskConfidenceEvaluator,
    Reversibility,
    RiskConfidenceEvaluator,
    RiskEvaluationResult,
    RiskEvaluationStatus,
    RiskLevel,
    RiskProfile,
    default_risk_profiles,
)

NOW = datetime(2026, 7, 26, 22, 0, tzinfo=timezone.utc)


def situation(**changes: object) -> DecisionSituation:
    values: dict[str, object] = {
        "kind": "runtime_component_unhealthy",
        "description": "A component is unhealthy",
        "evidence": ("component_id=vosk",),
        "observed_at": NOW,
        "source": "component_health.vosk",
        "urgency": 0.8,
        "situation_id": "situation-1",
    }
    values.update(changes)
    return DecisionSituation(**values)


def candidate(**changes: object) -> ActionCandidate:
    values: dict[str, object] = {
        "action": "restart_component",
        "description": "Restart component",
        "rationale": ("attempt_local_recovery",),
        "reversible": Reversibility.PARTIAL,
        "estimated_cost": 0.3,
        "candidate_id": "candidate-1",
    }
    values.update(changes)
    return ActionCandidate(**values)


def profile(**changes: object) -> RiskProfile:
    values: dict[str, object] = {
        "action": "restart_component",
        "base_risk": RiskLevel.MEDIUM,
        "base_confidence": 0.8,
        "base_impact": 0.4,
        "reasons": ("runtime_mutation",),
        "profile_id": "profile-1",
    }
    values.update(changes)
    return RiskProfile(**values)


@pytest.mark.parametrize("field", ("action", "profile_id"))
def test_profile_rejects_blank_identity(field):
    with pytest.raises(ValueError):
        profile(**{field: ""})


def test_profile_requires_reasons():
    with pytest.raises(ValueError):
        profile(reasons=())


@pytest.mark.parametrize("field", ("base_confidence", "base_impact"))
@pytest.mark.parametrize("value", (-0.1, 1.1))
def test_profile_rejects_values_outside_unit_interval(field, value):
    with pytest.raises(ValueError):
        profile(**{field: value})


def test_profile_normalizes_risk():
    assert profile(base_risk="high").base_risk is RiskLevel.HIGH


def test_evaluator_satisfies_protocol():
    evaluator = DeterministicRiskConfidenceEvaluator((profile(),))
    assert isinstance(evaluator, RiskConfidenceEvaluator)


def test_evaluator_rejects_duplicate_profile_ids():
    with pytest.raises(ValueError):
        DeterministicRiskConfidenceEvaluator(
            (profile(), replace(profile(), action="notify_user"))
        )


def test_evaluator_rejects_duplicate_actions():
    with pytest.raises(ValueError):
        DeterministicRiskConfidenceEvaluator(
            (profile(), replace(profile(), profile_id="profile-2"))
        )


def test_evaluator_exposes_immutable_profiles():
    profiles = (profile(),)
    assert DeterministicRiskConfidenceEvaluator(profiles).profiles == profiles


def test_no_candidates_returns_explicit_status():
    result = DeterministicRiskConfidenceEvaluator((profile(),)).evaluate(
        situation(), ()
    )
    assert result.status is RiskEvaluationStatus.NO_CANDIDATES
    assert result.assessments == ()


def test_unknown_action_returns_unsupported():
    result = DeterministicRiskConfidenceEvaluator((profile(),)).evaluate(
        situation(), (candidate(action="unknown"),)
    )
    assert result.status is RiskEvaluationStatus.UNSUPPORTED
    assert result.assessments == ()
    assert "unsupported_action=unknown" in result.rationale


def test_matching_profile_generates_assessment():
    result = DeterministicRiskConfidenceEvaluator((profile(),)).evaluate(
        situation(), (candidate(),)
    )
    assert result.status is RiskEvaluationStatus.ASSESSMENTS_GENERATED
    assert result.assessments[0].candidate_id == "candidate-1"


def test_assessment_preserves_traceability():
    assessment = DeterministicRiskConfidenceEvaluator((profile(),)).evaluate(
        situation(), (candidate(),)
    ).assessments[0]
    assert "profile_id=profile-1" in assessment.reasons
    assert "situation_id=situation-1" in assessment.reasons


def test_scoring_is_deterministic():
    evaluator = DeterministicRiskConfidenceEvaluator((profile(),))
    first = evaluator.evaluate(situation(), (candidate(),)).assessments
    second = evaluator.evaluate(situation(), (candidate(),)).assessments
    assert first == second


def test_higher_urgency_increases_confidence_and_impact():
    evaluator = DeterministicRiskConfidenceEvaluator((profile(),))
    low = evaluator.evaluate(
        situation(urgency=0.0), (candidate(),)
    ).assessments[0]
    high = evaluator.evaluate(
        situation(urgency=1.0), (candidate(),)
    ).assessments[0]
    assert high.confidence > low.confidence
    assert high.impact > low.impact


def test_higher_cost_reduces_confidence_and_increases_impact():
    evaluator = DeterministicRiskConfidenceEvaluator((profile(),))
    cheap = evaluator.evaluate(
        situation(), (candidate(estimated_cost=0.0),)
    ).assessments[0]
    costly = evaluator.evaluate(
        situation(), (candidate(estimated_cost=1.0),)
    ).assessments[0]
    assert costly.confidence < cheap.confidence
    assert costly.impact > cheap.impact


def test_irreversible_action_escalates_risk():
    evaluator = DeterministicRiskConfidenceEvaluator(
        (profile(base_risk="low"),)
    )
    assessment = evaluator.evaluate(
        situation(), (candidate(reversible="none"),)
    ).assessments[0]
    assert assessment.risk is RiskLevel.MEDIUM


def test_high_impact_escalates_risk():
    evaluator = DeterministicRiskConfidenceEvaluator(
        (profile(base_risk="low", base_impact=0.9),)
    )
    assessment = evaluator.evaluate(situation(), (candidate(),)).assessments[0]
    assert assessment.risk is RiskLevel.MEDIUM


def test_prohibited_risk_is_never_downgraded():
    evaluator = DeterministicRiskConfidenceEvaluator(
        (profile(base_risk="prohibited"),)
    )
    assessment = evaluator.evaluate(situation(), (candidate(),)).assessments[0]
    assert assessment.risk is RiskLevel.PROHIBITED


def test_scores_are_clamped_to_unit_interval():
    evaluator = DeterministicRiskConfidenceEvaluator(
        (profile(base_confidence=1.0, base_impact=1.0),)
    )
    assessment = evaluator.evaluate(
        situation(urgency=1.0), (candidate(estimated_cost=10.0),)
    ).assessments[0]
    assert 0.0 <= assessment.confidence <= 1.0
    assert 0.0 <= assessment.impact <= 1.0


def test_result_rejects_missing_assessment():
    with pytest.raises(ValueError):
        RiskEvaluationResult(
            status="assessments_generated",
            situation=situation(),
            candidates=(candidate(),),
            assessments=(),
            rationale=("x",),
        )


def test_result_rejects_unknown_assessment_candidate():
    assessment = DeterministicRiskConfidenceEvaluator((profile(),)).evaluate(
        situation(), (candidate(),)
    ).assessments[0]
    with pytest.raises(ValueError):
        RiskEvaluationResult(
            status="assessments_generated",
            situation=situation(),
            candidates=(candidate(candidate_id="another"),),
            assessments=(assessment,),
            rationale=("x",),
        )


def test_default_profiles_cover_default_candidate_actions():
    actions = {item.action for item in default_risk_profiles()}
    assert actions == {
        "deliver_reminder",
        "do_nothing",
        "enable_power_saving",
        "enter_degraded_mode",
        "notify_user",
        "postpone_reminder",
        "restart_component",
        "verify_component_health",
    }


def test_default_profiles_have_stable_ids():
    assert all(
        item.profile_id == f"risk-profile-{item.action}"
        for item in default_risk_profiles()
    )


def test_evaluator_has_no_decision_or_execution_methods():
    evaluator = DeterministicRiskConfidenceEvaluator(default_risk_profiles())
    assert not hasattr(evaluator, "decide")
    assert not hasattr(evaluator, "authorize")
    assert not hasattr(evaluator, "execute")
