from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.governed_proposal_presentation_policy import GovernedPresentationContext
from app.official_conversation_gateway import OfficialConversationGateway
from domain.governed_proposal import ProposalPriority, ProposalState

NOW = datetime(2026, 7, 29, 18, 0, tzinfo=timezone.utc)


def _gateway():
    return OfficialConversationGateway.__new__(OfficialConversationGateway)


def _configure(gateway):
    from app.governed_proposal_presentation_policy import (
        GovernedProposalPresentationPolicy,
    )
    from domain.governed_proposal import GovernedProposalModel
    from domain.governed_proposal_inbox import GovernedProposalInbox

    gateway._governed_proposal_model = GovernedProposalModel()
    gateway._governed_proposal_inbox = GovernedProposalInbox()
    gateway._governed_proposal_presentation_policy = (
        GovernedProposalPresentationPolicy()
    )
    return gateway


def _proposal(gateway, proposal_id="p-1", **overrides):
    fields = {
        "proposal_id": proposal_id,
        "source_id": "source",
        "title": "Title",
        "summary": "Summary",
        "category": "general",
        "relevance_score": 72,
        "priority": ProposalPriority.LOW,
        "created_at": NOW,
        "expires_at": NOW + timedelta(days=1),
    }
    fields.update(overrides)
    proposal = gateway._governed_proposal_model.create(**fields)
    return gateway._governed_proposal_inbox.enqueue(proposal, observed_at=NOW)


def test_m346_5_refines_priority_without_mutating_stored_proposal():
    gateway = _configure(_gateway())
    proposal = _proposal(gateway)

    decision = gateway.evaluate_governed_proposal_presentation(
        proposal.proposal_id,
        observed_at=NOW,
    )

    assert decision.effective_priority is ProposalPriority.NORMAL
    assert gateway._governed_proposal_inbox.find(proposal.proposal_id).priority is (
        ProposalPriority.LOW
    )


def test_m346_5_urgent_expiry_raises_effective_priority_one_level():
    gateway = _configure(_gateway())
    proposal = _proposal(
        gateway,
        relevance_score=72,
        priority=ProposalPriority.NORMAL,
        expires_at=NOW + timedelta(minutes=30),
    )

    decision = gateway.evaluate_governed_proposal_presentation(
        proposal.proposal_id,
        observed_at=NOW,
    )

    assert decision.effective_priority is ProposalPriority.HIGH


def test_m346_5_stale_proposal_is_downgraded_one_level():
    gateway = _configure(_gateway())
    proposal = _proposal(
        gateway,
        relevance_score=40,
        priority=ProposalPriority.HIGH,
        created_at=NOW - timedelta(days=8),
        expires_at=NOW + timedelta(days=1),
    )

    decision = gateway.evaluate_governed_proposal_presentation(
        proposal.proposal_id,
        observed_at=NOW,
    )

    assert decision.effective_priority is ProposalPriority.NORMAL


def test_m346_5_policy_never_presents_during_user_turn_or_silence():
    gateway = _configure(_gateway())
    proposal = _proposal(gateway, relevance_score=99)

    active = gateway.evaluate_governed_proposal_presentation(
        proposal.proposal_id,
        GovernedPresentationContext(user_turn_active=True),
        observed_at=NOW,
    )
    silent = gateway.evaluate_governed_proposal_presentation(
        proposal.proposal_id,
        GovernedPresentationContext(silence_requested=True),
        observed_at=NOW,
    )

    assert not active.presentable and active.reason == "user_turn_active"
    assert not silent.presentable and silent.reason == "silence_requested"


def test_m346_5_next_presentable_skips_items_below_policy():
    gateway = _configure(_gateway())
    _proposal(gateway, "low", relevance_score=45, priority=ProposalPriority.LOW)
    high = _proposal(
        gateway,
        "high",
        relevance_score=90,
        priority=ProposalPriority.HIGH,
    )

    decision = gateway.next_presentable_governed_proposal(
        GovernedPresentationContext(minimum_priority=ProposalPriority.HIGH),
        observed_at=NOW,
    )

    assert decision is not None
    assert decision.proposal.proposal_id == high.proposal_id
    assert decision.proposal.state is ProposalState.PENDING


def test_m346_5_policy_is_read_only_and_gateway_is_only_entry_point():
    source = Path("app/governed_proposal_presentation_policy.py").read_text()
    tree = ast.parse(source)
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    assert "transition" not in calls
    assert "offer" not in calls
    assert "accept" not in calls
    assert "dismiss" not in calls
    snapshot = _configure(_gateway()).governed_proposal_presentation_policy
    assert snapshot.schema_version == "m346.5"
    assert snapshot.mutates_proposals is False
    assert snapshot.autonomous_execution_enabled is False
    assert snapshot.conversational_delivery_enabled is False
