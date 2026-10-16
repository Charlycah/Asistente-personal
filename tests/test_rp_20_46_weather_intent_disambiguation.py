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


def _request(text):
    return GovernedConversationPipelineRequest(
        owner="Familia",
        session_id="home",
        text=text,
    )


def test_sports_prediction_does_not_trigger_weather_forecast():
    runtime = WeatherConversationInterceptionPort(WeatherAdapter(Provider()))

    result = runtime.intercept(
        _request("Roby tenes un pronostico entre Argentina y España quien gana?"),
        now=datetime.now(timezone.utc),
    )

    assert result is None


def test_missing_credentials_guard_does_not_capture_sports_prediction():
    runtime = WeatherUnavailableConversationInterceptionPort()

    result = runtime.intercept(
        _request("tenes un pronóstico para Argentina contra España?"),
        now=datetime.now(timezone.utc),
    )

    assert result is None


def test_explicit_extended_forecast_still_triggers_weather():
    assert WeatherConversationInterceptionPort.is_weather_request(
        "decime el pronóstico extendido para Buenos Aires"
    )


def test_weather_forecast_for_tomorrow_still_triggers_weather():
    assert WeatherConversationInterceptionPort.is_weather_request(
        "qué pronóstico hay para mañana"
    )


def test_ambiguous_prediction_word_alone_is_not_weather():
    assert not WeatherConversationInterceptionPort.is_weather_request(
        "qué pronóstico tenés para la final"
    )


@pytest.mark.parametrize(
    "text",
    (
        "decime el clima",
        "clima",
        "¿llueve?",
        "¿hay viento?",
        "¿qué temperatura hace?",
        "pronóstico para mañana",
        "¿necesito paraguas hoy?",
        "cómo está el clima en Córdoba?",
    ),
)
def test_explicit_or_short_weather_requests_remain_weather(text):
    assert WeatherConversationInterceptionPort.is_weather_request(text)


@pytest.mark.parametrize(
    "text",
    (
        "Pensamos que la ventana se rompió por el viento.",
        "La lluvia dañó el techo.",
        "La humedad dañó el papel.",
        "El calor deformó la pieza.",
        "El frío rompió la tubería.",
        "Compré un paraguas rojo.",
        "¿El viento pudo romper la ventana?",
        "¿La humedad puede dañar madera?",
    ),
)
def test_weather_vocabulary_inside_propositions_does_not_claim_weather(text):
    assert not WeatherConversationInterceptionPort.is_weather_request(text)


@pytest.mark.parametrize(
    "text",
    (
        "cómo viene la misión Artemis",
        "cómo viene Boca",
        "cómo viene la economía",
        "cómo viene el proyecto",
    ),
)
def test_cross_domain_how_is_it_going_phrases_are_not_weather(text):
    assert not WeatherConversationInterceptionPort.is_weather_request(text)


def test_guide_v2_evidence_revision_opening_is_not_intercepted_by_weather():
    runtime = WeatherConversationInterceptionPort(WeatherAdapter(Provider()))

    result = runtime.intercept(
        _request("Pensamos que la ventana se rompió por el viento."),
        now=datetime.now(timezone.utc),
    )

    assert result is None


def test_missing_credentials_guard_also_abstains_from_guide_v2_opening():
    runtime = WeatherUnavailableConversationInterceptionPort()

    result = runtime.intercept(
        _request("Pensamos que la ventana se rompió por el viento."),
        now=datetime.now(timezone.utc),
    )

    assert result is None
