from __future__ import annotations

import ast
from pathlib import Path

from app.governed_conversational_query import (
    GovernedConversationalQuery,
    GovernedConversationalQueryStatus,
)
from app.governed_source_query import GovernedSourceQuery
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic
from app.relevance_evaluator import RelevanceRecipient


class Runtime:
    pass


class NasaConversationAdapter:
    network_enabled = True

    def execute(self, query: GovernedSourceQuery):
        return (
            {
                "source_id": "nasa",
                "external_id": "ARTEMIS-001",
                "title": "  Artemis II crew preparation  ",
                "published_at": "2026-07-29T12:00:00Z",
                "topics": (InterestTopic.NASA_MISSIONS.value,),
                "tags": ("Artemis II", "Crew"),
                "verification": "confirmed",
                "information_kind": "release",
                "is_free": True,
                "importance": 5,
            },
        )


class InvalidConversationalItemAdapter:
    def execute(self, query: GovernedSourceQuery):
        return ({"external_id": "missing-title"},)


def request() -> GovernedConversationalQuery:
    return GovernedConversationalQuery(
        text="Roby, buscá novedades de Artemis",
        query=GovernedSourceQuery(
            source_id="nasa",
            topics=frozenset({InterestTopic.NASA_MISSIONS}),
            query_text="Artemis",
            limit=3,
        ),
    )


def test_m344_4_declares_explicit_conversational_query_boundary() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_conversational_query

    assert snapshot.schema_version == "m344.4"
    assert snapshot.explicit_queries_only is True
    assert snapshot.automatic_fetch_enabled is False
    assert snapshot.changes_cognitive_flow is False


def test_conversational_query_uses_existing_executor_and_normalizer() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter(
        "nasa", NasaConversationAdapter()
    )

    result = gateway.execute_governed_conversational_query(request())

    assert result.status is GovernedConversationalQueryStatus.SUCCEEDED
    assert result.answer_text == (
        "Encontré 1 resultado en la fuente gobernada nasa."
    )
    assert len(result.items) == 1
    information = result.items[0]
    assert information.normalized.canonical_id == "nasa:artemis-001"
    assert information.normalized.title == "Artemis II crew preparation"
    assert information.normalized.source_confidence == 98
    assert information.relevance.recipient is not RelevanceRecipient.NOBODY
    assert information.relevance.should_share is True


def test_explicit_query_evaluates_relevance_without_proposing_initiative() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter(
        "nasa", NasaConversationAdapter()
    )

    before = gateway.initiative_engine
    result = gateway.execute_governed_conversational_query(request())
    after = gateway.initiative_engine

    assert result.items[0].relevance.scores
    assert before == after


def test_unavailable_source_degrades_to_conversational_failure() -> None:
    gateway = OfficialConversationGateway(Runtime())

    result = gateway.execute_governed_conversational_query(request())

    assert result.status is GovernedConversationalQueryStatus.FAILED
    assert result.items == ()
    assert result.error is not None
    assert result.answer_text == "No pude consultar la fuente gobernada nasa."


def test_invalid_items_are_discarded_without_partial_failure() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter(
        "nasa", InvalidConversationalItemAdapter()
    )

    result = gateway.execute_governed_conversational_query(request())

    assert result.status is GovernedConversationalQueryStatus.EMPTY
    assert result.items == ()
    assert result.discarded_items == 1
    assert "no devolvió resultados válidos" in result.answer_text


def test_conversational_request_normalizes_whitespace() -> None:
    conversational_request = GovernedConversationalQuery(
        text="  Roby,   buscá   Artemis  ",
        query=request().query,
    )

    assert conversational_request.text == "Roby, buscá Artemis"


def test_m344_4_does_not_create_parallel_gateway_or_background_runtime() -> None:
    source = Path("app/governed_conversational_query.py").read_text(
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
        {"asyncio", "subprocess", "threading", "requests", "httpx"}
    )
    assert "class OfficialConversationGateway" not in source
    assert "class GovernedSourceQueryExecutor" not in source
    assert "propose_initiative" not in source
