from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.map_display import (
    MapDisplayRequest,
    MapDisplayResult,
    MapDisplayStatus,
    MapDisplayTarget,
    MapDocument,
    MapDocumentRenderer,
    MapGeocodingProvider,
    MapPresentationMode,
    MapPresentationResult,
    MapPresentationStatus,
    MapPresenter,
)
from core.maps_foundation import GeoPointSignal

NOW = datetime(2026, 7, 26, 18, 0, tzinfo=timezone.utc)
POINT = GeoPointSignal(-34.6083, -58.3712, 0.96, NOW, "nominatim")


def request(**changes):
    values = dict(owner="Carlos", query="Plaza de Mayo")
    values.update(changes)
    return MapDisplayRequest(**values)


def target(**changes):
    values = dict(
        label="Plaza de Mayo, Buenos Aires",
        point=POINT,
        confidence=0.96,
        source="Nominatim",
        external_id="osm:123",
    )
    values.update(changes)
    return MapDisplayTarget(**values)


def document(**changes):
    values = dict(
        uri="file:///tmp/roby-map.html",
        media_type="text/html",
        title="Mapa de Plaza de Mayo",
    )
    values.update(changes)
    return MapDocument(**values)


def presentation(**changes):
    values = dict(
        status=MapPresentationStatus.PRESENTED,
        presented=True,
        surface="Embedded_Window",
        rationale=("map_presented",),
    )
    values.update(changes)
    return MapPresentationResult(**values)


def ready_result(**changes):
    values = dict(
        request=request(),
        status=MapDisplayStatus.READY,
        target=target(),
        document=document(),
        presentation=presentation(),
        provider_required=False,
        clarification_required=False,
        rationale=("map_display_ready",),
    )
    values.update(changes)
    return MapDisplayResult(**values)


def test_request_normalizes_owner_and_query():
    result = request(owner="  Carlos   Alberto ", query="  Plaza   de Mayo ")
    assert result.owner == "Carlos Alberto"
    assert result.query == "Plaza de Mayo"


def test_request_accepts_string_presentation_mode():
    result = request(presentation_mode="system_browser")
    assert result.presentation_mode is MapPresentationMode.SYSTEM_BROWSER


@pytest.mark.parametrize("zoom", [0, 21])
def test_request_rejects_invalid_zoom(zoom):
    with pytest.raises(ValueError, match="zoom"):
        request(zoom=zoom)


@pytest.mark.parametrize("field", ["owner", "query"])
def test_request_rejects_blank_identity_fields(field):
    with pytest.raises(ValueError, match="must not be blank"):
        request(**{field: "   "})


def test_request_id_is_deterministic_and_case_insensitive():
    first = request(owner="Carlos", query="Plaza de Mayo")
    second = request(owner="CARLOS", query="plaza DE mayo")
    assert first.request_id == second.request_id


def test_request_rejects_inconsistent_id():
    with pytest.raises(ValueError, match="inconsistent"):
        request(request_id="invalid")


def test_target_normalizes_values():
    result = target(label="  Plaza   de Mayo ", source="  NOMINATIM  ")
    assert result.label == "Plaza de Mayo"
    assert result.source == "nominatim"


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_target_rejects_invalid_confidence(confidence):
    with pytest.raises(ValueError, match="confidence"):
        target(confidence=confidence)


def test_target_rejects_blank_external_id():
    with pytest.raises(ValueError, match="external id"):
        target(external_id=" ")


def test_document_requires_html():
    with pytest.raises(ValueError, match="text/html"):
        document(media_type="application/json")


def test_document_normalizes_metadata():
    result = document(media_type=" TEXT/HTML ", title="  Mapa   central ")
    assert result.media_type == "text/html"
    assert result.title == "Mapa central"


def test_presented_result_requires_surface():
    with pytest.raises(ValueError, match="active surface"):
        presentation(surface=None)


def test_failed_presentation_cannot_claim_surface():
    with pytest.raises(ValueError, match="cannot expose"):
        presentation(status="failed", presented=False)


def test_unavailable_presentation_is_valid_without_surface():
    result = presentation(
        status="unavailable",
        presented=False,
        surface=None,
        rationale=("presenter_unavailable",),
    )
    assert result.status is MapPresentationStatus.UNAVAILABLE


def test_ready_display_exposes_all_artifacts():
    result = ready_result()
    assert result.status is MapDisplayStatus.READY
    assert result.target is not None
    assert result.document is not None
    assert result.presentation is not None


def test_ready_display_requires_target_and_document():
    with pytest.raises(ValueError, match="target and document"):
        ready_result(target=None)


def test_ready_display_cannot_require_clarification():
    with pytest.raises(ValueError, match="cannot require clarification"):
        ready_result(clarification_required=True)


def test_ambiguous_display_requires_clarification():
    with pytest.raises(ValueError, match="must require clarification"):
        MapDisplayResult(
            request=request(),
            status="ambiguous",
            target=None,
            document=None,
            presentation=None,
            provider_required=False,
            clarification_required=False,
            rationale=("multiple_locations",),
        )


def test_inactive_display_cannot_expose_document():
    with pytest.raises(ValueError, match="cannot expose"):
        ready_result(status="not_found", target=None, presentation=None)


def test_display_result_id_is_deterministic():
    assert ready_result().result_id == ready_result().result_id


def test_display_result_rejects_inconsistent_id():
    with pytest.raises(ValueError, match="inconsistent"):
        ready_result(result_id="invalid")


def test_contracts_are_immutable():
    with pytest.raises(FrozenInstanceError):
        ready_result().status = MapDisplayStatus.FAILED


def test_replace_produces_a_new_consistent_request_id():
    original = request()
    updated = replace(original, query="Obelisco", request_id="")
    assert updated.request_id != original.request_id


def test_geocoding_protocol_is_runtime_checkable():
    class Provider:
        def resolve(self, request):
            return (target(),)

    assert isinstance(Provider(), MapGeocodingProvider)


def test_renderer_protocol_is_runtime_checkable():
    class Renderer:
        def render(self, request, target):
            return document()

    assert isinstance(Renderer(), MapDocumentRenderer)


def test_presenter_protocol_is_runtime_checkable():
    class Presenter:
        def present(self, document, *, mode):
            return presentation()

    assert isinstance(Presenter(), MapPresenter)
