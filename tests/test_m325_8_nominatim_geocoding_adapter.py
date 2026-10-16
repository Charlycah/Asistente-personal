from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest

from core.map_display import MapDisplayRequest, MapGeocodingProvider
from infrastructure.maps import (
    NominatimGeocodingAdapter,
    NominatimGeocodingConfig,
    NominatimResponseError,
    NominatimTimeoutError,
    NominatimTransportError,
)


def request(query: str = "Plaza de Mayo") -> MapDisplayRequest:
    return MapDisplayRequest(owner="Carlos", query=query)


def payload() -> list[dict[str, object]]:
    return [
        {
            "place_id": 123,
            "lat": "-34.6083696",
            "lon": "-58.3724715",
            "display_name": "Plaza de Mayo, Monserrat, Buenos Aires, Argentina",
            "importance": 0.82,
        }
    ]


def test_config_normalizes_values() -> None:
    config = NominatimGeocodingConfig(
        user_agent="  ROBY XI.2 maps  ",
        base_url="https://example.test/search?",
        language=" ES ",
        country_codes=(" AR ", "uy"),
    )
    assert config.user_agent == "ROBY XI.2 maps"
    assert config.base_url == "https://example.test/search"
    assert config.language == "es"
    assert config.country_codes == ("ar", "uy")


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"user_agent": " "}, "user agent"),
        ({"user_agent": "roby", "base_url": "ftp://example.test"}, "base url"),
        ({"user_agent": "roby", "timeout_seconds": 0}, "timeout"),
        ({"user_agent": "roby", "result_limit": 0}, "result limit"),
        ({"user_agent": "roby", "result_limit": 51}, "result limit"),
        ({"user_agent": "roby", "language": " "}, "language"),
        ({"user_agent": "roby", "cache_ttl_seconds": -1}, "cache ttl"),
        ({"user_agent": "roby", "minimum_interval_seconds": -1}, "minimum interval"),
        ({"user_agent": "roby", "country_codes": ("arg",)}, "country codes"),
    ],
)
def test_config_rejects_invalid_values(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        NominatimGeocodingConfig(**kwargs)


def test_adapter_implements_map_geocoding_protocol() -> None:
    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"), fetcher=lambda *_: []
    )
    assert isinstance(adapter, MapGeocodingProvider)


def test_resolve_builds_request_and_translates_result() -> None:
    calls: list[tuple[str, float, dict[str, str]]] = []

    def fetcher(url: str, timeout: float, headers: dict[str, str]):
        calls.append((url, timeout, headers))
        return payload()

    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(
            user_agent="ROBY XI.2 maps",
            timeout_seconds=4.5,
            result_limit=3,
            country_codes=("ar",),
        ),
        fetcher=fetcher,
    )
    targets = adapter.resolve(request())

    assert len(targets) == 1
    target = targets[0]
    assert target.label.startswith("Plaza de Mayo")
    assert target.point.latitude == pytest.approx(-34.6083696)
    assert target.point.longitude == pytest.approx(-58.3724715)
    assert target.confidence == pytest.approx(0.82)
    assert target.source == "nominatim"
    assert target.external_id == "123"
    assert target.point.source == "nominatim"
    url, timeout, headers = calls[0]
    query = parse_qs(urlparse(url).query)
    assert query["q"] == ["Plaza de Mayo"]
    assert query["format"] == ["jsonv2"]
    assert query["limit"] == ["3"]
    assert query["addressdetails"] == ["1"]
    assert query["countrycodes"] == ["ar"]
    assert timeout == 4.5
    assert headers["User-Agent"] == "ROBY XI.2 maps"
    assert headers["Accept-Language"] == "es"


def test_empty_provider_result_is_not_an_error() -> None:
    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"), fetcher=lambda *_: []
    )
    assert adapter.resolve(request()) == ()


def test_multiple_results_preserve_provider_order() -> None:
    results = payload() + [
        {
            "place_id": 456,
            "lat": "-31.4",
            "lon": "-64.2",
            "display_name": "Plaza de Mayo, Córdoba",
            "importance": 0.4,
        }
    ]
    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"), fetcher=lambda *_: results
    )
    targets = adapter.resolve(request())
    assert [target.external_id for target in targets] == ["123", "456"]


