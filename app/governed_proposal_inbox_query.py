from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.exceptions import DomainError
from domain.governed_proposal import GovernedProposal, ProposalPriority
from domain.governed_proposal_inbox import GovernedProposalInbox


@dataclass(frozen=True)
class GovernedProposalInboxQueryRequest:
    """Explicit read-only criteria for consulting the canonical proposal inbox."""

    source_id: str | None = None
    category: str | None = None
    minimum_priority: ProposalPriority | None = None
    limit: int | None = None

    def __post_init__(self) -> None:
        for field_name in ("source_id", "category"):
            value = getattr(self, field_name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise DomainError(f"{field_name} must be a non-empty string or None")
        if self.minimum_priority is not None and not isinstance(
            self.minimum_priority, ProposalPriority
        ):
            raise DomainError("minimum_priority must be a ProposalPriority or None")
        if self.limit is not None and (
            not isinstance(self.limit, int)
            or isinstance(self.limit, bool)
            or self.limit < 1
        ):
            raise DomainError("limit must be a positive integer or None")


@dataclass(frozen=True)
class GovernedProposalInboxQueryResult:
    proposals: tuple[GovernedProposal, ...]
    total_pending: int
    matched: int

    @property
    def next_proposal(self) -> GovernedProposal | None:
        return self.proposals[0] if self.proposals else None


@dataclass(frozen=True)
class GovernedProposalInboxQuerySnapshot:
    schema_version: str
    authority: str
    inbox_authority: str
    read_only: bool
    autonomous_execution_enabled: bool
    conversational_delivery_enabled: bool


class GovernedProposalInboxQuery:
    """Canonical read-only consultation service for the local proposal inbox."""

    SCHEMA_VERSION = "m346.3"
    AUTHORITY = (
        "app.governed_proposal_inbox_query:GovernedProposalInboxQuery"
    )

    def __init__(self, inbox: GovernedProposalInbox) -> None:
        if not isinstance(inbox, GovernedProposalInbox):
            raise DomainError("inbox must be the canonical GovernedProposalInbox")
        self._inbox = inbox

    @property
    def snapshot(self) -> GovernedProposalInboxQuerySnapshot:
        return GovernedProposalInboxQuerySnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            inbox_authority=self._inbox.AUTHORITY,
            read_only=True,
            autonomous_execution_enabled=False,
            conversational_delivery_enabled=False,
        )

    def query(
        self,
        request: GovernedProposalInboxQueryRequest | None = None,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedProposalInboxQueryResult:
        criteria = request or GovernedProposalInboxQueryRequest()
        if not isinstance(criteria, GovernedProposalInboxQueryRequest):
            raise DomainError("request must be a GovernedProposalInboxQueryRequest")

        pending = self._inbox.pending(observed_at=observed_at)
        selected = tuple(
            proposal
            for proposal in pending
            if self._matches(proposal, criteria)
        )
        if criteria.limit is not None:
            selected = selected[: criteria.limit]
        return GovernedProposalInboxQueryResult(
            proposals=selected,
            total_pending=len(pending),
            matched=len(selected),
        )

    @staticmethod
    def _matches(
        proposal: GovernedProposal,
        request: GovernedProposalInboxQueryRequest,
    ) -> bool:
        if request.source_id is not None and proposal.source_id != request.source_id:
            return False
        if request.category is not None and proposal.category != request.category:
            return False
        return not (
            request.minimum_priority is not None
            and proposal.priority < request.minimum_priority
        )
