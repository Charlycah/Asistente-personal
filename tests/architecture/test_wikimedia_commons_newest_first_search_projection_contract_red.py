from __future__ import annotations

import inspect
import json
from urllib.parse import parse_qs, urlparse

from app.governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from app.governed_source_query import (
    GovernedSourceQuery,
    GovernedSourceQueryOrder,
)
from app.wikimedia_commons_governed_source import (
    WikimediaCommonsGovernedSourceAdapter,
)


def _query(**changes: object) -> GovernedSourceQuery:
    values = {
        "source_id": "wikimedia_commons",
        "topics": frozenset(),
        "query_text": "Patagonian glaciers",
        "limit": 100,
        "mode": GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    }
    values.update(changes)
    return GovernedSourceQuery(**values)


def _parameters(query: GovernedSourceQuery) -> dict[str, list[str]]:
    url = WikimediaCommonsGovernedSourceAdapter._build_url(query)
    return parse_qs(urlparse(url).query)


def _page(page_id: int, timestamp: str) -> dict[str, object]:
    return {
        "pageid": page_id,
        "title": f"File:{page_id}.jpg",
        "imageinfo": [
            {
                "url": f"https://upload.wikimedia.org/{page_id}.jpg",
                "mime": "image/jpeg",
                "mediatype": "BITMAP",
                "timestamp": timestamp,
            }
        ],
    }


def test_newest_first_projects_exact_provider_create_order():
    parameters = _parameters(
        _query(order=GovernedSourceQueryOrder.NEWEST_FIRST)
    )
    assert parameters["gsrsort"] == ["create_timestamp_desc"]


def test_order_none_preserves_provider_default_without_sort_parameter():
    assert "gsrsort" not in _parameters(_query())


def test_newest_first_preserves_existing_bounded_search_parameters():
    parameters = _parameters(
        _query(order=GovernedSourceQueryOrder.NEWEST_FIRST)
    )
    assert parameters["generator"] == ["search"]
    assert parameters["gsrsearch"] == ["Patagonian glaciers filetype:bitmap"]
    assert parameters["gsrnamespace"] == ["6"]
    assert parameters["gsrlimit"] == ["20"]
    assert parameters["iiurlwidth"] == ["640"]


def test_provider_projection_never_uses_last_edit_order():
    source = inspect.getsource(WikimediaCommonsGovernedSourceAdapter)
    assert "last_edit_desc" not in source


def test_adapter_contains_no_local_result_sorting_authority():
    source = inspect.getsource(WikimediaCommonsGovernedSourceAdapter)
    assert "sorted(" not in source
    assert ".sort(" not in source


def test_provider_item_order_is_preserved_without_timestamp_sorting():
    payload = json.dumps(
        {
            "query": {
                "pages": {
                    "9": _page(9, "2020-01-01T00:00:00Z"),
                    "2": _page(2, "2026-01-01T00:00:00Z"),
                }
            }
        }
    ).encode("utf-8")
    adapter = WikimediaCommonsGovernedSourceAdapter(
        user_agent="ROBY-XI.2/1.0 (contact: operator@example.invalid)",
        transport=lambda _url, _timeout: payload,
    )
    items = adapter.execute(
        _query(order=GovernedSourceQueryOrder.NEWEST_FIRST)
    )
    assert [item["external_id"] for item in items] == ["9", "2"]
    assert [item["published_at"] for item in items] == [
        "2020-01-01T00:00:00Z",
        "2026-01-01T00:00:00Z",
    ]


def test_projection_introduces_no_implicit_date_window():
    query = _query(order=GovernedSourceQueryOrder.NEWEST_FIRST)
    assert query.published_after is None
    assert query.published_before is None


def test_projection_contract_does_not_reach_natural_language_admission():
    source = inspect.getsource(WikimediaCommonsGovernedSourceAdapter)
    assert "mostrame" not in source.casefold()
    assert "latest" not in source.casefold()
    assert "últim" not in source.casefold()
