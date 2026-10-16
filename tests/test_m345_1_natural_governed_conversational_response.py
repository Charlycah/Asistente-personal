from __future__ import annotations

import ast
from pathlib import Path

from app.governed_source_query import GovernedSourceQuery
from app.official_conversation_gateway import OfficialConversationGateway


class Runtime:
    pass


class NasaMultipleAdapter:
    network_enabled = True

    def execute(self, query: GovernedSourceQuery):
        return tuple(
            {
                "external_id": f"NASA-NATURAL-{index}",
                "title": title,
                "topics": tuple(topic.value for topic in query.topics),
                "verification": "confirmed",
                "information_kind": "release",
            }
            for index, title in enumerate(
                (
                    "Webb observa una galaxia distante",
                    "Nueva imagen de una nebulosa",
                    "Avance en el estudio de exoplanetas",
                    "Calibración de nuevos instrumentos",
                ),
                start=1,
            )
        )


class NasaEmptyAdapter:
    network_enabled = True

    def execute(self, query: GovernedSourceQuery):
        return ()


class NasaFailedAdapter:
    network_enabled = True

    def execute(self, query: GovernedSourceQuery):
        raise RuntimeError("simulated governed source failure")


def test_m345_1_declares_one_natural_response_authority() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.natural_governed_conversational_response

    assert snapshot.schema_version == "m345.1"
    assert snapshot.maximum_titles == 3
    assert snapshot.preserves_structured_result is True
    assert snapshot.network_enabled is False
    assert snapshot.autonomous_execution_enabled is False


def test_successful_applied_query_uses_titles_and_household_relevance() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter(
        "nasa",
        NasaMultipleAdapter(),
    )

    result = gateway.execute_applied_conversational_intelligence(
        "Roby, buscá novedades del James Webb"
    )

    assert result.conversational_result is not None
    assert len(result.conversational_result.items) == 4
    assert result.answer_text == (
        "Encontré 4 novedades sobre James Webb para vos y Cristina. "
        "Las principales son: «Webb observa una galaxia distante»; «Nueva imagen "
        "de una nebulosa»; «Avance en el estudio de exoplanetas». También hay 1 "
        "más."
    )


def test_empty_result_is_explained_without_technical_source_identifier() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", NasaEmptyAdapter())

    result = gateway.execute_applied_conversational_intelligence(
        "Roby, ¿hay novedades de NASA?"
    )

    assert result.answer_text == (
        "Consulté la fuente disponible, pero no encontré novedades válidas sobre "
        "NASA."
    )
    assert "fuente gobernada nasa" not in result.answer_text


def test_failed_result_is_explained_without_exposing_internal_error() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", NasaFailedAdapter())

    result = gateway.execute_applied_conversational_intelligence(
        "Roby, contame noticias de NASA"
    )

    assert result.answer_text == (
        "No pude consultar la fuente disponible sobre NASA en este momento."
    )
    assert "simulated" not in result.answer_text


def test_non_recognized_conversation_still_has_no_generated_answer() -> None:
    gateway = OfficialConversationGateway(Runtime())

    result = gateway.execute_applied_conversational_intelligence(
        "Roby, hoy quiero conversar con vos."
    )

    assert result.selection is None
    assert result.conversational_result is None
    assert result.answer_text is None


def test_m345_1_has_no_query_execution_or_parallel_gateway() -> None:
    source = Path(
        "app/natural_governed_conversational_response.py"
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
    assert ".execute(" not in source
