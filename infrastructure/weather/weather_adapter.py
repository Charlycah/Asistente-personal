from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from core.tool_gateway import ToolGatewayManager, ToolRequest, ToolResult
from infrastructure.config.config_schema import AppConfig
from infrastructure.weather.weather_client import (
    CurrentWeather,
    OpenWeatherMapClient,
    WeatherForecast,
)


class WeatherProvider(Protocol):
    """Contrato mínimo que M65 exige a cualquier proveedor de clima."""

    def get_current(self, location: str) -> CurrentWeather:
        """Devuelve condiciones actuales normalizadas."""

    def get_forecast(self, location: str, *, days: int = 5) -> WeatherForecast:
        """Devuelve pronóstico extendido normalizado."""


@dataclass(frozen=True)
class WeatherAdapterPolicy:
    """Política de M65 para respuestas climáticas naturales y seguras."""

    default_location: str = "Buenos Aires"
    default_forecast_days: int = 5
    cold_threshold_celsius: float = 12.0
    hot_threshold_celsius: float = 30.0
    rain_threshold_percent: int = 45

    def __post_init__(self) -> None:
        if not self.default_location.strip():
            raise ValueError("weather default location must not be empty")
        if self.default_forecast_days <= 0:
            raise ValueError("weather forecast days must be positive")
        if not 0 <= self.rain_threshold_percent <= 100:
            raise ValueError("weather rain threshold must be between 0 and 100")


class WeatherAdapter:
    """Adapter M65: conecta la capacidad clima sin acoplarla al core."""

    CURRENT_CAPABILITY = "weather.current"
    FORECAST_CAPABILITY = "weather.forecast"

    def __init__(
        self,
        provider: WeatherProvider,
        policy: WeatherAdapterPolicy | None = None,
    ) -> None:
        self.provider = provider
        self.policy = policy or WeatherAdapterPolicy()

    def register_with_gateway(self, gateway: ToolGatewayManager) -> None:
        """Registra handlers de clima ya declarados por Capability Registry."""

        gateway.register_capability(
            gateway.capabilities[self.CURRENT_CAPABILITY],
            handler=self.current_conditions,
        )
        gateway.register_capability(
            gateway.capabilities[self.FORECAST_CAPABILITY],
            handler=self.forecast,
        )

    def current_conditions(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        location = self._location_from(payload)
        weather = self.provider.get_current(location)
        advice = self._advice_for_current(weather)
        return {
            "capability": self.CURRENT_CAPABILITY,
            "kind": "current_weather",
            "weather": weather.to_dict(),
            "advice": advice,
            "natural_summary": self._current_summary(weather, advice),
        }

    def forecast(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        location = self._location_from(payload)
        days = int(payload.get("days", self.policy.default_forecast_days))
        forecast = self.provider.get_forecast(location, days=days)
        return {
            "capability": self.FORECAST_CAPABILITY,
            "kind": "weather_forecast",
            "forecast": forecast.to_dict(),
            "natural_summary": self._forecast_summary(forecast),
        }

    def execute_current(
        self,
        gateway: ToolGatewayManager,
        *,
        location: str | None = None,
        reason: str = "weather_current_requested",
    ) -> ToolResult:
        return gateway.execute(
            ToolRequest(
                self.CURRENT_CAPABILITY,
                payload={"location": location or self.policy.default_location},
                reason=reason,
            )
        )

    def execute_forecast(
        self,
        gateway: ToolGatewayManager,
        *,
        location: str | None = None,
        days: int | None = None,
        reason: str = "weather_forecast_requested",
    ) -> ToolResult:
        return gateway.execute(
            ToolRequest(
                self.FORECAST_CAPABILITY,
                payload={
                    "location": location or self.policy.default_location,
                    "days": days or self.policy.default_forecast_days,
                },
                reason=reason,
            )
        )

    def _location_from(self, payload: Mapping[str, Any]) -> str:
        location = str(payload.get("location") or self.policy.default_location)
        if not location.strip():
            raise ValueError("weather request location must not be empty")
        return location

    def _advice_for_current(self, weather: CurrentWeather) -> tuple[str, ...]:
        advice: list[str] = []
        if weather.feels_like_celsius <= self.policy.cold_threshold_celsius:
            advice.append("conviene salir con abrigo")
        if weather.temperature_celsius >= self.policy.hot_threshold_celsius:
            advice.append("hidratate y evitá sol fuerte")
        if weather.rain_probability_percent >= self.policy.rain_threshold_percent:
            advice.append("llevá paraguas por las dudas")
        if not advice:
            advice.append("condiciones normales para salir")
        return tuple(advice)

    @staticmethod
    def _current_summary(
        weather: CurrentWeather,
        advice: tuple[str, ...],
    ) -> str:
        return (
            f"En {weather.location} hay {weather.temperature_celsius:.0f}°C "
            f"y se siente como {weather.feels_like_celsius:.0f}°C; "
            f"{weather.description}. {advice[0].capitalize()}."
        )

    @staticmethod
    def _forecast_summary(forecast: WeatherForecast) -> str:
        first_day = forecast.days[0]
        return (
            f"El extendido para {forecast.location} arranca con "
            f"{first_day.min_celsius:.0f}°C a {first_day.max_celsius:.0f}°C "
            f"y {first_day.description}."
        )


def build_weather_adapter_from_config(config: AppConfig) -> WeatherAdapter:
    """Factory segura: lee credenciales centralizadas y arma el adapter real."""

    api_key = config.secrets.openweather_api_key
    if api_key is None or not api_key.strip():
        raise ValueError("OPENWEATHER_API_KEY is required for WeatherAdapter")
    provider = OpenWeatherMapClient(api_key)
    policy = WeatherAdapterPolicy(default_location=config.weather.default_city)
    return WeatherAdapter(provider, policy)
