from app.runtime_ui_adapter import ConversationalPersonalityUIAdapter
from app.ui_adapter import UIResponse
from app.voice_output import EdgeTTSVoiceOutput
from app.weather_conversation_runtime import WeatherConversationInterceptionPort
from m6.response.models import ResponseStatus


class RecordingAdapter:
    def __init__(self, response_text: str = "respuesta remota") -> None:
        self.response_text = response_text
        self.calls: list[str] = []

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.calls.append(text)
        return UIResponse(
            text=self.response_text,
            status=ResponseStatus.SUCCESS.value,
            session_id=session_id,
            needs_input=False,
        )


def test_common_greeting_is_answered_locally_without_runtime_call():
    runtime = RecordingAdapter()
    adapter = ConversationalPersonalityUIAdapter(runtime)

    response = adapter.submit_text("hola Roby, como te va ?", session_id="home")

    assert runtime.calls == []
    assert response.text == "Hola. Todo tranquilo por acá. ¿Cómo andás vos?"


def test_final_ui_sanitizer_removes_vale_and_mixed_english():
    runtime = RecordingAdapter("Vale! No problem then. ¿Quieres seguir?")
    adapter = ConversationalPersonalityUIAdapter(runtime)

    response = adapter.submit_text("seguimos", session_id="home")

    assert "vale" not in response.text.casefold()
    assert "problem" not in response.text.casefold()
    assert "queres" in response.text.casefold()


def test_current_weather_is_one_natural_paragraph():
    text = WeatherConversationInterceptionPort._render_current(
        {
            "weather": {
                "location": "Buenos Aires",
                "temperature_celsius": 10,
                "feels_like_celsius": 10,
                "description": "nublado",
                "humidity_percent": 88,
                "wind_kph": 4.8,
                "pressure_hpa": 1006,
                "rain_probability_percent": 0,
            },
            "advice": ("conviene salir con abrigo",),
        }
    )

    assert "\n" not in text
    assert text.startswith("Ahora en Buenos Aires está nublado")
    assert "La humedad está en 88% y el viento va a 4.8 km/h" in text


def test_short_weather_response_uses_one_tts_process_chunk():
    text = (
        "Ahora en Buenos Aires está nublado, con 10 grados. "
        "La humedad está en 88 por ciento y el viento va a 4.8 kilómetros "
        "por hora, con una presión de 1006 hectopascales. "
        "Te recomiendo salir con abrigo."
    )

    assert EdgeTTSVoiceOutput._speech_chunks(text) == (text,)


def test_full_forecast_stays_separated_by_day():
    text = (
        "Pronóstico extendido para Buenos Aires:\n\n"
        "- Domingo: lluvia y viento.\n\n"
        "- Lunes: nublado y fresco.\n\n"
        "- Martes: estable."
    )

    chunks = EdgeTTSVoiceOutput._speech_chunks(text)

    assert len(chunks) == 4
    assert chunks[0].startswith("Pronóstico extendido")
    assert chunks[-1].startswith("- Martes")


def test_weather_description_nubes_becomes_nublado():
    assert (
        WeatherConversationInterceptionPort._natural_description("nubes") == "nublado"
    )


def test_forecast_nubes_uses_natural_y_connector():
    assert (
        WeatherConversationInterceptionPort._forecast_description("nubes")
        == "y nublado"
    )


def test_current_weather_prioritizes_feels_like_and_practical_advice():
    payload = {
        "weather": {
            "location": "Buenos Aires",
            "temperature_celsius": 10,
            "feels_like_celsius": 6,
            "description": "lluvia ligera",
            "humidity_percent": 95,
            "wind_kph": 18.0,
            "pressure_hpa": 1014,
            "rain_probability_percent": 70,
        },
        "advice": (),
    }

    rendered = WeatherConversationInterceptionPort._render_current(payload)

    assert "sensación térmica de 6 °C" in rendered
    assert "humedad está en 95%" in rendered
    assert "viento va a 18.0 km/h" in rendered
    assert "presión de 1014 hPa" in rendered
    assert "probabilidad de lluvia es del 70%" in rendered
    assert "Llevate un buen abrigo" in rendered
    assert "llevá paraguas" in rendered
