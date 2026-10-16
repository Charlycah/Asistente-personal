from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

HttpFetcher = Callable[[str, float], Mapping[str, Any]]


@dataclass(frozen=True)
class CurrentWeather:
    """Condiciones climáticas actuales normalizadas para ROBY."""

    location: str
    temperature_celsius: float
    feels_like_celsius: float
    description: str
    humidity_percent: int
    wind_kph: float
    pressure_hpa: int = 0
    rain_probability_percent: int = 0
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.location.strip():
            raise ValueError("weather location must not be empty")
        if not self.description.strip():
            raise ValueError("weather description must not be empty")
        if not 0 <= self.humidity_percent <= 100:
            raise ValueError("weather humidity must be between 0 and 100")
        if not 0 <= self.rain_probability_percent <= 100:
            raise ValueError("weather rain probability must be between 0 and 100")
        if self.observed_at.tzinfo is None:
            raise ValueError("weather timestamp must be timezone-aware")

    def to_dict(self) -> dict[str, object]:
        return {
            "location": self.location,
            "temperature_celsius": self.temperature_celsius,
            "feels_like_celsius": self.feels_like_celsius,
            "description": self.description,
            "humidity_percent": self.humidity_percent,
            "wind_kph": self.wind_kph,
            "pressure_hpa": self.pressure_hpa,
            "rain_probability_percent": self.rain_probability_percent,
            "observed_at": self.observed_at.isoformat(),
        }


@dataclass(frozen=True)
class WeatherForecastDay:
    """Pronóstico diario normalizado para ROBY."""

    date: str
    min_celsius: float
    max_celsius: float
    description: str
    rain_probability_percent: int
    wind_kph: float = 0.0
    pressure_hpa: int = 0

    def __post_init__(self) -> None:
        if not self.date.strip():
            raise ValueError("forecast date must not be empty")
        if not self.description.strip():
            raise ValueError("forecast description must not be empty")
        if not 0 <= self.rain_probability_percent <= 100:
            raise ValueError("forecast rain probability must be between 0 and 100")

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date,
            "min_celsius": self.min_celsius,
            "max_celsius": self.max_celsius,
            "description": self.description,
            "rain_probability_percent": self.rain_probability_percent,
            "wind_kph": self.wind_kph,
            "pressure_hpa": self.pressure_hpa,
        }


@dataclass(frozen=True)
class WeatherForecast:
    """Pronóstico extendido normalizado para ROBY."""

    location: str
    days: tuple[WeatherForecastDay, ...]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.location.strip():
            raise ValueError("forecast location must not be empty")
        if not self.days:
            raise ValueError("forecast must include at least one day")
        if self.generated_at.tzinfo is None:
            raise ValueError("forecast timestamp must be timezone-aware")

    def to_dict(self) -> dict[str, object]:
        return {
            "location": self.location,
            "days": [day.to_dict() for day in self.days],
            "generated_at": self.generated_at.isoformat(),
        }


class WeatherProviderError(RuntimeError):
    """Error normalizado del proveedor meteorológico."""


class OpenWeatherMapClient:
    """Cliente OpenWeatherMap detrás del adapter, nunca usado por el core."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.openweathermap.org/data/2.5",
        fetcher: HttpFetcher | None = None,
        timeout_seconds: float = 8.0,
        language: str = "es",
    ) -> None:
        if not api_key.strip():
            raise ValueError("openweather api key must not be empty")
        if not base_url.strip():
            raise ValueError("openweather base url must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("openweather timeout must be positive")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.fetcher = fetcher or self._default_fetcher
        self.timeout_seconds = timeout_seconds
        self.language = language

    def get_current(self, location: str) -> CurrentWeather:
        payload = self._fetch(
            "weather",
            {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "lang": self.language,
            },
        )
        return self._parse_current(payload)

    def get_forecast(self, location: str, *, days: int = 5) -> WeatherForecast:
        if days <= 0:
            raise ValueError("forecast days must be positive")
        payload = self._fetch(
            "forecast",
            {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "lang": self.language,
            },
        )
        return self._parse_forecast(payload, limit_days=days)

    def _fetch(self, path: str, query: Mapping[str, object]) -> Mapping[str, Any]:
        url = f"{self.base_url}/{path}?{urlencode(query)}"
        try:
            return self.fetcher(url, self.timeout_seconds)
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise WeatherProviderError(str(exc)) from exc

    def _parse_current(self, payload: Mapping[str, Any]) -> CurrentWeather:
        try:
            main = payload["main"]
            weather = payload["weather"][0]
            wind = payload.get("wind", {})
            location = str(payload["name"])
            return CurrentWeather(
                location=location,
                temperature_celsius=float(main["temp"]),
                feels_like_celsius=float(main.get("feels_like", main["temp"])),
                description=str(weather["description"]),
                humidity_percent=int(main.get("humidity", 0)),
                wind_kph=round(float(wind.get("speed", 0.0)) * 3.6, 1),
                pressure_hpa=int(main.get("pressure", 0)),
            )
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise WeatherProviderError("invalid current weather payload") from exc

    def _parse_forecast(
        self,
        payload: Mapping[str, Any],
        *,
        limit_days: int,
    ) -> WeatherForecast:
        try:
            location = str(payload["city"]["name"])
            grouped: dict[str, list[Mapping[str, Any]]] = {}
            for item in payload["list"]:
                date = str(item["dt_txt"]).split(" ", maxsplit=1)[0]
                grouped.setdefault(date, []).append(item)

            days: list[WeatherForecastDay] = []
            for date, items in grouped.items():
                if len(days) >= limit_days:
                    break
                temps = [float(item["main"]["temp"]) for item in items]
                descriptions = [
                    str(item["weather"][0]["description"]) for item in items
                ]
                rain_probabilities = [
                    int(round(float(item.get("pop", 0.0)) * 100)) for item in items
                ]
                wind_speeds = [
                    float(item.get("wind", {}).get("speed", 0.0)) * 3.6
                    for item in items
                ]
                pressures = [
                    int(item.get("main", {}).get("pressure", 0)) for item in items
                ]
                days.append(
                    WeatherForecastDay(
                        date=date,
                        min_celsius=min(temps),
                        max_celsius=max(temps),
                        description=descriptions[0],
                        rain_probability_percent=max(rain_probabilities),
                        wind_kph=round(max(wind_speeds), 1),
                        pressure_hpa=round(sum(pressures) / len(pressures)),
                    )
                )
            return WeatherForecast(location=location, days=tuple(days))
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise WeatherProviderError("invalid forecast weather payload") from exc

    @staticmethod
    def _default_fetcher(url: str, timeout_seconds: float) -> Mapping[str, Any]:
        with urlopen(url, timeout=timeout_seconds) as response:  # nosec B310
            raw_data = response.read().decode("utf-8")
        loaded = json.loads(raw_data)
        if not isinstance(loaded, dict):
            raise WeatherProviderError("weather provider returned non-object JSON")
        return loaded
