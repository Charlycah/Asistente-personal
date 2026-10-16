from datetime import datetime, timedelta, timezone

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
    def __init__(self, targets=()):
        self.targets = targets
        self.calls = []

    def resolve(self, request):
        self.calls.append(request)
        return self.targets


class Renderer:
    def __init__(self):
        self.calls = []

    def render(self, request, target):
        self.calls.append((request, target))
        return MapDocument(
            "file:///tmp/map.html",
            "text/html",
            f"Mapa de {target.label}",
        )


class Presenter:
    def __init__(self):
        self.calls = []

    def present(self, document, *, mode):
        self.calls.append((document, mode))
        return MapPresentationResult(
            "presented",
            True,
            "system_browser",
            ("ok",),
        )


def target(label):
    return MapDisplayTarget(
        label=label,
        point=GeoPointSignal(
            -34.6,
            -58.4,
            0.9,
            datetime.now(timezone.utc),
            "test",
        ),
        confidence=0.9,
        source="test",
    )


def request(text, session_id="session-a"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


def runtime(policy=None):
    geocoder = Geocoder(
        (
            target("San Martín, Buenos Aires"),
            target("San Martín, Mendoza"),
            target("San Martín, Córdoba"),
            target("San Martín, Santa Fe"),
        )
    )
    renderer = Renderer()
    presenter = Presenter()
    service = MapConversationInterceptionPort(
        geocoder,
        renderer,
        presenter,
        policy,
    )
    return service, geocoder, renderer, presenter


def start_ambiguity(service, now=None, session_id="session-a"):
    return service.intercept(
        request("mapa de San Martín", session_id),
        now=now,
    )


def test_ambiguous_reply_numbers_at_most_three_choices():
    service, _, _, _ = runtime()
    result = start_ambiguity(service)
    assert "1. San Martín, Buenos Aires" in result.response_text
    assert "2. San Martín, Mendoza" in result.response_text
    assert "3. San Martín, Córdoba" in result.response_text
    assert "Santa Fe" not in result.response_text


@pytest.mark.parametrize(
    ("selection", "expected"),
    [
        ("1", "San Martín, Buenos Aires"),
        ("la primera", "San Martín, Buenos Aires"),
        ("opción 2", "San Martín, Mendoza"),
        ("la segunda", "San Martín, Mendoza"),
        ("número tres", "San Martín, Córdoba"),
        ("tercera", "San Martín, Córdoba"),
    ],
)
def test_numeric_and_ordinal_follow_up_opens_selected_target(selection, expected):
    service, geocoder, renderer, presenter = runtime()
    start_ambiguity(service)
    result = service.intercept(request(selection), now=None)
    assert result.rationale == "map_conversation_completed"
    assert expected in result.response_text
    assert len(geocoder.calls) == 1
    assert renderer.calls[-1][1].label == expected
    assert len(presenter.calls) == 1


@pytest.mark.parametrize(
    ("selection", "expected"),
    [
        ("la de Mendoza", "San Martín, Mendoza"),
        ("Córdoba", "San Martín, Córdoba"),
        ("Buenos Aires", "San Martín, Buenos Aires"),
    ],
)
def test_name_follow_up_opens_unique_matching_target(selection, expected):
    service, _, renderer, _ = runtime()
    start_ambiguity(service)
    result = service.intercept(request(selection), now=None)
    assert result.rationale == "map_conversation_completed"
    assert renderer.calls[-1][1].label == expected


@pytest.mark.parametrize("selection", ["cancelar", "ninguna", "dejalo"])
def test_cancel_follow_up_discards_pending_selection(selection):
    service, _, renderer, _ = runtime()
    start_ambiguity(service)
    result = service.intercept(request(selection), now=None)
    assert result.rationale == "map_conversation_clarification_cancelled"
    assert renderer.calls == []
    assert service.intercept(request("2"), now=None) is None


def test_invalid_selection_receives_bounded_clarification():
    service, _, renderer, _ = runtime()
    start_ambiguity(service)
    result = service.intercept(request("opción 9"), now=None)
    assert result.rationale == "map_conversation_clarification_invalid"
    assert "1, 2, 3" in result.response_text
    assert renderer.calls == []


def test_unrelated_turn_is_not_captured_while_clarification_is_pending():
    service, _, _, _ = runtime()
    start_ambiguity(service)
    assert service.intercept(request("cómo está el clima"), now=None) is None


def test_unrelated_turn_does_not_destroy_pending_selection():
    service, _, renderer, _ = runtime()
    start_ambiguity(service)
    service.intercept(request("gracias"), now=None)
    result = service.intercept(request("2"), now=None)
    assert result.rationale == "map_conversation_completed"
    assert renderer.calls[-1][1].label == "San Martín, Mendoza"


def test_pending_selection_is_isolated_by_session():
    service, _, renderer, _ = runtime()
    start_ambiguity(service, session_id="session-a")
    assert service.intercept(request("2", "session-b"), now=None) is None
    result = service.intercept(request("2", "session-a"), now=None)
    assert result.rationale == "map_conversation_completed"
    assert renderer.calls[-1][1].label == "San Martín, Mendoza"


def test_pending_selection_expires_after_policy_ttl():
    policy = MapConversationPolicy(clarification_ttl_seconds=10)
    service, _, _, _ = runtime(policy)
    started = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
    start_ambiguity(service, now=started)
    result = service.intercept(
        request("2"),
        now=started + timedelta(seconds=10),
    )
    assert result is None


def test_selection_before_expiry_is_accepted():
    policy = MapConversationPolicy(clarification_ttl_seconds=10)
    service, _, renderer, _ = runtime(policy)
    started = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
    start_ambiguity(service, now=started)
    result = service.intercept(
        request("2"),
        now=started + timedelta(seconds=9),
    )
    assert result.rationale == "map_conversation_completed"
    assert renderer.calls[-1][1].label == "San Martín, Mendoza"


def test_new_explicit_map_request_replaces_pending_selection():
    first = (
        target("San Martín, Buenos Aires"),
        target("San Martín, Mendoza"),
    )
    second = (target("Rosario, Santa Fe"),)
    geocoder = Geocoder(first)
    renderer = Renderer()
    presenter = Presenter()
    service = MapConversationInterceptionPort(geocoder, renderer, presenter)
    start_ambiguity(service)
    geocoder.targets = second
    result = service.intercept(request("mapa de Rosario"), now=None)
    assert result.rationale == "map_conversation_completed"
    assert service.intercept(request("2"), now=None) is None


def test_completed_follow_up_is_consumed_only_once():
    service, _, renderer, _ = runtime()
    start_ambiguity(service)
    service.intercept(request("2"), now=None)
    assert service.intercept(request("2"), now=None) is None
    assert len(renderer.calls) == 1


def test_pending_capacity_evicts_oldest_expiring_session():
    policy = MapConversationPolicy(
        clarification_ttl_seconds=60,
        maximum_pending_sessions=2,
    )
    service, _, renderer, _ = runtime(policy)
    base = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
    start_ambiguity(service, base, "session-a")
    start_ambiguity(service, base + timedelta(seconds=1), "session-b")
    start_ambiguity(service, base + timedelta(seconds=2), "session-c")
    assert service.intercept(request("1", "session-a"), now=base) is None
    result = service.intercept(request("1", "session-b"), now=base)
    assert result.rationale == "map_conversation_completed"
    assert renderer.calls[-1][1].label == "San Martín, Buenos Aires"


def test_policy_validates_follow_up_limits():
    with pytest.raises(ValueError):
        MapConversationPolicy(clarification_ttl_seconds=0)
    with pytest.raises(ValueError):
        MapConversationPolicy(maximum_pending_sessions=0)


def test_naive_timestamp_is_rejected():
    service, _, _, _ = runtime()
    with pytest.raises(ValueError):
        start_ambiguity(service, datetime(2026, 7, 26, 12, 0))
