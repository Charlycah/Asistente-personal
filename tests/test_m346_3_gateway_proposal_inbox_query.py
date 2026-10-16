from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.governed_proposal_inbox_query import GovernedProposalInboxQueryRequest
from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_proposal import ProposalPriority, ProposalState

NOW = datetime(2026, 7, 29, 22, 30, tzinfo=timezone.utc)


class Runtime:
    pass


def _enqueue(
    gateway: OfficialConversationGateway,
    *,
    proposal_id: str,
    source_id: str = "nasa",
    category: str = "space",
    priority: ProposalPriority = ProposalPriority.NORMAL,
    relevance_score: int = 80,
    expires_at=None,
):
    proposal = gateway.create_governed_proposal(
        proposal_id=proposal_id,
        source_id=source_id,
        title=f"Proposal {proposal_id}",
        summary="Governed household proposal.",
        category=category,
        relevance_score=relevance_score,
        priority=priority,
        created_at=NOW,
        expires_at=expires_at,
    )
    return gateway.enqueue_governed_proposal(proposal, observed_at=NOW)


def test_gateway_exposes_single_read_only_inbox_query_authority() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_proposal_inbox_query

    assert snapshot.schema_version == "m346.3"
    assert snapshot.authority == (
        "app.governed_proposal_inbox_query:GovernedProposalInboxQuery"
    )
    assert snapshot.inbox_authority == gateway.governed_proposal_inbox.authority
    assert snapshot.read_only is True
    assert snapshot.autonomous_execution_enabled is False
    assert snapshot.conversational_delivery_enabled is False


def test_gateway_queries_pending_proposals_in_canonical_order() -> None:
    gateway = OfficialConversationGateway(Runtime())
    normal = _enqueue(gateway, proposal_id="normal", relevance_score=99)
    high = _enqueue(
        gateway,
        proposal_id="high",
        priority=ProposalPriority.HIGH,
        relevance_score=70,
    )

    result = gateway.query_governed_proposal_inbox(observed_at=NOW)

    assert result.proposals == (high, normal)
    assert result.total_pending == 2
    assert result.matched == 2
    assert result.next_proposal == high
    assert all(item.state is ProposalState.PENDING for item in result.proposals)


def test_query_filters_without_modifying_proposal_state() -> None:
    gateway = OfficialConversationGateway(Runtime())
    nasa = _enqueue(gateway, proposal_id="nasa", source_id="nasa")
    _enqueue(
        gateway,
        proposal_id="culture",
        source_id="cultura_caba",
        category="culture",
    )
    request = GovernedProposalInboxQueryRequest(
        source_id="nasa",
        category="space",
        minimum_priority=ProposalPriority.NORMAL,
        limit=1,
    )

    result = gateway.query_governed_proposal_inbox(request, observed_at=NOW)

    assert result.proposals == (nasa,)
    assert result.total_pending == 2
    assert result.matched == 1
    assert gateway.find_governed_proposal("nasa").state is ProposalState.PENDING


def test_query_excludes_and_expires_stale_pending_proposals() -> None:
    gateway = OfficialConversationGateway(Runtime())
    stale = _enqueue(
        gateway,
        proposal_id="stale",
        expires_at=NOW + timedelta(minutes=1),
    )

    result = gateway.query_governed_proposal_inbox(
        observed_at=NOW + timedelta(minutes=2)
    )

    assert result.proposals == ()
    assert result.total_pending == 0
    assert result.next_proposal is None
    stored = gateway.find_governed_proposal(stale.proposal_id)
    assert stored.state is ProposalState.EXPIRED


def test_query_request_rejects_invalid_filters() -> None:
    with pytest.raises(DomainError):
        GovernedProposalInboxQueryRequest(source_id=" ")
    with pytest.raises(DomainError):
        GovernedProposalInboxQueryRequest(limit=0)
    with pytest.raises(DomainError):
        GovernedProposalInboxQueryRequest(minimum_priority="high")


def test_query_has_no_scheduler_disk_credentials_or_speech_authority() -> None:
    source = Path("app/governed_proposal_inbox_query.py").read_text(
        encoding="utf-8"
    )
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
    assert "transition_to" not in source
    assert "speak" not in source.lower()
    assert "notify" not in source.lower()
    assert "scheduler" not in source.lower()
