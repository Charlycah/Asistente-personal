from __future__ import annotations

from pathlib import Path

import pytest

import main

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("retired_option", ("--observe", "--no-lifecycle"))
def test_console_only_options_are_absent_from_production_parser(
    retired_option: str, capsys
) -> None:
    with pytest.raises(SystemExit) as captured:
        main.build_parser().parse_args([retired_option])

    assert captured.value.code == 2
    assert f"unrecognized arguments: {retired_option}" in capsys.readouterr().err


def test_main_has_no_console_configuration_dependency() -> None:
    source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    for retired_surface in (
        "DevelopmentConsoleConfig",
        "observe_each_turn",
        "use_lifecycle",
        "args.observe",
        "args.no_lifecycle",
        '"--observe"',
        '"--no-lifecycle"',
    ):
        assert retired_surface not in source


def test_config_path_remains_a_neutral_maintenance_input() -> None:
    args = main.build_parser().parse_args(["--config", "personal-config.json"])

    assert args.config == "personal-config.json"
    assert main.build_parser().parse_args(["--doctor"]).doctor is True
    assert main.build_parser().parse_args(["--setup"]).setup is True


def test_legacy_configuration_and_bridge_are_physically_absent() -> None:
    legacy_config = (
        PROJECT_ROOT / "app" / "development_console.py"
    ).read_text(encoding="utf-8")
    legacy_bridge = PROJECT_ROOT / "app" / "legacy_console_compatibility.py"

    assert "class DevelopmentConsoleConfig" not in legacy_config
    assert not legacy_bridge.exists()


def test_retirement_document_records_production_config_decoupling() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Production configuration decoupling" in document
    assert "no longer accepts `--observe` or `--no-lifecycle`" in document
    assert "legacy compatibility module" in document
    assert "physically removed" in document
