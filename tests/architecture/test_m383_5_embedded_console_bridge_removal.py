from __future__ import annotations

from pathlib import Path

import pytest

import main

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_explicit_programmatic_console_request_is_rejected(capsys) -> None:
    with pytest.raises(SystemExit) as captured:
        main.main(["--console"])
    assert captured.value.code == 2
    assert "unrecognized arguments: --console" in capsys.readouterr().err


def test_main_has_no_console_builders_factories_or_announcers() -> None:
    source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    for retired_name in (
        "LocalConversationConsole",
        "build_local_conversation_from_environment",
        "announce_gmail_startup_from_environment",
        "run_embedded_console_compatibility",
        "legacy_console_compatibility",
    ):
        assert retired_name not in source


def test_historical_tests_no_longer_target_the_removed_library() -> None:
    for relative in (
        "tests/test_m221_hal_development_console.py",
        "tests/test_m228_2_gmail_startup_runtime_wiring.py",
    ):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "run_embedded_console_compatibility" not in source
        assert "legacy_console_compatibility" not in source
        assert 'main.main(["--console"' not in source


def test_desktop_and_main_have_no_legacy_compatibility_dependency() -> None:
    for relative in (
        "main.py",
        "app/desktop_bootstrap.py",
        "app/desktop_ui.py",
        "app/runtime_ui_adapter.py",
        "app/unified_brain.py",
    ):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "legacy_console_compatibility" not in source


def test_retirement_document_declares_no_remaining_entrypoint_bridge() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "there is no remaining production bridge" in document
    assert "physically removed" in document
