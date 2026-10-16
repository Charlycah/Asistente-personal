from __future__ import annotations

from datetime import datetime

from app.governed_reasoning_runtime import (
    GovernedCreativeCandidateCriticalDisposition,
    GovernedCreativeCandidateCriticalDispositionStatus,
)
from domain.governed_proposal import GovernedProposalModel, ProposalPriority
from domain.governed_proposal_inbox import GovernedProposalInbox


class GovernedCreativeDispositionProposalProjection:
    """Bounded explicit-human promotion into existing Proposal authorities."""

    def __init__(
        self,
        *,
        proposal_model: GovernedProposalModel,
        proposal_inbox: GovernedProposalInbox,
    ) -> None:
        self._proposal_model = proposal_model
        self._proposal_inbox = proposal_inbox
        self._promotions: dict[str, str] = {}

    def promote(
        self,
        *,
        disposition: GovernedCreativeCandidateCriticalDisposition,
        session_id: str,
        human_confirmation: bool,
        promotion_attempt_id: str,
        observed_at: datetime,
    ):
        if not human_confirmation:
            return None
        if (
            disposition.status
            is not GovernedCreativeCandidateCriticalDispositionStatus.REVIEW_REQUIRED
        ):
            return None

        existing_id = self._promotions.get(promotion_attempt_id)
        if existing_id is not None:
            return self._proposal_inbox.find(existing_id)

        metadata = {
            "disposition_id": disposition.disposition_id,
            "synthesis_source_fingerprint": disposition.synthesis_source_fingerprint,
            "hypothesis_candidate_id": disposition.hypothesis_candidate_id,
            "hypothesis_source_claim_fingerprint": (
                disposition.hypothesis_source_claim_fingerprint
            ),
            "disposition_status": disposition.status.value,
            "canonical_source_authority": "governed_reasoning",
            "independent_evidence_required": "true",
            "rationale_codes": "|".join(disposition.rationale_codes),
            "session_id": session_id,
            "promotion_attempt_id": promotion_attempt_id,
        }
        proposal = self._proposal_model.create(
            proposal_id=f"creative-disposition-proposal:{promotion_attempt_id}",
            source_id="governed_reasoning",
            title="Creative critical disposition",
            summary=disposition.disposition_id,
            category="creative_critical_disposition",
            relevance_score=50,
            priority=ProposalPriority.NORMAL,
            created_at=observed_at,
            metadata=metadata,
        )
        admitted = self._proposal_inbox.enqueue(proposal, observed_at=observed_at)
        self._promotions[promotion_attempt_id] = admitted.proposal_id
        return admitted
