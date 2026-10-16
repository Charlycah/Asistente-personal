import json

import pytest

from infrastructure.config.config_schema import AppConfig
from infrastructure.config.settings_loader import SettingsLoader

VALID_CONFIG = {
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
        "enabled": False,
        "tts_provider": "gtts",
        "stt_provider": "vosk",
    },
    "debug": True,
}


def write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_settings_loader_builds_app_config_from_local_json(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    monkeypatch.delenv("WEATHERAPI_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_TOKEN_FILE", raising=False)
    monkeypatch.delenv("GMAIL_ADDRESS", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CAMERA_INDEX", raising=False)

    config_path = tmp_path / "config.local.json"
    credentials_path = tmp_path / "credentials.json"

    write_json(config_path, VALID_CONFIG)
    write_json(
        credentials_path,
        {
            "credentials": {
                "OPENWEATHER_API_KEY": "openweather-test-key",
                "WEATHERAPI_KEY": "weatherapi-test-key",
                "GOOGLE_CLIENT_SECRET_FILE": "credentials.test.json",
                "GOOGLE_TOKEN_FILE": "token.test.pickle",
                "GMAIL_ADDRESS": "roby@example.com",
                "GMAIL_APP_PASSWORD": "gmail-app-password-test",
                "GEMINI_API_KEY": "gemini-test-key",
                "OPENROUTER_API_KEY": "openrouter-test-key",
                "MISTRAL_API_KEY": "mistral-test-key",
                "OPENAI_API_KEY": "openai-test-key",
                "CAMERA_INDEX": 2,
            }
        },
    )

    config = SettingsLoader(
        config_path=str(config_path),
        credentials_path=str(credentials_path),
    ).load()

    assert isinstance(config, AppConfig)
    assert config.assistant.name == "ROBY"
    assert config.assistant.language == "es"
    assert config.assistant.timezone == "America/Argentina/Buenos_Aires"
    assert config.weather.default_city == "Buenos Aires"
    assert config.weather.provider == "openweather"
    assert config.weather.extended_provider == "weatherapi"
    assert config.memory.enabled is True
    assert config.memory.database_path == "data/asistente.db"
    assert config.reminders.enabled is True
    assert config.reminders.check_interval_seconds == 30
    assert config.llm.provider == "ollama"
    assert config.llm.model == "llama3"
    assert config.voice.enabled is False
    assert config.voice.tts_provider == "gtts"
    assert config.voice.stt_provider == "vosk"
    assert config.debug is True
    assert config.secrets.openweather_api_key == "openweather-test-key"
    assert config.secrets.weatherapi_key == "weatherapi-test-key"
    assert config.secrets.google_client_secret_file == "credentials.test.json"
    assert config.secrets.google_token_file == "token.test.pickle"
    assert config.secrets.gmail_address == "roby@example.com"
    assert config.secrets.gmail_app_password == "gmail-app-password-test"
    assert config.secrets.gemini_api_key == "gemini-test-key"
    assert config.secrets.openrouter_api_key == "openrouter-test-key"
    assert config.secrets.mistral_api_key == "mistral-test-key"
    assert config.secrets.openai_api_key == "openai-test-key"
    assert config.secrets.camera_index == 2


def test_settings_loader_uses_false_debug_by_default(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    monkeypatch.delenv("WEATHERAPI_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_TOKEN_FILE", raising=False)
    monkeypatch.delenv("GMAIL_ADDRESS", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CAMERA_INDEX", raising=False)

    config_without_debug = dict(VALID_CONFIG)
    config_without_debug.pop("debug")

    config_path = tmp_path / "config.local.json"
    credentials_path = tmp_path / "credentials.json"

    write_json(config_path, config_without_debug)
    write_json(credentials_path, {"credentials": {}})

    config = SettingsLoader(
        config_path=str(config_path),
        credentials_path=str(credentials_path),
    ).load()

    assert config.debug is False


def test_settings_loader_allows_missing_optional_secrets(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    monkeypatch.delenv("WEATHERAPI_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_TOKEN_FILE", raising=False)
    monkeypatch.delenv("GMAIL_ADDRESS", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CAMERA_INDEX", raising=False)

    config_path = tmp_path / "config.local.json"
    credentials_path = tmp_path / "credentials.json"

    write_json(config_path, VALID_CONFIG)
    write_json(credentials_path, {"credentials": {}})

    config = SettingsLoader(
        config_path=str(config_path),
        credentials_path=str(credentials_path),
    ).load()

    assert config.secrets.openweather_api_key is None
    assert config.secrets.weatherapi_key is None
    assert config.secrets.google_client_secret_file is None
    assert config.secrets.google_token_file is None
    assert config.secrets.gmail_address is None
    assert config.secrets.gmail_app_password is None
    assert config.secrets.gemini_api_key is None
    assert config.secrets.openrouter_api_key is None
    assert config.secrets.mistral_api_key is None
    assert config.secrets.openai_api_key is None
    assert config.secrets.camera_index == 0


def test_settings_loader_raises_when_config_file_does_not_exist(tmp_path):
    missing_config_path = tmp_path / "missing-config.json"
    credentials_path = tmp_path / "credentials.json"
    write_json(credentials_path, {"credentials": {}})

    with pytest.raises(FileNotFoundError):
        SettingsLoader(
            config_path=str(missing_config_path),
            credentials_path=str(credentials_path),
        ).load()


def test_settings_loader_rejects_invalid_camera_index(tmp_path, monkeypatch):
    monkeypatch.delenv("CAMERA_INDEX", raising=False)

    config_path = tmp_path / "config.local.json"
    credentials_path = tmp_path / "credentials.json"

    write_json(config_path, VALID_CONFIG)
    write_json(credentials_path, {"credentials": {"CAMERA_INDEX": "main-camera"}})

    with pytest.raises(Exception, match="CAMERA_INDEX"):
        SettingsLoader(
            config_path=str(config_path),
            credentials_path=str(credentials_path),
        ).load()
