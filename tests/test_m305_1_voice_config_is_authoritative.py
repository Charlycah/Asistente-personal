from app.audio_engine import VoskAudioEngine
from app.voice_input import build_voice_input_from_environment


def test_voice_config_ignores_stale_process_environment(monkeypatch):
    monkeypatch.setenv("ROBY_CONTINUOUS_LISTENING_ENABLED", "false")
    monkeypatch.setenv("ROBY_AUDIO_BACKEND", "powershell")
    monkeypatch.setenv("ROBY_AUDIO_DIAGNOSTIC_MODE", "false")

    voice_input = build_voice_input_from_environment()

    assert isinstance(voice_input, VoskAudioEngine)
    assert voice_input.config.diagnostic_mode is True
