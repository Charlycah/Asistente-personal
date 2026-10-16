from __future__ import annotations

import inspect

import pytest

from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionRequest,
    GovernedConversationalSourceSelectionStatus,
    GovernedConversationalSourceSelector,
)
from app.governed_information_sources import GovernedInformationSources
from app.governed_source_query import GovernedSourceQuery
from app.personal_interest_center import InterestTopic


def _request_mode_type():
    module = __import__(
        "app.governed_conversational_source_selection",
        fromlist=["GovernedConversationalRequestMode"],
    )
    return module.GovernedConversationalRequestMode


def test_request_contract_declares_explicit_open_visual_subject_mode() -> None:
    mode = _request_mode_type()

    assert mode.TOPIC_CONSTRAINED.value == "topic_constrained"
    assert mode.OPEN_VISUAL_SUBJECT.value == "open_visual_subject"


def test_legacy_topic_constrained_request_remains_valid() -> None:
    mode = _request_mode_type()
    request = GovernedConversationalSourceSelectionRequest(
        text="Roby, buscá novedades de James Webb",
        topics=frozenset({InterestTopic.JAMES_WEBB_SPACE_TELESCOPE}),
        query_text="James Webb",
        mode=mode.TOPIC_CONSTRAINED,
    )

    assert request.topics == frozenset(
        {InterestTopic.JAMES_WEBB_SPACE_TELESCOPE}
    )
    assert request.query_text == "James Webb"
    assert request.mode is mode.TOPIC_CONSTRAINED


def test_open_visual_subject_request_preserves_query_without_topic() -> None:
    mode = _request_mode_type()
    request = GovernedConversationalSourceSelectionRequest(
        text="Roby, mostrame imágenes de las pistas de Nazca",
        topics=frozenset(),
        query_text="pistas de Nazca",
        mode=mode.OPEN_VISUAL_SUBJECT,
    )

    assert request.topics == frozenset()
    assert request.query_text == "pistas de Nazca"
    assert request.mode is mode.OPEN_VISUAL_SUBJECT


def test_open_visual_subject_requires_non_empty_query_text() -> None:
    mode = _request_mode_type()

    with pytest.raises(ValueError, match="query text"):
        GovernedConversationalSourceSelectionRequest(
            text="Roby, mostrame imágenes",
            topics=frozenset(),
            query_text=None,
            mode=mode.OPEN_VISUAL_SUBJECT,
        )


def test_empty_topics_remain_invalid_for_topic_constrained_mode() -> None:
    mode = _request_mode_type()

    with pytest.raises(ValueError, match="topic"):
        GovernedConversationalSourceSelectionRequest(
            text="Roby, buscá información",
            topics=frozenset(),
            query_text="información",
            mode=mode.TOPIC_CONSTRAINED,
        )


def test_open_visual_empty_topics_do_not_make_nasa_eligible() -> None:
    mode = _request_mode_type()
    request = GovernedConversationalSourceSelectionRequest(
        text="Roby, mostrame imágenes de las pistas de Nazca",
        topics=frozenset(),
        query_text="pistas de Nazca",
        mode=mode.OPEN_VISUAL_SUBJECT,
    )
    selector = GovernedConversationalSourceSelector(
        GovernedInformationSources()
    )

    selection = selector.select(request, registered_sources=("nasa",))

    assert selection.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE
    assert selection.source is None
    assert selection.query is None
    assert "nasa" not in selection.eligible_sources


def test_governed_query_contract_can_preserve_open_visual_mode() -> None:
    mode = _request_mode_type()
    query = GovernedSourceQuery(
        source_id="future_open_visual_source",
        topics=frozenset(),
        query_text="pistas de Nazca",
        mode=mode.OPEN_VISUAL_SUBJECT,
    )

    assert query.query_text == "pistas de Nazca"
    assert query.mode is mode.OPEN_VISUAL_SUBJECT
    assert query.topics == frozenset()


def test_no_parallel_visual_router_selector_or_executor_is_introduced() -> None:
    root = __import__("app", fromlist=["__path__"]).__path__[0]
    forbidden = (
        "OpenVisualSubjectRouter",
        "GeneralImageSourceSelector",
        "OpenVisualQueryExecutor",
    )

    from pathlib import Path

    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path(root).glob("*.py")
    )
    for name in forbidden:
        assert name not in source


def test_existing_selector_remains_canonical_selection_surface() -> None:
    source = inspect.getsource(GovernedConversationalSourceSelector.select)

    assert "_is_eligible" in source
    assert "registered_sources" in source


def test_contract_red_does_not_introduce_freshness_or_presentation_semantics() -> None:
    source = inspect.getsource(
        GovernedConversationalSourceSelectionRequest
    )

    assert "newest" not in source
    assert "latest" not in source
    assert "presentation" not in source
