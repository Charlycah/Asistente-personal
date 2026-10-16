from __future__ import annotations

import importlib
import inspect

from app.governed_conversational_source_selection import (
    GovernedConversationalSourceSelectionRequest,
    GovernedConversationalSourceSelector,
)
from app.governed_information_sources import GovernedInformationSources
from app.governed_source_query import GovernedSourceQuery, GovernedSourceQueryContract
from app.governed_source_query_executor import GovernedSourceQueryExecutor

MODULE = "app.governed_place_business_source_query_composition"
TYPE = "GovernedPlaceBusinessSourceQueryComposition"


def _seam_type() -> type:
    try:
        module = importlib.import_module(MODULE)
    except ModuleNotFoundError:
        raise AssertionError(
            "RED: bounded governed place/business source-query composition "
            "seam is missing"
        ) from None
    return getattr(module, TYPE)


def test_existing_governed_source_query_authorities_are_reused() -> None:
    assert GovernedInformationSources is not None
    assert GovernedConversationalSourceSelectionRequest is not None
    assert GovernedConversationalSourceSelector is not None
    assert GovernedSourceQuery is not None
    assert GovernedSourceQueryContract is not None
    assert GovernedSourceQueryExecutor is not None


def test_red_bounded_place_business_source_query_seam_exists() -> None:
    seam = _seam_type()
    assert inspect.isclass(seam)


def test_red_seam_requires_explicit_intent_and_bounded_geography() -> None:
    seam = _seam_type()
    signature = inspect.signature(seam.compose)
    assert "explicit_local_business_intent" in signature.parameters
    assert "geographic_context" in signature.parameters


def test_red_locality_text_does_not_require_precise_device_location() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    assert "near" in source
    assert "latitude" not in inspect.signature(seam.compose).parameters
    assert "longitude" not in inspect.signature(seam.compose).parameters


def test_red_missing_geography_fails_closed_without_ip_fallback() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    assert "NOT_AUTHORIZED" in source or "UNAVAILABLE" in source
    forbidden = (
        "ip_geolocation",
        "ip_location",
        "geoip",
        "get_current_location",
    )
    assert not any(token in source.casefold() for token in forbidden)


def test_red_query_fields_and_result_limit_are_bounded() -> None:
    seam = _seam_type()
    signature = inspect.signature(seam.compose)
    assert "query_text" in signature.parameters
    assert "limit" in signature.parameters
    assert "fields" in signature.parameters


def test_red_reuses_existing_selector_and_query_contract() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    assert "GovernedConversationalSourceSelector" in source
    assert "GovernedSourceQuery" in source
    assert "GovernedSourceQueryContract" in source


def test_red_seam_stops_before_retrieval_or_network_execution() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    forbidden = (
        "OfficialExternalRetrievalRuntimeGateway",
        "OfficialUnifiedRetrievalExecutionRuntimeGateway",
        ".execute(",
        "requests.",
        "httpx.",
        "urllib.request",
        "subprocess.",
    )
    assert not any(token in source for token in forbidden)


def test_red_provider_is_adapter_edge_not_canonical_authority() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    assert "foursquare" in source.casefold()
    forbidden = (
        "FoursquareBrain",
        "FoursquareManager",
        "FoursquareCoordinator",
        "FoursquareReasoning",
        "RestaurantAgent",
        "LocalBrain",
        "MapsBrain",
    )
    assert not any(token in source for token in forbidden)


def test_red_discovery_does_not_authorize_reservation_or_navigation() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    forbidden = (
        "book_reservation(",
        "reserve_table(",
        "create_route(",
        "navigate_to(",
        "booking_gateway",
        "navigation_gateway",
    )
    assert not any(token in source for token in forbidden)


def test_red_preserves_no_memory_learning_planning_execution_authority() -> None:
    seam = _seam_type()
    source = inspect.getsource(importlib.import_module(seam.__module__))
    forbidden = (
        "remember_governed_learning",
        "memory_gateway.write",
        "learning_gateway",
        "planning_gateway",
        "execution_gateway",
        "publish_text",
        "retrieval_enabled=True",
    )
    assert not any(token in source for token in forbidden)
