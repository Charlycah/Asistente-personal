from app.audio_engine import VoskAudioEngine
from app.roby_config import activate_roby_config, resolve_roby_config_path
from app.voice_input import build_voice_input_from_environment


def test_config_activates_same_vosk_path_as_manual_powershell(monkeypatch):
    monkeypatch.setenv("ROBY_CONTINUOUS_LISTENING_ENABLED", "false")
    monkeypatch.setenv("ROBY_AUDIO_BACKEND", "powershell")
    monkeypatch.setenv("ROBY_AUDIO_DIAGNOSTIC_MODE", "false")

    activate_roby_config(resolve_roby_config_path(), override_existing=True)
    voice_input = build_voice_input_from_environment()

    assert isinstance(voice_input, VoskAudioEngine)
    assert voice_input.config.diagnostic_mode is True
