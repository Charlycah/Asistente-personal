from app.runtime_ui_adapter import ConversationalPersonalityUIAdapter
from app.ui_adapter import UIResponse
from app.weather_conversation_runtime import WeatherConversationInterceptionPort
from m6.response.models import ResponseStatus


class StubAdapter:
    def __init__(self):
        self.requests = []

    def submit_text(self, text, session_id=None):
        self.requests.append(text)
        if "pronóstico" in text or "pronostico" in text:
            body = "Pronóstico extendido para Buenos Aires:\n- Lunes: entre 10 y 15 °C."
        else:
            body = "En Buenos Aires tenemos 12 °C y nubes.\nLa humedad está en 70%."
        return UIResponse(
            text=body,
            status=ResponseStatus.SUCCESS.value,
            session_id=session_id,
            needs_input=False,
        )


def test_weather_offer_and_affirmative_follow_up_use_real_forecast_route():
    stub = StubAdapter()
    adapter = ConversationalPersonalityUIAdapter(stub)
    current = adapter.submit_text("roby decime el clima", session_id="s1")
    assert "Si querés" in current.text
    forecast = adapter.submit_text("sí", session_id="s1")
    assert stub.requests[-1] == "decime el pronóstico extendido"
    assert "Pronóstico extendido" in forecast.text


def test_thanks_closes_pending_context_without_replaying_weather():
    stub = StubAdapter()
    adapter = ConversationalPersonalityUIAdapter(stub)
    adapter.submit_text("decime el clima", session_id="s1")
    result = adapter.submit_text("Gracias ROBY", session_id="s1")
    assert result.text == "De nada."
    assert len(stub.requests) == 1


def test_weather_advice_sounds_conversational():
    assert (
        WeatherConversationInterceptionPort._natural_advice("conviene salir con abrigo")
        == "Te recomiendo salir con abrigo."
    )


def test_weather_context_survives_rain_and_cold_then_ambiguous_forecast():
    stub = StubAdapter()
    adapter = ConversationalPersonalityUIAdapter(stub)

    current = adapter.submit_text(
        "bien Roby pero con lluvia y frio", session_id="weather-context"
    )
    assert "Si querés" in current.text

    forecast = adapter.submit_text(
        "y el pronostico Roby?", session_id="weather-context"
    )
    assert stub.requests[-1] == "decime el pronóstico extendido"
    assert "Pronóstico extendido" in forecast.text


def test_weather_context_accepts_short_tomorrow_follow_up():
    stub = StubAdapter()
    adapter = ConversationalPersonalityUIAdapter(stub)
    adapter.submit_text("está lloviendo y hace frío", session_id="weather-tomorrow")

    adapter.submit_text("¿y mañana?", session_id="weather-tomorrow")

    assert stub.requests[-1] == "decime el pronóstico extendido"


def test_weather_offer_accepts_natural_double_affirmative_follow_up():
    stub = StubAdapter()
    adapter = ConversationalPersonalityUIAdapter(stub)

    current = adapter.submit_text("con un poco de frio", session_id="s-natural")
    assert "Si querés" in current.text

    forecast = adapter.submit_text("dale contame", session_id="s-natural")

    assert stub.requests[-1] == "decime el pronóstico extendido"
    assert "Pronóstico extendido" in forecast.text


def test_weather_offer_accepts_yes_tell_me_follow_up():
    stub = StubAdapter()
    adapter = ConversationalPersonalityUIAdapter(stub)
    adapter.submit_text("hace frío", session_id="s-si-contame")

    adapter.submit_text("sí contame Roby", session_id="s-si-contame")

    assert stub.requests[-1] == "decime el pronóstico extendido"


def test_weather_offer_accepts_give_me_forecast_follow_up():
    stub = StubAdapter()
    adapter = ConversationalPersonalityUIAdapter(stub)
    adapter.submit_text("roby decime el clima", session_id="s-dame-pronostico")

    result = adapter.submit_text(
        "dame el pronostico", session_id="s-dame-pronostico"
    )

    assert stub.requests[-1] == "decime el pronóstico extendido"
    assert "Pronóstico extendido" in result.text
