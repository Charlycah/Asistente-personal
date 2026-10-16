from __future__ import annotations

import importlib
from dataclasses import replace

import pytest

from app.governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionRequest,
    GovernedConversationalSourceSelectionStatus,
    GovernedConversationalSourceSelector,
)
from app.governed_information_sources import GovernedInformationSources
from app.governed_source_query import (
    GovernedSourceQuery,
    GovernedSourceQueryContract,
)


def _source_module():
    return importlib.import_module("app.governed_information_sources")


def _capability_type():
    return getattr(_source_module(), "InformationSourceCapability")


def _nasa_source():
    return GovernedInformationSources().source_for("nasa")


def _open_request():
    return GovernedConversationalSourceSelectionRequest(
        text="Roby, mostrame imágenes de las pistas de Nazca.",
        topics=frozenset(),
        query_text="pistas de Nazca",
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )


def test_source_capability_contract_declares_open_visual_subject_query():
    capability_type = _capability_type()
    assert capability_type.OPEN_VISUAL_SUBJECT_QUERY.value == (
        "open_visual_subject_query"
    )


def test_legacy_sources_default_to_empty_capability_set():
    assert _nasa_source().capabilities == frozenset()


def test_nasa_does_not_claim_general_open_visual_capability():
    capability_type = _capability_type()
    assert capability_type.OPEN_VISUAL_SUBJECT_QUERY not in _nasa_source().capabilities


def test_open_visual_request_without_capable_source_is_unavailable():
    selector = GovernedConversationalSourceSelector(GovernedInformationSources())
    selection = selector.select(_open_request(), registered_sources=())
    assert selection.status is GovernedConversationalSourceSelectionStatus.UNAVAILABLE
    assert selection.source is None
    assert selection.query is None


def test_selector_accepts_explicitly_capable_synthetic_source():
    capability_type = _capability_type()
    sources = GovernedInformationSources()
    nasa = _nasa_source()
    synthetic = replace(
        nasa,
        source_id="synthetic-open-visual",
        name="Synthetic Open Visual",
        capabilities=frozenset({capability_type.OPEN_VISUAL_SUBJECT_QUERY}),
    )
    sources.admit_non_default(synthetic)
    selection = GovernedConversationalSourceSelector(sources).select(
        _open_request(), registered_sources=(synthetic.source_id,)
    )
    assert selection.status is GovernedConversationalSourceSelectionStatus.SELECTED
    assert selection.source == synthetic
    assert selection.query is not None
    assert selection.query.source_id == synthetic.source_id
    assert selection.query.mode is GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT
    assert selection.query.query_text == "pistas de Nazca"
    assert selection.query.topics == frozenset()


def test_query_contract_rejects_open_visual_query_for_non_capable_source():
    sources = GovernedInformationSources()
    source = _nasa_source()
    contract = GovernedSourceQueryContract(sources)
    query = GovernedSourceQuery(
        source_id=source.source_id,
        topics=frozenset(),
        query_text="pistas de Nazca",
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )
    with pytest.raises(ValueError, match="capab|open visual"):
        contract.prepare(query)


def test_query_contract_accepts_open_visual_query_for_capable_synthetic_source():
    capability_type = _capability_type()
    sources = GovernedInformationSources()
    nasa = _nasa_source()
    synthetic = replace(
        nasa,
        source_id="synthetic-open-visual",
        name="Synthetic Open Visual",
        capabilities=frozenset({capability_type.OPEN_VISUAL_SUBJECT_QUERY}),
    )
    sources.admit_non_default(synthetic)
    contract = GovernedSourceQueryContract(sources)
    query = GovernedSourceQuery(
        source_id=synthetic.source_id,
        topics=frozenset(),
        query_text="pistas de Nazca",
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )
    result = contract.prepare(query)
    assert result.source == synthetic
    assert result.query == query


def test_contract_red_does_not_add_parallel_visual_authorities():
    forbidden = (
        "app.visual_source_selector",
        "app.open_visual_source_registry",
        "app.open_visual_query_executor",
    )
    for module_name in forbidden:
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)
