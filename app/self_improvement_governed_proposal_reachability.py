from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from core.self_diagnostics import DiagnosticProposal, DiagnosticProposalStatus
from domain.governed_proposal import GovernedProposal, ProposalPriority


class GovernedProposalGateway(Protocol):
    @property
    def governed_proposal_model(self): ...

    @property
    def governed_proposal_inbox(self): ...

    def create_governed_proposal(self, **proposal_fields): ...

    def enqueue_governed_proposal(self, proposal, *, observed_at=None): ...


@dataclass(frozen=True)
class SelfImprovementGovernedProposalReachabilitySnapshot:
    authority: str
    diagnostic_authority: str
    proposal_authority: str
    inbox_authority: str
    autonomous_execution_enabled: bool
    code_mutation_enabled: bool


class SelfImprovementGovernedProposalReachability:
    """Bounded adapter from an inert diagnostic proposal into the governed inbox."""

    AUTHORITY = (
        "app.self_improvement_governed_proposal_reachability:"
        "SelfImprovementGovernedProposalReachability"
    )
    SOURCE_ID = "self_diagnostics"
    CATEGORY = "self_improvement_review"
    RELEVANCE_SCORE = 100
    PRIORITY = ProposalPriority.HIGH

    def __init__(self, *, gateway: GovernedProposalGateway) -> None:
        self._gateway = gateway

    @property
    def snapshot(self) -> SelfImprovementGovernedProposalReachabilitySnapshot:
        return SelfImprovementGovernedProposalReachabilitySnapshot(
            authority=self.AUTHORITY,
            diagnostic_authority="core.self_diagnostics:GovernedSelfDiagnostics",
            proposal_authority=self._gateway.governed_proposal_model.authority,
            inbox_authority=self._gateway.governed_proposal_inbox.authority,
            autonomous_execution_enabled=False,
            code_mutation_enabled=False,
        )

    def enqueue(
        self,
        diagnostic_proposal: DiagnosticProposal,
        *,
        observed_at: datetime | None = None,
    ) -> GovernedProposal:
        if not isinstance(diagnostic_proposal, DiagnosticProposal):
            raise TypeError("diagnostic_proposal must be a DiagnosticProposal")
        if diagnostic_proposal.status is not DiagnosticProposalStatus.DRAFT:
            raise ValueError("only DRAFT diagnostic proposals may be presented")
        effective_time = observed_at or datetime.now(timezone.utc)
        if effective_time.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")

        proposal = self._gateway.create_governed_proposal(
            proposal_id=f"self-improvement-{diagnostic_proposal.proposal_id}",
            source_id=self.SOURCE_ID,
            title=diagnostic_proposal.title,
            summary=self._summary(diagnostic_proposal),
            category=self.CATEGORY,
            relevance_score=self.RELEVANCE_SCORE,
            priority=self.PRIORITY,
            created_at=effective_time,
            metadata={
                "recipient": "both",
                "diagnostic_proposal_id": diagnostic_proposal.proposal_id,
                "diagnostic_proof_id": diagnostic_proposal.proof_id,
                "diagnostic_hypothesis_id": diagnostic_proposal.hypothesis_id,
                "diagnostic_review_path": diagnostic_proposal.review_path,
                "human_review_required": "true",
                "autonomous_execution": "false",
            },
        )
        return self._gateway.enqueue_governed_proposal(
            proposal,
            observed_at=effective_time,
        )

    @staticmethod
    def _summary(proposal: DiagnosticProposal) -> str:
        files = ", ".join(proposal.affected_files)
        return (
            f"ROBY encontró una posible mejora para revisar: {proposal.change_intent} "
            f"Archivos en alcance: {files}. La propuesta no autoriza ningún cambio; "
            "requiere revisión humana."
        )
