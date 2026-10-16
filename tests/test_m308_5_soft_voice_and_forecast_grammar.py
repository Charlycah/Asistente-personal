from pathlib import Path

from app.audio_engine import VoskAudioEngine, VoskAudioEngineConfig
from app.weather_conversation_runtime import WeatherConversationInterceptionPort


def test_m308_5_defaults_are_more_tolerant_of_soft_voice(tmp_path: Path) -> None:
    config = VoskAudioEngineConfig(model_path=tmp_path)

    assert config.voice_threshold == 380
    assert config.noise_multiplier == 2.2
    assert config.target_peak == 14000
    assert config.max_gain == 4.0


def test_m308_5_soft_speech_can_pass_the_energy_gate(tmp_path: Path) -> None:
    engine = VoskAudioEngine(VoskAudioEngineConfig(model_path=tmp_path))
    engine._webrtc_speech_ratio = lambda _data: 0.25  # type: ignore[method-assign]

    assert engine._is_probable_speech(b"\x00\x00" * 320, 400)


def test_m308_5_forecast_uses_y_for_adjectival_cloud_conditions() -> None:
    render = WeatherConversationInterceptionPort._forecast_description

    assert render("muy nublado") == "y muy nublado"
    assert render("parcialmente nublado") == "y parcialmente nublado"
    assert render("nublado") == "y nublado"
    assert render("lluvia ligera") == "con lluvia ligera"
