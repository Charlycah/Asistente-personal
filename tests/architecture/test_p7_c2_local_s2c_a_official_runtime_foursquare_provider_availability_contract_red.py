from __future__ import annotations

import inspect
from pathlib import Path

from app.foursquare_governed_source import FoursquareGovernedSourceAdapter
from app.official_conversation_gateway import OfficialConversationGateway
from app.official_runtime_composition import build_official_runtime_from_environment
from app.runtime_environment_wiring import (
    build_foursquare_governed_source_from_environment,
)

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_RUNTIME = ROOT / "app" / "official_runtime_composition.py"
GATEWAY = ROOT / "app" / "official_conversation_gateway.py"


def _runtime_builder_source() -> str:
    return inspect.getsource(build_official_runtime_from_environment)


def test_s2c_a_reuses_existing_provider_builder_and_registration_authority() -> None:
    assert callable(build_foursquare_governed_source_from_environment)
    assert callable(OfficialConversationGateway.register_governed_source_query_adapter)
    assert FoursquareGovernedSourceAdapter.SOURCE_ID == "foursquare_places"


def test_s2c_a_existing_provider_builder_is_fail_closed_and_non_executing() -> None:
    source = inspect.getsource(build_foursquare_governed_source_from_environment)
    assert "ROBY_FOURSQUARE_PLACES_ENABLED" in source
    assert "FOURSQUARE_SERVICE_API_KEY" in source
    assert "return None" in source
    assert "execute_governed_source_query" not in source


def test_s2c_a_official_runtime_builder_consumes_existing_provider_builder() -> None:
    source = _runtime_builder_source()
    assert "build_foursquare_governed_source_from_environment" in source, (
        "RED: official runtime does not consume the existing Foursquare builder"
    )


def test_s2c_a_registers_available_provider_through_existing_gateway_surface() -> None:
    source = _runtime_builder_source()
    assert "register_governed_source_query_adapter" in source, (
        "RED: official runtime does not register the available provider"
    )
    assert "FoursquareGovernedSourceAdapter.SOURCE_ID" in source


def test_s2c_a_provider_unavailable_remains_fail_closed() -> None:
    source = _runtime_builder_source()
    assert "if foursquare" in source.casefold()
    assert "is not None" in source


def test_s2c_a_startup_registration_does_not_execute_or_authorize_network() -> None:
    source = _runtime_builder_source()
    forbidden = (
        "execute_governed_source_query(",
        "external_access_authorized=True",
        "external_access_requested=True",
        "network_used=True",
    )
    assert not any(token in source for token in forbidden)


def test_s2c_a_preserves_protected_conversation_gateway_bytes() -> None:
    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source
    assert OFFICIAL_RUNTIME.exists()
