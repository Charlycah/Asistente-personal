from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from core.controlled_autonomy import (
    ActionCandidate,
    AutonomyDecision,
    AutonomyLevel,
    DecisionDisposition,
    DecisionOutcome,
    DecisionPolicy,
    DeterministicOutcomeSupervisor,
    OutcomeDirective,
    OutcomeStatus,
    OutcomeSupervisionResult,
    OutcomeSupervisionStatus,
    OutcomeSupervisor,
    Reversibility,
    RiskLevel,
)

NOW = datetime(2026, 7, 26, 20, 0, tzinfo=timezone.utc)


def candidate(
    *,
    reversible: Reversibility = Reversibility.FULL,
    candidate_id: str = "candidate-1",
) -> ActionCandidate:
    return ActionCandidate(
        action="restart_component",
        description="restart the unhealthy component",
        rationale=("generated",),
        reversible=reversible,
        candidate_id=candidate_id,
    )


def decision(
    *,
    disposition: DecisionDisposition = DecisionDisposition.AUTHORIZE,
    candidate_id: str | None = "candidate-1",
    decision_id: str = "decision-1",
) -> AutonomyDecision:
    return AutonomyDecision(
        situation_id="situation-1",
        candidate_id=candidate_id,
        disposition=disposition,
        confidence=0.95,
        risk=RiskLevel.LOW,
        rationale=("gate_complete",),
        decided_at=NOW,
        policy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        decision_id=decision_id,
    )


def outcome(
    status: OutcomeStatus,
    *,
    decision_id: str = "decision-1",
) -> DecisionOutcome:
    return DecisionOutcome(
        decision_id=decision_id,
        status=status,
        observed_at=NOW + timedelta(seconds=1),
        summary=f"outcome: {status.value}",
        evidence=("runtime_observation",),
        outcome_id=f"outcome-{status.value}",
    )


def supervisor() -> DeterministicOutcomeSupervisor:
    return DeterministicOutcomeSupervisor(clock=lambda: NOW)


def test_protocol_is_runtime_checkable() -> None:
    assert isinstance(supervisor(), OutcomeSupervisor)


def test_success_completes_without_notification() -> None:
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.SUCCEEDED),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=1,
    )
    assert result.status is OutcomeSupervisionStatus.COMPLETED
    assert result.directive is OutcomeDirective.COMPLETE
    assert result.notify_user is False


def test_failure_retries_when_budget_is_available() -> None:
    policy = DecisionPolicy(simulation_mode=False, maximum_attempts=2)
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.FAILED),
        policy,
        candidate(),
        attempts_used=1,
    )
    assert result.directive is OutcomeDirective.RETRY
    assert result.status is OutcomeSupervisionStatus.FOLLOW_UP_REQUIRED
    assert result.notify_user is False


def test_failure_does_not_retry_after_budget_is_exhausted() -> None:
    policy = DecisionPolicy(simulation_mode=False, maximum_attempts=2)
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.FAILED),
        policy,
        candidate(),
        attempts_used=2,
    )
    assert result.directive is OutcomeDirective.REVERT


def test_failure_reverts_a_reversible_candidate() -> None:
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.FAILED),
        DecisionPolicy(simulation_mode=False),
        candidate(reversible=Reversibility.PARTIAL),
        attempts_used=1,
    )
    assert result.directive is OutcomeDirective.REVERT
    assert result.notify_user is True


def test_failure_degrades_when_candidate_is_irreversible() -> None:
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.FAILED),
        DecisionPolicy(simulation_mode=False),
        candidate(reversible=Reversibility.NONE),
        attempts_used=1,
    )
    assert result.directive is OutcomeDirective.DEGRADE
    assert result.notify_user is True


def test_reverted_outcome_completes_and_notifies() -> None:
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.REVERTED),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=1,
    )
    assert result.directive is OutcomeDirective.COMPLETE
    assert result.notify_user is True


def test_degraded_outcome_requires_human_attention() -> None:
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.DEGRADED),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=1,
    )
    assert result.directive is OutcomeDirective.DEGRADE
    assert result.status is OutcomeSupervisionStatus.HUMAN_ATTENTION_REQUIRED
    assert result.notify_user is True


def test_unknown_outcome_requires_notification() -> None:
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.UNKNOWN),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=1,
    )
    assert result.directive is OutcomeDirective.NONE
    assert result.notify_user is True


def test_not_executed_authorization_requires_attention() -> None:
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.NOT_EXECUTED),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=0,
    )
    assert result.status is OutcomeSupervisionStatus.HUMAN_ATTENTION_REQUIRED
    assert result.directive is OutcomeDirective.NONE
    assert result.notify_user is True


@pytest.mark.parametrize(
    "disposition",
    [
        DecisionDisposition.OBSERVE,
        DecisionDisposition.RECOMMEND,
        DecisionDisposition.REQUEST_CONFIRMATION,
        DecisionDisposition.SIMULATE,
        DecisionDisposition.BLOCK,
    ],
)
def test_non_authorized_decisions_are_not_applicable(
    disposition: DecisionDisposition,
) -> None:
    selected = disposition in {
        DecisionDisposition.RECOMMEND,
        DecisionDisposition.REQUEST_CONFIRMATION,
        DecisionDisposition.SIMULATE,
    }
    current_decision = decision(
        disposition=disposition,
        candidate_id="candidate-1" if selected else None,
    )
    result = supervisor().supervise(
        current_decision,
        outcome(OutcomeStatus.NOT_EXECUTED),
        DecisionPolicy(simulation_mode=False),
        candidate() if selected else None,
        attempts_used=0,
    )
    assert result.status is OutcomeSupervisionStatus.NOT_APPLICABLE
    assert result.directive is OutcomeDirective.NONE
    assert result.notify_user is False


