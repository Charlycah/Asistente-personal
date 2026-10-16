from datetime import datetime, timezone

from app.roby_config import activate_roby_config
from app.unified_experience_layer import UnifiedExperienceLayer
from app.unified_runtime_integration import MailUnavailableConversationInterceptionPort
from app.voice_output import VOICE_PRESETS, VoiceProsodyFormatter
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


def request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        text=text, owner="Carlos", session_id="s1"
    )


def test_casual_female_profile_is_more_fluid():
    profile = VOICE_PRESETS["casual_female"]
    assert profile.voice == "es-AR-ElenaNeural"
    assert profile.rate == "+3%"
    assert profile.pitch == "+2Hz"


def test_weather_metrics_flow_without_long_full_stop_pauses():
    spoken = VoiceProsodyFormatter().format(
        "La humedad está en 89%.\n"
        "El viento va a 4.8 km/h.\n"
        "La presión atmosférica es de 1004 hPa."
    )
    assert "por ciento, El viento" in spoken
    assert ", y La presión" in spoken


def test_mail_unavailable_never_invents_messages():
    port = MailUnavailableConversationInterceptionPort()
    result = port.intercept(
        request("me decis si tengo correos?"), now=datetime.now(timezone.utc)
    )
    assert result is not None
    assert "No tengo acceso real" in result.response_text
    assert "María" not in result.response_text


def test_polite_closure_cannot_replay_weather_context():
    layer = UnifiedExperienceLayer()
    result = layer.present(
        GovernedOperationalInterception(
            response_text="Voy a decirte el pronóstico otra vez.",
            rationale="bad_context",
        ),
        request=request("no, gracias roby"),
    )
    assert result.response_text == "De nada."


def test_default_config_uses_wake_word_only_and_casual_voice(monkeypatch, tmp_path):
    config = tmp_path / "config.json"
    monkeypatch.delenv("ROBY_AMBIENT_COMMENTS_ENABLED", raising=False)
    activate_roby_config(config, override_existing=True)
    import os

    assert os.environ["ROBY_VOICE_PROFILE"] == "casual_female"
    assert os.environ.get("ROBY_AMBIENT_COMMENTS_ENABLED", "false") == "false"
