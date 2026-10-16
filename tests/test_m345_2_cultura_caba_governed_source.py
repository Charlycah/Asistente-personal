from __future__ import annotations

import ast
from pathlib import Path

from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligenceStatus,
)
from app.cultura_caba_governed_source import (
    CULTURA_CABA_AGENDA_ENDPOINT,
    CulturaCabaGovernedSourceAdapter,
)
from app.governed_information_sources import InformationRegion
from app.governed_source_query import GovernedSourceQuery, GovernedSourceQueryStatus
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


def cultura_query(**changes) -> GovernedSourceQuery:
    values = {
        "source_id": "cultura_caba",
        "topics": frozenset({InterestTopic.CULTURE_CABA}),
        "query_text": "agenda cultural",
        "limit": 3,
        "region": InformationRegion.CABA,
    }
    values.update(changes)
    return GovernedSourceQuery(**values)


def cultura_page() -> bytes:
    return b"""
    <html><body>
      <h2>Concierto gratuito en la Usina del Arte</h2>
      <h2>Nueva muestra en el Museo Moderno</h2>
      <h3>Obra teatral en el Cultural San Martin</h3>
      <h2>Tambien te puede interesar</h2>
    </body></html>
    """


def test_cultura_caba_source_is_real_official_and_not_automatic() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.cultura_caba_governed_source

    assert snapshot.schema_version == "m345.2"
    assert snapshot.source_id == "cultura_caba"
    assert snapshot.endpoint == CULTURA_CABA_AGENDA_ENDPOINT
    assert snapshot.network_enabled is True
    assert snapshot.automatic_fetch_enabled is False
    assert snapshot.credentials_required is False
    assert snapshot.official_public_source is True
    assert gateway.governed_source_query_executor.registered_sources == ()


def test_explicit_enable_registers_cultura_in_canonical_executor() -> None:
    gateway = OfficialConversationGateway(Runtime())

    gateway.enable_cultura_caba_governed_source()

    assert gateway.governed_source_query_executor.registered_sources == (
        "cultura_caba",
    )
    assert gateway.governed_source_query_executor.network_enabled is True


def test_cultura_adapter_parses_and_bounds_official_agenda_items() -> None:
    observed = {}

    def transport(url: str, timeout: float) -> bytes:
        observed["url"] = url
        observed["timeout"] = timeout
        return cultura_page()

    adapter = CulturaCabaGovernedSourceAdapter(transport=transport)
    items = adapter.execute(cultura_query(limit=2, timeout_seconds=6.5))

    assert observed == {"url": CULTURA_CABA_AGENDA_ENDPOINT, "timeout": 6.5}
    assert len(items) == 2
    assert items[0]["source_id"] == "cultura_caba"
    assert items[0]["title"] == "Concierto gratuito en la Usina del Arte"
    assert items[0]["is_free"] is True
    assert items[0]["information_kind"] == "event"
    assert items[0]["verification"] == "confirmed"


def test_applied_intelligence_recognizes_caba_culture_and_region() -> None:
    gateway = OfficialConversationGateway(Runtime())

    interpretation = gateway.interpret_applied_conversational_intelligence(
        "Roby, ¿qué actividades culturales hay en Buenos Aires?"
    )

    assert interpretation.status is AppliedConversationalIntelligenceStatus.RECOGNIZED
    assert interpretation.request is not None
    assert interpretation.request.region is InformationRegion.CABA
    assert interpretation.request.query_text == "agenda cultural"
    assert InterestTopic.CULTURE_CABA in interpretation.matched_topics


def test_cultura_request_runs_through_selection_and_natural_answer() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway._cultura_caba_governed_source_adapter = (
        CulturaCabaGovernedSourceAdapter(
            transport=lambda _url, _timeout: cultura_page()
        )
    )
    gateway.enable_cultura_caba_governed_source()

    result = gateway.execute_applied_conversational_intelligence(
        "Roby, ¿qué actividades culturales hay en Buenos Aires?"
    )

    assert result.selection is not None
    assert result.selection.source is not None
    assert result.selection.source.source_id == "cultura_caba"
    assert result.conversational_result is not None
    assert result.conversational_result.source_result.status is (
        GovernedSourceQueryStatus.SUCCEEDED
    )
    assert result.conversational_result.items[0].normalized.region is (
        InformationRegion.CABA
    )
    assert "Encontré 3 novedades sobre agenda cultural" in result.answer_text
    assert "vos y Cristina" in result.answer_text


def test_cultura_source_has_no_scheduler_credentials_or_parallel_executor() -> None:
    source = Path("app/cultura_caba_governed_source.py").read_text(
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
