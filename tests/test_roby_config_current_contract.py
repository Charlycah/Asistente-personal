from __future__ import annotations

from pathlib import Path

import pytest

from app.roby_config import DEFAULT_CONFIG
from main import build_parser, main


def test_parser_uses_config_json_instead_of_legacy_migration() -> None:
    args = build_parser().parse_args(["--config", ".roby/config.json"])
    assert args.config == ".roby/config.json"
    assert not hasattr(args, "import_legacy_config")


def test_main_setup_does_not_create_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["--setup"]) == 0
    assert (tmp_path / ".roby" / "config.json").exists()
    assert not (tmp_path / ".env").exists()


def test_roby_config_contains_domestic_defaults() -> None:
    assert DEFAULT_CONFIG["household"]["city"] == "Buenos Aires"
    assert DEFAULT_CONFIG["household"]["language"] == "es"
    assert (
        DEFAULT_CONFIG["runtime"]["factory"]
        == "app.runtime_root_factory:build_runtime_root"
    )
