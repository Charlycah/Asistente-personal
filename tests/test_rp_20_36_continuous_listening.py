from app.roby_config import environment_values
from app.voice_input import (
    SafeVoiceInput,
    build_voice_input_from_environment,
)


def test_config_exposes_continuous_listening_settings():
    values = environment_values(
        {
            "services": {
                "voice": {
                    "continuous_listening": {
                        "enabled": True,
                        "language": "es-AR",
                        "wake_word": "roby",
                        "ambient_comments": True,
                        "comment_cooldown_seconds": 90,
                        "utterance_timeout_seconds": 8,
                    }
                }
            }
        }
    )
    assert values["ROBY_CONTINUOUS_LISTENING_ENABLED"] == "true"
    assert values["ROBY_SPEECH_LANGUAGE"] == "es-AR"
    assert values["ROBY_VOICE_WAKE_WORD"] == "roby"


def test_windows_local_voice_input_is_built_when_enabled(monkeypatch, tmp_path):
    config_dir = tmp_path / ".roby"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(
        '{"runtime":{},"services":{"voice":{"continuous_listening":'
        '{"enabled":true,"audio_backend":"powershell"}}}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "app.roby_config.resolve_roby_config_path", lambda: config_dir / "config.json"
    )

    voice_input = build_voice_input_from_environment()

    assert isinstance(voice_input, SafeVoiceInput)
