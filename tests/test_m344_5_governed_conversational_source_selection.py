from __future__ import annotations

import ast
from pathlib import Path

from app.governed_conversational_query import GovernedConversationalQueryStatus
from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionRequest,
    GovernedConversationalSourceSelectionStatus,
)
from app.governed_information_sources import InformationRegion
from app.governed_source_query import GovernedSourceQuery
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


class NasaSelectionAdapter:
    network_enabled = True

    def execute(self, query: GovernedSourceQuery):
        return (
            {
                "external_id": "JWST-001",
                "title": "James Webb observation",
                "topics": tuple(topic.value for topic in query.topics),
                "verification": "confirmed",
                "information_kind": "release",
            },
        )


class CultureSelectionAdapter:
    network_enabled = True

    def execute(self, query: GovernedSourceQuery):
        return ()


def nasa_request() -> GovernedConversationalSourceSelectionRequest:
    return GovernedConversationalSourceSelectionRequest(
        text="Roby, buscá novedades del telescopio Webb",
        topics=frozenset({InterestTopic.JAMES_WEBB_SPACE_TELESCOPE}),
        query_text="James Webb",
        limit=3,
        region=InformationRegion.GLOBAL,
    )


def test_m344_5_declares_deterministic_registered_source_selection() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_conversational_source_selection

    assert snapshot.schema_version == "m344.5"
    assert snapshot.registered_sources_only is True
    assert snapshot.deterministic_selection is True
    assert snapshot.automatic_fetch_enabled is False
    assert snapshot.changes_cognitive_flow is False


def test_selection_ignores_declared_sources_without_registered_adapter() -> None:
    gateway = OfficialConversationGateway(Runtime())

    selection = gateway.select_governed_conversational_source(nasa_request())

    assert selection.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE
    assert selection.source is None
    assert selection.query is None
    assert selection.eligible_sources == ()


def test_selection_builds_existing_governed_query_for_registered_source() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", NasaSelectionAdapter())

    selection = gateway.select_governed_conversational_source(nasa_request())

    assert selection.status is GovernedConversationalSourceSelectionStatus.SELECTED
    assert selection.source is not None
    assert selection.source.source_id == "nasa"
    assert selection.query is not None
    assert selection.query.source_id == "nasa"
    assert selection.query.query_text == "James Webb"
    assert selection.eligible_sources == ("nasa",)


def test_selected_query_reuses_m344_4_conversational_execution() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", NasaSelectionAdapter())

    selection, result = gateway.execute_selected_governed_conversational_query(
        nasa_request()
    )

    assert selection.source is not None
    assert selection.source.source_id == "nasa"
    assert result is not None
    assert result.status is GovernedConversationalQueryStatus.SUCCEEDED
    assert result.request.query.source_id == "nasa"
    assert result.items[0].normalized.canonical_id == "nasa:jwst-001"


def test_unavailable_selection_does_not_execute_or_record_query() -> None:
    gateway = OfficialConversationGateway(Runtime())
    before = gateway.governed_source_query_observability

    selection, result = gateway.execute_selected_governed_conversational_query(
        nasa_request()
    )
    after = gateway.governed_source_query_observability

    assert selection.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE
    assert result is None
    assert after.total_queries == before.total_queries


def test_selection_respects_topic_and_region_coverage() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter(
        "cultura_caba", CultureSelectionAdapter()
    )
    request = GovernedConversationalSourceSelectionRequest(
        text="Roby, buscá museos gratuitos en Buenos Aires",
        topics=frozenset(
            {InterestTopic.MUSEUMS, InterestTopic.FREE_ACTIVITIES}
        ),
        query_text="museos gratuitos",
        region=InformationRegion.CABA,
    )

    selection = gateway.select_governed_conversational_source(request)

    assert selection.source is not None
    assert selection.source.source_id == "cultura_caba"
    assert selection.query is not None
    assert selection.query.region is InformationRegion.CABA


def test_selection_normalizes_conversational_whitespace() -> None:
    request = GovernedConversationalSourceSelectionRequest(
        text="  Roby,   buscá   Artemis  ",
        topics=frozenset({InterestTopic.NASA_MISSIONS}),
    )

    assert request.text == "Roby, buscá Artemis"


def test_m344_5_does_not_create_router_executor_or_background_runtime() -> None:
    source = Path(
        "app/governed_conversational_source_selection.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_roots.isdisjoint(
        {"asyncio", "subprocess", "threading", "requests", "httpx"}
    )
    assert "class OfficialConversationGateway" not in source
    assert "class GovernedSourceQueryExecutor" not in source
    assert "Router" not in source
    assert "propose_initiative" not in source
