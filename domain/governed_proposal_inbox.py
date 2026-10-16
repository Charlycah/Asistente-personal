from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .exceptions import DomainError
from .governed_proposal import GovernedProposal, ProposalState


@dataclass(frozen=True)
class GovernedProposalInboxSnapshot:
    schema_version: str
    authority: str
    persistence_enabled: bool
    autonomous_delivery_enabled: bool
    total_proposals: int
    pending_proposals: int


class GovernedProposalInbox:
    """Canonical local inbox for governed household proposals."""

    SCHEMA_VERSION = "m346.1"
    AUTHORITY = "domain.governed_proposal_inbox:GovernedProposalInbox"

    def __init__(self) -> None:
        self._proposals: dict[str, GovernedProposal] = {}

    @property
    def snapshot(self) -> GovernedProposalInboxSnapshot:
        return GovernedProposalInboxSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            persistence_enabled=False,
            autonomous_delivery_enabled=False,
            total_proposals=len(self._proposals),
            pending_proposals=sum(
                proposal.state is ProposalState.PENDING
                for proposal in self._proposals.values()
            ),
        )

    def enqueue(
        self,
        proposal: GovernedProposal,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedProposal:
        if not isinstance(proposal, GovernedProposal):
            raise DomainError("proposal must be a GovernedProposal")
        if proposal.proposal_id in self._proposals:
            raise DomainError(f"duplicate proposal_id: {proposal.proposal_id}")
        if proposal.state is not ProposalState.NEW:
            raise DomainError("only NEW proposals can enter the local inbox")
        pending = proposal.transition_to(
            ProposalState.PENDING,
            observed_at=observed_at or datetime.now(timezone.utc),
        )
        self._proposals[pending.proposal_id] = pending
        return pending

    def find(self, proposal_id: str) -> GovernedProposal | None:
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise DomainError("proposal_id must be a non-empty string")
        return self._proposals.get(proposal_id)

    def transition(
        self,
        proposal_id: str,
        target: ProposalState,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedProposal:
        proposal = self.find(proposal_id)
        if proposal is None:
            raise DomainError(f"unknown proposal_id: {proposal_id}")
        transitioned = proposal.transition_to(
            target,
            observed_at=observed_at or datetime.now(timezone.utc),
        )
        self._proposals[proposal_id] = transitioned
        return transitioned

    def expire_due(
        self,
        *,
        observed_at: datetime | None = None,
    ) -> tuple[GovernedProposal, ...]:
        effective_time = observed_at or datetime.now(timezone.utc)
        GovernedProposal._validate_datetime("observed_at", effective_time)
        expired: list[GovernedProposal] = []
        for proposal_id, proposal in tuple(self._proposals.items()):
            if not proposal.is_terminal and proposal.is_expired_at(effective_time):
                transitioned = proposal.transition_to(
                    ProposalState.EXPIRED,
                    observed_at=effective_time,
                )
                self._proposals[proposal_id] = transitioned
                expired.append(transitioned)
        return tuple(expired)

    def pending(
        self,
        *,
        observed_at: datetime | None = None,
    ) -> tuple[GovernedProposal, ...]:
        effective_time = observed_at or datetime.now(timezone.utc)
        GovernedProposal._validate_datetime("observed_at", effective_time)
        self.expire_due(observed_at=effective_time)
        proposals = (
            proposal
            for proposal in self._proposals.values()
            if proposal.state is ProposalState.PENDING
        )
        return tuple(
            sorted(
                proposals,
                key=lambda proposal: (
                    -int(proposal.priority),
                    -proposal.relevance_score,
                    proposal.created_at,
                    proposal.proposal_id,
                ),
            )
        )
