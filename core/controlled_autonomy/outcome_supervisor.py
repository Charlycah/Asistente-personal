from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Protocol, runtime_checkable

from .contracts import (
    ActionCandidate,
    AutonomyDecision,
    DecisionDisposition,
    DecisionOutcome,
    DecisionPolicy,
    OutcomeStatus,
    Reversibility,
)


class OutcomeDirective(str, Enum):
    """Next governed response after observing an action outcome."""

    NONE = "none"
    COMPLETE = "complete"
    RETRY = "retry"
    REVERT = "revert"
    DEGRADE = "degrade"


class OutcomeSupervisionStatus(str, Enum):
    """Classification produced by the outcome supervisor."""

    NOT_APPLICABLE = "not_applicable"
    COMPLETED = "completed"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    HUMAN_ATTENTION_REQUIRED = "human_attention_required"


@dataclass(frozen=True)
class OutcomeSupervisionResult:
    """Auditable follow-up directive; this contract never performs it."""

    status: OutcomeSupervisionStatus | str
    directive: OutcomeDirective | str
    decision: AutonomyDecision
    outcome: DecisionOutcome
    candidate: ActionCandidate | None
    attempts_used: int
    notify_user: bool
    rationale: tuple[str, ...]
    supervised_at: datetime
    supervisor_id: str = field(default="deterministic-outcome-supervisor")

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OutcomeSupervisionStatus(self.status))
        object.__setattr__(self, "directive", OutcomeDirective(self.directive))
        _require_text(self.supervisor_id, "supervisor id")
        _require_items(self.rationale, "supervision rationale")
        _require_aware(self.supervised_at, "supervision timestamp")
        if self.attempts_used < 0:
            raise ValueError("attempts used must not be negative")
        if self.outcome.decision_id != self.decision.decision_id:
            raise ValueError("outcome must reference the supervised decision")
        if self.decision.candidate_id is None:
            if self.candidate is not None:
                raise ValueError("candidate requires a selected decision candidate")
        elif self.candidate is None:
            raise ValueError("selected decision requires its candidate")
        elif self.candidate.candidate_id != self.decision.candidate_id:
            raise ValueError("candidate must match the supervised decision")
        if self.directive is OutcomeDirective.RETRY and self.attempts_used <= 0:
            raise ValueError("retry supervision requires at least one attempt")
        if self.directive is OutcomeDirective.REVERT:
            if self.candidate is None:
                raise ValueError("revert supervision requires a candidate")
            if self.candidate.reversible is Reversibility.NONE:
                raise ValueError("irreversible candidates cannot be reverted")


@runtime_checkable
class OutcomeSupervisor(Protocol):
    """Evaluates observed results without executing recovery actions."""

    def supervise(
        self,
        decision: AutonomyDecision,
        outcome: DecisionOutcome,
        policy: DecisionPolicy,
        candidate: ActionCandidate | None,
        *,
        attempts_used: int,
    ) -> OutcomeSupervisionResult: ...


class DeterministicOutcomeSupervisor:
    """Pure supervisor that derives one deterministic follow-up directive."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def supervise(
        self,
        decision: AutonomyDecision,
        outcome: DecisionOutcome,
        policy: DecisionPolicy,
        candidate: ActionCandidate | None,
        *,
        attempts_used: int,
    ) -> OutcomeSupervisionResult:
        _validate_inputs(decision, outcome, candidate, attempts_used)
        status, directive, notify_user, rationale = _supervision_directive(
            decision,
            outcome,
            policy,
            candidate,
            attempts_used,
        )
        return OutcomeSupervisionResult(
            status=status,
            directive=directive,
            decision=decision,
            outcome=outcome,
            candidate=candidate,
            attempts_used=attempts_used,
            notify_user=notify_user,
            rationale=rationale,
            supervised_at=self._clock(),
        )


def _supervision_directive(
    decision: AutonomyDecision,
    outcome: DecisionOutcome,
    policy: DecisionPolicy,
    candidate: ActionCandidate | None,
    attempts_used: int,
) -> tuple[
    OutcomeSupervisionStatus,
    OutcomeDirective,
    bool,
    tuple[str, ...],
]:
    if decision.disposition is not DecisionDisposition.AUTHORIZE:
        return (
            OutcomeSupervisionStatus.NOT_APPLICABLE,
            OutcomeDirective.NONE,
            False,
            ("decision_was_not_authorized",),
        )
    if outcome.status is OutcomeStatus.SUCCEEDED:
        return (
            OutcomeSupervisionStatus.COMPLETED,
            OutcomeDirective.COMPLETE,
            False,
            ("authorized_action_succeeded",),
        )
    if outcome.status is OutcomeStatus.NOT_EXECUTED:
        return (
            OutcomeSupervisionStatus.HUMAN_ATTENTION_REQUIRED,
            OutcomeDirective.NONE,
            True,
            ("authorized_action_was_not_executed",),
        )
    if outcome.status is OutcomeStatus.FAILED:
        if attempts_used < policy.maximum_attempts:
            return (
                OutcomeSupervisionStatus.FOLLOW_UP_REQUIRED,
                OutcomeDirective.RETRY,
                False,
                (
                    "authorized_action_failed",
                    "retry_budget_available",
                    f"attempts_used={attempts_used}",
                    f"maximum_attempts={policy.maximum_attempts}",
                ),
            )
        if candidate is not None and candidate.reversible is not Reversibility.NONE:
            return (
                OutcomeSupervisionStatus.FOLLOW_UP_REQUIRED,
                OutcomeDirective.REVERT,
                True,
                (
                    "authorized_action_failed",
                    "retry_budget_exhausted",
                    "candidate_can_be_reverted",
                ),
            )
        return (
            OutcomeSupervisionStatus.FOLLOW_UP_REQUIRED,
            OutcomeDirective.DEGRADE,
            True,
            (
                "authorized_action_failed",
                "retry_budget_exhausted",
                "candidate_cannot_be_reverted",
            ),
        )
    if outcome.status is OutcomeStatus.REVERTED:
        return (
            OutcomeSupervisionStatus.COMPLETED,
            OutcomeDirective.COMPLETE,
            True,
            ("action_was_reverted",),
        )
    if outcome.status is OutcomeStatus.DEGRADED:
        return (
            OutcomeSupervisionStatus.HUMAN_ATTENTION_REQUIRED,
            OutcomeDirective.DEGRADE,
            True,
            ("runtime_is_in_degraded_state",),
        )
    return (
        OutcomeSupervisionStatus.HUMAN_ATTENTION_REQUIRED,
        OutcomeDirective.NONE,
        True,
        ("outcome_status_unknown",),
    )


def _validate_inputs(
    decision: AutonomyDecision,
    outcome: DecisionOutcome,
    candidate: ActionCandidate | None,
    attempts_used: int,
) -> None:
    if attempts_used < 0:
        raise ValueError("attempts used must not be negative")
    if outcome.decision_id != decision.decision_id:
        raise ValueError("outcome must reference the supervised decision")
    if decision.candidate_id is None:
        if candidate is not None:
            raise ValueError("candidate requires a selected decision candidate")
        return
    if candidate is None:
        raise ValueError("selected decision requires its candidate")
    if candidate.candidate_id != decision.candidate_id:
        raise ValueError("candidate must match the supervised decision")


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be blank")


def _require_items(values: tuple[str, ...], label: str) -> None:
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must contain non-blank items")


def _require_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must include timezone information")
