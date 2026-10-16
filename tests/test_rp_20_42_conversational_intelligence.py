from __future__ import annotations

import json
import os
from pathlib import Path

from app.companion_expression_policy import CompanionExpressionPolicy
from app.credentials import activate_credentials
from app.roby_config import load_roby_config
from app.unified_experience_layer import UnifiedExperienceLayer
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


class _Request:
    def __init__(self, text: str) -> None:
        self.text = text


def _result(text: str) -> GovernedOperationalInterception:
    return GovernedOperationalInterception(response_text=text, rationale="test")


def test_vale_and_mixed_english_are_removed_from_visible_response():
    policy = CompanionExpressionPolicy()

    assert policy.apply("Vale! No problem then. ¿Quieres seguir?") == (
        "¿queres seguir?"
    )


def test_reordered_thanks_closes_without_reopening_previous_topic():
    layer = UnifiedExperienceLayer()

    result = layer.present(
        _result("Vale, no problem then. Seguimos con el clima."),
        request=_Request("No, Roby, gracias."),
    )

    assert result is not None
    assert result.response_text == "De nada."


def test_deferral_turn_gets_one_short_closure():
    layer = UnifiedExperienceLayer()

    result = layer.present(
        _result("Decime cuando estés listo. ¿Querés hacer algo más?"),
        request=_Request("Ok Roby, voy a revisar y después seguimos."),
    )

    assert result is not None
    assert result.response_text == "Perfecto. Hablamos después."


def test_default_config_migrates_from_hal_directory(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    legacy = tmp_path / ".hal" / "config.json"
    legacy.parent.mkdir(parents=True)
    legacy.write_text(
        json.dumps(
            {
                "version": 1,
                "assistant": {"name": "HAL", "aliases": ["hal"]},
                "household": {"city": "Buenos Aires"},
                "services": {
                    "weather": {"enabled": True, "provider": "openweather"},
                    "voice": {"continuous_listening": {"wake_word": "hal"}},
                },
            }
        ),
        encoding="utf-8",
    )

    result = load_roby_config()

    assert result.path == Path(".roby/config.json")
    assert result.data["assistant"] == {"name": "Roby", "aliases": []}
    assert (
        result.data["services"]["voice"]["continuous_listening"]["wake_word"] == "roby"
    )
    assert result.data["services"]["weather"]["enabled"] is True
    assert (tmp_path / ".roby" / "config.json").exists()


def test_credentials_migrate_from_hal_directory(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    legacy = tmp_path / ".hal" / "credentials.json"
    legacy.parent.mkdir(parents=True)
    legacy.write_text(
        json.dumps({"weather": {"OPENWEATHER_API_KEY": "real-test-key"}}),
        encoding="utf-8",
    )

    activated = activate_credentials()

    assert "OPENWEATHER_API_KEY" in activated
    assert (tmp_path / ".roby" / "credentials.json").exists()
    migrated = json.loads(
        (tmp_path / ".roby" / "credentials.json").read_text(encoding="utf-8")
    )
    assert migrated["credentials"]["OPENWEATHER_API_KEY"] == "real-test-key"


def test_credentials_accept_roby_spanish_singular_filename(
    tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    source = tmp_path / ".roby" / "credencial.json"
    source.parent.mkdir(parents=True)
    source.write_text(
        json.dumps({"weather": {"OPENWEATHER_API_KEY": "singular-key"}}),
        encoding="utf-8",
    )

    activated = activate_credentials()

    assert "OPENWEATHER_API_KEY" in activated
    assert os.environ["OPENWEATHER_API_KEY"] == "singular-key"
    canonical = tmp_path / ".roby" / "credentials.json"
    assert canonical.exists()


def test_credentials_accept_legacy_spanish_singular_filename(
    tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    source = tmp_path / ".hal" / "credencial.json"
    source.parent.mkdir(parents=True)
    source.write_text(
        json.dumps({"OPENWEATHER_API_KEY": "legacy-singular-key"}),
        encoding="utf-8",
    )

    activated = activate_credentials()

    assert "OPENWEATHER_API_KEY" in activated
    assert os.environ["OPENWEATHER_API_KEY"] == "legacy-singular-key"
    assert (tmp_path / ".roby" / "credentials.json").exists()


def test_credentials_resolve_from_project_root_when_started_elsewhere(
    tmp_path: Path, monkeypatch
):
    from infrastructure.config import secrets_loader

    project = tmp_path / "revision"
    launch_directory = tmp_path / "shortcut-start"
    credentials = project / ".roby" / "credentials.json"
    credentials.parent.mkdir(parents=True)
    launch_directory.mkdir()
    credentials.write_text(
        json.dumps({"credentials": {"OPENWEATHER_API_KEY": "project-key"}}),
        encoding="utf-8",
    )
    monkeypatch.chdir(launch_directory)
    monkeypatch.delenv("ROBY_HOME", raising=False)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    monkeypatch.setattr(
        secrets_loader,
        "credential_search_roots",
        lambda: (launch_directory, project),
    )

    loader = secrets_loader.SecretsLoader()

    assert loader.credentials_path == credentials
    assert loader.get("OPENWEATHER_API_KEY") == "project-key"


def test_credentials_accept_roby_credentials_wrapper(
    tmp_path: Path, monkeypatch
):
    from infrastructure.config.secrets_loader import SecretsLoader

    credentials = tmp_path / ".roby" / "credentials.json"
    credentials.parent.mkdir(parents=True)
    credentials.write_text(
        json.dumps({"credentials": {"OPENWEATHER_API_KEY": "wrapped-key"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ROBY_HOME", str(tmp_path))
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)

    loader = SecretsLoader()

    assert loader.credentials_path == credentials
    assert loader.get("OPENWEATHER_API_KEY") == "wrapped-key"
