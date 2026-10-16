from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    ActionCandidate,
    AutonomyDecision,
    AutonomyGate,
    AutonomyGateResult,
    AutonomyLevel,
    DecisionDisposition,
    DecisionPolicy,
    DeterministicAutonomyGate,
    GateEvaluationStatus,
    Reversibility,
    RiskAssessment,
    RiskLevel,
)

NOW = datetime(2026, 7, 26, 19, 0, tzinfo=timezone.utc)


def candidate(
    *,
    action: str = "restart_component",
    reversible: Reversibility = Reversibility.FULL,
) -> ActionCandidate:
    return ActionCandidate(
        action=action,
        description="candidate",
        rationale=("generated",),
        reversible=reversible,
        candidate_id="candidate-1",
    )


def assessment(
    *,
    risk: RiskLevel = RiskLevel.LOW,
    confidence: float = 0.95,
    reversible: Reversibility = Reversibility.FULL,
) -> RiskAssessment:
    return RiskAssessment(
        candidate_id="candidate-1",
        risk=risk,
        confidence=confidence,
        impact=0.2,
        reversibility=reversible,
        reasons=("evaluated",),
    )


def decision(
    *,
    disposition: DecisionDisposition = DecisionDisposition.RECOMMEND,
    risk: RiskLevel = RiskLevel.LOW,
    confidence: float = 0.95,
    candidate_id: str | None = "candidate-1",
    level: AutonomyLevel = AutonomyLevel.RECOMMEND,
) -> AutonomyDecision:
    return AutonomyDecision(
        situation_id="situation-1",
        candidate_id=candidate_id,
        disposition=disposition,
        confidence=confidence,
        risk=risk,
        rationale=("policy_engine_complete",),
        decided_at=NOW,
        policy_level=level,
        decision_id="policy-decision-1",
    )


def gate() -> DeterministicAutonomyGate:
    return DeterministicAutonomyGate(clock=lambda: NOW)


def test_protocol_is_runtime_checkable() -> None:
    assert isinstance(gate(), AutonomyGate)


def test_default_simulation_remains_simulation() -> None:
    result = gate().evaluate(decision(), DecisionPolicy(), candidate(), assessment())
    assert result.gated_decision.disposition is DecisionDisposition.SIMULATE
    assert result.status is GateEvaluationStatus.PASSTHROUGH


def test_existing_simulation_is_preserved() -> None:
    policy_decision = decision(disposition=DecisionDisposition.SIMULATE)
    policy = DecisionPolicy(simulation_mode=False)
    result = gate().evaluate(policy_decision, policy, candidate(), assessment())
    assert result.gated_decision.disposition is DecisionDisposition.SIMULATE


def test_existing_block_is_preserved() -> None:
    policy_decision = decision(disposition=DecisionDisposition.BLOCK)
    result = gate().evaluate(
        policy_decision,
        DecisionPolicy(simulation_mode=False),
        candidate(),
        assessment(),
    )
    assert result.gated_decision.disposition is DecisionDisposition.BLOCK
    assert result.status is GateEvaluationStatus.PASSTHROUGH


def test_existing_observe_without_candidate_is_preserved() -> None:
    policy_decision = decision(
        disposition=DecisionDisposition.OBSERVE,
        confidence=0.0,
        candidate_id=None,
    )
    result = gate().evaluate(
        policy_decision,
        DecisionPolicy(simulation_mode=False),
        None,
        None,
    )
    assert result.gated_decision.disposition is DecisionDisposition.OBSERVE


def test_prohibited_policy_blocks() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.PROHIBITED,
        simulation_mode=False,
    )
    result = gate().evaluate(decision(), policy, candidate(), assessment())
    assert result.gated_decision.disposition is DecisionDisposition.BLOCK
    assert result.status is GateEvaluationStatus.BLOCKED


def test_observe_only_policy_observes() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.OBSERVE_ONLY,
        simulation_mode=False,
    )
    result = gate().evaluate(decision(), policy, candidate(), assessment())
    assert result.gated_decision.disposition is DecisionDisposition.OBSERVE


def test_recommend_policy_recommends() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.RECOMMEND,
        simulation_mode=False,
    )
    result = gate().evaluate(decision(), policy, candidate(), assessment())
    assert result.gated_decision.disposition is DecisionDisposition.RECOMMEND


def test_confirmation_policy_requests_confirmation() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.CONFIRM_BEFORE_ACTION,
        simulation_mode=False,
    )
    result = gate().evaluate(decision(), policy, candidate(), assessment())
    assert result.gated_decision.disposition is DecisionDisposition.REQUEST_CONFIRMATION


def test_low_risk_autonomous_policy_authorizes() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        simulation_mode=False,
    )
    result = gate().evaluate(decision(), policy, candidate(), assessment())
    assert result.gated_decision.disposition is DecisionDisposition.AUTHORIZE


def test_medium_risk_never_authorizes() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        simulation_mode=False,
        maximum_automatic_risk=RiskLevel.MEDIUM,
    )
    result = gate().evaluate(
        decision(risk=RiskLevel.MEDIUM),
        policy,
        candidate(),
        assessment(risk=RiskLevel.MEDIUM),
    )
    assert result.gated_decision.disposition is DecisionDisposition.REQUEST_CONFIRMATION
    assert "authorization_requires_low_risk" in result.rationale


