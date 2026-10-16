from datetime import datetime, timezone

from app.runtime_environment_wiring import build_weather_conversation_from_environment
from app.unified_experience_layer import UnifiedExperienceLayer
from app.voice_output import EdgeTTSVoiceOutput
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


def _request(text: str):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="test", text=text
    )


def test_missing_openweather_key_never_falls_through_to_model(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_WEATHER_ENABLED", "true")
    monkeypatch.setenv("ROBY_HOME", str(tmp_path))
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    runtime = build_weather_conversation_from_environment()
    result = runtime.intercept(
        _request("me decis como esta el clima"), now=datetime.now(timezone.utc)
    )
    assert "falta la clave de OpenWeather" in result.response_text
    assert "no problems" not in result.response_text.casefold()


def test_non_greeting_answer_drops_repeated_hola():
    layer = UnifiedExperienceLayer()
    result = layer.present(
        GovernedOperationalInterception(
            response_text="Hola! El pronóstico extendido está disponible.",
            rationale="test",
        ),
        request=_request("me decis el pronostico"),
    )
    assert result.response_text == "El pronóstico extendido está disponible."


def test_actual_greeting_keeps_hola():
    layer = UnifiedExperienceLayer()
    result = layer.present(
        GovernedOperationalInterception(
            response_text="Hola! ¿Cómo estás?", rationale="test"
        ),
        request=_request("hola roby"),
    )
    assert result.response_text.startswith("Hola")


def test_extended_forecast_is_split_into_short_voice_chunks():
    text = " ".join(
        (
            f"Día {number}. Temperatura de veinte grados. "
            "Viento de diez kilómetros por hora. "
            "Presión de mil quince hectopascales."
        )
        for number in range(1, 6)
    )
    chunks = EdgeTTSVoiceOutput._speech_chunks(text)
    assert len(chunks) >= 2
    assert all(len(chunk) <= 360 for chunk in chunks)
