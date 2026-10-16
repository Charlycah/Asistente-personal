from __future__ import annotations

import ast
from pathlib import Path

from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligenceStatus,
)
from app.argentina_healthy_eating_governed_source import (
    HEALTHY_EATING_ENDPOINT,
    HEALTHY_RECIPES_ENDPOINT,
    ArgentinaHealthyEatingGovernedSourceAdapter,
)
from app.governed_information_sources import InformationRegion
from app.governed_source_query import GovernedSourceQuery, GovernedSourceQueryStatus
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


def healthy_query(**changes) -> GovernedSourceQuery:
    values = {
        "source_id": "argentina_healthy_eating",
        "topics": frozenset({InterestTopic.HEALTHY_EATING}),
        "query_text": "alimentación saludable",
        "limit": 3,
        "region": InformationRegion.ARGENTINA,
    }
    values.update(changes)
    return GovernedSourceQuery(**values)


def official_health_html() -> bytes:
    return """
    <html><body>
      <h2>Alimentación saludable</h2>
      <a href="/salud/alimentacion-saludable/grafico">
        Gráfica de alimentación saludable
      </a>
      <a href="/salud/alimentacion-saludable/recetas">
        Recetas saludables para toda la familia
      </a>
      <a href="/tramites">Trámites</a>
    </body></html>
    """.encode("utf-8")


def test_health_source_is_official_evidence_based_and_not_automatic() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.argentina_healthy_eating_governed_source

    assert snapshot.schema_version == "m345.4"
    assert snapshot.source_id == "argentina_healthy_eating"
    assert snapshot.endpoints == (HEALTHY_EATING_ENDPOINT, HEALTHY_RECIPES_ENDPOINT)
    assert snapshot.network_enabled is True
    assert snapshot.automatic_fetch_enabled is False
    assert snapshot.credentials_required is False
    assert snapshot.official_public_source is True
    assert snapshot.evidence_based is True
    assert gateway.governed_source_query_executor.registered_sources == ()


def test_explicit_enable_registers_health_source_in_canonical_executor() -> None:
    gateway = OfficialConversationGateway(Runtime())

    gateway.enable_argentina_healthy_eating_governed_source()

    assert gateway.governed_source_query_executor.registered_sources == (
        "argentina_healthy_eating",
    )


def test_adapter_uses_official_recipe_endpoint_and_normalizes_guidance() -> None:
    observed = {}

    def transport(url: str, timeout: float) -> bytes:
        observed["url"] = url
        observed["timeout"] = timeout
        return official_health_html()

    adapter = ArgentinaHealthyEatingGovernedSourceAdapter(transport=transport)
    items = adapter.execute(
        healthy_query(
            topics=frozenset({InterestTopic.HEALTHY_RECIPES}),
            query_text="recetas saludables",
            timeout_seconds=6.5,
        )
    )

    assert observed == {"url": HEALTHY_RECIPES_ENDPOINT, "timeout": 6.5}
    assert len(items) == 3
    assert items[0]["source_id"] == "argentina_healthy_eating"
    assert items[0]["information_kind"] == "guidance"
    assert items[0]["verification"] == "confirmed"
    assert items[0]["region"] == "argentina"


def test_applied_intelligence_recognizes_healthy_eating_topics() -> None:
    gateway = OfficialConversationGateway(Runtime())

    interpretation = gateway.interpret_applied_conversational_intelligence(
        "Roby, buscá recetas saludables basadas en evidencia."
    )

    assert interpretation.status is AppliedConversationalIntelligenceStatus.RECOGNIZED
    assert interpretation.request is not None
    assert interpretation.request.region is InformationRegion.ARGENTINA
    assert interpretation.request.query_text == "recetas saludables"
    assert InterestTopic.HEALTHY_RECIPES in interpretation.matched_topics


def test_health_request_runs_through_complete_governed_flow() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway._argentina_healthy_eating_governed_source_adapter = (
        ArgentinaHealthyEatingGovernedSourceAdapter(
            transport=lambda _url, _timeout: official_health_html()
        )
    )
    gateway.enable_argentina_healthy_eating_governed_source()

    result = gateway.execute_applied_conversational_intelligence(
        "Roby, buscá alimentación saludable."
    )

    assert result.selection is not None
    assert result.selection.source is not None
    assert result.selection.source.source_id == "argentina_healthy_eating"
    assert result.conversational_result is not None
    assert result.conversational_result.source_result.status is (
        GovernedSourceQueryStatus.SUCCEEDED
    )
    assert result.conversational_result.items[0].normalized.region is (
        InformationRegion.ARGENTINA
    )
    assert "alimentación saludable" in result.answer_text
    assert "para vos" in result.answer_text


def test_health_source_has_no_scheduler_credentials_or_parallel_flow() -> None:
    source = Path("app/argentina_healthy_eating_governed_source.py").read_text(
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
