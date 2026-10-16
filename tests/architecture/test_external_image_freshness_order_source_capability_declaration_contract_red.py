from __future__ import annotations

import importlib
from dataclasses import replace
from pathlib import Path

import pytest

from app.governed_information_sources import GovernedInformationSources


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _app_file(*parts: str) -> Path:
    return _repo_root().joinpath("app", *parts)


def _source_module():
    return importlib.import_module("app.governed_information_sources")


def _capability_type():
    return getattr(_source_module(), "InformationSourceCapability")


def _nasa_source():
    return GovernedInformationSources().source_for("nasa")


def _wikimedia_declaration():
    module = importlib.import_module("app.wikimedia_commons_governed_source")
    return module.WikimediaCommonsGovernedSourceAdapter.source_declaration


def test_red_declares_external_image_newest_first_query_capability():
    capability_type = _capability_type()
    assert capability_type.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY.value == (
        "external_image_newest_first_query"
    )


def test_red_legacy_default_sources_keep_empty_capability_sets():
    sources = GovernedInformationSources()
    assert all(
        source.capabilities == frozenset() for source in sources.sources.values()
    )


def test_red_nasa_does_not_claim_newest_first_capability():
    capability_type = _capability_type()
    assert (
        capability_type.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY
        not in _nasa_source().capabilities
    )


def test_red_wikimedia_explicitly_declares_both_visual_capabilities():
    capability_type = _capability_type()
    declaration = _wikimedia_declaration()
    assert declaration.capabilities == frozenset(
        {
            capability_type.OPEN_VISUAL_SUBJECT_QUERY,
            capability_type.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY,
        }
    )


def test_red_newest_first_capability_is_independent_for_topical_source():

    capability_type = _capability_type()
    source = replace(
        _nasa_source(),
        source_id="synthetic-newest-first",
        name="Synthetic Newest First",
        capabilities=frozenset({capability_type.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY}),
    )
    assert source.topics
    assert source.capabilities == frozenset(
        {capability_type.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY}
    )
    assert capability_type.OPEN_VISUAL_SUBJECT_QUERY not in source.capabilities


def test_red_newest_first_capability_alone_does_not_authorize_empty_topics():
    capability_type = _capability_type()
    with pytest.raises(ValueError, match="topic"):
        replace(
            _nasa_source(),
            source_id="synthetic-empty-newest-first",
            name="Synthetic Empty Newest First",
            topics=frozenset(),
            capabilities=frozenset({capability_type.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY}),
        )


def test_red_open_visual_capability_still_authorizes_empty_topics():
    capability_type = _capability_type()
    source = replace(
        _nasa_source(),
        source_id="synthetic-open-visual",
        name="Synthetic Open Visual",
        topics=frozenset(),
        capabilities=frozenset({capability_type.OPEN_VISUAL_SUBJECT_QUERY}),
    )
    assert source.topics == frozenset()


def test_red_timestamp_metadata_does_not_infer_source_capability():
    source_module = _source_module()
    capability_type = _capability_type()
    item = source_module.GovernedInformationItem(
        source_id="nasa",
        external_id="item-1",
        title="Timestamped item",
        topics=_nasa_source().topics,
    )
    assert item.published_at is None
    assert _nasa_source().capabilities == frozenset()
    assert (
        capability_type.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY
        not in _nasa_source().capabilities
    )


def test_red_does_not_add_freshness_wiring_or_parallel_authorities():
    source_selection = Path(
        "app/governed_conversational_source_selection.py"
    ).read_text(encoding="utf-8")
    source_query = Path("app/governed_source_query.py").read_text(encoding="utf-8")
    ()
    forbidden_text = (
        "freshness_order",
        "newest_first=",
    )
    assert all(term not in source_selection for term in forbidden_text)
    assert all(term not in source_query for term in forbidden_text)

    forbidden_modules = (
        "app.external_image_freshness_manager",
        "app.external_image_freshness_selector",
        "app.external_image_freshness_executor",
        "app.wikimedia_commons_freshness_manager",
    )
    for module_name in forbidden_modules:
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)