def test_result_preserves_all_input_contracts() -> None:
    current_decision = decision()
    current_outcome = outcome(OutcomeStatus.SUCCEEDED)
    current_candidate = candidate()
    policy = DecisionPolicy(simulation_mode=False)
    result = supervisor().supervise(
        current_decision,
        current_outcome,
        policy,
        current_candidate,
        attempts_used=1,
    )
    assert result.decision is current_decision
    assert result.outcome is current_outcome
    assert result.candidate is current_candidate
    assert result.attempts_used == 1


def test_result_timestamp_comes_from_injected_clock() -> None:
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.SUCCEEDED),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=1,
    )
    assert result.supervised_at == NOW


def test_result_rationale_is_auditable() -> None:
    policy = DecisionPolicy(simulation_mode=False, maximum_attempts=3)
    result = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.FAILED),
        policy,
        candidate(),
        attempts_used=1,
    )
    assert "authorized_action_failed" in result.rationale
    assert "retry_budget_available" in result.rationale
    assert "attempts_used=1" in result.rationale
    assert "maximum_attempts=3" in result.rationale


def test_negative_attempts_are_rejected() -> None:
    with pytest.raises(ValueError, match="attempts used"):
        supervisor().supervise(
            decision(),
            outcome(OutcomeStatus.SUCCEEDED),
            DecisionPolicy(simulation_mode=False),
            candidate(),
            attempts_used=-1,
        )


def test_outcome_must_reference_decision() -> None:
    with pytest.raises(ValueError, match="reference"):
        supervisor().supervise(
            decision(),
            outcome(OutcomeStatus.SUCCEEDED, decision_id="other"),
            DecisionPolicy(simulation_mode=False),
            candidate(),
            attempts_used=1,
        )


def test_selected_decision_requires_candidate() -> None:
    with pytest.raises(ValueError, match="requires its candidate"):
        supervisor().supervise(
            decision(),
            outcome(OutcomeStatus.SUCCEEDED),
            DecisionPolicy(simulation_mode=False),
            None,
            attempts_used=1,
        )


def test_candidate_must_match_decision() -> None:
    with pytest.raises(ValueError, match="must match"):
        supervisor().supervise(
            decision(),
            outcome(OutcomeStatus.SUCCEEDED),
            DecisionPolicy(simulation_mode=False),
            candidate(candidate_id="other"),
            attempts_used=1,
        )


def test_unselected_decision_rejects_candidate() -> None:
    current_decision = decision(
        disposition=DecisionDisposition.OBSERVE,
        candidate_id=None,
    )
    with pytest.raises(ValueError, match="candidate requires"):
        supervisor().supervise(
            current_decision,
            outcome(OutcomeStatus.NOT_EXECUTED),
            DecisionPolicy(simulation_mode=False),
            candidate(),
            attempts_used=0,
        )


def test_result_rejects_naive_timestamp() -> None:
    valid = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.SUCCEEDED),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=1,
    )
    with pytest.raises(ValueError, match="timezone"):
        replace(valid, supervised_at=datetime(2026, 7, 26, 20, 0))


def test_result_rejects_blank_rationale() -> None:
    valid = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.SUCCEEDED),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=1,
    )
    with pytest.raises(ValueError, match="rationale"):
        replace(valid, rationale=("",))


def test_result_rejects_blank_supervisor_id() -> None:
    valid = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.SUCCEEDED),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=1,
    )
    with pytest.raises(ValueError, match="supervisor id"):
        replace(valid, supervisor_id=" ")


def test_result_rejects_retry_without_an_attempt() -> None:
    valid = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.FAILED),
        DecisionPolicy(simulation_mode=False, maximum_attempts=2),
        candidate(),
        attempts_used=1,
    )
    with pytest.raises(ValueError, match="at least one attempt"):
        replace(valid, attempts_used=0)


def test_result_rejects_revert_for_irreversible_candidate() -> None:
    valid = supervisor().supervise(
        decision(),
        outcome(OutcomeStatus.FAILED),
        DecisionPolicy(simulation_mode=False),
        candidate(),
        attempts_used=1,
    )
    with pytest.raises(ValueError, match="cannot be reverted"):
        replace(
            valid,
            candidate=candidate(reversible=Reversibility.NONE),
        )


def test_public_result_contract_can_be_constructed() -> None:
    result = OutcomeSupervisionResult(
        status=OutcomeSupervisionStatus.COMPLETED,
        directive=OutcomeDirective.COMPLETE,
        decision=decision(),
        outcome=outcome(OutcomeStatus.SUCCEEDED),
        candidate=candidate(),
        attempts_used=1,
        notify_user=False,
        rationale=("completed",),
        supervised_at=NOW,
    )
    assert result.directive is OutcomeDirective.COMPLETE


def test_supervisor_has_no_execution_methods() -> None:
    current = supervisor()
    assert not hasattr(current, "execute")
    assert not hasattr(current, "run_action")
    assert not hasattr(current, "retry")
    assert not hasattr(current, "revert")
    assert not hasattr(current, "notify")
