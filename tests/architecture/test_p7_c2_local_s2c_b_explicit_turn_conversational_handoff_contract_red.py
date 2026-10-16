from __future__ import annotations

import inspect

from app import official_conversation_gateway, official_runtime_composition

OfficialConversationGateway = official_conversation_gateway.OfficialConversationGateway
OfficialROBYRuntime = official_runtime_composition.OfficialROBYRuntime


ENTRY = "submit_governed_local_business_turn"


def _runtime_source() -> str:
    return inspect.getsource(OfficialROBYRuntime)


def test_s2c_b_entry_belongs_to_existing_official_runtime() -> None:
    assert hasattr(OfficialROBYRuntime, ENTRY), (
        "RED: OfficialROBYRuntime lacks the bounded local/business entry"
    )


def test_s2c_b_entry_requires_explicit_local_business_intent() -> None:
    source = _runtime_source()
    assert "explicit_local_business_intent" in source, (
        "RED: explicit local/business intent is not carried by runtime composition"
    )


def test_s2c_b_entry_carries_bounded_geographic_context() -> None:
    source = _runtime_source()
    assert "geographic_context" in source, (
        "RED: bounded geography is not carried into the existing S1 seam"
    )


def test_s2c_b_entry_requires_explicit_external_access_authorization() -> None:
    source = _runtime_source()
    assert "external_access_authorized" in source, (
        "RED: per-turn external-access authorization is not explicit"
    )


def test_s2c_b_reuses_existing_s1_composition() -> None:
    source = _runtime_source()
    assert "GovernedPlaceBusinessSourceQueryComposition" in source, (
        "RED: existing S1 composition is not reused"
    )


def test_s2c_b_reuses_existing_s2b_a_composition() -> None:
    source = _runtime_source()
    assert "GovernedPlaceBusinessExternalExecutionComposition" in source, (
        "RED: existing S2B-A composition is not reused"
    )


def test_s2c_b_reuses_existing_s2b_b_composition() -> None:
    source = _runtime_source()
    assert "GovernedExternalCognitiveAdmissionComposition" in source, (
        "RED: existing S2B-B composition is not reused"
    )


def test_s2c_b_existing_conversation_handoff_accepts_external_evidence() -> None:
    signature = inspect.signature(OfficialConversationGateway.submit)
    assert "external_evidence" in signature.parameters


def test_s2c_b_runtime_exposes_existing_conversation_gateway() -> None:
    assert isinstance(OfficialROBYRuntime.conversation, property)


def test_s2c_b_handoff_uses_existing_submit_surface() -> None:
    source = _runtime_source()
    assert ".submit(" in source and "external_evidence=" in source, (
        "RED: M401 admission is not handed to the existing conversation submit"
    )


def test_s2c_b_does_not_create_parallel_runtime_or_gateway() -> None:
    source = _runtime_source()
    forbidden = ("LocalBusinessRuntime", "RestaurantAgent", "MapsBrain")
    assert all(marker not in source for marker in forbidden)


def test_s2c_b_does_not_embed_provider_startup_as_turn_authorization() -> None:
    source = _runtime_source()
    assert "ROBY_FOURSQUARE_PLACES_ENABLED" not in source


def test_s2c_b_does_not_add_booking_or_navigation_authority() -> None:
    source = _runtime_source().casefold()
    assert "book_reservation" not in source
    assert "navigate_to_place" not in source


def test_s2c_b_does_not_add_location_persistence() -> None:
    source = _runtime_source().casefold()
    assert "persist_location" not in source
    assert "remember_location" not in source


def test_s2c_b_does_not_add_memory_learning_or_execution_authority() -> None:
    source = _runtime_source()
    assert "local_business_memory" not in source
    assert "local_business_learning" not in source
    assert "local_business_execution" not in source


def test_s2c_b_entry_returns_existing_conversational_result_contract() -> None:
    source = _runtime_source()
    assert "LocalConversationTurn" in source, (
        "RED: bounded entry does not expose the existing conversation result contract"
    )
