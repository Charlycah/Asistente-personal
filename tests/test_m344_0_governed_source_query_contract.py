from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.governed_information_sources import InformationRegion
from app.governed_source_query import (
    GovernedSourceQuery,
    GovernedSourceQueryErrorKind,
    GovernedSourceQueryStatus,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


def test_query_normalizes_identity_text_parameters_and_dates() -> None:
    query = GovernedSourceQuery(
        source_id=" NASA ",
        topics=frozenset({InterestTopic.NASA_MISSIONS}),
        query_text="  Artemis II  ",
        published_after=datetime(2026, 1, 1),
        parameters={" mission ": " artemis "},
    )

    assert query.source_id == "nasa"
    assert query.query_text == "Artemis II"
    assert query.published_after == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert dict(query.parameters or {}) == {"mission": "artemis"}


def test_query_rejects_invalid_limit_timeout_and_time_window() -> None:
    topics = frozenset({InterestTopic.NASA_MISSIONS})
    with pytest.raises(ValueError, match="limit"):
        GovernedSourceQuery(source_id="nasa", topics=topics, limit=0)
    with pytest.raises(ValueError, match="timeout"):
        GovernedSourceQuery(source_id="nasa", topics=topics, timeout_seconds=61)
    with pytest.raises(ValueError, match="time window"):
        GovernedSourceQuery(
            source_id="nasa",
            topics=topics,
            published_after=datetime.now(timezone.utc),
            published_before=datetime.now(timezone.utc) - timedelta(days=1),
        )


def test_contract_prepares_declared_source_without_execution() -> None:
    gateway = OfficialConversationGateway(Runtime())
    query = GovernedSourceQuery(
        source_id="nasa",
        topics=frozenset({InterestTopic.NASA_MISSIONS}),
        region=InformationRegion.GLOBAL,
    )

    result = gateway.prepare_governed_source_query(query)

    assert result.status is GovernedSourceQueryStatus.PREPARED
    assert result.source.source_id == "nasa"
    assert result.execution_enabled is False


def test_contract_rejects_undeclared_topics() -> None:
    gateway = OfficialConversationGateway(Runtime())
    query = GovernedSourceQuery(
        source_id="nasa",
        topics=frozenset({InterestTopic.BOCA_JUNIORS}),
    )

    with pytest.raises(ValueError, match="undeclared source topics"):
        gateway.prepare_governed_source_query(query)


def test_contract_rejects_region_outside_source_coverage() -> None:
    gateway = OfficialConversationGateway(Runtime())
    query = GovernedSourceQuery(
        source_id="sports_editorial",
        topics=frozenset({InterestTopic.BOCA_JUNIORS}),
        region=InformationRegion.CABA,
    )

    with pytest.raises(ValueError, match="outside source coverage"):
        gateway.prepare_governed_source_query(query)


def test_unavailable_response_is_typed_and_non_retryable() -> None:
    gateway = OfficialConversationGateway(Runtime())
    query = GovernedSourceQuery(
        source_id="nasa",
        topics=frozenset({InterestTopic.NASA_MISSIONS}),
    )

    response = gateway.governed_source_query_unavailable_response(query)

    assert response.status is GovernedSourceQueryStatus.FAILED
    assert response.error is not None
    assert response.error.kind is GovernedSourceQueryErrorKind.EXECUTION_UNAVAILABLE
    assert response.error.retryable is False


def test_gateway_exposes_single_m344_0_contract() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.governed_source_query_contract

    assert snapshot.schema_version == "m344.0"
    assert snapshot.authority.endswith(":OfficialConversationGateway")
    assert snapshot.execution_enabled is False
    assert snapshot.network_enabled is False


def test_m344_0_contract_has_no_network_or_background_execution() -> None:
    source = Path("app/governed_source_query.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_roots.isdisjoint(
        {"asyncio", "httpx", "requests", "socket", "subprocess", "threading", "urllib"}
    )
    assert "schedule" not in source.casefold()
    assert "adapter" not in source.casefold()
