from __future__ import annotations

from datetime import datetime

from domain.governed_proposal import GovernedProposal

from .governed_proposal_human_review_projection import (
    GovernedProposalHumanReviewProjection,
)


class GovernedPresentedProposalReviewTransport:
    """Carry exact presented proposal references to the certified review projection."""

    def __init__(
        self,
        *,
        projection: GovernedProposalHumanReviewProjection,
    ) -> None:
        if not isinstance(projection, GovernedProposalHumanReviewProjection):
            raise TypeError(
                "projection must be a GovernedProposalHumanReviewProjection instance"
            )
        self._projection = projection
        self._presented_references: set[str] = set()

    def retain_presented_proposal_reference(self, proposal_id: str) -> bool:
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            return False
        self._presented_references.add(proposal_id)
        return True

    def review_presented_proposal(
        self,
        *,
        response: str,
        observed_at: datetime | None = None,
    ) -> GovernedProposal | None:
        if len(self._presented_references) != 1:
            return None

        proposal_id = next(iter(self._presented_references))
        reviewed = self._projection.review(
            proposal_id=proposal_id,
            response=response,
            observed_at=observed_at,
        )
        if reviewed is not None:
            self._presented_references.discard(proposal_id)
        return reviewed
