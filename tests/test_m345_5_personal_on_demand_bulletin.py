from __future__ import annotations

import ast
from pathlib import Path

from app.apple_audiovisual_governed_source import (
    AppleAudiovisualGovernedSourceAdapter,
)
from app.argentina_healthy_eating_governed_source import (
    ArgentinaHealthyEatingGovernedSourceAdapter,
)
from app.cultura_caba_governed_source import CulturaCabaGovernedSourceAdapter
from app.nasa_governed_source import NasaGovernedSourceAdapter
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_on_demand_bulletin import PersonalOnDemandBulletinStatus


class Runtime:
    pass


def test_bulletin_is_explicit_under_demand_and_not_autonomous() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.personal_on_demand_bulletin

    assert snapshot.schema_version == "m345.5"
    assert snapshot.under_demand_only is True
    assert snapshot.automatic_execution_enabled is False
    assert snapshot.autonomous_initiatives_enabled is False
    assert snapshot.uses_canonical_governed_flow is True


def test_bulletin_does_not_intercept_ordinary_conversation() -> None:
    gateway = OfficialConversationGateway(Runtime())

    result = gateway.execute_personal_on_demand_bulletin("Roby, hoy estoy contento.")

    assert result.status is PersonalOnDemandBulletinStatus.NOT_RECOGNIZED
    assert result.sections == ()
    assert result.answer_text is None


def test_bulletin_without_registered_sources_executes_nothing() -> None:
    gateway = OfficialConversationGateway(Runtime())

    result = gateway.execute_personal_on_demand_bulletin(
        "Roby, dame nuestro boletín personal."
    )

    assert result.status is PersonalOnDemandBulletinStatus.EMPTY
    assert len(result.sections) == 4
    assert gateway.governed_source_query_observability.total_queries == 0


def test_bulletin_reuses_all_registered_governed_sources() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway._nasa_governed_source_adapter = NasaGovernedSourceAdapter(
        transport=lambda _url, _timeout: b'{"collection":{"items":[]}}'
    )
    gateway._cultura_caba_governed_source_adapter = CulturaCabaGovernedSourceAdapter(
        transport=lambda _url, _timeout: b"<html><body></body></html>"
    )
    gateway._apple_audiovisual_governed_source_adapter = (
        AppleAudiovisualGovernedSourceAdapter(
            transport=lambda _url, _timeout: b'{"results":[]}'
        )
    )
    gateway._argentina_healthy_eating_governed_source_adapter = (
        ArgentinaHealthyEatingGovernedSourceAdapter(
            transport=lambda _url, _timeout: b"<html><body></body></html>"
        )
    )
    gateway.enable_nasa_governed_source()
    gateway.enable_cultura_caba_governed_source()
    gateway.enable_apple_audiovisual_governed_source()
    gateway.enable_argentina_healthy_eating_governed_source()

    result = gateway.execute_personal_on_demand_bulletin(
        "Roby, ¿qué hay interesante para nosotros hoy?"
    )

    assert result.status is PersonalOnDemandBulletinStatus.EMPTY
    assert gateway.governed_source_query_observability.total_queries == 4
    assert tuple(
        section.selection.source.source_id for section in result.sections
    ) == (
        "nasa",
        "cultura_caba",
        "apple_audiovisual",
        "argentina_healthy_eating",
    )


def test_bulletin_composes_household_answer_from_governed_results() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway._nasa_governed_source_adapter = NasaGovernedSourceAdapter(
        transport=lambda _url, _timeout: (
            b'{"collection":{"items":[{"data":[{"nasa_id":"webb-1",'
            b'"title":"Nueva imagen del James Webb",'
            b'"description":"Observacion oficial"}],"links":[]}]}}'
        )
    )
    gateway.enable_nasa_governed_source()

    result = gateway.execute_personal_on_demand_bulletin(
        "Roby, dame el boletín personal de hoy."
    )

    assert result.status is PersonalOnDemandBulletinStatus.COMPLETED
    assert "para vos y Cristina" in result.answer_text
    assert "Espacio" in result.answer_text
    assert "Nueva imagen del James Webb" in result.answer_text


def test_bulletin_has_no_scheduler_credentials_or_parallel_gateway() -> None:
    source = Path("app/personal_on_demand_bulletin.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_roots.isdisjoint({"asyncio", "subprocess", "threading"})
    assert "credentials.json" not in source
    assert "OfficialConversationGateway(" not in source
    assert "class GovernedSourceQueryExecutor" not in source
