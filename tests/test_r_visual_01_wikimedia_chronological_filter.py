from urllib.parse import parse_qs, urlsplit

from app.applied_conversational_intelligence import (
    AppliedConversationalIntelligence,
)
from app.governed_source_query import (
    GovernedSourceQuery,
    GovernedSourceQueryOrder,
)
from app.wikimedia_commons_governed_source import (
    WikimediaCommonsGovernedSourceAdapter,
)


def _query(*, newest: bool) -> GovernedSourceQuery:
    interpretation = AppliedConversationalIntelligence().interpret(
        "mostrame las ultimas fotos de marte"
    )
    request = interpretation.request
    assert request is not None

    return GovernedSourceQuery(
        source_id=WikimediaCommonsGovernedSourceAdapter.SOURCE_ID,
        topics=request.topics,
        query_text=request.query_text,
        limit=request.limit,
        region=request.region,
        order=(
            GovernedSourceQueryOrder.NEWEST_FIRST
            if newest
            else None
        ),
        mode=request.mode,
    )


def _parameters(query: GovernedSourceQuery) -> dict[str, list[str]]:
    url = WikimediaCommonsGovernedSourceAdapter._build_url(query)
    return parse_qs(urlsplit(url).query)


def test_visual_newest_search_restricts_to_bitmap() -> None:
    query = _query(newest=True)
    parameters = _parameters(query)

    assert parameters["gsrsearch"] == ["marte filetype:bitmap"]


def test_visual_default_order_keeps_original_search() -> None:
    query = _query(newest=False)
    parameters = _parameters(query)

    assert parameters["gsrsearch"] == ["marte"]
    assert "gsrsort" not in parameters


def test_visual_newest_preserves_chronological_order() -> None:
    query = _query(newest=True)
    parameters = _parameters(query)

    assert parameters["gsrsort"] == ["create_timestamp_desc"]


def test_visual_newest_preserves_governed_limits() -> None:
    query = _query(newest=True)
    parameters = _parameters(query)

    assert parameters["gsrlimit"] == ["5"]
    assert parameters["gsrnamespace"] == ["6"]


def test_visual_newest_does_not_mutate_query_text() -> None:
    query = _query(newest=True)

    assert query.query_text == "marte"

    _parameters(query)

    assert query.query_text == "marte"


def test_nonvisual_newest_does_not_add_bitmap_filter() -> None:
    visual = _query(newest=True)

    query = GovernedSourceQuery(
        source_id=visual.source_id,
        topics=frozenset({"space"}),
        query_text=visual.query_text,
        limit=visual.limit,
        region=visual.region,
        order=visual.order,
    )

    parameters = _parameters(query)

    assert parameters["gsrsearch"] == ["marte"]
    assert parameters["gsrsort"] == ["create_timestamp_desc"]
