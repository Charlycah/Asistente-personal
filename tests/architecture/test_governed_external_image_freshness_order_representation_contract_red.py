from __future__ import annotations

import importlib
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionRequest,
    GovernedConversationalSourceSelectionStatus,
    GovernedConversationalSourceSelector,
)
from app.governed_information_sources import (
    GovernedInformationSources,
    InformationSourceCapability,
)
from app.governed_source_query import GovernedSourceQuery, GovernedSourceQueryContract
from app.governed_source_query_executor import GovernedSourceQueryExecutor


def _order_type():
    module = importlib.import_module("app.governed_source_query")
    return getattr(module, "GovernedSourceQueryOrder")


def _nasa_source():
    return GovernedInformationSources().source_for("nasa")


def _capable_source(*, open_visual: bool = False):
    capabilities = {InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY}
    topics = _nasa_source().topics
    if open_visual:
        capabilities.add(InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY)
        topics = frozenset()
    return replace(
        _nasa_source(),
        source_id="synthetic-newest-first",
        name="Synthetic Newest First",
        topics=topics,
        capabilities=frozenset(capabilities),
    )


def _selector_with(source):
    sources = GovernedInformationSources()
    sources.admit_non_default(source)
    return GovernedConversationalSourceSelector(sources)


def test_red_declares_typed_newest_first_order():
    assert _order_type().NEWEST_FIRST.value == "newest_first"


def test_red_selection_request_and_query_default_to_no_order():
    request = GovernedConversationalSourceSelectionRequest(
        text="NASA",
        topics=_nasa_source().topics,
    )
    query = GovernedSourceQuery(
        source_id="nasa",
        topics=_nasa_source().topics,
    )
    assert request.order is None
    assert query.order is None


def test_red_invalid_string_order_fails_closed():
    with pytest.raises(ValueError, match="order"):
        GovernedConversationalSourceSelectionRequest(
            text="NASA",
            topics=_nasa_source().topics,
            order="newest_first",
        )
    with pytest.raises(ValueError, match="order"):
        GovernedSourceQuery(
            source_id="nasa",
            topics=_nasa_source().topics,
            order="newest_first",
        )


def test_red_selector_projects_newest_first_order_unchanged():
    order = _order_type().NEWEST_FIRST
    source = _capable_source()
    selection = _selector_with(source).select(
        GovernedConversationalSourceSelectionRequest(
            text="NASA",
            topics=source.topics,
            order=order,
        ),
        registered_sources=(source.source_id,),
    )
    assert selection.status is GovernedConversationalSourceSelectionStatus.SELECTED
    assert selection.query is not None
    assert selection.query.order is order


def test_red_topic_newest_first_requires_capability():
    order = _order_type().NEWEST_FIRST
    selector = GovernedConversationalSourceSelector(GovernedInformationSources())
    selection = selector.select(
        GovernedConversationalSourceSelectionRequest(
            text="NASA",
            topics=_nasa_source().topics,
            order=order,
        ),
        registered_sources=("nasa",),
    )
    assert selection.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE


def test_red_open_visual_newest_first_requires_both_capabilities():
    order = _order_type().NEWEST_FIRST
    open_only = replace(
        _nasa_source(),
        source_id="open-only",
        name="Open Only",
        topics=frozenset(),
        capabilities=frozenset(
            {InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY}
        ),
    )
    request = GovernedConversationalSourceSelectionRequest(
        text="mostrame fotos de Saturno",
        topics=frozenset(),
        query_text="Saturno",
        order=order,
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )
    unavailable = _selector_with(open_only).select(
        request,
        registered_sources=(open_only.source_id,),
    )
    assert unavailable.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE

    capable = _capable_source(open_visual=True)
    selected = _selector_with(capable).select(
        request,
        registered_sources=(capable.source_id,),
    )
    assert selected.status is GovernedConversationalSourceSelectionStatus.SELECTED


def test_red_query_contract_gates_newest_first_capability():
    order = _order_type().NEWEST_FIRST
    query = GovernedSourceQuery(
        source_id="nasa",
        topics=_nasa_source().topics,
        order=order,
    )
    with pytest.raises(ValueError, match="capab|newest"):
        GovernedSourceQueryContract(GovernedInformationSources()).prepare(query)

    source = _capable_source()
    sources = GovernedInformationSources()
    sources.admit_non_default(source)
    admitted = replace(query, source_id=source.source_id, topics=source.topics)
    result = GovernedSourceQueryContract(sources).prepare(admitted)
    assert result.query is admitted


def test_red_date_bounds_coexist_with_newest_first():
    order = _order_type().NEWEST_FIRST
    after = datetime(2025, 1, 1, tzinfo=timezone.utc)
    before = datetime(2025, 12, 31, tzinfo=timezone.utc)
    query = GovernedSourceQuery(
        source_id="nasa",
        topics=_nasa_source().topics,
        published_after=after,
        published_before=before,
        order=order,
    )
    assert query.published_after == after
    assert query.published_before == before
    assert query.order is order


def test_red_execution_identity_includes_order():
    order = _order_type().NEWEST_FIRST
    base = GovernedSourceQuery(
        source_id="nasa",
        topics=_nasa_source().topics,
    )
    ordered = replace(base, order=order)
    executor = GovernedSourceQueryExecutor(
        GovernedSourceQueryContract(GovernedInformationSources())
    )
    response_type = importlib.import_module(
        "app.governed_source_query"
    ).GovernedSourceQueryResponse
    status_type = importlib.import_module(
        "app.governed_source_query"
    ).GovernedSourceQueryStatus
    received = datetime(2026, 1, 1, tzinfo=timezone.utc)
    response = response_type(
        source_id="nasa",
        status=status_type.EMPTY,
        raw_items=(),
        received_at=received,
    )
    first = executor._execution_id(
        query=base,
        response=response,
        started_at=received,
    )
    second = executor._execution_id(
        query=ordered,
        response=response,
        started_at=received,
    )
    assert first != second


def test_red_does_not_add_sorting_provider_projection_or_parallel_authority():
    root = Path(__file__).resolve().parents[2]
    executor = (root / "app/governed_source_query_executor.py").read_text(
        encoding="utf-8"
    )
    aci = (root / "app/applied_conversational_intelligence.py").read_text(
        encoding="utf-8"
    )
    assert "sorted(raw_items" not in executor
    assert "sorted(response.raw_items" not in executor
    for term in ("gsrsort", "create_timestamp_desc"):
        assert term not in aci.casefold()

    for module_name in (
        "app.external_image_freshness_manager",
        "app.external_image_freshness_selector",
        "app.external_image_freshness_executor",
    ):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)
