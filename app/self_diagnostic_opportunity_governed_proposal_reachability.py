from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.self_improvement_governed_proposal_reachability import (
    SelfImprovementGovernedProposalReachability,
)
from app.self_improvement_proposal_generation import (
    DiagnosticProjectEvidence,
    generate_diagnostic_proposal_request,
)
from core.self_diagnostics import (
    DiagnosticHypothesis,
    DiagnosticObservation,
    DiagnosticProofStatus,
    DiagnosticProposal,
    DiagnosticThreshold,
    GovernedSelfDiagnostics,
)
from domain.governed_proposal import GovernedProposal


@dataclass(frozen=True)
class SelfDiagnosticOpportunity:
    """Explicit evidence bundle; it is not an inferred cause or repair command."""

    observations: tuple[DiagnosticObservation, ...]
    threshold: DiagnosticThreshold
    hypothesis: DiagnosticHypothesis
    project_evidence: DiagnosticProjectEvidence
    project_root: Path
    proof_id: str
    proposal_id: str


@dataclass(frozen=True)
class SelfDiagnosticOpportunityReachabilitySnapshot:
    authority: str
    diagnostic_authority: str
    autonomous_hypothesis_generation_enabled: bool
    background_monitoring_enabled: bool
    autonomous_execution_enabled: bool
    code_mutation_enabled: bool


@dataclass(frozen=True)
class SelfDiagnosticOpportunityResult:
    diagnostic_proposal: DiagnosticProposal
    governed_proposal: GovernedProposal


class SelfDiagnosticOpportunityGovernedProposalReachability:
    """Compose existing diagnostic stages into the existing governed proposal path."""

    AUTHORITY = (
        "app.self_diagnostic_opportunity_governed_proposal_reachability:"
        "SelfDiagnosticOpportunityGovernedProposalReachability"
    )

    def __init__(
        self,
        *,
        diagnostics: GovernedSelfDiagnostics,
        proposal_reachability: SelfImprovementGovernedProposalReachability,
    ) -> None:
        self._diagnostics = diagnostics
        self._proposal_reachability = proposal_reachability

    @property
    def snapshot(self) -> SelfDiagnosticOpportunityReachabilitySnapshot:
        return SelfDiagnosticOpportunityReachabilitySnapshot(
            authority=self.AUTHORITY,
            diagnostic_authority=self._diagnostics.authority_id,
            autonomous_hypothesis_generation_enabled=False,
            background_monitoring_enabled=False,
            autonomous_execution_enabled=False,
            code_mutation_enabled=False,
        )

    def submit(
        self,
        opportunity: SelfDiagnosticOpportunity,
        *,
        observed_at: datetime | None = None,
    ) -> SelfDiagnosticOpportunityResult:
        report = self._diagnostics.diagnose(
            opportunity.observations,
            threshold=opportunity.threshold,
        )
        assessment = self._diagnostics.assess_hypothesis(
            report,
            opportunity.hypothesis,
        )
        proof = self._diagnostics.prepare_reproducible_proof(
            report,
            assessment,
            proof_id=opportunity.proof_id,
        )
        proof_result = self._diagnostics.run_reproducible_proof(
            report,
            proof,
        )
        if proof_result.status is not DiagnosticProofStatus.REPRODUCED:
            raise ValueError("self-diagnostic opportunity proof was not reproduced")

        request = generate_diagnostic_proposal_request(
            proof,
            proof_result,
            opportunity.project_evidence,
            project_root=opportunity.project_root,
            proposal_id=opportunity.proposal_id,
        )
        diagnostic_proposal = self._diagnostics.prepare_isolated_proposal(
            proof,
            proof_result,
            request,
        )
        governed_proposal = self._proposal_reachability.enqueue(
            diagnostic_proposal,
            observed_at=observed_at,
        )
        return SelfDiagnosticOpportunityResult(
            diagnostic_proposal=diagnostic_proposal,
            governed_proposal=governed_proposal,
        )
