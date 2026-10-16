from __future__ import annotations

import importlib
import inspect
from datetime import datetime, timezone

import pytest

from app.governed_proposal_human_review_projection import (
    GovernedProposalHumanReviewProjection,
)
from app.governed_proposal_lifecycle import GovernedProposalLifecycle
from domain.governed_proposal import GovernedProposal, ProposalPriority, ProposalState
from domain.governed_proposal_inbox import GovernedProposalInbox

SEAM_MODULE = "app.governed_presented_proposal_review_transport"
SEAM_TYPE = "GovernedPresentedProposalReviewTransport"
NOW = datetime(2026, 9, 23, 16, 30, tzinfo=timezone.utc)


def _offered(
    inbox: GovernedProposalInbox,
    lifecycle: GovernedProposalLifecycle,
    pid: str,
):
    proposal = GovernedProposal(
        proposal_id=pid,
        source_id="self_improvement",
        title=f"Proposal {pid}",
        summary="Bounded governed proposal for explicit human review.",
        category="self_improvement",
        relevance_score=90,
        priority=ProposalPriority.HIGH,
        created_at=NOW,
    )
    inbox.enqueue(proposal, observed_at=NOW)
    lifecycle.offer(pid, observed_at=NOW)
    return proposal


def test_red_exact_presented_proposal_reference_human_review_transport_contract(
) -> None:
    """RED: preserve exact presented identity to the certified review projection."""
    try:
        module = importlib.import_module(SEAM_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: exact presented proposal identity is lost before the human-response "
            "edge; no bounded transport reaches the certified review projection"
        )

    seam_type = getattr(module, SEAM_TYPE, None)
    assert seam_type is not None, (
        "RED: bounded presented-proposal review transport missing"
    )

    source = inspect.getsource(seam_type)
    lowered = source.casefold()

    # The transport must reuse the already-certified semantic owner/projection.
    assert "GovernedProposalHumanReviewProjection" in source
    assert "GovernedProposalLifecycle(" not in source
    assert "GovernedProposalInbox(" not in source

    inbox = GovernedProposalInbox()
    lifecycle = GovernedProposalLifecycle(inbox)
    projection = GovernedProposalHumanReviewProjection(
        lifecycle=lifecycle,
        proposal_lookup=inbox.find,
    )
    first = _offered(inbox, lifecycle, "e1-b-s1-b-first")

    transport = seam_type(projection=projection)

    # Identity is retained only as an exact presented reference; the proposal itself
    # remains owned by the canonical inbox/lifecycle.
    assert transport.retain_presented_proposal_reference(first.proposal_id) is True
    accepted = transport.review_presented_proposal(
        response="Acepto esta propuesta.",
        observed_at=NOW,
    )
    assert accepted is not None
    assert accepted.proposal_id == first.proposal_id
    assert accepted.state is ProposalState.ACCEPTED

    # Successful terminal disposition consumes only that transport reference.
    assert transport.review_presented_proposal(
        response="Acepto esta propuesta.",
        observed_at=NOW,
    ) is None

    # More than one unresolved presented reference is ambiguous and must fail closed.
    second = _offered(inbox, lifecycle, "e1-b-s1-b-second")
    third = _offered(inbox, lifecycle, "e1-b-s1-b-third")
    assert transport.retain_presented_proposal_reference(second.proposal_id) is True
    assert transport.retain_presented_proposal_reference(third.proposal_id) is True
    assert transport.review_presented_proposal(
        response="Descarto esta propuesta.",
        observed_at=NOW,
    ) is None
    assert inbox.find(second.proposal_id).state is ProposalState.OFFERED
    assert inbox.find(third.proposal_id).state is ProposalState.OFFERED

    # No proposal semantics, lookup heuristics, persistence, or downstream authority.
    forbidden = (
        "latest",
        "title",
        "summary",
        "unique_offered",
        "governedproposalinbox(",
        "governedproposallifecycle(",
        "planning",
        "authorization",
        "execute_",
        "remember_governed_learning",
        "subprocess",
        "requests.",
        "self_modif",
    )
    assert not any(token in lowered for token in forbidden)
