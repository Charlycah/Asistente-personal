from __future__ import annotations

import ast
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app.governed_source_query import GovernedSourceQuery, GovernedSourceQueryStatus
from app.nasa_governed_source import NasaGovernedSourceAdapter
from app.official_conversation_gateway import OfficialConversationGateway
from app.personal_interest_center import InterestTopic


class Runtime:
    pass


def nasa_query(**changes) -> GovernedSourceQuery:
    values = {
        "source_id": "nasa",
        "topics": frozenset({InterestTopic.NASA_MISSIONS}),
        "query_text": "Artemis",
        "limit": 2,
    }
    values.update(changes)
    return GovernedSourceQuery(**values)


def nasa_payload() -> bytes:
    return json.dumps(
        {
            "collection": {
                "items": [
                    {
                        "data": [
                            {
                                "nasa_id": "ARTEMIS-001",
                                "title": "Artemis mission update",
                                "description": "Official NASA material",
                                "date_created": "2026-07-20T12:00:00Z",
                                "keywords": ["Artemis", "Moon"],
                                "media_type": "image",
                                "center": "HQ",
                            }
                        ],
                        "links": [{"href": "https://images-assets.nasa.gov/a.jpg"}],
                    }
                ]
            }
        }
    ).encode()


def test_nasa_source_is_real_but_not_automatic() -> None:
    gateway = OfficialConversationGateway(Runtime())

    snapshot = gateway.nasa_governed_source

    assert snapshot.schema_version == "m344.2"
    assert snapshot.source_id == "nasa"
    assert snapshot.endpoint == "https://images-api.nasa.gov/search"
    assert snapshot.network_enabled is True
    assert snapshot.automatic_fetch_enabled is False
    assert snapshot.credentials_required is False
    assert gateway.governed_source_query_executor.network_enabled is False


def test_explicit_enable_registers_only_the_canonical_nasa_adapter() -> None:
    gateway = OfficialConversationGateway(Runtime())

    gateway.enable_nasa_governed_source()
    snapshot = gateway.governed_source_query_executor

    assert snapshot.registered_sources == ("nasa",)
    assert snapshot.network_enabled is True


def test_nasa_adapter_uses_fixed_official_endpoint_and_query_limits() -> None:
    observed = {}

    def transport(url: str, timeout: float) -> bytes:
        observed["url"] = url
        observed["timeout"] = timeout
        return nasa_payload()

    adapter = NasaGovernedSourceAdapter(transport=transport)
    items = adapter.execute(nasa_query(timeout_seconds=7.5))
    parsed = urlparse(observed["url"])
    parameters = parse_qs(parsed.query)

    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == (
        "https://images-api.nasa.gov/search"
    )
    assert parameters["q"] == ["Artemis"]
    assert parameters["page_size"] == ["2"]
    assert parameters["media_type"] == ["image"]
    assert observed["timeout"] == 7.5
    assert items[0]["external_id"] == "ARTEMIS-001"
    assert items[0]["verification"] == "confirmed"


def test_gateway_executes_real_source_through_existing_executor() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway._nasa_governed_source_adapter = NasaGovernedSourceAdapter(
        transport=lambda _url, _timeout: nasa_payload()
    )
    gateway.enable_nasa_governed_source()

    result = gateway.execute_governed_source_query(nasa_query())

    assert result.status is GovernedSourceQueryStatus.SUCCEEDED
    assert result.response is not None
    assert result.response.raw_items[0]["source_id"] == "nasa"
    assert result.response.raw_items[0]["title"] == "Artemis mission update"


def test_invalid_nasa_media_type_fails_inside_governed_execution() -> None:
    gateway = OfficialConversationGateway(Runtime())
    gateway.enable_nasa_governed_source()

    result = gateway.execute_governed_source_query(
        nasa_query(parameters={"media_type": "document"})
    )

    assert result.status is GovernedSourceQueryStatus.FAILED
    assert result.response is not None
    assert result.response.error is not None
    assert result.response.error.retryable is True


def test_nasa_source_has_no_scheduler_or_credential_access() -> None:
    source = Path("app/nasa_governed_source.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_roots.isdisjoint({"asyncio", "subprocess", "threading"})
    assert "credentials.json" not in source
    assert "schedule" not in source.casefold()
