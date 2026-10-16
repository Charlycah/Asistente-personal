from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    ActionCandidate,
    AutonomyLevel,
    CandidatePolicyScore,
    DecisionDisposition,
    DecisionPolicy,
    DecisionPolicyEngine,
    DecisionSituation,
    DeterministicDecisionPolicyEngine,
    PolicyEvaluationStatus,
    Reversibility,
    RiskAssessment,
    RiskLevel,
)

NOW = datetime(2026, 7, 26, 18, 0, tzinfo=timezone.utc)


def situation() -> DecisionSituation:
    return DecisionSituation(
        kind="runtime_component_unhealthy",
        description="Vosk is unhealthy",
        evidence=("component_id=vosk",),
        observed_at=NOW,
        source="component_health.vosk",
        urgency=0.8,
        situation_id="situation-1",
    )


def candidate(
    candidate_id: str,
    action: str,
    *,
    cost: float = 0.1,
    reversible: Reversibility = Reversibility.FULL,
) -> ActionCandidate:
    return ActionCandidate(
        action=action,
        description=action.replace("_", " "),
        rationale=("generated_for_test",),
        reversible=reversible,
        estimated_cost=cost,
        candidate_id=candidate_id,
    )


def assessment(
    candidate_id: str,
    *,
    risk: RiskLevel = RiskLevel.LOW,
    confidence: float = 0.9,
    impact: float = 0.2,
    reversibility: Reversibility = Reversibility.FULL,
) -> RiskAssessment:
    return RiskAssessment(
        candidate_id=candidate_id,
        risk=risk,
        confidence=confidence,
        impact=impact,
        reversibility=reversibility,
        reasons=("profile=test",),
    )


def engine() -> DeterministicDecisionPolicyEngine:
    return DeterministicDecisionPolicyEngine(clock=lambda: NOW)


def test_protocol_is_runtime_checkable() -> None:
    assert isinstance(engine(), DecisionPolicyEngine)


def test_score_contract_validates_candidate_id() -> None:
    with pytest.raises(ValueError, match="candidate id"):
        CandidatePolicyScore("", True, 0.5, ("reason",))


def test_score_contract_validates_score_bounds() -> None:
    with pytest.raises(ValueError, match="between"):
        CandidatePolicyScore("c1", True, 1.1, ("reason",))


def test_score_contract_requires_reasons() -> None:
    with pytest.raises(ValueError, match="reasons"):
        CandidatePolicyScore("c1", True, 0.5, ())


def test_no_candidates_produces_observe_decision() -> None:
    result = engine().decide(situation(), (), (), DecisionPolicy())
    assert result.status is PolicyEvaluationStatus.NO_CANDIDATES
    assert result.decision.disposition is DecisionDisposition.OBSERVE
    assert result.decision.candidate_id is None


def test_no_candidates_uses_zero_confidence_and_low_risk() -> None:
    result = engine().decide(situation(), (), (), DecisionPolicy())
    assert result.decision.confidence == 0.0
    assert result.decision.risk is RiskLevel.LOW


def test_default_simulation_policy_produces_simulate() -> None:
    candidates = (candidate("c1", "notify_user"),)
    assessments = (assessment("c1"),)
    result = engine().decide(situation(), candidates, assessments, DecisionPolicy())
    assert result.decision.disposition is DecisionDisposition.SIMULATE


def test_non_simulation_recommend_policy_produces_recommendation() -> None:
    policy = DecisionPolicy(simulation_mode=False)
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        policy,
    )
    assert result.decision.disposition is DecisionDisposition.RECOMMEND


def test_observe_only_policy_produces_observe() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.OBSERVE_ONLY,
        simulation_mode=False,
    )
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        policy,
    )
    assert result.decision.disposition is DecisionDisposition.OBSERVE


def test_engine_never_authorizes() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        simulation_mode=False,
    )
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        policy,
    )
    assert result.decision.disposition is DecisionDisposition.RECOMMEND


def test_engine_never_requests_confirmation() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.CONFIRM_BEFORE_ACTION,
        simulation_mode=False,
    )
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        policy,
    )
    assert result.decision.disposition is DecisionDisposition.RECOMMEND


def test_highest_score_is_selected() -> None:
    candidates = (
        candidate("c1", "restart_component", cost=0.6),
        candidate("c2", "notify_user", cost=0.0),
    )
    assessments = (
        assessment("c1", risk=RiskLevel.MEDIUM, confidence=0.8, impact=0.6),
        assessment("c2", confidence=0.95, impact=0.1),
    )
    result = engine().decide(situation(), candidates, assessments, DecisionPolicy())
    assert result.decision.candidate_id == "c2"


def test_ties_preserve_original_candidate_order() -> None:
    candidates = (
        candidate("c1", "notify_user"),
        candidate("c2", "deliver_reminder"),
    )
    assessments = (assessment("c1"), assessment("c2"))
    result = engine().decide(situation(), candidates, assessments, DecisionPolicy())
    assert result.decision.candidate_id == "c1"


def test_low_confidence_candidate_is_ineligible() -> None:
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1", confidence=0.5),),
        DecisionPolicy(minimum_confidence=0.8),
    )
    assert result.scores[0].eligible is False
    assert result.decision.disposition is DecisionDisposition.BLOCK


