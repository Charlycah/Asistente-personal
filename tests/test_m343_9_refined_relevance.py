from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.governed_information_normalizer import (
    GovernedInformationNormalizer,
    InformationVerificationStatus,
    NormalizedInformationKind,
    RawGovernedInformation,
)
from app.governed_information_sources import GovernedInformationSources
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic, PersonalInterestCenter
from app.relevance_evaluator import RelevanceCandidate, RelevanceEvaluator

NOW = datetime(2026, 7, 29, 14, tzinfo=timezone.utc)


def test_legacy_candidate_scores_remain_compatible() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    decision = evaluator.evaluate(
        RelevanceCandidate(
            title="Boca juega esta noche",
            topics=frozenset({InterestTopic.BOCA_JUNIORS}),
            time_sensitive=True,
            importance=10,
        ),
        now=NOW,
    )

    assert decision.scores == {"Carlos": 70, "Cristina": 0}


def test_very_high_personal_priority_outweighs_generic_interest() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    decision = evaluator.evaluate(
        RelevanceCandidate(
            title="Estreno de ciencia ficción dura",
            topics=frozenset({InterestTopic.HARD_SCIENCE_FICTION}),
        ),
        now=NOW,
    )

    assert decision.scores["Carlos"] == 65
    assert decision.breakdowns["Carlos"].priority_bonus == 10
    assert "high_personal_priority" in decision.reasons


def test_governed_source_confidence_and_confirmation_are_explainable() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    decision = evaluator.evaluate(
        RelevanceCandidate(
            title="NASA confirma misión",
            topics=frozenset({InterestTopic.NASA_MISSIONS}),
            source_confidence=98,
            verification="confirmed",
        ),
        now=NOW,
    )

    breakdown = decision.breakdowns["Carlos"]
    assert breakdown.source_quality_adjustment == 5
    assert breakdown.verification_adjustment == 5
    assert breakdown.total == 65


def test_unverified_low_confidence_information_is_penalized() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    decision = evaluator.evaluate(
        RelevanceCandidate(
            title="Rumor tecnológico",
            topics=frozenset({InterestTopic.TECHNOLOGY}),
            source_confidence=40,
            verification="unverified",
        ),
        now=NOW,
    )

    assert decision.scores["Carlos"] == 35
    assert decision.should_share is False


def test_fresh_information_scores_above_stale_information() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    fresh = RelevanceCandidate(
        title="Novedad de programación",
        topics=frozenset({InterestTopic.PROGRAMMING}),
        published_at=NOW - timedelta(hours=2),
    )
    stale = RelevanceCandidate(
        title="Novedad antigua de programación",
        topics=frozenset({InterestTopic.PROGRAMMING}),
        published_at=NOW - timedelta(days=100),
    )

    fresh_decision = evaluator.evaluate(fresh, now=NOW)
    stale_decision = evaluator.evaluate(stale, now=NOW)

    assert fresh_decision.scores["Carlos"] == 60
    assert stale_decision.scores["Carlos"] == 45


def test_upcoming_event_receives_temporal_bonus() -> None:
    evaluator = RelevanceEvaluator(PersonalInterestCenter())
    decision = evaluator.evaluate(
        RelevanceCandidate(
            title="Próximo estreno",
            topics=frozenset({InterestTopic.RELEASES}),
            information_kind="release",
            event_at=NOW + timedelta(days=10),
        ),
        now=NOW,
    )

    breakdown = decision.breakdowns["Carlos"]
    assert breakdown.priority_bonus == 5
    assert breakdown.freshness_adjustment == 5
    assert breakdown.kind_adjustment == 4
    assert breakdown.total == 69


def test_normalized_information_transfers_all_relevance_metadata() -> None:
    raw = RawGovernedInformation(
        source_id="nasa",
        external_id="mission-update",
        title="NASA confirma una misión",
        topics=frozenset({InterestTopic.NASA_MISSIONS}),
        kind=NormalizedInformationKind.DISCOVERY,
        verification=InformationVerificationStatus.CONFIRMED,
        published_at=NOW - timedelta(hours=1),
    )
    candidate = GovernedInformationNormalizer(
        GovernedInformationSources()
    ).normalize_to_candidate(raw)

    assert candidate.source_confidence == 98
    assert candidate.verification == "confirmed"
    assert candidate.information_kind == "discovery"
    assert candidate.published_at == NOW - timedelta(hours=1)
    assert candidate.region == "global"


def test_m343_9_keeps_single_evaluator_authority_and_no_external_execution() -> None:
    path = Path("app/relevance_evaluator.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )

    assert imported_roots.isdisjoint(
        {"asyncio", "requests", "socket", "subprocess", "threading", "urllib"}
    )
    assert gateway_source.count("RelevanceEvaluator(") == 1

    class Runtime:
        bootstrap = object()
        history = ()
        traces = ()

    gateway = OfficialConversationGateway(Runtime())
    assert gateway.relevance_evaluator.schema_version == "m343.3"
