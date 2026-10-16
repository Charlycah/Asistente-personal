from datetime import datetime, timezone

import pytest

from app.map_conversation_runtime import (
    MapConversationInterceptionPort,
    MapConversationPolicy,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.map_display import MapDisplayTarget, MapDocument, MapPresentationResult
from core.maps_foundation import GeoPointSignal


class Geocoder:
    def __init__(self, targets=(), error=None):
        self.targets = targets
        self.error = error
        self.calls = []

    def resolve(self, request):
        self.calls.append(request)
        if self.error:
            raise self.error
        return self.targets


class Renderer:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    def render(self, request, target):
        self.calls.append((request, target))
        if self.error:
            raise self.error
        return MapDocument(
            "file:///tmp/map.html",
            "text/html",
            f"Mapa de {target.label}",
        )


class Presenter:
    def __init__(self, result=None, error=None):
        self.result = result or MapPresentationResult(
            "presented", True, "system_browser", ("ok",)
        )
        self.error = error
        self.calls = []

    def present(self, document, *, mode):
        self.calls.append((document, mode))
        if self.error:
            raise self.error
        return self.result


def target(label="Plaza de Mayo, Buenos Aires"):
    return MapDisplayTarget(
        label=label,
        point=GeoPointSignal(
            -34.6083, -58.3712, 0.9, datetime.now(timezone.utc), "test"
        ),
        confidence=0.9,
        source="test",
    )


def request(text):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="test", text=text
    )


@pytest.mark.parametrize(
    "text",
    [
        "mostrame el mapa de Plaza de Mayo",
        "abrí un mapa de Rosario",
        "¿dónde queda Ushuaia?",
        "ubicación de Córdoba",
        "mostrame Buenos Aires en el mapa",
        "mapa del Obelisco",
    ],
)
def test_detects_map_requests(text):
    assert MapConversationInterceptionPort.is_map_request(text)


@pytest.mark.parametrize(
    "text",
    [
        "cómo está el clima",
        "dame las noticias",
        "quién juega hoy",
        "hola roby",
        "mostrame una foto",
    ],
)
def test_rejects_non_map_requests(text):
    assert not MapConversationInterceptionPort.is_map_request(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("mostrame el mapa de Plaza de Mayo", "Plaza de Mayo"),
        ("abrí un mapa de Rosario", "Rosario"),
        ("¿dónde queda Ushuaia?", "Ushuaia"),
        ("ubicación de Córdoba", "Córdoba"),
        ("mostrame Buenos Aires en el mapa", "Buenos Aires"),
        ("mapa del Obelisco", "del Obelisco"),
    ],
)
def test_extracts_location_query(text, expected):
    assert MapConversationInterceptionPort.extract_query(text) == expected


def test_non_map_request_returns_none():
    runtime = MapConversationInterceptionPort(Geocoder(), Renderer(), Presenter())
    assert runtime.intercept(request("hola"), now=None) is None


def test_missing_location_requests_clarification():
    runtime = MapConversationInterceptionPort(Geocoder(), Renderer(), Presenter())
    result = runtime.intercept(request("abrí un mapa"), now=None)
    assert "qué lugar" in result.response_text
    assert result.rationale == "map_conversation_location_required"


def test_success_orchestrates_all_components():
    geocoder, renderer, presenter = Geocoder((target(),)), Renderer(), Presenter()
    runtime = MapConversationInterceptionPort(geocoder, renderer, presenter)
    result = runtime.intercept(request("mostrame el mapa de Plaza de Mayo"), now=None)
    assert result.response_text.startswith("Abrí el mapa de")
    assert result.rationale == "map_conversation_completed"
    assert len(geocoder.calls) == len(renderer.calls) == len(presenter.calls) == 1
    assert geocoder.calls[0].query == "Plaza de Mayo"
    assert geocoder.calls[0].explicit_user_request is True


def test_not_found_is_conversational():
    runtime = MapConversationInterceptionPort(Geocoder(()), Renderer(), Presenter())
    result = runtime.intercept(request("mapa de Lugar Inexistente"), now=None)
    assert "No pude encontrar" in result.response_text
    assert result.rationale == "map_conversation_location_not_found"


def test_ambiguous_result_requests_choice():
    runtime = MapConversationInterceptionPort(
        Geocoder((target("Uno"), target("Dos"))), Renderer(), Presenter()
    )
    result = runtime.intercept(request("mapa de San Martín"), now=None)
    assert "varias ubicaciones" in result.response_text
    assert "Uno" in result.response_text and "Dos" in result.response_text
    assert result.rationale == "map_conversation_location_ambiguous"


def test_geocoder_error_is_contained():
    runtime = MapConversationInterceptionPort(
        Geocoder(error=RuntimeError()), Renderer(), Presenter()
    )
    result = runtime.intercept(request("mapa de Rosario"), now=None)
    assert result.rationale == "map_conversation_geocoder_failed"


def test_renderer_error_is_contained():
    runtime = MapConversationInterceptionPort(
        Geocoder((target(),)), Renderer(error=RuntimeError()), Presenter()
    )
    result = runtime.intercept(request("mapa de Rosario"), now=None)
    assert "no pude generar" in result.response_text
    assert result.rationale == "map_conversation_renderer_failed"


def test_presenter_exception_is_contained():
    runtime = MapConversationInterceptionPort(
        Geocoder((target(),)), Renderer(), Presenter(error=RuntimeError())
    )
    result = runtime.intercept(request("mapa de Rosario"), now=None)
    assert "no pude abrirlo" in result.response_text
    assert result.rationale == "map_conversation_presenter_failed"


@pytest.mark.parametrize(
    ("status", "rationale"),
    [
        ("unavailable", "map_conversation_presentation_unavailable"),
        ("failed", "map_conversation_presentation_failed"),
    ],
)
def test_non_presented_result_has_natural_response(status, rationale):
    presentation = MapPresentationResult(status, False, None, ("reason",))
    runtime = MapConversationInterceptionPort(
        Geocoder((target(),)), Renderer(), Presenter(presentation)
    )
    result = runtime.intercept(request("mapa de Rosario"), now=None)
    assert result.rationale == rationale
    assert "Generé el mapa" in result.response_text


def test_policy_defaults_to_system_browser():
    policy = MapConversationPolicy()
    assert policy.presentation_mode.value == "system_browser"
    assert policy.zoom == 16


def test_policy_validates_owner_and_zoom():
    with pytest.raises(ValueError):
        MapConversationPolicy(owner=" ")
    with pytest.raises(ValueError):
        MapConversationPolicy(zoom=0)


def test_policy_values_reach_display_request():
    geocoder = Geocoder((target(),))
    runtime = MapConversationInterceptionPort(
        geocoder,
        Renderer(),
        Presenter(),
        MapConversationPolicy(
            owner="Casa", zoom=12, presentation_mode="embedded_window"
        ),
    )
    runtime.intercept(request("mapa de Rosario"), now=None)
    built = geocoder.calls[0]
    assert built.owner == "Casa"
    assert built.zoom == 12
    assert built.presentation_mode.value == "embedded_window"
