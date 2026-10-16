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


class ManyItemsAdapter:
    def execute(self, query: GovernedSourceQuery):
        return tuple({"index": index} for index in range(query.limit + 3))


class InvalidSequenceAdapter:
    def execute(self, query: GovernedSourceQuery):
        return {"unexpected": query.source_id}


class InvalidItemAdapter:
    def execute(self, query: GovernedSourceQuery):
        return ({"valid": True}, "invalid")


class TimeoutAdapter:
    def execute(self, query: GovernedSourceQuery):
        raise TimeoutError


def nasa_query(*, limit: int = 2) -> GovernedSourceQuery:
    return GovernedSourceQuery(
        source_id="nasa",
        topics=frozenset({InterestTopic.NASA_MISSIONS}),
        query_text="Artemis",
        limit=limit,
    )


def test_executor_reports_resilience_and_observability() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_source_query_executor
    observability = gateway.governed_source_query_observability

    assert snapshot.schema_version == "m344.1"
    assert observability.schema_version == "m344.3"
    assert snapshot.resilience_enabled is True
    assert snapshot.observability_enabled is True
    assert observability.total_queries == 0
    assert observability.max_observations == 100


def test_executor_enforces_query_limit_and_counts_dropped_items() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", ManyItemsAdapter())

    result = gateway.execute_governed_source_query(nasa_query(limit=2))
    metrics = gateway.governed_source_query_observability

    assert result.response is not None
    assert len(result.response.raw_items) == 2
    assert metrics.succeeded_queries == 1
    assert metrics.returned_items == 2
    assert metrics.dropped_items == 3
    assert metrics.last_observation is not None
    assert metrics.last_observation.dropped_items == 3


def test_invalid_adapter_sequence_degrades_to_typed_failure() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter(
        "nasa", InvalidSequenceAdapter()
    )

    result = gateway.execute_governed_source_query(nasa_query())

    assert result.response is not None
    assert result.response.error is not None
    assert (
        result.response.error.kind
        is GovernedSourceExecutionErrorKind.INVALID_ADAPTER_RESPONSE
    )
    assert result.response.error.retryable is False
    assert gateway.governed_source_query_observability.invalid_response_queries == 1


def test_invalid_adapter_item_degrades_without_partial_data() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", InvalidItemAdapter())

    result = gateway.execute_governed_source_query(nasa_query())

    assert result.status is GovernedSourceQueryStatus.FAILED
    assert result.response is not None
    assert result.response.raw_items == ()


def test_timeout_is_observed_without_leaking_exception() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.register_governed_source_query_adapter("nasa", TimeoutAdapter())

    gateway.execute_governed_source_query(nasa_query())
    observation = gateway.governed_source_query_observations[-1]
    metrics = gateway.governed_source_query_observability

    assert metrics.timeout_queries == 1
    assert metrics.failed_queries == 1
    assert observation.status is GovernedSourceQueryStatus.FAILED
    assert observation.retryable is True
    assert observation.duration_ms >= 0


def test_contract_rejection_is_observed_and_still_raised() -> None:
    gateway = OfficialConversationGateway(Runtime())
    query = GovernedSourceQuery(
        source_id="nasa",
        topics=frozenset({InterestTopic.BOCA_JUNIORS}),
    )

    try:
        gateway.execute_governed_source_query(query)
    except ValueError:
        pass
    else:
        raise AssertionError("contract rejection must remain visible to caller")

    metrics = gateway.governed_source_query_observability
    assert metrics.total_queries == 1
    assert metrics.rejected_queries == 1
    assert metrics.last_observation is not None
    assert metrics.last_observation.status is GovernedSourceQueryStatus.REJECTED


def test_observation_history_is_bounded() -> None:
    gateway = OfficialConversationGateway(Runtime())

    for _ in range(105):
        gateway.execute_governed_source_query(nasa_query())

    observations = gateway.governed_source_query_observations
    assert len(observations) == 100
    assert observations[0].sequence_id == 6
    assert observations[-1].sequence_id == 105


def test_m344_3_has_no_background_runtime_or_second_executor() -> None:
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
        {"asyncio", "subprocess", "threading", "requests", "httpx"}
    )
    assert source.count("class GovernedSourceQueryExecutor:") == 1
