from __future__ import annotations

import ast
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app.apple_audiovisual_governed_source import (
    APPLE_SEARCH_ENDPOINT,
    AppleAudiovisualGovernedSourceAdapter,
)
from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligenceStatus,
)
from app.governed_information_sources import InformationRegion
from app.governed_source_query import GovernedSourceQuery, GovernedSourceQueryStatus
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


def audiovisual_query(**changes) -> GovernedSourceQuery:
    values = {
        "source_id": "apple_audiovisual",
        "topics": frozenset({InterestTopic.RELEASES, InterestTopic.SCIENCE_FICTION}),
        "query_text": "ciencia ficción",
        "limit": 3,
        "region": InformationRegion.ARGENTINA,
    }
    values.update(changes)
    return GovernedSourceQuery(**values)


def apple_payload() -> bytes:
    return json.dumps(
        {
            "resultCount": 3,
            "results": [
                {
                    "trackId": 101,
                    "trackName": "Órbita profunda",
                    "kind": "feature-movie",
                    "primaryGenreName": "Science Fiction & Fantasy",
                    "longDescription": (
                        "Exploración espacial científicamente plausible."
                    ),
                    "releaseDate": "2026-07-10T07:00:00Z",
                    "trackViewUrl": "https://tv.apple.com/ar/movie/orbita/101",
                },
                {
                    "trackId": 102,
                    "trackName": "Horizonte de eventos",
                    "kind": "feature-movie",
                    "primaryGenreName": "Science Fiction & Fantasy",
                    "releaseDate": "2026-07-17T07:00:00Z",
                    "trackViewUrl": "https://tv.apple.com/ar/movie/horizonte/102",
                },
                {
                    "trackId": 103,
                    "trackName": "Cosmos observado",
                    "kind": "feature-movie",
                    "primaryGenreName": "Documentary",
                    "releaseDate": "2026-07-20T07:00:00Z",
                    "trackViewUrl": "https://tv.apple.com/ar/movie/cosmos/103",
                },
            ],
        }
    ).encode("utf-8")


def test_apple_audiovisual_source_is_real_official_and_not_automatic() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.apple_audiovisual_governed_source

    assert snapshot.schema_version == "m345.3"
    assert snapshot.source_id == "apple_audiovisual"
    assert snapshot.endpoint == APPLE_SEARCH_ENDPOINT
    assert snapshot.network_enabled is True
    assert snapshot.automatic_fetch_enabled is False
    assert snapshot.credentials_required is False
    assert snapshot.official_public_source is True
    assert snapshot.supported_media == ("movie", "tvShow")
    assert gateway.governed_source_query_executor.registered_sources == ()


def test_explicit_enable_registers_audiovisual_in_canonical_executor() -> None:
    gateway = OfficialConversationGateway(Runtime())

    gateway.enable_apple_audiovisual_governed_source()

    assert gateway.governed_source_query_executor.registered_sources == (
        "apple_audiovisual",
    )
    assert gateway.governed_source_query_executor.network_enabled is True


def test_adapter_builds_governed_argentine_movie_search_and_normalizes() -> None:
    observed = {}

    def transport(url: str, timeout: float) -> bytes:
        observed["url"] = url
        observed["timeout"] = timeout
        return apple_payload()

    adapter = AppleAudiovisualGovernedSourceAdapter(transport=transport)
    items = adapter.execute(audiovisual_query(limit=2, timeout_seconds=6.5))
    parameters = parse_qs(urlparse(observed["url"]).query)

    assert observed["timeout"] == 6.5
    assert observed["url"].startswith(APPLE_SEARCH_ENDPOINT)
    assert parameters["country"] == ["AR"]
    assert parameters["media"] == ["movie"]
    assert parameters["limit"] == ["2"]
    assert len(items) == 2
    assert items[0]["source_id"] == "apple_audiovisual"
    assert items[0]["title"] == "Órbita profunda"
    assert items[0]["information_kind"] == "release"
    assert items[0]["verification"] == "confirmed"


def test_applied_intelligence_recognizes_audiovisual_topics() -> None:
    gateway = OfficialConversationGateway(Runtime())

    interpretation = gateway.interpret_applied_conversational_intelligence(
        "Roby, buscá estrenos de ciencia ficción dura."
    )

    assert interpretation.status is AppliedConversationalIntelligenceStatus.RECOGNIZED
    assert interpretation.request is not None
    assert interpretation.request.region is InformationRegion.GLOBAL
    assert interpretation.request.query_text == "ciencia ficción dura"
    assert InterestTopic.RELEASES in interpretation.matched_topics
    assert InterestTopic.SCIENCE_FICTION in interpretation.matched_topics
    assert InterestTopic.HARD_SCIENCE_FICTION in interpretation.matched_topics


def test_audiovisual_request_runs_through_complete_governed_flow() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway._apple_audiovisual_governed_source_adapter = (
        AppleAudiovisualGovernedSourceAdapter(
            transport=lambda _url, _timeout: apple_payload()
        )
    )
    gateway.enable_apple_audiovisual_governed_source()

    result = gateway.execute_applied_conversational_intelligence(
        "Roby, buscá estrenos de ciencia ficción."
    )

    assert result.selection is not None
    assert result.selection.source is not None
    assert result.selection.source.source_id == "apple_audiovisual"
    assert result.conversational_result is not None
    assert result.conversational_result.source_result.status is (
        GovernedSourceQueryStatus.SUCCEEDED
    )
    assert result.conversational_result.items[0].normalized.region is (
        InformationRegion.ARGENTINA
    )
    assert "Encontré 3 novedades sobre ciencia ficción" in result.answer_text
    assert "para vos" in result.answer_text


def test_audiovisual_source_has_no_scheduler_credentials_or_parallel_flow() -> None:
    source = Path("app/apple_audiovisual_governed_source.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_roots.isdisjoint({"asyncio", "subprocess", "threading"})
    assert "credentials.json" not in source
    assert "class GovernedSourceQueryExecutor" not in source
    assert "OfficialConversationGateway(" not in source
