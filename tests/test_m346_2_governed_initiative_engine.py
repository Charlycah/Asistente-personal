from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.governed_initiative_engine import GovernedInitiativeCandidate
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic
from app.relevance_evaluator import RelevanceCandidate
from domain.governed_proposal import ProposalPriority, ProposalState

NOW = datetime(2026, 7, 29, 22, 0, tzinfo=timezone.utc)


class Runtime:
    pass


def _candidate(*, title: str = "Nueva imagen del James Webb", importance: int = 15):
    return GovernedInitiativeCandidate(
        source_id="nasa",
        summary="NASA publicó una novedad espacial relevante para el hogar.",
        category="space",
        relevance_candidate=RelevanceCandidate(
            title=title,
            topics=frozenset({InterestTopic.SPACE_EXPLORATION}),
            importance=importance,
            source_confidence=99,
            verification="confirmed",
            information_kind="discovery",
        ),
        expires_at=NOW + timedelta(days=7),
        metadata={"origin": "governed_source"},
    )


def test_gateway_exposes_single_governed_initiative_engine() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_initiative_engine

    assert snapshot.schema_version == "m346.2"
    assert snapshot.authority == (
        "app.governed_initiative_engine:GovernedInitiativeEngine"
    )
    assert snapshot.proposal_authority == gateway.governed_proposal_model.authority
    assert snapshot.inbox_authority == gateway.governed_proposal_inbox.authority
    assert snapshot.autonomous_execution_enabled is False
    assert snapshot.conversational_delivery_enabled is False


def test_relevant_candidate_becomes_pending_governed_proposal() -> None:
    gateway = OfficialConversationGateway(Runtime())

    result = gateway.generate_governed_initiative(_candidate(), observed_at=NOW)

    assert result.accepted is True
    assert result.reason == "proposal_enqueued"
    assert result.proposal is not None
    assert result.proposal.state is ProposalState.PENDING
    assert result.proposal.source_id == "nasa"
    assert result.proposal.metadata["initiative_engine"] == "m346.2"
    assert gateway.pending_governed_proposals(observed_at=NOW) == (result.proposal,)


def test_irrelevant_candidate_is_not_created_or_enqueued() -> None:
    gateway = OfficialConversationGateway(Runtime())
    candidate = GovernedInitiativeCandidate(
        source_id="unknown",
        summary="Información sin afinidad doméstica.",
        category="other",
        relevance_candidate=RelevanceCandidate(
            title="Tema sin interés registrado",
            topics=frozenset(),
        ),
    )

    result = gateway.generate_governed_initiative(candidate, observed_at=NOW)

    assert result.accepted is False
    assert result.reason == "not_relevant_enough"
    assert result.proposal is None
    assert gateway.governed_proposal_inbox.total_proposals == 0


def test_expired_candidate_is_rejected_before_relevance_evaluation() -> None:
    gateway = OfficialConversationGateway(Runtime())
    candidate = GovernedInitiativeCandidate(
        source_id="nasa",
        summary="Información vencida.",
        category="space",
        relevance_candidate=_candidate().relevance_candidate,
        expires_at=NOW - timedelta(seconds=1),
    )

    result = gateway.generate_governed_initiative(candidate, observed_at=NOW)

    assert result.accepted is False
    assert result.reason == "candidate_expired"
    assert result.proposal is None


def test_priority_is_derived_from_canonical_relevance_score() -> None:
    gateway = OfficialConversationGateway(Runtime())

    result = gateway.generate_governed_initiative(_candidate(), observed_at=NOW)

    assert result.proposal is not None
    assert result.proposal.priority in {
        ProposalPriority.HIGH,
        ProposalPriority.CRITICAL,
    }
    assert result.proposal.relevance_score >= 80


def test_engine_has_no_scheduler_disk_credentials_or_speech_authority() -> None:
    source = Path("app/governed_initiative_engine.py").read_text(encoding="utf-8")
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
