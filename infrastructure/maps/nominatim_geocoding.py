from __future__ import annotations

import json
import socket
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from core.map_display import MapDisplayRequest, MapDisplayTarget
from core.maps_foundation import GeoPointSignal

NominatimPayload = Sequence[Mapping[str, Any]]
NominatimFetcher = Callable[[str, float, Mapping[str, str]], NominatimPayload]
Clock = Callable[[], float]
Sleeper = Callable[[float], None]


class NominatimGeocodingError(RuntimeError):
    """Base error exposed by the Nominatim geocoding boundary."""


class NominatimTimeoutError(NominatimGeocodingError):
    """The provider did not answer within the configured timeout."""


class NominatimRateLimitError(NominatimGeocodingError):
    """The provider rejected the request because of rate limiting."""


class NominatimTransportError(NominatimGeocodingError):
    """The provider could not be reached or returned an HTTP failure."""


class NominatimResponseError(NominatimGeocodingError):
    """The provider returned a malformed or unsupported payload."""


@dataclass(frozen=True)
class NominatimGeocodingConfig:
    user_agent: str
    base_url: str = "https://nominatim.openstreetmap.org/search"
    timeout_seconds: float = 8.0
    result_limit: int = 5
    language: str = "es"
    country_codes: tuple[str, ...] = ()
    cache_ttl_seconds: float = 900.0
    minimum_interval_seconds: float = 1.0

    def __post_init__(self) -> None:
        normalized_agent = " ".join(self.user_agent.strip().split())
        normalized_url = self.base_url.strip().rstrip("?")
        normalized_language = self.language.strip().casefold()
        normalized_countries = tuple(
            country.strip().casefold()
            for country in self.country_codes
            if country.strip()
        )
        if not normalized_agent:
            raise ValueError("nominatim user agent must not be blank")
        if not normalized_url.startswith(("https://", "http://")):
            raise ValueError("nominatim base url must use http or https")
        if self.timeout_seconds <= 0:
            raise ValueError("nominatim timeout must be positive")
        if not 1 <= self.result_limit <= 50:
            raise ValueError("nominatim result limit must be between 1 and 50")
        if not normalized_language:
            raise ValueError("nominatim language must not be blank")
        if self.cache_ttl_seconds < 0:
            raise ValueError("nominatim cache ttl must not be negative")
        if self.minimum_interval_seconds < 0:
            raise ValueError("nominatim minimum interval must not be negative")
        invalid_country = any(
            len(country) != 2 or not country.isalpha()
            for country in normalized_countries
        )
        if invalid_country:
            raise ValueError("nominatim country codes must use two letters")
        object.__setattr__(self, "user_agent", normalized_agent)
        object.__setattr__(self, "base_url", normalized_url)
        object.__setattr__(self, "language", normalized_language)
        object.__setattr__(self, "country_codes", normalized_countries)


@dataclass(frozen=True)
class _CacheEntry:
    stored_at: float
    targets: tuple[MapDisplayTarget, ...]


