from __future__ import annotations

import json
import os

import pytest

from app.roby_config import activate_roby_config, load_roby_config


def test_missing_config_is_created_with_domestic_defaults(tmp_path):
    path = tmp_path / ".roby" / "config.json"
    result = load_roby_config(path)
    assert result.created
    assert result.data["providers"]["local"]["model"] == "llama3:latest"
    assert path.exists()


def test_config_activates_legacy_wiring_without_dotenv(tmp_path, monkeypatch):
    path = tmp_path / ".roby" / "config.json"
    path.parent.mkdir()
    path.write_text(
        json.dumps(
            {
                "providers": {
                    "local": {
                        "endpoint": "http://127.0.0.1:11434/v1",
                        "model": "family-model:latest",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("ROBY_LOCAL_PROVIDER_MODEL", raising=False)
    activate_roby_config(path)
    assert os.environ["ROBY_LOCAL_PROVIDER_MODEL"] == "family-model:latest"


def test_invalid_json_reports_location(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"bad":,}', encoding="utf-8")
    with pytest.raises(ValueError, match="línea"):
        load_roby_config(path)


def test_plaintext_legacy_secrets_are_not_migrated(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "modelo_ollama": "llama3",
                "gemini_api_key": "do-not-copy",
                "openweather_api_key": "do-not-copy",
            }
        ),
        encoding="utf-8",
    )
    result = load_roby_config(path)
    serialized = json.dumps(result.data)
    assert "do-not-copy" not in serialized


def test_explicit_process_override_is_preserved(tmp_path, monkeypatch):
    path = tmp_path / ".roby" / "config.json"
    load_roby_config(path)
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "temporary-test-model")
    activate_roby_config(path)
    assert os.environ["ROBY_LOCAL_PROVIDER_MODEL"] == "temporary-test-model"


def test_config_never_creates_dotenv(tmp_path):
    path = tmp_path / ".roby" / "config.json"
    load_roby_config(path)
    assert not (tmp_path / ".env").exists()