def test_low_confidence_requests_confirmation() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        minimum_confidence=0.9,
        simulation_mode=False,
    )
    result = gate().evaluate(
        decision(confidence=0.7),
        policy,
        candidate(),
        assessment(confidence=0.7),
    )
    assert result.gated_decision.disposition is DecisionDisposition.REQUEST_CONFIRMATION


def test_partial_reversibility_requests_confirmation_by_default() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        simulation_mode=False,
    )
    result = gate().evaluate(
        decision(),
        policy,
        candidate(reversible=Reversibility.PARTIAL),
        assessment(reversible=Reversibility.PARTIAL),
    )
    assert result.gated_decision.disposition is DecisionDisposition.REQUEST_CONFIRMATION


def test_partial_reversibility_can_be_authorized_when_policy_allows() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        require_reversible_automatic_actions=False,
        simulation_mode=False,
    )
    result = gate().evaluate(
        decision(),
        policy,
        candidate(reversible=Reversibility.PARTIAL),
        assessment(reversible=Reversibility.PARTIAL),
    )
    assert result.gated_decision.disposition is DecisionDisposition.AUTHORIZE


def test_prohibited_action_is_blocked() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        simulation_mode=False,
        prohibited_actions=("restart_component",),
    )
    result = gate().evaluate(decision(), policy, candidate(), assessment())
    assert result.gated_decision.disposition is DecisionDisposition.BLOCK


def test_prohibited_risk_is_blocked() -> None:
    policy = DecisionPolicy(
        autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        simulation_mode=False,
    )
    blocked = decision(
        disposition=DecisionDisposition.BLOCK,
        risk=RiskLevel.PROHIBITED,
    )
    result = gate().evaluate(
        blocked,
        policy,
        candidate(),
        assessment(risk=RiskLevel.PROHIBITED),
    )
    assert result.gated_decision.disposition is DecisionDisposition.BLOCK


def test_candidate_must_match_decision() -> None:
    other = replace(candidate(), candidate_id="other")
    with pytest.raises(ValueError, match="candidate must match"):
        gate().evaluate(decision(), DecisionPolicy(), other, assessment())


def test_assessment_must_match_candidate() -> None:
    other = replace(assessment(), candidate_id="other")
    with pytest.raises(ValueError, match="assessment must match"):
        gate().evaluate(decision(), DecisionPolicy(), candidate(), other)


def test_confidence_must_match_policy_decision() -> None:
    with pytest.raises(ValueError, match="confidence"):
        gate().evaluate(
            decision(),
            DecisionPolicy(),
            candidate(),
            assessment(confidence=0.8),
        )


def test_risk_must_match_policy_decision() -> None:
    with pytest.raises(ValueError, match="risk"):
        gate().evaluate(
            decision(),
            DecisionPolicy(),
            candidate(),
            assessment(risk=RiskLevel.MEDIUM),
        )


def test_selected_decision_requires_candidate_and_assessment() -> None:
    with pytest.raises(ValueError, match="requires candidate and assessment"):
        gate().evaluate(decision(), DecisionPolicy(), None, None)


def test_unselected_decision_rejects_candidate_data() -> None:
    observe = decision(
        disposition=DecisionDisposition.OBSERVE,
        confidence=0.0,
        candidate_id=None,
    )
    with pytest.raises(ValueError, match="requires a selected"):
        gate().evaluate(observe, DecisionPolicy(), candidate(), assessment())


def test_result_requires_timezone_aware_timestamp() -> None:
    result = gate().evaluate(decision(), DecisionPolicy(), candidate(), assessment())
    with pytest.raises(ValueError, match="timezone"):
        replace(result, evaluated_at=NOW.replace(tzinfo=None))


def test_result_requires_rationale() -> None:
    result = gate().evaluate(decision(), DecisionPolicy(), candidate(), assessment())
    with pytest.raises(ValueError, match="rationale"):
        replace(result, rationale=())


def test_result_preserves_situation_and_candidate() -> None:
    result = gate().evaluate(decision(), DecisionPolicy(), candidate(), assessment())
    assert result.gated_decision.situation_id == "situation-1"
    assert result.gated_decision.candidate_id == "candidate-1"


def test_gate_appends_audit_rationale() -> None:
    result = gate().evaluate(decision(), DecisionPolicy(), candidate(), assessment())
    assert "autonomy_gate_applied" in result.gated_decision.rationale


def test_gate_has_no_execution_method() -> None:
    instance = gate()
    assert not hasattr(instance, "execute")
    assert not hasattr(instance, "run_action")


def test_gate_result_is_frozen() -> None:
    result = gate().evaluate(decision(), DecisionPolicy(), candidate(), assessment())
    with pytest.raises(Exception):
        result.status = GateEvaluationStatus.BLOCKED  # type: ignore[misc]


def test_result_contract_rejects_mismatched_candidate() -> None:
    result = gate().evaluate(decision(), DecisionPolicy(), candidate(), assessment())
    with pytest.raises(ValueError, match="candidate must match"):
        AutonomyGateResult(
            status=result.status,
            policy_decision=result.policy_decision,
            gated_decision=result.gated_decision,
            policy=result.policy,
            candidate=replace(candidate(), candidate_id="other"),
            assessment=result.assessment,
            rationale=result.rationale,
            evaluated_at=result.evaluated_at,
        )