class NominatimGeocodingAdapter:
    """Map geocoding adapter backed by Nominatim with cache and rate control."""

    def __init__(
        self,
        config: NominatimGeocodingConfig,
        *,
        fetcher: NominatimFetcher | None = None,
        clock: Clock = time.monotonic,
        sleeper: Sleeper = time.sleep,
    ) -> None:
        self.config = config
        self._fetcher = fetcher or self._default_fetcher
        self._clock = clock
        self._sleeper = sleeper
        self._cache: dict[str, _CacheEntry] = {}
        self._last_request_at: float | None = None

    def resolve(self, request: MapDisplayRequest) -> tuple[MapDisplayTarget, ...]:
        cache_key = request.query.casefold()
        now = self._clock()
        cached = self._cache.get(cache_key)
        cache_age = None if cached is None else now - cached.stored_at
        if cached is not None and cache_age <= self.config.cache_ttl_seconds:
            return cached.targets
        if cached is not None:
            self._cache.pop(cache_key, None)

        self._respect_rate_limit(now)
        url = self._build_url(request.query)
        headers = {
            "Accept": "application/json",
            "Accept-Language": self.config.language,
            "User-Agent": self.config.user_agent,
        }
        try:
            payload = self._fetcher(url, self.config.timeout_seconds, headers)
        except NominatimGeocodingError:
            raise
        except TimeoutError as exc:
            raise NominatimTimeoutError("nominatim request timed out") from exc
        except (socket.timeout,) as exc:
            raise NominatimTimeoutError("nominatim request timed out") from exc
        except Exception as exc:  # pragma: no cover - defensive adapter boundary
            message = str(exc) or "nominatim transport failed"
            raise NominatimTransportError(message) from exc
        finally:
            self._last_request_at = self._clock()

        targets = self._parse_payload(payload)
        self._cache[cache_key] = _CacheEntry(
            stored_at=self._clock(),
            targets=targets,
        )
        return targets

    def clear_cache(self) -> None:
        self._cache.clear()

    def _respect_rate_limit(self, now: float) -> None:
        if self._last_request_at is None:
            return
        remaining = self.config.minimum_interval_seconds - (now - self._last_request_at)
        if remaining > 0:
            self._sleeper(remaining)

    def _build_url(self, query: str) -> str:
        parameters: dict[str, str | int] = {
            "q": query,
            "format": "jsonv2",
            "limit": self.config.result_limit,
            "addressdetails": 1,
        }
        if self.config.country_codes:
            parameters["countrycodes"] = ",".join(self.config.country_codes)
        return f"{self.config.base_url}?{urlencode(parameters)}"

    def _parse_payload(self, payload: NominatimPayload) -> tuple[MapDisplayTarget, ...]:
        scalar_payload = isinstance(payload, (str, bytes, bytearray))
        invalid_sequence = scalar_payload or not isinstance(payload, Sequence)
        if invalid_sequence:
            raise NominatimResponseError("nominatim response must be a sequence")
        targets: list[MapDisplayTarget] = []
        for item in payload:
            if not isinstance(item, Mapping):
                raise NominatimResponseError("nominatim result must be an object")
            targets.append(self._parse_item(item))
        return tuple(targets)

    @staticmethod
    def _parse_item(item: Mapping[str, Any]) -> MapDisplayTarget:
        try:
            label = str(item["display_name"])
            latitude = float(item["lat"])
            longitude = float(item["lon"])
        except (KeyError, TypeError, ValueError) as exc:
            message = "nominatim result is missing valid coordinates"
            raise NominatimResponseError(message) from exc

        importance_value = item.get("importance", 0.5)
        try:
            confidence = min(1.0, max(0.0, float(importance_value)))
        except (TypeError, ValueError) as exc:
            message = "nominatim importance must be numeric"
            raise NominatimResponseError(message) from exc

        external_id_value = item.get("place_id")
        external_id = None if external_id_value is None else str(external_id_value)
        try:
            point = GeoPointSignal(
                latitude=latitude,
                longitude=longitude,
                confidence=confidence,
                observed_at=datetime.now(timezone.utc),
                source="nominatim",
            )
            return MapDisplayTarget(
                label=label,
                point=point,
                confidence=confidence,
                source="nominatim",
                external_id=external_id,
            )
        except ValueError as exc:
            raise NominatimResponseError(str(exc)) from exc

    @staticmethod
    def _default_fetcher(
        url: str,
        timeout_seconds: float,
        headers: Mapping[str, str],
    ) -> NominatimPayload:
        request = Request(url, headers=dict(headers), method="GET")
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code == 429:
                raise NominatimRateLimitError("nominatim rate limit exceeded") from exc
            raise NominatimTransportError(
                f"nominatim http failure: {exc.code}"
            ) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise NominatimTimeoutError("nominatim request timed out") from exc
        except URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise NominatimTimeoutError("nominatim request timed out") from exc
            raise NominatimTransportError("nominatim network failure") from exc
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise NominatimResponseError("nominatim returned invalid json") from exc
        if not isinstance(payload, list):
            raise NominatimResponseError("nominatim json root must be a list")
        return payload
