from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from domain.exceptions import DomainError
from domain.governed_proposal import GovernedProposal, ProposalState

from .governed_proposal_lifecycle import GovernedProposalLifecycle

_ACCEPT = frozenset(
    {
        "acepto esta propuesta.",
        "acepto esta propuesta",
        "acepto la propuesta.",
        "acepto la propuesta",
        "i accept this proposal.",
        "i accept this proposal",
    }
)
_DISMISS = frozenset(
    {
        "descarto esta propuesta.",
        "descarto esta propuesta",
        "descarto la propuesta.",
        "descarto la propuesta",
        "i dismiss this proposal.",
        "i dismiss this proposal",
    }
)


def _review_intent(response: str) -> ProposalState | None:
    if not isinstance(response, str):
        return None
    normalized = " ".join(response.strip().casefold().split())
    if normalized in _ACCEPT:
        return ProposalState.ACCEPTED
    if normalized in _DISMISS:
        return ProposalState.DISMISSED
    return None


class GovernedProposalHumanReviewProjection:
    """Bind explicit review text to the existing proposal lifecycle."""

    def __init__(
        self,
        *,
        lifecycle: GovernedProposalLifecycle,
        proposal_lookup: Callable[[str], GovernedProposal | None],
    ) -> None:
        if not isinstance(lifecycle, GovernedProposalLifecycle):
            raise DomainError("lifecycle must be a GovernedProposalLifecycle instance")
        if not callable(proposal_lookup):
            raise DomainError("proposal_lookup must be callable")
        self._lifecycle = lifecycle
        self._proposal_lookup = proposal_lookup

    def review(
        self,
        *,
        proposal_id: str,
        response: str,
        observed_at: datetime | None = None,
    ) -> GovernedProposal | None:
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            return None
        proposal = self._proposal_lookup(proposal_id)
        if proposal is None or proposal.proposal_id != proposal_id:
            return None
        if proposal.state is not ProposalState.OFFERED:
            return None

        target = _review_intent(response)
        if target is None:
            return None

        try:
            if target is ProposalState.ACCEPTED:
                return self._lifecycle.accept(proposal_id, observed_at=observed_at)
            return self._lifecycle.dismiss(proposal_id, observed_at=observed_at)
        except DomainError:
            return None
