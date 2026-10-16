from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.governed_information_sources import (
    DEFAULT_GOVERNED_INFORMATION_SOURCES,
    GovernedInformationItem,
    GovernedInformationSource,
    GovernedInformationSources,
    InformationSourceKind,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


def test_default_sources_are_declared_and_inactive() -> None:
    registry = GovernedInformationSources()

    assert len(registry.snapshot.sources) == 6
    assert registry.snapshot.network_enabled is False
    assert registry.snapshot.automatic_fetch_enabled is False
    assert all(not source.network_enabled for source in registry.snapshot.sources)
    assert all(
        not source.automatic_fetch_enabled for source in registry.snapshot.sources
    )


def test_default_sources_cover_shared_and_personal_interests() -> None:
    topics = frozenset(
        topic
        for source in DEFAULT_GOVERNED_INFORMATION_SOURCES
        for topic in source.topics
    )

    assert InterestTopic.NASA_MISSIONS in topics
    assert InterestTopic.CULTURE_CABA in topics
    assert InterestTopic.PROGRAMMING in topics
    assert InterestTopic.CINEMA in topics
    assert InterestTopic.SERIES in topics
    assert InterestTopic.BOCA_JUNIORS in topics
    assert InterestTopic.RIVER_PLATE in topics


def test_source_rejects_active_network_or_automatic_fetch() -> None:
    with pytest.raises(ValueError, match="must remain inactive"):
        GovernedInformationSource(
            source_id="unsafe",
            name="Unsafe",
            kind=InformationSourceKind.EDITORIAL,
            topics=frozenset({InterestTopic.TECHNOLOGY}),
            network_enabled=True,
        )


def test_accept_converts_governed_item_to_relevance_candidate() -> None:
    registry = GovernedInformationSources()
    item = GovernedInformationItem(
        source_id="cultura_caba",
        external_id="event-1",
        title="Concierto gratuito en CABA",
        topics=frozenset(
            {InterestTopic.CULTURE_CABA, InterestTopic.FREE_ACTIVITIES}
        ),
        location="CABA",
        is_free=True,
        time_sensitive=True,
        importance=5,
    )

    candidate = registry.accept(item)

    assert candidate.title == item.title
    assert candidate.topics == item.topics
    assert candidate.location == "CABA"
    assert candidate.is_free is True


def test_accept_rejects_unknown_source() -> None:
    registry = GovernedInformationSources()
    item = GovernedInformationItem(
        source_id="unknown",
        external_id="item-1",
        title="Unknown item",
        topics=frozenset({InterestTopic.TECHNOLOGY}),
    )

    with pytest.raises(KeyError, match="unknown governed information source"):
        registry.accept(item)


def test_accept_rejects_topics_not_declared_by_source() -> None:
    registry = GovernedInformationSources()
    item = GovernedInformationItem(
        source_id="nasa",
        external_id="item-2",
        title="Unrelated sports item",
        topics=frozenset({InterestTopic.BOCA_JUNIORS}),
    )

    with pytest.raises(ValueError, match="undeclared source topics"):
        registry.accept(item)


def test_gateway_exposes_same_governed_source_registry() -> None:
    gateway = object.__new__(OfficialConversationGateway)

    class Runtime:
        pass

    OfficialConversationGateway.__init__(gateway, Runtime())

    snapshot = gateway.governed_information_sources

    assert snapshot.schema_version == "m343.5"
    assert snapshot.authority.endswith(":OfficialConversationGateway")


def test_gateway_accepts_item_before_relevance_and_initiative() -> None:
    gateway = object.__new__(OfficialConversationGateway)

    class Runtime:
        pass

    OfficialConversationGateway.__init__(gateway, Runtime())
    item = GovernedInformationItem(
        source_id="sports_editorial",
        external_id="boca-1",
        title="Boca juega una final",
        topics=frozenset({InterestTopic.BOCA_JUNIORS}),
        time_sensitive=True,
        importance=20,
    )

    candidate = gateway.accept_information_item(item)
    relevance = gateway.evaluate_relevance(candidate)
    initiative = gateway.propose_initiative(candidate)

    assert relevance.recipient.value == "carlos"
    assert initiative.recipient.value == "carlos"
    assert initiative.should_speak is True


def test_m343_5_has_no_network_scheduler_or_background_execution() -> None:
    source = Path("app/governed_information_sources.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_roots.isdisjoint(
        {"asyncio", "requests", "socket", "subprocess", "threading", "urllib"}
    )
    assert "schedule" not in source.casefold()
    assert "fetch(" not in source
