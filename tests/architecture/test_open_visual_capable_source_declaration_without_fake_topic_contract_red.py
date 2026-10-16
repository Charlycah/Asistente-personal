from __future__ import annotations

import importlib
from dataclasses import replace

import pytest

from app.governed_conversational_request_mode import GovernedConversationalRequestMode
from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionRequest,
    GovernedConversationalSourceSelectionStatus,
    GovernedConversationalSourceSelector,
)
from app.governed_information_sources import (
    GovernedInformationItem,
    GovernedInformationSources,
    InformationSourceCapability,
)
from app.governed_source_query import GovernedSourceQuery, GovernedSourceQueryContract
from app.personal_interest_center import InterestTopic


def _nasa_source():
    return GovernedInformationSources().source_for("nasa")


def _open_capability():
    return InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY


def _empty_topic_capable_source():
    return replace(
        _nasa_source(),
        source_id="synthetic-open-visual-empty-topics",
        name="Synthetic Open Visual Empty Topics",
        topics=frozenset(),
        capabilities=frozenset({_open_capability()}),
    )


def _open_request():
    return GovernedConversationalSourceSelectionRequest(
        text="Roby, mostrame imágenes de las pistas de Nazca.",
        topics=frozenset(),
        query_text="pistas de Nazca",
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )


def test_empty_topic_source_without_open_visual_capability_remains_invalid():
    with pytest.raises(ValueError, match="topic"):
        replace(
            _nasa_source(),
            source_id="synthetic-empty-topics-without-capability",
            name="Synthetic Empty Topics Without Capability",
            topics=frozenset(),
        )


def test_empty_topic_source_with_explicit_open_visual_capability_is_valid():
    source = _empty_topic_capable_source()
    assert source.topics == frozenset()
    assert _open_capability() in source.capabilities


def test_open_visual_capability_does_not_require_empty_topics():
    source = replace(
        _nasa_source(),
        source_id="synthetic-open-visual-with-topics",
        name="Synthetic Open Visual With Topics",
        capabilities=frozenset({_open_capability()}),
    )
    assert source.topics
    assert _open_capability() in source.capabilities


def test_default_sources_keep_real_topic_declarations():
    sources = GovernedInformationSources()
    assert all(source.topics for source in sources.snapshot.sources)


def test_nasa_remains_topic_bounded_and_not_open_visual_capable():
    nasa = _nasa_source()
    assert nasa.topics
    assert _open_capability() not in nasa.capabilities


def test_empty_topic_capable_source_uses_existing_non_default_admission_path():
    sources = GovernedInformationSources()
    source = _empty_topic_capable_source()
    sources.admit_non_default(source)
    assert sources.source_for(source.source_id) == source


def test_registered_empty_topic_capable_source_is_open_visual_eligible():
    sources = GovernedInformationSources()
    source = _empty_topic_capable_source()
    sources.admit_non_default(source)
    selection = GovernedConversationalSourceSelector(sources).select(
        _open_request(), registered_sources=(source.source_id,)
    )
    assert selection.status is GovernedConversationalSourceSelectionStatus.SELECTED
    assert selection.source == source
    assert selection.query is not None
    assert selection.query.topics == frozenset()


def test_empty_topic_capable_source_is_not_topic_constrained_wildcard():
    sources = GovernedInformationSources()
    source = _empty_topic_capable_source()
    sources.admit_non_default(source)
    request = GovernedConversationalSourceSelectionRequest(
        text="Roby, buscá novedades de NASA.",
        topics=frozenset({InterestTopic.NASA_MISSIONS}),
        query_text="NASA",
    )
    selection = GovernedConversationalSourceSelector(sources).select(
        request, registered_sources=(source.source_id,)
    )
    assert selection.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE
    assert selection.source is None


def test_query_contract_accepts_empty_topics_only_by_explicit_capability():
    sources = GovernedInformationSources()
    source = _empty_topic_capable_source()
    sources.admit_non_default(source)
    query = GovernedSourceQuery(
        source_id=source.source_id,
        topics=frozenset(),
        query_text="pistas de Nazca",
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )
    result = GovernedSourceQueryContract(sources).prepare(query)
    assert result.source == source
    assert result.query == query


def test_governed_information_item_empty_topics_remains_invalid():
    with pytest.raises(ValueError, match="topic"):
        GovernedInformationItem(
            source_id="synthetic-open-visual-empty-topics",
            external_id="image-1",
            title="Image",
            topics=frozenset(),
        )


def test_contract_red_adds_no_provider_or_parallel_authority():
    forbidden = (
        "app.open_visual_source_registry",
        "app.open_visual_source_selector",
        "app.open_visual_query_executor",
    )
    for module_name in forbidden:
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)
