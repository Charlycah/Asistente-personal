from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_proposal import ProposalPriority, ProposalState

NOW = datetime(2026, 7, 29, 21, 0, tzinfo=timezone.utc)


class Runtime:
    pass


def _proposal(
    gateway: OfficialConversationGateway,
    proposal_id: str,
    *,
    priority: ProposalPriority = ProposalPriority.NORMAL,
    relevance_score: int = 80,
    expires_at: datetime | None = None,
):
    return gateway.create_governed_proposal(
        proposal_id=proposal_id,
        source_id="nasa",
        title=f"Propuesta {proposal_id}",
        summary="Información gobernada relevante para el hogar.",
        category="space",
        relevance_score=relevance_score,
        priority=priority,
        created_at=NOW,
        expires_at=expires_at,
    )


def test_gateway_exposes_single_canonical_local_proposal_inbox() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_proposal_inbox

    assert snapshot.schema_version == "m346.1"
    assert snapshot.authority == (
        "domain.governed_proposal_inbox:GovernedProposalInbox"
    )
    assert snapshot.persistence_enabled is False
    assert snapshot.autonomous_delivery_enabled is False
    assert snapshot.total_proposals == 0
    assert snapshot.pending_proposals == 0


def test_enqueue_transitions_new_proposal_to_pending() -> None:
    gateway = OfficialConversationGateway(Runtime())
    proposal = _proposal(gateway, "proposal-1")

    pending = gateway.enqueue_governed_proposal(proposal, observed_at=NOW)

    assert proposal.state is ProposalState.NEW
    assert pending.state is ProposalState.PENDING
    assert gateway.find_governed_proposal("proposal-1") is pending
    assert gateway.governed_proposal_inbox.pending_proposals == 1


def test_inbox_rejects_duplicates_and_non_new_entries() -> None:
    gateway = OfficialConversationGateway(Runtime())
    proposal = _proposal(gateway, "proposal-duplicate")
    pending = gateway.enqueue_governed_proposal(proposal, observed_at=NOW)

    with pytest.raises(DomainError, match="duplicate proposal_id"):
        gateway.enqueue_governed_proposal(proposal, observed_at=NOW)

    other_gateway = OfficialConversationGateway(Runtime())
    with pytest.raises(DomainError, match="only NEW proposals"):
        other_gateway.enqueue_governed_proposal(pending, observed_at=NOW)


def test_pending_proposals_are_ordered_by_priority_then_relevance() -> None:
    gateway = OfficialConversationGateway(Runtime())
    normal = _proposal(
        gateway,
        "normal",
        priority=ProposalPriority.NORMAL,
        relevance_score=99,
    )
    high_lower = _proposal(
        gateway,
        "high-lower",
        priority=ProposalPriority.HIGH,
        relevance_score=80,
    )
    high_higher = _proposal(
        gateway,
        "high-higher",
        priority=ProposalPriority.HIGH,
        relevance_score=95,
    )
    for proposal in (normal, high_lower, high_higher):
        gateway.enqueue_governed_proposal(proposal, observed_at=NOW)

    pending = gateway.pending_governed_proposals(observed_at=NOW)

    assert [proposal.proposal_id for proposal in pending] == [
        "high-higher",
        "high-lower",
        "normal",
    ]


def test_pending_query_expires_stale_proposals_without_offering_them() -> None:
    gateway = OfficialConversationGateway(Runtime())
    proposal = _proposal(
        gateway,
        "short-lived",
        expires_at=NOW + timedelta(minutes=10),
    )
    gateway.enqueue_governed_proposal(proposal, observed_at=NOW)

    pending = gateway.pending_governed_proposals(
        observed_at=NOW + timedelta(minutes=11)
    )

    assert pending == ()
    stored = gateway.find_governed_proposal("short-lived")
    assert stored is not None
    assert stored.state is ProposalState.EXPIRED


def test_inbox_has_no_disk_scheduler_credentials_or_conversation_authority() -> None:
    source = Path("domain/governed_proposal_inbox.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_roots.isdisjoint(
        {"asyncio", "json", "pathlib", "sqlite3", "subprocess", "threading"}
    )
    assert "credentials.json" not in source
    assert "OfficialConversationGateway(" not in source
    assert "speak" not in source.lower()
    assert "notify" not in source.lower()
