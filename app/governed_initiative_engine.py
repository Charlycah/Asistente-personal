from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from types import MappingProxyType
from typing import Mapping

from domain.exceptions import DomainError
from domain.governed_proposal import (
    GovernedProposal,
    GovernedProposalModel,
    ProposalPriority,
)
from domain.governed_proposal_inbox import GovernedProposalInbox

from .relevance_evaluator import RelevanceCandidate, RelevanceEvaluator


@dataclass(frozen=True)
class GovernedInitiativeCandidate:
    """Candidate envelope required before creating a governed proposal."""

    source_id: str
    summary: str
    category: str
    relevance_candidate: RelevanceCandidate
    expires_at: datetime | None = None
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        for field_name in ("source_id", "summary", "category"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        if not isinstance(self.relevance_candidate, RelevanceCandidate):
            raise DomainError("relevance_candidate must be a RelevanceCandidate")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise DomainError("expires_at must be timezone-aware")
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata or {})),
        )


@dataclass(frozen=True)
class GovernedInitiativeResult:
    accepted: bool
    reason: str
    proposal: GovernedProposal | None


@dataclass(frozen=True)
class GovernedInitiativeEngineSnapshot:
    schema_version: str
    authority: str
    proposal_authority: str
    inbox_authority: str
    autonomous_execution_enabled: bool
    conversational_delivery_enabled: bool


class GovernedInitiativeEngine:
    """Single authority that turns relevant candidates into pending proposals."""

    SCHEMA_VERSION = "m346.2"
    AUTHORITY = "app.governed_initiative_engine:GovernedInitiativeEngine"

    def __init__(
        self,
        relevance_evaluator: RelevanceEvaluator,
        proposal_model: GovernedProposalModel,
        proposal_inbox: GovernedProposalInbox,
    ) -> None:
        self._relevance_evaluator = relevance_evaluator
        self._proposal_model = proposal_model
        self._proposal_inbox = proposal_inbox

    @property
    def snapshot(self) -> GovernedInitiativeEngineSnapshot:
        return GovernedInitiativeEngineSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            proposal_authority=self._proposal_model.snapshot.authority,
            inbox_authority=self._proposal_inbox.snapshot.authority,
            autonomous_execution_enabled=False,
            conversational_delivery_enabled=False,
        )

    def generate(
        self,
        candidate: GovernedInitiativeCandidate,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedInitiativeResult:
        if not isinstance(candidate, GovernedInitiativeCandidate):
            raise DomainError("candidate must be a GovernedInitiativeCandidate")
        effective_time = observed_at or datetime.now(timezone.utc)
        if effective_time.tzinfo is None:
            raise DomainError("observed_at must be timezone-aware")
        if candidate.expires_at is not None and candidate.expires_at <= effective_time:
            return GovernedInitiativeResult(False, "candidate_expired", None)

        relevance = self._relevance_evaluator.evaluate(
            candidate.relevance_candidate,
            now=effective_time,
        )
        if not relevance.should_share:
            return GovernedInitiativeResult(False, "not_relevant_enough", None)

        relevance_score = max(relevance.scores.values(), default=0)
        proposal = self._proposal_model.create(
            proposal_id=self._proposal_id(candidate, effective_time),
            source_id=candidate.source_id,
            title=candidate.relevance_candidate.title,
            summary=candidate.summary,
            category=candidate.category,
            relevance_score=relevance_score,
            priority=self._priority_for(relevance_score),
            created_at=effective_time,
            expires_at=candidate.expires_at,
            metadata={
                **candidate.metadata,
                "recipient": relevance.recipient.value,
                "initiative_engine": self.SCHEMA_VERSION,
            },
        )
        pending = self._proposal_inbox.enqueue(proposal, observed_at=effective_time)
        return GovernedInitiativeResult(True, "proposal_enqueued", pending)

    @staticmethod
    def _priority_for(relevance_score: int) -> ProposalPriority:
        if relevance_score >= 90:
            return ProposalPriority.CRITICAL
        if relevance_score >= 80:
            return ProposalPriority.HIGH
        if relevance_score >= 70:
            return ProposalPriority.NORMAL
        return ProposalPriority.LOW

    @staticmethod
    def _proposal_id(
        candidate: GovernedInitiativeCandidate,
        observed_at: datetime,
    ) -> str:
        material = "|".join(
            (
                candidate.source_id.strip().casefold(),
                candidate.category.strip().casefold(),
                candidate.relevance_candidate.title.strip().casefold(),
                observed_at.isoformat(),
            )
        )
        return f"initiative-{sha256(material.encode('utf-8')).hexdigest()[:20]}"
