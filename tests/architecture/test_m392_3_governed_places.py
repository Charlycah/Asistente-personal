from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.governed_places_representation import PlaceRepresentationStatus
from core.location_resolution import (
    LocationCandidate,
    LocationReferenceKind,
    LocationResolutionAction,
    LocationResolutionRequest,
    LocationResolutionStatus,
    ResolvedLocation,
)
from core.maps_foundation import (
    GeoPointSignal,
    MapContext,
    MapFoundationAction,
    MapFoundationStatus,
    MapPrecision,
    MapPurpose,
    MapScope,
    MapsFoundationRequest,
)
from core.places_knowledge import (
    PlaceFact,
    PlaceFactKind,
    PlacesKnowledgeEngine,
    PlacesKnowledgeRequest,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 12, 0, tzinfo=timezone.utc)
POINT = GeoPointSignal(-26.83, -65.20, 0.9, NOW, "declared")


def _profile():
    map_request = MapsFoundationRequest(
        owner="Carlos",
        purpose=MapPurpose.PLACE_CONTEXT,
        requested_precision=MapPrecision.NEIGHBORHOOD,
        requested_scope=MapScope.LOCAL,
        location=POINT,
        explicit_user_consent=True,
    )
    context = MapContext(
        request=map_request,
        status=MapFoundationStatus.READY,
        action=MapFoundationAction.ESTABLISH,
        effective_precision=MapPrecision.NEIGHBORHOOD,
        effective_scope=MapScope.LOCAL,
        location_available=True,
        provider_required=False,
        route_computation_allowed=False,
        rationale=("maps_context_ready",),
        created_at=NOW,
    )
    candidate = LocationCandidate(
        label="Casa",
        kind=LocationReferenceKind.PLACE,
        confidence=0.9,
        point=POINT,
    )
    resolution_request = LocationResolutionRequest(
        owner="Carlos",
        map_context=context,
        reference="Casa",
        reference_kind=LocationReferenceKind.PLACE,
        candidates=(candidate,),
    )
    resolution = ResolvedLocation(
        request=resolution_request,
        status=LocationResolutionStatus.RESOLVED,
        action=LocationResolutionAction.ACCEPT,
        selected_candidate=candidate,
        resolved_label="Casa",
        resolved_point=POINT,
        confidence=0.9,
        provider_required=False,
        clarification_required=False,
        rationale=("location_resolution_declared_candidate_selected",),
        created_at=NOW,
    )
    request = PlacesKnowledgeRequest(
        owner="Carlos",
        resolved_location=resolution,
        facts=(
            PlaceFact(
                kind=PlaceFactKind.CATEGORY,
                name="category",
                value="home",
                confidence=0.9,
                source="declared",
            ),
        ),
    )
    return PlacesKnowledgeEngine().establish(request, now=NOW)


def test_m392_3_uses_internal_world_model_authority() -> None:
    report = InternalWorldModelFoundation().places_representation((_profile(),))
    assert report.canonical_authority == "internal_world_model"
    assert report.status is PlaceRepresentationStatus.COMPLETE


def test_m392_3_projects_ready_place_profile() -> None:
    report = InternalWorldModelFoundation().places_representation((_profile(),))
    place = report.places[0]
    assert place.label == "Casa"
    assert place.reference_kind == "place"
    assert place.facts[0].value == "home"


def test_m392_3_does_not_expose_live_coordinates() -> None:
    report = InternalWorldModelFoundation().places_representation((_profile(),))
    place = report.places[0]
    assert not hasattr(place, "point")
    assert not hasattr(place, "latitude")
    assert report.uses_live_location is False


def test_m392_3_is_read_only_and_non_persistent() -> None:
    report = InternalWorldModelFoundation().places_representation((_profile(),))
    assert report.read_only is True
    assert report.persistence_added is False
    assert report.modifies_source_data is False
    assert report.tracks_people is False


def test_m392_3_is_deterministic() -> None:
    profile = _profile()
    foundation = InternalWorldModelFoundation()
    first = foundation.places_representation((profile,))
    second = foundation.places_representation((profile,))
    assert first == second


def test_m392_3_empty_input_stays_empty() -> None:
    report = InternalWorldModelFoundation().places_representation()
    assert report.status is PlaceRepresentationStatus.EMPTY
    assert report.places == ()


def test_m392_3_duplicate_profile_is_rejected() -> None:
    profile = _profile()
    with pytest.raises(ValueError, match="profile ids must be unique"):
        InternalWorldModelFoundation().places_representation((profile, profile))


def test_m392_3_report_is_immutable() -> None:
    report = InternalWorldModelFoundation().places_representation((_profile(),))
    with pytest.raises(FrozenInstanceError):
        report.read_only = False


def test_m392_3_does_not_reference_credentials() -> None:
    paths = (
        ROOT / "core" / "governed_places_representation.py",
        ROOT / "app" / "internal_world_model_foundation.py",
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "credentials.json" not in text
    assert ".roby" not in text


def test_m392_3_preserves_core_constructor_contract() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    lines = [
        index
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if "CanonicalCognitiveCore(" in line
    ]
    assert lines == [52]