def test_prohibited_action_is_ineligible() -> None:
    result = engine().decide(
        situation(),
        (candidate("c1", "restart_component"),),
        (assessment("c1"),),
        DecisionPolicy(prohibited_actions=("restart_component",)),
    )
    assert "action_prohibited_by_policy" in result.scores[0].reasons
    assert result.decision.disposition is DecisionDisposition.BLOCK


def test_prohibited_risk_is_ineligible_and_blocked() -> None:
    result = engine().decide(
        situation(),
        (candidate("c1", "dangerous_action"),),
        (assessment("c1", risk=RiskLevel.PROHIBITED),),
        DecisionPolicy(),
    )
    assert result.scores[0].eligible is False
    assert result.decision.risk is RiskLevel.PROHIBITED
    assert result.decision.disposition is DecisionDisposition.BLOCK


def test_prohibited_policy_level_blocks_every_candidate() -> None:
    policy = DecisionPolicy(autonomy_level=AutonomyLevel.PROHIBITED)
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        policy,
    )
    assert result.decision.disposition is DecisionDisposition.BLOCK


def test_policy_scores_are_bounded() -> None:
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user", cost=100.0),),
        (assessment("c1", risk=RiskLevel.HIGH, confidence=0.0, impact=1.0),),
        DecisionPolicy(minimum_confidence=0.0),
    )
    assert result.scores[0].score == 0.0


def test_full_reversibility_scores_better_than_none() -> None:
    candidates = (
        candidate("c1", "a", reversible=Reversibility.FULL),
        candidate("c2", "b", reversible=Reversibility.NONE),
    )
    assessments = (
        assessment("c1", reversibility=Reversibility.FULL),
        assessment("c2", reversibility=Reversibility.NONE),
    )
    result = engine().decide(situation(), candidates, assessments, DecisionPolicy())
    assert result.scores[0].score > result.scores[1].score


def test_lower_cost_scores_better() -> None:
    candidates = (
        candidate("c1", "a", cost=0.0),
        candidate("c2", "b", cost=1.0),
    )
    assessments = (assessment("c1"), assessment("c2"))
    result = engine().decide(situation(), candidates, assessments, DecisionPolicy())
    assert result.scores[0].score > result.scores[1].score


def test_lower_risk_scores_better() -> None:
    candidates = (candidate("c1", "a"), candidate("c2", "b"))
    assessments = (
        assessment("c1", risk=RiskLevel.LOW),
        assessment("c2", risk=RiskLevel.HIGH),
    )
    result = engine().decide(situation(), candidates, assessments, DecisionPolicy())
    assert result.scores[0].score > result.scores[1].score


def test_decision_uses_injected_aware_clock() -> None:
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        DecisionPolicy(),
    )
    assert result.decision.decided_at is NOW


def test_result_rejects_authorize_disposition() -> None:
    base = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        DecisionPolicy(),
    )
    invalid = replace(
        base.decision,
        disposition=DecisionDisposition.AUTHORIZE,
        policy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
    )
    with pytest.raises(ValueError, match="autonomy gating"):
        replace(base, decision=invalid)


def test_result_rejects_request_confirmation_disposition() -> None:
    base = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        DecisionPolicy(),
    )
    invalid = replace(
        base.decision,
        disposition=DecisionDisposition.REQUEST_CONFIRMATION,
    )
    with pytest.raises(ValueError, match="autonomy gating"):
        replace(base, decision=invalid)


def test_result_requires_assessment_for_every_candidate() -> None:
    base = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        DecisionPolicy(),
    )
    with pytest.raises(ValueError, match="assessment"):
        replace(base, assessments=())


def test_result_requires_score_for_every_candidate() -> None:
    base = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        DecisionPolicy(),
    )
    with pytest.raises(ValueError, match="score"):
        replace(base, scores=())


def test_engine_rejects_missing_assessment() -> None:
    with pytest.raises(ValueError, match="assessment"):
        engine().decide(
            situation(),
            (candidate("c1", "notify_user"),),
            (),
            DecisionPolicy(),
        )


def test_engine_rejects_unknown_assessment_candidate() -> None:
    with pytest.raises(ValueError, match="assessment"):
        engine().decide(
            situation(),
            (candidate("c1", "notify_user"),),
            (assessment("other"),),
            DecisionPolicy(),
        )


def test_engine_rejects_duplicate_candidate_ids() -> None:
    candidates = (
        candidate("c1", "notify_user"),
        candidate("c1", "do_nothing"),
    )
    with pytest.raises(ValueError, match="unique"):
        engine().decide(
            situation(),
            candidates,
            (assessment("c1"), assessment("c2")),
            DecisionPolicy(),
        )


def test_engine_rejects_duplicate_assessments() -> None:
    with pytest.raises(ValueError, match="unique"):
        engine().decide(
            situation(),
            (candidate("c1", "notify_user"), candidate("c2", "do_nothing")),
            (assessment("c1"), assessment("c1")),
            DecisionPolicy(),
        )


def test_decision_rationale_contains_selected_score() -> None:
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        DecisionPolicy(),
    )
    assert any(item.startswith("selected_score=") for item in result.decision.rationale)


def test_result_records_candidate_count() -> None:
    result = engine().decide(
        situation(),
        (candidate("c1", "notify_user"),),
        (assessment("c1"),),
        DecisionPolicy(),
    )
    assert "candidate_count=1" in result.rationale


def test_engine_has_no_execute_or_authorize_methods() -> None:
    instance = engine()
    assert not hasattr(instance, "execute")
    assert not hasattr(instance, "authorize")
    assert not hasattr(instance, "request_confirmation")
