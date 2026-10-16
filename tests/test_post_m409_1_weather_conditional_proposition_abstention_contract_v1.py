from datetime import datetime, timezone

import pytest

from app.weather_conversation_runtime import (
    WeatherConversationInterceptionPort,
    WeatherUnavailableConversationInterceptionPort,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from infrastructure.weather.weather_adapter import WeatherAdapter
from infrastructure.weather.weather_client import CurrentWeather, WeatherForecast


class Provider:
    def get_current(self, location):
        return CurrentWeather(
            location=location,
            temperature_celsius=12,
            feels_like_celsius=11,
            description="nubes",
            humidity_percent=88,
            wind_kph=3.2,
        )

    def get_forecast(self, location, *, days=5):
        return WeatherForecast(location=location, days=())


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Familia",
        session_id="guide-v2-k",
        text=text,
    )


@pytest.mark.parametrize(
    "text",
    (
        "Si mañana llueve, Marta irá en taxi.",
        "Cuando llueve, cierro las ventanas.",
        "Si mañana hay viento, iremos en auto.",
        "Si hace frío, Pedro llevará abrigo.",
    ),
)
def test_weather_abstains_from_conditional_propositions(text: str) -> None:
    assert not WeatherConversationInterceptionPort.is_weather_request(text)


@pytest.mark.parametrize(
    "text",
    (
        "¿llueve?",
        "¿va a llover mañana?",
        "¿hay viento?",
        "¿hace frío?",
    ),
)
def test_explicit_weather_requests_remain_weather(text: str) -> None:
    assert WeatherConversationInterceptionPort.is_weather_request(text)


def test_available_weather_runtime_does_not_capture_guide_v2_k_opening() -> None:
    runtime = WeatherConversationInterceptionPort(WeatherAdapter(Provider()))

    result = runtime.intercept(
        _request("Si mañana llueve, Marta irá en taxi."),
        now=datetime.now(timezone.utc),
    )

    assert result is None


def test_unavailable_weather_guard_does_not_capture_guide_v2_k_opening() -> None:
    runtime = WeatherUnavailableConversationInterceptionPort()

    result = runtime.intercept(
        _request("Si mañana llueve, Marta irá en taxi."),
        now=datetime.now(timezone.utc),
    )

    assert result is None
