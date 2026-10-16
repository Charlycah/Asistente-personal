from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.governed_information_normalizer import (
    GovernedInformationNormalizer,
    InformationVerificationStatus,
    NormalizedInformationKind,
    RawGovernedInformation,
)
from app.governed_information_sources import (
    GovernedInformationSources,
    InformationRegion,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


def _raw(**overrides):
    values = {
        "source_id": "nasa",
        "external_id": " Artemis II / Update ",
        "title": "  NASA   confirma   novedades de Artemis II  ",
        "topics": frozenset(
            {InterestTopic.SPACE_EXPLORATION, InterestTopic.NASA_MISSIONS}
        ),
        "kind": NormalizedInformationKind.DISCOVERY,
        "verification": InformationVerificationStatus.CONFIRMED,
        "tags": ("Official Announcement", "space", "space"),
    }
    values.update(overrides)
    return RawGovernedInformation(**values)


def test_normalizer_creates_stable_canonical_contract() -> None:
    normalizer = GovernedInformationNormalizer(GovernedInformationSources())

    result = normalizer.normalize(_raw())

    assert result.canonical_id == "nasa:artemis-ii-update"
    assert result.title == "NASA confirma novedades de Artemis II"
    assert result.tags == ("official-announcement", "space")
    assert result.source_confidence == 98
    assert result.region is InformationRegion.GLOBAL


def test_normalizer_converts_dates_to_utc() -> None:
    local = datetime(2026, 7, 29, 9, tzinfo=timezone(timedelta(hours=-3)))
    result = GovernedInformationNormalizer(
        GovernedInformationSources()
    ).normalize(_raw(published_at=local))

    assert result.published_at == datetime(2026, 7, 29, 12, tzinfo=timezone.utc)


def test_normalizer_infers_most_specific_source_region() -> None:
    raw = RawGovernedInformation(
        source_id="cultura_caba",
        external_id="evento-1",
        title="Actividad gratuita en museo",
        topics=frozenset(
            {InterestTopic.MUSEUMS, InterestTopic.FREE_ACTIVITIES}
        ),
    )

    result = GovernedInformationNormalizer(
        GovernedInformationSources()
    ).normalize(raw)

    assert result.region is InformationRegion.CABA


def test_normalizer_preserves_explicit_region() -> None:
    result = GovernedInformationNormalizer(
        GovernedInformationSources()
    ).normalize(_raw(region=InformationRegion.ARGENTINA))

    assert result.region is InformationRegion.ARGENTINA


def test_normalizer_rejects_topics_not_governed_by_source() -> None:
    normalizer = GovernedInformationNormalizer(GovernedInformationSources())

    with pytest.raises(ValueError, match="undeclared source topics"):
        normalizer.normalize(_raw(topics=frozenset({InterestTopic.BOCA_JUNIORS})))


def test_normalized_information_converts_to_existing_candidate() -> None:
    candidate = GovernedInformationNormalizer(
        GovernedInformationSources()
    ).normalize_to_candidate(_raw(importance=9, time_sensitive=True))

    assert candidate.title == "NASA confirma novedades de Artemis II"
    assert candidate.importance == 9
    assert candidate.time_sensitive is True


def test_gateway_owns_single_normalizer_and_exposes_it() -> None:
    class Runtime:
        pass

    gateway = OfficialConversationGateway(Runtime())
    result = gateway.normalize_information(_raw())

    assert gateway.governed_information_normalizer.schema_version == "m343.8"
    assert result.canonical_id == "nasa:artemis-ii-update"


def test_m343_8_adds_no_network_or_parallel_gateway() -> None:
    path = Path("app/governed_information_normalizer.py")
    source = path.read_text(encoding="utf-8")
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
    assert "class OfficialConversationGateway" not in source
    assert "network_enabled=False" in source
