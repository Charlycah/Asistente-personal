from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from domain.exceptions import DomainError
from domain.governed_proposal import (
    GovernedProposal,
    ProposalPriority,
    ProposalState,
)


@dataclass(frozen=True)
class GovernedPresentationContext:
    """Explicit conversational conditions used to evaluate presentation."""

    user_turn_active: bool = False
    silence_requested: bool = False
    minimum_priority: ProposalPriority = ProposalPriority.NORMAL

    def __post_init__(self) -> None:
        if not isinstance(self.user_turn_active, bool):
            raise DomainError("user_turn_active must be a bool")
        if not isinstance(self.silence_requested, bool):
            raise DomainError("silence_requested must be a bool")
        if not isinstance(self.minimum_priority, ProposalPriority):
            raise DomainError("minimum_priority must be a ProposalPriority")


@dataclass(frozen=True)
class GovernedPresentationDecision:
    proposal: GovernedProposal
    presentable: bool
    reason: str
    effective_priority: ProposalPriority


@dataclass(frozen=True)
class GovernedProposalPresentationPolicySnapshot:
    schema_version: str
    authority: str
    mutates_proposals: bool
    autonomous_execution_enabled: bool
    conversational_delivery_enabled: bool


class GovernedProposalPresentationPolicy:
    """Read-only authority for priority refinement and presentation eligibility."""

    SCHEMA_VERSION = "m346.5"
    AUTHORITY = (
        "app.governed_proposal_presentation_policy:"
        "GovernedProposalPresentationPolicy"
    )
    _URGENT_WINDOW = timedelta(hours=2)
    _STALE_WINDOW = timedelta(days=7)

    @property
    def snapshot(self) -> GovernedProposalPresentationPolicySnapshot:
        return GovernedProposalPresentationPolicySnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            mutates_proposals=False,
            autonomous_execution_enabled=False,
            conversational_delivery_enabled=False,
        )

    def evaluate(
        self,
        proposal: GovernedProposal,
        context: GovernedPresentationContext | None = None,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedPresentationDecision:
        if not isinstance(proposal, GovernedProposal):
            raise DomainError("proposal must be a GovernedProposal")
        conditions = context or GovernedPresentationContext()
        if not isinstance(conditions, GovernedPresentationContext):
            raise DomainError("context must be a GovernedPresentationContext")
        effective_time = observed_at or datetime.now(timezone.utc)
        GovernedProposal._validate_datetime("observed_at", effective_time)
        priority = self.refine_priority(proposal, observed_at=effective_time)

        if proposal.state is not ProposalState.PENDING:
            return self._decision(proposal, False, "proposal_not_pending", priority)
        if proposal.is_expired_at(effective_time):
            return self._decision(proposal, False, "proposal_expired", priority)
        if conditions.silence_requested:
            return self._decision(proposal, False, "silence_requested", priority)
        if conditions.user_turn_active:
            return self._decision(proposal, False, "user_turn_active", priority)
        if priority < conditions.minimum_priority:
            return self._decision(proposal, False, "priority_below_policy", priority)
        return self._decision(proposal, True, "presentation_eligible", priority)

    def refine_priority(
        self,
        proposal: GovernedProposal,
        *,
        observed_at: datetime | None = None,
    ) -> ProposalPriority:
        if not isinstance(proposal, GovernedProposal):
            raise DomainError("proposal must be a GovernedProposal")
        effective_time = observed_at or datetime.now(timezone.utc)
        GovernedProposal._validate_datetime("observed_at", effective_time)

        relevance_priority = self._priority_for_relevance(proposal.relevance_score)
        priority = max(proposal.priority, relevance_priority)
        if (
            proposal.expires_at is not None
            and proposal.expires_at > effective_time
            and proposal.expires_at - effective_time <= self._URGENT_WINDOW
        ):
            priority = self._raise(priority)
        if effective_time - proposal.created_at >= self._STALE_WINDOW:
            priority = self._lower(priority)
        return priority

    @staticmethod
    def _priority_for_relevance(score: int) -> ProposalPriority:
        if score >= 95:
            return ProposalPriority.CRITICAL
        if score >= 85:
            return ProposalPriority.HIGH
        if score >= 70:
            return ProposalPriority.NORMAL
        return ProposalPriority.LOW

    @staticmethod
    def _raise(priority: ProposalPriority) -> ProposalPriority:
        members = tuple(ProposalPriority)
        index = members.index(priority)
        return members[min(index + 1, len(members) - 1)]

    @staticmethod
    def _lower(priority: ProposalPriority) -> ProposalPriority:
        members = tuple(ProposalPriority)
        index = members.index(priority)
        return members[max(index - 1, 0)]

    @staticmethod
    def _decision(
        proposal: GovernedProposal,
        presentable: bool,
        reason: str,
        priority: ProposalPriority,
    ) -> GovernedPresentationDecision:
        return GovernedPresentationDecision(
            proposal=proposal,
            presentable=presentable,
            reason=reason,
            effective_priority=priority,
        )
