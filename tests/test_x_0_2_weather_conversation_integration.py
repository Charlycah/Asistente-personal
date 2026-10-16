from datetime import datetime, timezone

from app.weather_conversation_runtime import WeatherConversationInterceptionPort
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from infrastructure.weather.weather_adapter import WeatherAdapter
from infrastructure.weather.weather_client import (
    CurrentWeather,
    WeatherForecast,
    WeatherForecastDay,
)


class Provider:
    def get_current(self, location):
        return CurrentWeather(
            location=location,
            temperature_celsius=13,
            feels_like_celsius=11,
            description="parcialmente nublado",
            humidity_percent=74,
            wind_kph=18,
        )

    def get_forecast(self, location, *, days=5):
        return WeatherForecast(
            location=location,
            days=(
                WeatherForecastDay(
                    date="2026-07-16",
                    min_celsius=10,
                    max_celsius=17,
                    description="parcialmente nublado",
                    rain_probability_percent=20,
                ),
            ),
        )


def request(text):
    return GovernedConversationPipelineRequest(
        owner="Familia",
        session_id="household-main",
        text=text,
    )


def runtime():
    return WeatherConversationInterceptionPort(WeatherAdapter(Provider()))


def test_current_weather_uses_default_household_location():
    result = runtime().intercept(
        request("cómo está el clima"), now=datetime.now(timezone.utc)
    )
    assert (
        "Ahora en Buenos Aires está parcialmente nublado, con 13 °C"
        in result.response_text
    )
    assert "13 °C" in result.response_text
    assert result.rationale == "weather_current_conversation_completed"


def test_weather_location_is_extracted_from_natural_request():
    result = runtime().intercept(
        request("cómo está el clima en Córdoba?"),
        now=datetime.now(timezone.utc),
    )
    assert (
        "Ahora en Córdoba está parcialmente nublado, con 13 °C" in result.response_text
    )


def test_equal_temperature_and_sensation_are_still_reported():
    class EqualProvider(Provider):
        def get_current(self, location):
            weather = super().get_current(location)
            return CurrentWeather(
                location=weather.location,
                temperature_celsius=14,
                feels_like_celsius=14,
                description="nubes",
                humidity_percent=93,
                wind_kph=3.2,
            )

    runtime_port = WeatherConversationInterceptionPort(WeatherAdapter(EqualProvider()))
    result = runtime_port.intercept(
        request("cómo está el clima en Buenos Aires?"),
        now=datetime.now(timezone.utc),
    )
    assert result.response_text.count("14 °C") == 2
    assert "sensación térmica de 14 °C" in result.response_text
    assert "el viento va a 3.2 km/h." in result.response_text


def test_extended_forecast_is_executed_before_llm_fallback():
    result = runtime().intercept(
        request("dame el pronóstico extendido para Buenos Aires"),
        now=datetime.now(timezone.utc),
    )
    assert "Pronóstico extendido para Buenos Aires" in result.response_text
    assert "Jueves" in result.response_text
    assert result.rationale == "weather_forecast_conversation_completed"


def test_non_weather_turn_is_not_intercepted():
    assert (
        runtime().intercept(request("hola ROBY"), now=datetime.now(timezone.utc))
        is None
    )


def test_current_weather_includes_pressure_when_provider_reports_it():
    class PressureProvider(Provider):
        def get_current(self, location):
            return CurrentWeather(
                location=location,
                temperature_celsius=18,
                feels_like_celsius=18,
                description="nublado",
                humidity_percent=75,
                wind_kph=10,
                pressure_hpa=1017,
            )

    runtime_port = WeatherConversationInterceptionPort(
        WeatherAdapter(PressureProvider())
    )
    result = runtime_port.intercept(
        request("decime el clima"), now=datetime.now(timezone.utc)
    )

    assert "el viento va a 10.0 km/h," in result.response_text
    assert "con una presión de 1017 hPa." in result.response_text