def test_confidence_is_clamped_to_contract_range() -> None:
    results = payload()
    results[0]["importance"] = 7
    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"), fetcher=lambda *_: results
    )
    assert adapter.resolve(request())[0].confidence == 1.0


def test_missing_importance_uses_neutral_confidence() -> None:
    results = payload()
    del results[0]["importance"]
    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"), fetcher=lambda *_: results
    )
    assert adapter.resolve(request())[0].confidence == 0.5


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"not": "a list"},
        ["not an object"],
        [{"display_name": "Missing coordinates"}],
        [{"display_name": "Bad latitude", "lat": "x", "lon": "1"}],
        [{"display_name": "Bad importance", "lat": "1", "lon": "1", "importance": "x"}],
        [{"display_name": "Out of range", "lat": "100", "lon": "1"}],
    ],
)
def test_malformed_payload_raises_normalized_response_error(
    bad_payload: object,
) -> None:
    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"), fetcher=lambda *_: bad_payload
    )
    with pytest.raises(NominatimResponseError):
        adapter.resolve(request())


def test_timeout_is_translated() -> None:
    def fetcher(*_args):
        raise TimeoutError("slow")

    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"), fetcher=fetcher
    )
    with pytest.raises(NominatimTimeoutError, match="timed out"):
        adapter.resolve(request())


def test_unexpected_transport_failure_is_translated() -> None:
    def fetcher(*_args):
        raise OSError("offline")

    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"), fetcher=fetcher
    )
    with pytest.raises(NominatimTransportError, match="offline"):
        adapter.resolve(request())


def test_cache_avoids_repeated_provider_calls() -> None:
    calls = 0

    def fetcher(*_args):
        nonlocal calls
        calls += 1
        return payload()

    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"),
        fetcher=fetcher,
        clock=lambda: 10.0,
    )
    first = adapter.resolve(request("  Plaza   de Mayo "))
    second = adapter.resolve(request("plaza de mayo"))
    assert first == second
    assert calls == 1


def test_expired_cache_calls_provider_again() -> None:
    now = [0.0]
    calls = 0

    def fetcher(*_args):
        nonlocal calls
        calls += 1
        return payload()

    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(
            user_agent="roby", cache_ttl_seconds=5, minimum_interval_seconds=0
        ),
        fetcher=fetcher,
        clock=lambda: now[0],
    )
    adapter.resolve(request())
    now[0] = 6.0
    adapter.resolve(request())
    assert calls == 2


def test_clear_cache_forces_new_lookup() -> None:
    calls = 0

    def fetcher(*_args):
        nonlocal calls
        calls += 1
        return payload()

    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby", minimum_interval_seconds=0),
        fetcher=fetcher,
    )
    adapter.resolve(request())
    adapter.clear_cache()
    adapter.resolve(request())
    assert calls == 2


def test_rate_limit_waits_before_distinct_provider_request() -> None:
    now = [0.0]
    waits: list[float] = []

    def clock() -> float:
        return now[0]

    def sleeper(seconds: float) -> None:
        waits.append(seconds)
        now[0] += seconds

    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(
            user_agent="roby", minimum_interval_seconds=1.0
        ),
        fetcher=lambda *_: payload(),
        clock=clock,
        sleeper=sleeper,
    )
    adapter.resolve(request("Buenos Aires"))
    now[0] = 0.25
    adapter.resolve(request("Córdoba"))
    assert waits == [pytest.approx(0.75)]


def test_rate_limit_does_not_wait_for_cached_lookup() -> None:
    waits: list[float] = []
    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"),
        fetcher=lambda *_: payload(),
        clock=lambda: 0.0,
        sleeper=waits.append,
    )
    adapter.resolve(request())
    adapter.resolve(request())
    assert waits == []


def test_provider_error_is_preserved_without_wrapping() -> None:
    error = NominatimResponseError("bad payload")

    def fetcher(*_args):
        raise error

    adapter = NominatimGeocodingAdapter(
        NominatimGeocodingConfig(user_agent="roby"), fetcher=fetcher
    )
    with pytest.raises(NominatimResponseError) as captured:
        adapter.resolve(request())
    assert captured.value is error
