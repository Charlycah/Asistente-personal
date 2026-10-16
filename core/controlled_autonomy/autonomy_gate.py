from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Protocol, runtime_checkable

from .contracts import (
    ActionCandidate,
    AutonomyDecision,
    AutonomyLevel,
    DecisionDisposition,
    DecisionPolicy,
    Reversibility,
    RiskAssessment,
    RiskLevel,
)


class GateEvaluationStatus(str, Enum):
    """Outcome category produced by the autonomy gate."""

    PASSTHROUGH = "passthrough"
    GATED = "gated"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class AutonomyGateResult:
    """Auditable result of applying authority limits to a policy decision."""

    status: GateEvaluationStatus | str
    policy_decision: AutonomyDecision
    gated_decision: AutonomyDecision
    policy: DecisionPolicy
    candidate: ActionCandidate | None
    assessment: RiskAssessment | None
    rationale: tuple[str, ...]
    evaluated_at: datetime
    gate_id: str = field(default="deterministic-autonomy-gate")

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", GateEvaluationStatus(self.status))
        _require_text(self.gate_id, "gate id")
        _require_items(self.rationale, "gate rationale")
        _require_aware(self.evaluated_at, "gate timestamp")
        if self.gated_decision.situation_id != self.policy_decision.situation_id:
            raise ValueError("gated decision must reference the same situation")
        if self.gated_decision.candidate_id != self.policy_decision.candidate_id:
            raise ValueError("gated decision must preserve the selected candidate")
        if self.candidate is None:
            if self.policy_decision.candidate_id is not None:
                raise ValueError("selected decision requires its candidate")
            if self.assessment is not None:
                raise ValueError("assessment requires a candidate")
        else:
            if self.candidate.candidate_id != self.policy_decision.candidate_id:
                raise ValueError("candidate must match the policy decision")
            if self.assessment is None:
                raise ValueError("selected candidate requires its assessment")
            if self.assessment.candidate_id != self.candidate.candidate_id:
                raise ValueError("assessment must match the selected candidate")


@runtime_checkable
class AutonomyGate(Protocol):
    """Converts a policy recommendation into governed execution authority."""

    def evaluate(
        self,
        policy_decision: AutonomyDecision,
        policy: DecisionPolicy,
        candidate: ActionCandidate | None,
        assessment: RiskAssessment | None,
    ) -> AutonomyGateResult: ...


