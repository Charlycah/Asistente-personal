from __future__ import annotations

from pathlib import Path

import pytest

import main

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_console_option_is_rejected_before_activation(monkeypatch, capsys) -> None:
    activated: list[str] = []
    monkeypatch.setattr(
        main,
        "activate_roby_config",
        lambda path: activated.append("config"),
    )
    monkeypatch.setattr(
        main,
        "activate_credentials",
        lambda: activated.append("credentials"),
    )

    with pytest.raises(SystemExit) as captured:
        main.main(["--console"])
    assert captured.value.code == 2
    assert activated == []
    assert "unrecognized arguments: --console" in capsys.readouterr().err


def test_main_contains_no_embedded_console_compatibility() -> None:
    source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    assert "--console" not in source
    assert "args.console" not in source
    assert "run_embedded_console_compatibility" not in source
    assert "LocalConversationConsole" not in source


def test_desktop_has_no_access_to_embedded_console_compatibility() -> None:
    for relative in (
        "app/desktop_bootstrap.py",
        "app/desktop_ui.py",
        "app/runtime_ui_adapter.py",
        "app/unified_brain.py",
    ):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "--console" not in source
        assert "LocalConversationConsole" not in source


def test_maintenance_commands_are_not_part_of_console_deactivation() -> None:
    parser = main.build_parser()

    assert parser.parse_args(["--doctor"]).doctor is True
    assert parser.parse_args(["--setup"]).setup is True


def test_retirement_document_declares_command_line_deactivation() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "no longer starts an interactive conversation" in document
    assert "before configuration, credentials" in document
