import json

from infrastructure.config.settings_loader import SettingsLoader


def test_config_loader_manual_smoke(tmp_path):
    config_path = tmp_path / "config.json"
    credentials_path = tmp_path / "credentials.json"

    config_path.write_text(
        json.dumps(
            {
                "assistant": {
                    "name": "ROBY",
                    "language": "es",
                    "timezone": "America/Argentina/Buenos_Aires",
                },
                "weather": {
                    "default_city": "Buenos Aires",
                    "provider": "openweather",
                    "extended_provider": "weatherapi",
                },
                "memory": {
                    "enabled": True,
                    "database_path": "data/asistente.db",
                },
                "reminders": {
                    "enabled": True,
                    "check_interval_seconds": 30,
                },
                "llm": {
                    "provider": "ollama",
                    "model": "llama3",
                },
                "voice": {
                    "enabled": True,
                    "tts_provider": "edge-tts",
                    "stt_provider": "vosk",
                },
                "debug": False,
            }
        ),
        encoding="utf-8",
    )
    credentials_path.write_text(
        json.dumps({"credentials": {}}),
        encoding="utf-8",
    )

    config = SettingsLoader(
        config_path=str(config_path),
        credentials_path=str(credentials_path),
    ).load()

    assert config.assistant.name == "ROBY"
    assert config.voice.stt_provider == "vosk"
