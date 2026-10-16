from __future__ import annotations

import ast
from pathlib import Path

from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligenceStatus,
)
from app.governed_conversational_query import GovernedConversationalQueryStatus
from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionStatus,
)
from app.governed_source_query import GovernedSourceQuery
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


class NasaAdapter:
    network_enabled = True

    def execute(self, query: GovernedSourceQuery):
        return (
            {
                "external_id": "JWST-APPLIED-001",
                "title": "Nueva observación del James Webb",
                "topics": tuple(topic.value for topic in query.topics),
                "verification": "confirmed",
                "information_kind": "release",
            },
        )


def test_m345_0_declares_one_applied_conversational_bridge() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.applied_conversational_intelligence

    assert snapshot.schema_version == "m345.0"
    assert snapshot.explicit_requests_only is True
    assert snapshot.uses_governed_source_selection is True
    assert snapshot.automatic_fetch_enabled is False
    assert snapshot.autonomous_initiatives_enabled is False


def test_everyday_james_webb_request_becomes_governed_request() -> None:
    gateway = OfficialConversationGateway(Runtime())

    interpretation = gateway.interpret_applied_conversational_intelligence(
        "Roby, ¿hay novedades del telescopio Webb?"
    )

    assert interpretation.status is AppliedConversationalIntelligenceStatus.RECOGNIZED
    assert interpretation.request is not None
    assert interpretation.request.query_text == "James Webb"
    assert interpretation.matched_topics == frozenset(
        {InterestTopic.JAMES_WEBB_SPACE_TELESCOPE}
    )


def test_non_informational_conversation_is_not_intercepted() -> None:
    gateway = OfficialConversationGateway(Runtime())

    interpretation = gateway.interpret_applied_conversational_intelligence(
        "Roby, hoy estoy contento."
    )

    assert interpretation.status is (
        AppliedConversationalIntelligenceStatus.NOT_RECOGNIZED
    )
    assert interpretation.request is None


def test_applied_bridge_reuses_complete_existing_governed_flow() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", NasaAdapter())

    result = gateway.execute_applied_conversational_intelligence(
        "Roby, buscá novedades del James Webb"
    )

    assert result.selection is not None
    assert result.selection.status is (
        GovernedConversationalSourceSelectionStatus.SELECTED
    )
    assert result.selection.source is not None
    assert result.selection.source.source_id == "nasa"
    assert result.conversational_result is not None
    assert result.conversational_result.status is (
        GovernedConversationalQueryStatus.SUCCEEDED
    )
    assert result.conversational_result.items[0].normalized.canonical_id == (
        "nasa:jwst-applied-001"
    )
    assert result.answer_text == (
        "Encontré una novedad sobre James Webb para vos y Cristina: "
        "«Nueva observación del James Webb»."
    )


def test_recognized_request_without_enabled_source_degrades_safely() -> None:
    gateway = OfficialConversationGateway(Runtime())
    before = gateway.governed_source_query_observability

    result = gateway.execute_applied_conversational_intelligence(
        "Roby, ¿qué hay de nuevo en NASA?"
    )
    after = gateway.governed_source_query_observability

    assert result.selection is not None
    assert result.selection.status is (
        GovernedConversationalSourceSelectionStatus.UNAVAILABLE
    )
    assert result.conversational_result is None
    assert result.answer_text == (
        "Entendí que querés saber sobre NASA, pero todavía no tengo una fuente "
        "gobernada disponible para responderte."
    )
    assert after.total_queries == before.total_queries


def test_m345_0_does_not_duplicate_core_authorities_or_background_work() -> None:
    source = Path("app/applied_conversational_intelligence.py").read_text(
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
    assert "class RelevanceEvaluator" not in source
    assert "propose_initiative" not in source