class DeterministicAutonomyGate:
    """Pure, deterministic authority gate with no execution capability."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def evaluate(
        self,
        policy_decision: AutonomyDecision,
        policy: DecisionPolicy,
        candidate: ActionCandidate | None,
        assessment: RiskAssessment | None,
    ) -> AutonomyGateResult:
        _validate_inputs(policy_decision, candidate, assessment)
        disposition, status, rationale = _gate_disposition(
            policy_decision,
            policy,
            candidate,
            assessment,
        )
        gated_decision = AutonomyDecision(
            situation_id=policy_decision.situation_id,
            candidate_id=policy_decision.candidate_id,
            disposition=disposition,
            confidence=policy_decision.confidence,
            risk=policy_decision.risk,
            rationale=(
                *policy_decision.rationale,
                "autonomy_gate_applied",
                *rationale,
            ),
            decided_at=self._clock(),
            policy_level=policy.autonomy_level,
        )
        return AutonomyGateResult(
            status=status,
            policy_decision=policy_decision,
            gated_decision=gated_decision,
            policy=policy,
            candidate=candidate,
            assessment=assessment,
            rationale=rationale,
            evaluated_at=self._clock(),
        )


def _gate_disposition(
    decision: AutonomyDecision,
    policy: DecisionPolicy,
    candidate: ActionCandidate | None,
    assessment: RiskAssessment | None,
) -> tuple[DecisionDisposition, GateEvaluationStatus, tuple[str, ...]]:
    if decision.disposition is DecisionDisposition.BLOCK:
        return (
            DecisionDisposition.BLOCK,
            GateEvaluationStatus.PASSTHROUGH,
            ("policy_decision_already_blocked",),
        )
    if decision.disposition is DecisionDisposition.OBSERVE:
        return (
            DecisionDisposition.OBSERVE,
            GateEvaluationStatus.PASSTHROUGH,
            ("policy_decision_observe_only",),
        )
    if policy.simulation_mode or decision.disposition is DecisionDisposition.SIMULATE:
        return (
            DecisionDisposition.SIMULATE,
            GateEvaluationStatus.PASSTHROUGH,
            ("simulation_mode_active",),
        )
    if policy.autonomy_level is AutonomyLevel.PROHIBITED:
        return (
            DecisionDisposition.BLOCK,
            GateEvaluationStatus.BLOCKED,
            ("policy_level_prohibited",),
        )
    if candidate is None or assessment is None:
        return (
            DecisionDisposition.OBSERVE,
            GateEvaluationStatus.PASSTHROUGH,
            ("no_selected_candidate",),
        )
    if candidate.action in policy.prohibited_actions:
        return (
            DecisionDisposition.BLOCK,
            GateEvaluationStatus.BLOCKED,
            ("action_prohibited_by_policy",),
        )
    if assessment.risk is RiskLevel.PROHIBITED:
        return (
            DecisionDisposition.BLOCK,
            GateEvaluationStatus.BLOCKED,
            ("assessment_risk_prohibited",),
        )
    if policy.autonomy_level is AutonomyLevel.OBSERVE_ONLY:
        return (
            DecisionDisposition.OBSERVE,
            GateEvaluationStatus.GATED,
            ("authority_limited_to_observation",),
        )
    if policy.autonomy_level is AutonomyLevel.RECOMMEND:
        return (
            DecisionDisposition.RECOMMEND,
            GateEvaluationStatus.GATED,
            ("authority_limited_to_recommendation",),
        )
    if policy.autonomy_level is AutonomyLevel.CONFIRM_BEFORE_ACTION:
        return (
            DecisionDisposition.REQUEST_CONFIRMATION,
            GateEvaluationStatus.GATED,
            ("human_confirmation_required",),
        )
    automatic_reasons = _automatic_blocking_reasons(policy, candidate, assessment)
    if not automatic_reasons:
        return (
            DecisionDisposition.AUTHORIZE,
            GateEvaluationStatus.GATED,
            ("low_risk_autonomous_authority_granted",),
        )
    return (
        DecisionDisposition.REQUEST_CONFIRMATION,
        GateEvaluationStatus.GATED,
        ("automatic_authority_not_granted", *automatic_reasons),
    )


def _automatic_blocking_reasons(
    policy: DecisionPolicy,
    candidate: ActionCandidate,
    assessment: RiskAssessment,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if assessment.confidence < policy.minimum_confidence:
        reasons.append("confidence_below_policy_minimum")
    if _risk_rank(assessment.risk) > _risk_rank(policy.maximum_automatic_risk):
        reasons.append("risk_exceeds_automatic_limit")
    if assessment.risk is not RiskLevel.LOW:
        reasons.append("authorization_requires_low_risk")
    if (
        policy.require_reversible_automatic_actions
        and candidate.reversible is not Reversibility.FULL
    ):
        reasons.append("automatic_action_requires_full_reversibility")
    if assessment.reversibility is not candidate.reversible:
        reasons.append("candidate_assessment_reversibility_mismatch")
    return tuple(reasons)


def _validate_inputs(
    decision: AutonomyDecision,
    candidate: ActionCandidate | None,
    assessment: RiskAssessment | None,
) -> None:
    if decision.candidate_id is None:
        if candidate is not None or assessment is not None:
            raise ValueError("candidate data requires a selected decision candidate")
        return
    if candidate is None or assessment is None:
        raise ValueError("selected decision requires candidate and assessment")
    if candidate.candidate_id != decision.candidate_id:
        raise ValueError("candidate must match the selected decision")
    if assessment.candidate_id != candidate.candidate_id:
        raise ValueError("assessment must match the selected candidate")
    if assessment.confidence != decision.confidence:
        raise ValueError("assessment confidence must match the policy decision")
    if assessment.risk is not decision.risk:
        raise ValueError("assessment risk must match the policy decision")


def _risk_rank(value: RiskLevel) -> int:
    return {
        RiskLevel.LOW: 0,
        RiskLevel.MEDIUM: 1,
        RiskLevel.HIGH: 2,
        RiskLevel.PROHIBITED: 3,
    }[value]


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be blank")


def _require_items(values: tuple[str, ...], label: str) -> None:
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must contain non-blank items")


def _require_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must include timezone information")
