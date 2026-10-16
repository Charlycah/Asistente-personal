from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import pytest

from core.capability_registry import (
    CapabilityRegistryManager,
    default_semantic_capabilities,
)
from core.permission_consent import PermissionConsentManager
from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus, ToolRequest
from infrastructure.config.config_schema import (
    AppConfig,
    AssistantConfig,
    LLMConfig,
    MemoryConfig,
    RemindersConfig,
    SecretsConfig,
    VoiceConfig,
    WeatherConfig,
)
from infrastructure.weather.weather_adapter import (
    WeatherAdapter,
    WeatherAdapterPolicy,
    build_weather_adapter_from_config,
)
from infrastructure.weather.weather_client import (
    CurrentWeather,
    OpenWeatherMapClient,
    WeatherForecast,
    WeatherForecastDay,
    WeatherProviderError,
)


class FakeWeatherProvider:
    def get_current(self, location: str) -> CurrentWeather:
        return CurrentWeather(
            location=location,
            temperature_celsius=9.0,
            feels_like_celsius=7.5,
            description="cielo claro",
            humidity_percent=71,
            wind_kph=11.0,
            rain_probability_percent=10,
            observed_at=datetime(2026, 7, 9, tzinfo=timezone.utc),
        )

    def get_forecast(self, location: str, *, days: int = 5) -> WeatherForecast:
        forecast_days = tuple(
            WeatherForecastDay(
                date=f"2026-07-{10 + index:02d}",
                min_celsius=8.0 + index,
                max_celsius=15.0 + index,
                description="parcialmente nublado",
                rain_probability_percent=20 + index,
            )
            for index in range(days)
        )
        return WeatherForecast(location=location, days=forecast_days)


def build_gateway() -> ToolGatewayManager:
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    permissions = PermissionConsentManager()
    return ToolGatewayManager(
        capability_registry=registry,
        permission_consent=permissions,
    )


def test_weather_adapter_registers_current_and_forecast_handlers():
    gateway = build_gateway()
    adapter = WeatherAdapter(FakeWeatherProvider())

    adapter.register_with_gateway(gateway)

    result = gateway.execute(
        ToolRequest("weather.current", payload={"location": "Buenos Aires"})
    )

    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert result.output["kind"] == "current_weather"
    assert "Buenos Aires" in result.output["natural_summary"]


def test_current_weather_adapter_adds_clothing_advice_for_cold_weather():
    adapter = WeatherAdapter(FakeWeatherProvider())

    output = adapter.current_conditions({"location": "Buenos Aires"})

    assert "conviene salir con abrigo" in output["advice"]
    assert output["weather"]["feels_like_celsius"] == 7.5


def test_forecast_adapter_returns_requested_number_of_days():
    adapter = WeatherAdapter(FakeWeatherProvider())

    output = adapter.forecast({"location": "Buenos Aires", "days": 3})

    assert output["kind"] == "weather_forecast"
    assert len(output["forecast"]["days"]) == 3
    assert "extendido" in output["natural_summary"]


def test_weather_adapter_uses_default_location_for_natural_short_queries():
    gateway = build_gateway()
    adapter = WeatherAdapter(
        FakeWeatherProvider(),
        WeatherAdapterPolicy(default_location="Buenos Aires"),
    )
    adapter.register_with_gateway(gateway)

    result = adapter.execute_current(gateway)

    assert result.succeeded is True
    assert result.output["weather"]["location"] == "Buenos Aires"


def test_semantic_registry_discovers_weather_before_gateway_execution():
    gateway = build_gateway()
    adapter = WeatherAdapter(FakeWeatherProvider())
    adapter.register_with_gateway(gateway)

    snapshot = gateway.observe_turn("ROBY, qué frío hace, necesito abrigo?")

    assert "weather.current" in snapshot.requested_capabilities


def test_weather_adapter_respects_permissions_layer_for_network_capability():
    gateway = build_gateway()
    adapter = WeatherAdapter(FakeWeatherProvider())
    adapter.register_with_gateway(gateway)

    result = gateway.execute(
        ToolRequest("weather.forecast", payload={"location": "Buenos Aires"})
    )

    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert gateway.permission_consent is not None
    assert gateway.permission_consent.last_decision is not None
    assert gateway.permission_consent.last_decision.allowed is True


def test_openweather_client_builds_current_request_and_parses_response():
    captured_urls: list[str] = []

    def fake_fetcher(url: str, timeout_seconds: float):
        captured_urls.append(url)
        assert timeout_seconds == 8.0
        return {
            "name": "Buenos Aires",
            "main": {"temp": 11.2, "feels_like": 9.8, "humidity": 80},
            "weather": [{"description": "nublado"}],
            "wind": {"speed": 4.0},
        }

    client = OpenWeatherMapClient("test-key", fetcher=fake_fetcher)

    weather = client.get_current("Buenos Aires")

    parsed = urlparse(captured_urls[0])
    query = parse_qs(parsed.query)
    assert query["q"] == ["Buenos Aires"]
    assert query["appid"] == ["test-key"]
    assert weather.wind_kph == 14.4


def test_openweather_client_parses_grouped_forecast_response():
    def fake_fetcher(url: str, timeout_seconds: float):
        return {
            "city": {"name": "Buenos Aires"},
            "list": [
                {
                    "dt_txt": "2026-07-10 09:00:00",
                    "main": {"temp": 10.0},
                    "weather": [{"description": "fresco"}],
                    "pop": 0.2,
                },
                {
                    "dt_txt": "2026-07-10 15:00:00",
                    "main": {"temp": 17.0},
                    "weather": [{"description": "soleado"}],
                    "pop": 0.1,
                },
                {
                    "dt_txt": "2026-07-11 09:00:00",
                    "main": {"temp": 12.0},
                    "weather": [{"description": "lluvia"}],
                    "pop": 0.8,
                },
            ],
        }

    client = OpenWeatherMapClient("test-key", fetcher=fake_fetcher)

    forecast = client.get_forecast("Buenos Aires", days=2)

    assert len(forecast.days) == 2
    assert forecast.days[0].min_celsius == 10.0
    assert forecast.days[0].max_celsius == 17.0
    assert forecast.days[1].rain_probability_percent == 80


def test_openweather_client_rejects_invalid_payloads():
    client = OpenWeatherMapClient("test-key", fetcher=lambda url, timeout: {})

    with pytest.raises(WeatherProviderError):
        client.get_current("Buenos Aires")


def test_build_weather_adapter_from_config_requires_openweather_secret():
    config = AppConfig(
        assistant=AssistantConfig("ROBY", "es", "America/Argentina/Buenos_Aires"),
        weather=WeatherConfig("Buenos Aires", "openweather", "openweather"),
        memory=MemoryConfig(True, "roby.db"),
        reminders=RemindersConfig(True, 60),
        llm=LLMConfig("none", "none"),
        voice=VoiceConfig(False, "none", "none"),
        secrets=SecretsConfig(
            openweather_api_key=None,
            weatherapi_key=None,
            google_client_secret_file=None,
            google_token_file=None,
            gmail_address=None,
            gmail_app_password=None,
            gemini_api_key=None,
            openrouter_api_key=None,
            mistral_api_key=None,
            openai_api_key=None,
            camera_index=0,
        ),
        debug=False,
    )

    with pytest.raises(ValueError, match="OPENWEATHER_API_KEY"):
        build_weather_adapter_from_config(config)
