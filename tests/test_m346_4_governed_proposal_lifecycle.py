from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_proposal import ProposalPriority, ProposalState

NOW = datetime(2026, 7, 30, 0, 0, tzinfo=timezone.utc)


class Runtime:
    pass


def _pending(
    gateway: OfficialConversationGateway,
    proposal_id: str,
    *,
    expires_at: datetime | None = None,
):
    proposal = gateway.create_governed_proposal(
        proposal_id=proposal_id,
        source_id="nasa",
        title=f"Proposal {proposal_id}",
        summary="Governed household proposal.",
        category="space",
        relevance_score=90,
        priority=ProposalPriority.HIGH,
        created_at=NOW,
        expires_at=expires_at,
    )
    return gateway.enqueue_governed_proposal(proposal, observed_at=NOW)


def test_gateway_exposes_single_canonical_lifecycle_authority() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_proposal_lifecycle

    assert snapshot.schema_version == "m346.4"
    assert snapshot.authority == (
        "app.governed_proposal_lifecycle:GovernedProposalLifecycle"
    )
    assert snapshot.inbox_authority == gateway.governed_proposal_inbox.authority
    assert snapshot.autonomous_execution_enabled is False
    assert snapshot.conversational_delivery_enabled is False
    assert snapshot.persistence_enabled is False


def test_gateway_runs_pending_offered_accepted_lifecycle() -> None:
    gateway = OfficialConversationGateway(Runtime())
    _pending(gateway, "accepted")

    offered = gateway.offer_governed_proposal("accepted", observed_at=NOW)
    accepted = gateway.accept_governed_proposal("accepted", observed_at=NOW)

    assert offered.state is ProposalState.OFFERED
    assert accepted.state is ProposalState.ACCEPTED
    assert gateway.find_governed_proposal("accepted") is accepted
    assert accepted.is_terminal is True


def test_gateway_can_dismiss_pending_or_offered_proposal() -> None:
    gateway = OfficialConversationGateway(Runtime())
    _pending(gateway, "pending-dismiss")
    _pending(gateway, "offered-dismiss")
    gateway.offer_governed_proposal("offered-dismiss", observed_at=NOW)

    pending = gateway.dismiss_governed_proposal("pending-dismiss", observed_at=NOW)
    offered = gateway.dismiss_governed_proposal("offered-dismiss", observed_at=NOW)

    assert pending.state is ProposalState.DISMISSED
    assert offered.state is ProposalState.DISMISSED


def test_lifecycle_rejects_unknown_and_invalid_transitions() -> None:
    gateway = OfficialConversationGateway(Runtime())
    _pending(gateway, "invalid")

    with pytest.raises(DomainError, match="unknown proposal_id"):
        gateway.offer_governed_proposal("missing", observed_at=NOW)
    with pytest.raises(DomainError, match="invalid proposal transition"):
        gateway.accept_governed_proposal("invalid", observed_at=NOW)


def test_expiration_covers_pending_and_offered_without_delivery() -> None:
    gateway = OfficialConversationGateway(Runtime())
    expiry = NOW + timedelta(minutes=5)
    _pending(gateway, "pending-expiry", expires_at=expiry)
    _pending(gateway, "offered-expiry", expires_at=expiry)
    gateway.offer_governed_proposal("offered-expiry", observed_at=NOW)

    expired = gateway.expire_governed_proposals(
        observed_at=NOW + timedelta(minutes=6)
    )

    assert {item.proposal_id for item in expired} == {
        "pending-expiry",
        "offered-expiry",
    }
    assert all(item.state is ProposalState.EXPIRED for item in expired)
    assert gateway.pending_governed_proposals(
        observed_at=NOW + timedelta(minutes=6)
    ) == ()


def test_lifecycle_has_no_scheduler_disk_credentials_or_speech_authority() -> None:
    source = Path("app/governed_proposal_lifecycle.py").read_text(
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
    assert "speak" not in source.lower()
    assert "notify" not in source.lower()
    assert "scheduler" not in source.lower()
