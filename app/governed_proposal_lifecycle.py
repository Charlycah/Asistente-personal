from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.exceptions import DomainError
from domain.governed_proposal import GovernedProposal, ProposalState
from domain.governed_proposal_inbox import GovernedProposalInbox


@dataclass(frozen=True)
class GovernedProposalLifecycleSnapshot:
    schema_version: str
    authority: str
    inbox_authority: str
    autonomous_execution_enabled: bool
    conversational_delivery_enabled: bool
    persistence_enabled: bool


class GovernedProposalLifecycle:
    """Canonical authority for stored proposal state transitions and expiry."""

    SCHEMA_VERSION = "m346.4"
    AUTHORITY = "app.governed_proposal_lifecycle:GovernedProposalLifecycle"

    def __init__(self, inbox: GovernedProposalInbox) -> None:
        if not isinstance(inbox, GovernedProposalInbox):
            raise DomainError("inbox must be the canonical GovernedProposalInbox")
        self._inbox = inbox

    @property
    def snapshot(self) -> GovernedProposalLifecycleSnapshot:
        return GovernedProposalLifecycleSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            inbox_authority=self._inbox.AUTHORITY,
            autonomous_execution_enabled=False,
            conversational_delivery_enabled=False,
            persistence_enabled=False,
        )

    def offer(
        self,
        proposal_id: str,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedProposal:
        return self._transition(
            proposal_id,
            ProposalState.OFFERED,
            observed_at=observed_at,
        )

    def accept(
        self,
        proposal_id: str,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedProposal:
        return self._transition(
            proposal_id,
            ProposalState.ACCEPTED,
            observed_at=observed_at,
        )

    def dismiss(
        self,
        proposal_id: str,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedProposal:
        return self._transition(
            proposal_id,
            ProposalState.DISMISSED,
            observed_at=observed_at,
        )

    def expire_due(
        self,
        *,
        observed_at: datetime | None = None,
    ) -> tuple[GovernedProposal, ...]:
        return self._inbox.expire_due(observed_at=observed_at)

    def _transition(
        self,
        proposal_id: str,
        target: ProposalState,
        *,
        observed_at: datetime | None,
    ) -> GovernedProposal:
        return self._inbox.transition(
            proposal_id,
            target,
            observed_at=observed_at,
        )
