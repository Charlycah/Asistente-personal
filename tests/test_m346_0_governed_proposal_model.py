from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from domain.exceptions import DomainError
from domain.governed_proposal import ProposalPriority, ProposalState

NOW = datetime(2026, 7, 29, 20, 0, tzinfo=timezone.utc)


class Runtime:
    pass


def _proposal(gateway: OfficialConversationGateway, **overrides):
    fields = {
        "proposal_id": "proposal-nasa-webb-1",
        "source_id": "nasa",
        "title": "Nueva imagen del James Webb",
        "summary": "Una observación oficial que puede interesar en casa.",
        "category": "space",
        "relevance_score": 92,
        "priority": ProposalPriority.HIGH,
        "created_at": NOW,
        "expires_at": NOW + timedelta(days=3),
        "metadata": {"origin": "governed_source"},
    }
    fields.update(overrides)
    return gateway.create_governed_proposal(**fields)


def test_gateway_exposes_single_canonical_proposal_model() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_proposal_model

    assert snapshot.schema_version == "m346.0"
    assert snapshot.authority == "domain.governed_proposal:GovernedProposalModel"
    assert snapshot.persistence_enabled is False
    assert snapshot.autonomous_delivery_enabled is False
    assert snapshot.states == tuple(ProposalState)
    assert snapshot.priorities == tuple(ProposalPriority)


def test_gateway_creates_immutable_valid_governed_proposal() -> None:
    gateway = OfficialConversationGateway(Runtime())

    proposal = _proposal(gateway)

    assert proposal.state is ProposalState.NEW
    assert proposal.priority is ProposalPriority.HIGH
    assert proposal.metadata == {"origin": "governed_source"}
    with pytest.raises(TypeError):
        proposal.metadata["origin"] = "changed"


def test_proposal_lifecycle_accepts_only_governed_transitions() -> None:
    gateway = OfficialConversationGateway(Runtime())

    pending = _proposal(gateway).transition_to(ProposalState.PENDING, observed_at=NOW)
    offered = pending.transition_to(ProposalState.OFFERED, observed_at=NOW)
    accepted = offered.transition_to(ProposalState.ACCEPTED, observed_at=NOW)

    assert pending.state is ProposalState.PENDING
    assert offered.state is ProposalState.OFFERED
    assert accepted.state is ProposalState.ACCEPTED
    assert accepted.is_terminal is True


def test_invalid_or_terminal_transitions_are_rejected() -> None:
    gateway = OfficialConversationGateway(Runtime())
    proposal = _proposal(gateway)

    with pytest.raises(DomainError, match="invalid proposal transition"):
        proposal.transition_to(ProposalState.ACCEPTED, observed_at=NOW)

    dismissed = proposal.transition_to(ProposalState.DISMISSED, observed_at=NOW)
    with pytest.raises(DomainError, match="invalid proposal transition"):
        dismissed.transition_to(ProposalState.PENDING, observed_at=NOW)


def test_expiration_is_explicit_and_cannot_be_bypassed() -> None:
    gateway = OfficialConversationGateway(Runtime())
    proposal = _proposal(gateway, expires_at=NOW + timedelta(hours=1))
    after_expiration = NOW + timedelta(hours=2)

    assert proposal.is_expired_at(after_expiration) is True
    with pytest.raises(DomainError, match="can only transition to EXPIRED"):
        proposal.transition_to(ProposalState.PENDING, observed_at=after_expiration)

    expired = proposal.transition_to(
        ProposalState.EXPIRED, observed_at=after_expiration
    )
    assert expired.state is ProposalState.EXPIRED
    assert expired.is_terminal is True


def test_model_has_no_storage_scheduler_credentials_or_conversation_authority() -> None:
    source = Path("domain/governed_proposal.py").read_text(encoding="utf-8")
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
