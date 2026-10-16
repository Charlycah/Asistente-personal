from __future__ import annotations

import ast
from pathlib import Path

from app.governed_source_query import (
    GovernedSourceQuery,
    GovernedSourceQueryStatus,
)
from app.governed_source_query_executor import GovernedSourceExecutionErrorKind
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


class SuccessfulAdapter:
    def execute(self, query: GovernedSourceQuery):
        return ({"title": query.query_text or "Artemis"},)


class EmptyAdapter:
    def execute(self, query: GovernedSourceQuery):
        return ()


class TimeoutAdapter:
    def execute(self, query: GovernedSourceQuery):
        raise TimeoutError


class FailingAdapter:
    def execute(self, query: GovernedSourceQuery):
        raise RuntimeError("source failed")


def nasa_query() -> GovernedSourceQuery:
    return GovernedSourceQuery(
        source_id="nasa",
        topics=frozenset({InterestTopic.NASA_MISSIONS}),
        query_text="Artemis",
    )


def test_executor_reports_single_canonical_authority() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_source_query_executor

    assert snapshot.schema_version == "m344.1"
    assert snapshot.authority.endswith(":OfficialConversationGateway")
    assert snapshot.execution_enabled is True
    assert snapshot.network_enabled is False


def test_executor_rejects_execution_without_registered_adapter() -> None:
    gateway = OfficialConversationGateway(Runtime())

    result = gateway.execute_governed_source_query(nasa_query())

    assert result.status is GovernedSourceQueryStatus.FAILED
    assert result.response is not None
    assert result.response.error is not None
    assert (
        result.response.error.kind
        is GovernedSourceExecutionErrorKind.ADAPTER_UNAVAILABLE
    )


def test_registered_adapter_executes_prepared_query() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("NASA", SuccessfulAdapter())

    result = gateway.execute_governed_source_query(nasa_query())

    assert result.status is GovernedSourceQueryStatus.SUCCEEDED
    assert result.response is not None
    assert result.response.raw_items[0]["title"] == "Artemis"
    assert result.execution_enabled is True


def test_empty_adapter_result_is_explicit() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", EmptyAdapter())

    result = gateway.execute_governed_source_query(nasa_query())

    assert result.status is GovernedSourceQueryStatus.EMPTY
    assert result.response is not None
    assert result.response.raw_items == ()


def test_timeout_is_typed_and_retryable() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", TimeoutAdapter())

    result = gateway.execute_governed_source_query(nasa_query())

    assert result.response is not None
    assert result.response.error is not None
    assert result.response.error.kind is GovernedSourceExecutionErrorKind.TIMEOUT
    assert result.response.error.retryable is True


def test_adapter_failure_is_typed_without_leaking_error_text() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", FailingAdapter())

    result = gateway.execute_governed_source_query(nasa_query())

    assert result.response is not None
    assert result.response.error is not None
    assert (
        result.response.error.kind
        is GovernedSourceExecutionErrorKind.ADAPTER_FAILURE
    )
    assert "source failed" not in result.response.error.message


def test_executor_keeps_contract_validation_before_adapter_call() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", SuccessfulAdapter())
    query = GovernedSourceQuery(
        source_id="nasa",
        topics=frozenset({InterestTopic.BOCA_JUNIORS}),
    )

    try:
        gateway.execute_governed_source_query(query)
    except ValueError as exc:
        assert "undeclared source topics" in str(exc)
    else:
        raise AssertionError("contract validation must reject undeclared topics")


def test_m344_1_executor_has_no_embedded_network_or_background_runtime() -> None:
    source = Path("app/governed_source_query_executor.py").read_text(
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
        {
            "asyncio",
            "httpx",
            "requests",
            "socket",
            "subprocess",
            "threading",
            "urllib",
        }
    )
    assert "schedule" not in source.casefold()
