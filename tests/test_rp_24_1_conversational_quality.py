from app.conversational_quality_policy import ConversationalQualityPolicy
from app.runtime_ui_adapter import ConversationalPersonalityUIAdapter
from app.ui_adapter import UIResponse
from m6.response.models import ResponseStatus


class _Adapter:
    def __init__(self, response: str) -> None:
        self.response = response

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        return UIResponse(
            text=self.response,
            status=ResponseStatus.SUCCESS.value,
            session_id=session_id,
            needs_input=False,
        )


def test_removes_redundant_roby_identity_opener():
    policy = ConversationalQualityPolicy()
    result = policy.apply(
        request_text="¿Hay noticias relevantes?",
        response_text=(
            "Como Roby soy consciente de que actualmente no hay noticias relevadas."
        ),
    )
    assert result == "Actualmente no hay noticias relevadas."
    assert policy.snapshot.self_references_removed == 1


def test_contextualizes_cloudy_weather_after_bad_day_comment():
    policy = ConversationalQualityPolicy()
    result = policy.apply(
        request_text="Qué feo día hoy",
        response_text=(
            "Ahora en Buenos Aires está nublado, con 10 °C. "
            "La humedad está en 88%."
        ),
    )
    assert result.startswith("Sí, hoy está bastante nublado en Buenos Aires")
    assert "10 °C" in result


def test_does_not_force_contextual_weather_for_direct_query():
    policy = ConversationalQualityPolicy()
    result = policy.apply(
        request_text="¿Cómo está el clima?",
        response_text="Ahora en Buenos Aires está nublado, con 10 °C.",
    )
    assert result == "Ahora en Buenos Aires está nublado, con 10 °C."


def test_restores_single_explicit_time_from_user_request():
    policy = ConversationalQualityPolicy()
    result = policy.apply(
        request_text="Recordame el viernes el turno a las 15.30",
        response_text="Listo. Te recordaré el viernes a las 15:00.",
    )
    assert result == "Listo. Te recordaré el viernes a las 15:30."
    assert policy.snapshot.exact_times_restored == 1


def test_keeps_matching_time_unchanged():
    policy = ConversationalQualityPolicy()
    result = policy.apply(
        request_text="Recordame el turno a las 9:05",
        response_text="Listo. Te recordaré a las 09:05.",
    )
    assert result == "Listo. Te recordaré a las 09:05."
    assert policy.snapshot.exact_times_restored == 0


def test_does_not_guess_when_request_has_multiple_times():
    policy = ConversationalQualityPolicy()
    result = policy.apply(
        request_text="Entre 15:30 y 16:00 tengo el turno",
        response_text="Agendé el turno a las 15:00.",
    )
    assert result == "Agendé el turno a las 15:00."


def test_removes_generic_robotic_closing():
    policy = ConversationalQualityPolicy()
    result = policy.apply(
        request_text="Qué feo día",
        response_text=(
            "Ahora en Buenos Aires está nublado, con 10 °C. "
            "¿Necesitas algo más?"
        ),
    )
    assert "¿Necesitas algo más?" not in result


def test_ui_adapter_applies_time_protection_to_final_response():
    adapter = ConversationalPersonalityUIAdapter(
        _Adapter("Listo. Te recordaré el viernes a las 15:00.")
    )
    response = adapter.submit_text(
        "Recordame el viernes el turno a las 15.30",
        session_id="carlos",
    )
    assert "15:30" in response.text
    assert "15:00" not in response.text


def test_ui_adapter_uses_natural_cloudy_phrase_for_contextual_comment():
    adapter = ConversationalPersonalityUIAdapter(
        _Adapter("Ahora en Buenos Aires está nublado, con 10 °C.")
    )
    response = adapter.submit_text("Qué feo día hoy", session_id="carlos")
    assert response.text.startswith("Sí, hoy está bastante nublado")
