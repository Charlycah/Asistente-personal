from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from .models import (
    AutonomyEvent,
    AutonomyEventType,
    AutonomyProposal,
    AutonomyRisk,
    AutonomyStatus,
    ExecutionAuthorization,
    SupervisedAutonomyPolicy,
    SupervisedAutonomySnapshot,
)


class SupervisedAutonomyService:
    """Authorizes bounded actions; execution remains in governed adapters."""

    _TERMINAL = {
        AutonomyStatus.COMPLETED,
        AutonomyStatus.FAILED,
        AutonomyStatus.CANCELLED,
        AutonomyStatus.REJECTED,
        AutonomyStatus.EXPIRED,
        AutonomyStatus.BLOCKED,
    }

    def __init__(self, policy: SupervisedAutonomyPolicy | None = None) -> None:
        self.policy = policy or SupervisedAutonomyPolicy()
        self._proposals: dict[str, AutonomyProposal] = {}
        self._events: list[AutonomyEvent] = []

    @property
    def snapshot(self) -> SupervisedAutonomySnapshot:
        return SupervisedAutonomySnapshot(
            proposals=tuple(self._proposals.values()),
            events=tuple(self._events),
        )

    def propose(
        self,
        action: str,
        description: str,
        *,
        requested_by: str,
        now: datetime | None = None,
    ) -> AutonomyProposal:
        timestamp = now or datetime.now(timezone.utc)
        self._require_aware(timestamp)
        action = action.strip()
        description = description.strip()
        requested_by = requested_by.strip()
        if not action or not description or not requested_by:
            raise ValueError("autonomy proposal fields must not be blank")
        pending = sum(
            item.normalized_status not in self._TERMINAL
            for item in self._proposals.values()
        )
        if pending >= self.policy.maximum_pending:
            raise RuntimeError("maximum pending autonomy proposals reached")
        risk = self._classify(action)
        proposal_id = sha256(
            f"{action}|{description}|{requested_by}|{timestamp.isoformat()}".encode()
        ).hexdigest()
        if proposal_id in self._proposals:
            raise ValueError("duplicate autonomy proposal")
        status = self._initial_status(risk)
        rationale = self._initial_rationale(risk, status)
        proposal = AutonomyProposal(
            proposal_id=proposal_id,
            action=action,
            description=description,
            requested_by=requested_by,
            created_at=timestamp,
            expires_at=timestamp + self.policy.proposal_ttl,
            risk=risk,
            status=status,
            rationale=rationale,
        )
        self._proposals[proposal_id] = proposal
        event_type = (
            AutonomyEventType.BLOCKED
            if status is AutonomyStatus.BLOCKED
            else AutonomyEventType.PROPOSED
        )
        self._record(event_type, proposal, timestamp, requested_by, rationale)
        if status is AutonomyStatus.AWAITING_APPROVAL:
            self._record(
                AutonomyEventType.APPROVAL_REQUIRED,
                proposal,
                timestamp,
                "ROBY",
                ("explicit human approval is required before execution",),
            )
        return proposal

    def approve(
        self,
        proposal_id: str,
        *,
        approved_by: str,
        now: datetime | None = None,
    ) -> AutonomyProposal:
        timestamp = now or datetime.now(timezone.utc)
        self._require_aware(timestamp)
        proposal = self._active(proposal_id, timestamp)
        if proposal.normalized_status is not AutonomyStatus.AWAITING_APPROVAL:
            raise ValueError("proposal is not awaiting approval")
        approved_by = approved_by.strip()
        if not approved_by:
            raise ValueError("approval actor must not be blank")
        updated = proposal.with_changes(
            status=AutonomyStatus.APPROVED,
            approved_by=approved_by,
            approved_at=timestamp,
            execution_deadline=timestamp + self.policy.execution_ttl,
            rationale=proposal.rationale + ("explicit human approval recorded",),
        )
        self._proposals[proposal_id] = updated
        self._record(
            AutonomyEventType.APPROVED,
            updated,
            timestamp,
            approved_by,
            ("explicit human approval recorded",),
        )
        return updated

    def reject(
        self,
        proposal_id: str,
        *,
        rejected_by: str,
        reason: str,
        now: datetime | None = None,
    ) -> AutonomyProposal:
        return self._terminate(
            proposal_id,
            AutonomyStatus.REJECTED,
            AutonomyEventType.REJECTED,
            rejected_by,
            reason,
            now,
        )

    def authorize_execution(
        self,
        proposal_id: str,
        *,
        now: datetime | None = None,
    ) -> ExecutionAuthorization:
        timestamp = now or datetime.now(timezone.utc)
        self._require_aware(timestamp)
        proposal = self._active(proposal_id, timestamp)
        if proposal.normalized_status is not AutonomyStatus.APPROVED:
            raise PermissionError("proposal is not approved for execution")
        deadline = proposal.execution_deadline
        if deadline is None or timestamp >= deadline:
            expired = proposal.with_changes(status=AutonomyStatus.EXPIRED)
            self._proposals[proposal_id] = expired
            self._record(
                AutonomyEventType.EXPIRED,
                expired,
                timestamp,
                "ROBY",
                ("execution authorization expired",),
            )
            raise PermissionError("execution authorization expired")
        executing = proposal.with_changes(status=AutonomyStatus.EXECUTING)
        self._proposals[proposal_id] = executing
        self._record(
            AutonomyEventType.EXECUTION_AUTHORIZED,
            executing,
            timestamp,
            "ROBY",
            ("bounded execution token issued to governed adapter",),
        )
        return ExecutionAuthorization(
            proposal_id=proposal_id,
            action=proposal.action,
            authorized_at=timestamp,
            expires_at=deadline,
        )

    def complete(
        self,
        proposal_id: str,
        *,
        result_summary: str,
        now: datetime | None = None,
    ) -> AutonomyProposal:
        return self._finish_execution(
            proposal_id,
            AutonomyStatus.COMPLETED,
            AutonomyEventType.COMPLETED,
            result_summary,
            now,
        )

    def fail(
        self,
        proposal_id: str,
        *,
        error_summary: str,
        now: datetime | None = None,
    ) -> AutonomyProposal:
        return self._finish_execution(
            proposal_id,
            AutonomyStatus.FAILED,
            AutonomyEventType.FAILED,
            error_summary,
            now,
        )

    def cancel(
        self,
        proposal_id: str,
        *,
        cancelled_by: str,
        reason: str,
        now: datetime | None = None,
    ) -> AutonomyProposal:
        return self._terminate(
            proposal_id,
            AutonomyStatus.CANCELLED,
            AutonomyEventType.CANCELLED,
            cancelled_by,
            reason,
            now,
        )

    def expire_pending(self, *, now: datetime | None = None) -> tuple[str, ...]:
        timestamp = now or datetime.now(timezone.utc)
        self._require_aware(timestamp)
        expired_ids: list[str] = []
        for proposal_id, proposal in tuple(self._proposals.items()):
            if proposal.normalized_status in self._TERMINAL:
                continue
            proposal_expired = timestamp >= proposal.expires_at
            execution_expired = (
                proposal.normalized_status is AutonomyStatus.APPROVED
                and proposal.execution_deadline is not None
                and timestamp >= proposal.execution_deadline
            )
            if not proposal_expired and not execution_expired:
                continue
            updated = proposal.with_changes(status=AutonomyStatus.EXPIRED)
            self._proposals[proposal_id] = updated
            self._record(
                AutonomyEventType.EXPIRED,
                updated,
                timestamp,
                "ROBY",
                ("autonomy proposal expired without execution",),
            )
            expired_ids.append(proposal_id)
        return tuple(expired_ids)

    def get(self, proposal_id: str) -> AutonomyProposal:
        try:
            return self._proposals[proposal_id]
        except KeyError as exc:
            raise KeyError("autonomy proposal was not found") from exc

    def _active(self, proposal_id: str, timestamp: datetime) -> AutonomyProposal:
        proposal = self.get(proposal_id)
        if proposal.normalized_status in self._TERMINAL:
            raise ValueError("autonomy proposal is already terminal")
        if timestamp >= proposal.expires_at:
            updated = proposal.with_changes(status=AutonomyStatus.EXPIRED)
            self._proposals[proposal_id] = updated
            self._record(
                AutonomyEventType.EXPIRED,
                updated,
                timestamp,
                "ROBY",
                ("autonomy proposal expired",),
            )
            raise ValueError("autonomy proposal expired")
        return proposal

    def _terminate(
        self,
        proposal_id: str,
        status: AutonomyStatus,
        event_type: AutonomyEventType,
        actor: str,
        reason: str,
        now: datetime | None,
    ) -> AutonomyProposal:
        timestamp = now or datetime.now(timezone.utc)
        self._require_aware(timestamp)
        proposal = self._active(proposal_id, timestamp)
        actor = actor.strip()
        reason = reason.strip()
        if not actor or not reason:
            raise ValueError("autonomy termination actor and reason are required")
        updated = proposal.with_changes(
            status=status,
            rationale=proposal.rationale + (reason,),
        )
        self._proposals[proposal_id] = updated
        self._record(event_type, updated, timestamp, actor, (reason,))
        return updated

    def _finish_execution(
        self,
        proposal_id: str,
        status: AutonomyStatus,
        event_type: AutonomyEventType,
        summary: str,
        now: datetime | None,
    ) -> AutonomyProposal:
        timestamp = now or datetime.now(timezone.utc)
        self._require_aware(timestamp)
        proposal = self.get(proposal_id)
        if proposal.normalized_status is not AutonomyStatus.EXECUTING:
            raise ValueError("proposal is not executing")
        summary = summary.strip()
        if not summary:
            raise ValueError("execution result summary must not be blank")
        updated = proposal.with_changes(status=status, result_summary=summary)
        self._proposals[proposal_id] = updated
        self._record(event_type, updated, timestamp, "adapter", (summary,))
        return updated

    def _classify(self, action: str) -> AutonomyRisk:
        if action in self.policy.prohibited_actions:
            return AutonomyRisk.PROHIBITED
        if action in self.policy.high_risk_actions:
            return AutonomyRisk.HIGH
        if action in self.policy.medium_risk_actions:
            return AutonomyRisk.MEDIUM
        return AutonomyRisk.LOW

    def _initial_status(self, risk: AutonomyRisk) -> AutonomyStatus:
        if risk is AutonomyRisk.PROHIBITED:
            return AutonomyStatus.BLOCKED
        if risk is AutonomyRisk.LOW and self.policy.allow_low_risk_automatic_approval:
            return AutonomyStatus.APPROVED
        return AutonomyStatus.AWAITING_APPROVAL

    @staticmethod
    def _initial_rationale(
        risk: AutonomyRisk,
        status: AutonomyStatus,
    ) -> tuple[str, ...]:
        if status is AutonomyStatus.BLOCKED:
            return ("action is prohibited by supervised autonomy policy",)
        if status is AutonomyStatus.APPROVED:
            return ("low-risk action approved by explicit local policy",)
        return (f"{risk.value}-risk action requires human supervision",)

    @staticmethod
    def _require_aware(value: datetime) -> None:
        if value.tzinfo is None:
            raise ValueError("autonomy processing time must be timezone-aware")

    def _record(
        self,
        event_type: AutonomyEventType,
        proposal: AutonomyProposal,
        timestamp: datetime,
        actor: str,
        rationale: tuple[str, ...],
    ) -> AutonomyEvent:
        event = AutonomyEvent(
            event_type=event_type,
            proposal_id=proposal.proposal_id,
            occurred_at=timestamp,
            actor=actor,
            rationale=rationale,
        )
        self._events.append(event)
        return event
