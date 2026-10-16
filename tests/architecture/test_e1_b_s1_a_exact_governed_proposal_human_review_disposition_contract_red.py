from __future__ import annotations

import importlib
import inspect
from datetime import datetime, timezone

import pytest

from app.governed_proposal_lifecycle import GovernedProposalLifecycle
from domain.governed_proposal import GovernedProposal, ProposalPriority, ProposalState
from domain.governed_proposal_inbox import GovernedProposalInbox

SEAM_MODULE = "app.governed_proposal_human_review_projection"
SEAM_TYPE = "GovernedProposalHumanReviewProjection"
NOW = datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)


def test_red_exact_governed_proposal_human_review_disposition_contract() -> None:
    """RED: bind explicit human review to the existing proposal lifecycle only."""
    try:
        module = importlib.import_module(SEAM_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: an OFFERED governed proposal has no bounded explicit-human-review "
            "projection into the existing GovernedProposalLifecycle disposition owner"
        )

    seam_type = getattr(module, SEAM_TYPE, None)
    assert seam_type is not None, (
        "RED: bounded proposal human-review projection missing"
    )

    source = inspect.getsource(seam_type)
    lowered = source.casefold()

    # Existing lifecycle remains the sole disposition owner.
    assert "GovernedProposalLifecycle" in source
    assert "GovernedProposalInbox(" not in source
    assert "GovernedProposalModel(" not in source

    inbox = GovernedProposalInbox()
    lifecycle = GovernedProposalLifecycle(inbox)
    proposal = GovernedProposal(
        proposal_id="e1-b-s1-a-proposal",
        source_id="self_improvement",
        title="Governed improvement proposal",
        summary="Review this bounded proposal.",
        category="self_improvement",
        relevance_score=90,
        priority=ProposalPriority.HIGH,
        created_at=NOW,
    )
    inbox.enqueue(proposal, observed_at=NOW)
    lifecycle.offer(proposal.proposal_id, observed_at=NOW)

    projector = seam_type(lifecycle=lifecycle, proposal_lookup=inbox.find)

    # Explicit positive review disposes only the exact OFFERED proposal.
    accepted = projector.review(
        proposal_id=proposal.proposal_id,
        response="Acepto esta propuesta.",
        observed_at=NOW,
    )
    assert accepted is not None
    assert accepted.proposal_id == proposal.proposal_id
    assert accepted.state is ProposalState.ACCEPTED

    # A different exact proposal can be explicitly dismissed.
    second = GovernedProposal(
        proposal_id="e1-b-s1-a-dismiss",
        source_id="self_improvement",
        title="Second governed improvement proposal",
        summary="Review this second bounded proposal.",
        category="self_improvement",
        relevance_score=80,
        priority=ProposalPriority.NORMAL,
        created_at=NOW,
    )
    inbox.enqueue(second, observed_at=NOW)
    lifecycle.offer(second.proposal_id, observed_at=NOW)
    dismissed = projector.review(
        proposal_id=second.proposal_id,
        response="Descarto esta propuesta.",
        observed_at=NOW,
    )
    assert dismissed is not None
    assert dismissed.proposal_id == second.proposal_id
    assert dismissed.state is ProposalState.DISMISSED

    # Ambiguous text must fail closed and leave the exact proposal unchanged.
    third = GovernedProposal(
        proposal_id="e1-b-s1-a-ambiguous",
        source_id="self_improvement",
        title="Third governed improvement proposal",
        summary="Review this third bounded proposal.",
        category="self_improvement",
        relevance_score=75,
        priority=ProposalPriority.NORMAL,
        created_at=NOW,
    )
    inbox.enqueue(third, observed_at=NOW)
    lifecycle.offer(third.proposal_id, observed_at=NOW)
    assert projector.review(
        proposal_id=third.proposal_id,
        response="Bueno, veremos.",
        observed_at=NOW,
    ) is None
    assert inbox.find(third.proposal_id).state is ProposalState.OFFERED

    # Human review is disposition only: no downstream authority is gained.
    forbidden = (
        "execute_authorized",
        "execute_certified",
        "remember_governed_learning",
        "officialmemorygateway",
        "planning",
        "authorization",
        "subprocess",
        "requests.",
        "self_modif",
    )
    assert not any(token in lowered for token in forbidden)
