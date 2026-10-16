from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import IntEnum, StrEnum
from types import MappingProxyType
from typing import Mapping

from .exceptions import DomainError


class ProposalState(StrEnum):
    """Canonical lifecycle states for a governed household proposal."""

    NEW = "new"
    PENDING = "pending"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class ProposalPriority(IntEnum):
    """Importance only; priority never grants permission to interrupt."""

    LOW = 10
    NORMAL = 20
    HIGH = 30
    CRITICAL = 40


_ALLOWED_TRANSITIONS: Mapping[ProposalState, frozenset[ProposalState]] = {
    ProposalState.NEW: frozenset(
        {ProposalState.PENDING, ProposalState.DISMISSED, ProposalState.EXPIRED}
    ),
    ProposalState.PENDING: frozenset(
        {ProposalState.OFFERED, ProposalState.DISMISSED, ProposalState.EXPIRED}
    ),
    ProposalState.OFFERED: frozenset(
        {ProposalState.ACCEPTED, ProposalState.DISMISSED, ProposalState.EXPIRED}
    ),
    ProposalState.ACCEPTED: frozenset(),
    ProposalState.DISMISSED: frozenset(),
    ProposalState.EXPIRED: frozenset(),
}


@dataclass(frozen=True)
class GovernedProposal:
    """Immutable proposal governed by explicit lifecycle transitions."""

    proposal_id: str
    source_id: str
    title: str
    summary: str
    category: str
    relevance_score: int
    priority: ProposalPriority
    created_at: datetime
    expires_at: datetime | None = None
    state: ProposalState = ProposalState.NEW
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        for field_name in ("proposal_id", "source_id", "title", "summary", "category"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        if not 0 <= self.relevance_score <= 100:
            raise DomainError("relevance_score must be between 0 and 100")
        if not isinstance(self.priority, ProposalPriority):
            raise DomainError("priority must be a ProposalPriority")
        if not isinstance(self.state, ProposalState):
            raise DomainError("state must be a ProposalState")
        self._validate_datetime("created_at", self.created_at)
        if self.expires_at is not None:
            self._validate_datetime("expires_at", self.expires_at)
            if self.expires_at <= self.created_at:
                raise DomainError("expires_at must be later than created_at")
        immutable_metadata = MappingProxyType(dict(self.metadata or {}))
        object.__setattr__(self, "metadata", immutable_metadata)

    @staticmethod
    def _validate_datetime(field_name: str, value: datetime) -> None:
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise DomainError(f"{field_name} must be timezone-aware")

    @property
    def is_terminal(self) -> bool:
        return not _ALLOWED_TRANSITIONS[self.state]

    def can_transition_to(self, target: ProposalState) -> bool:
        return target in _ALLOWED_TRANSITIONS[self.state]

    def transition_to(
        self,
        target: ProposalState,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedProposal:
        if not isinstance(target, ProposalState):
            raise DomainError("target must be a ProposalState")
        effective_time = observed_at or datetime.now(timezone.utc)
        self._validate_datetime("observed_at", effective_time)
        if target is not ProposalState.EXPIRED and self.is_expired_at(effective_time):
            raise DomainError("expired proposal can only transition to EXPIRED")
        if not self.can_transition_to(target):
            raise DomainError(f"invalid proposal transition: {self.state} -> {target}")
        return replace(self, state=target)

    def is_expired_at(self, observed_at: datetime) -> bool:
        self._validate_datetime("observed_at", observed_at)
        return self.expires_at is not None and observed_at >= self.expires_at


@dataclass(frozen=True)
class GovernedProposalModelSnapshot:
    schema_version: str
    authority: str
    persistence_enabled: bool
    autonomous_delivery_enabled: bool
    states: tuple[ProposalState, ...]
    priorities: tuple[ProposalPriority, ...]


class GovernedProposalModel:
    """Single canonical authority for creating valid governed proposals."""

    SCHEMA_VERSION = "m346.0"
    AUTHORITY = "domain.governed_proposal:GovernedProposalModel"

    @property
    def snapshot(self) -> GovernedProposalModelSnapshot:
        return GovernedProposalModelSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            persistence_enabled=False,
            autonomous_delivery_enabled=False,
            states=tuple(ProposalState),
            priorities=tuple(ProposalPriority),
        )

    def create(
        self,
        *,
        proposal_id: str,
        source_id: str,
        title: str,
        summary: str,
        category: str,
        relevance_score: int,
        priority: ProposalPriority = ProposalPriority.NORMAL,
        created_at: datetime,
        expires_at: datetime | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> GovernedProposal:
        return GovernedProposal(
            proposal_id=proposal_id,
            source_id=source_id,
            title=title,
            summary=summary,
            category=category,
            relevance_score=relevance_score,
            priority=priority,
            created_at=created_at,
            expires_at=expires_at,
            metadata=metadata,
        )
