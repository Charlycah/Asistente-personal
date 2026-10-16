from __future__ import annotations

from pathlib import Path

import pytest

import main

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_desktop_is_the_default_and_console_option_is_retired() -> None:
    default_args = main.build_parser().parse_args([])

    assert not hasattr(default_args, "console")
    with pytest.raises(SystemExit) as captured:
        main.build_parser().parse_args(["--console"])
    assert captured.value.code == 2


def test_main_contains_no_console_activation_branch() -> None:
    source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    assert "--console" not in source
    assert "args.console" not in source


def test_current_guides_no_longer_recommend_console_startup() -> None:
    for guide in ("ROBY_FIRST_STEPS.md", "HAL_FIRST_STEPS.md"):
        content = (PROJECT_ROOT / "docs" / "guides" / guide).read_text(encoding="utf-8")
        assert "python main.py --console" not in content
        assert "retiro controlado" in content
        assert "python main.py" in content


def test_maintenance_commands_remain_available() -> None:
    parser = main.build_parser()

    assert parser.parse_args(["--doctor"]).doctor is True
    assert parser.parse_args(["--setup"]).setup is True


def test_desktop_wiring_never_imports_the_historical_console() -> None:
    for path in (
        PROJECT_ROOT / "app" / "desktop_bootstrap.py",
        PROJECT_ROOT / "app" / "runtime_ui_adapter.py",
        PROJECT_ROOT / "app" / "unified_brain.py",
    ):
        source = path.read_text(encoding="utf-8")
        assert "LocalConversationConsole" not in source
        assert "local_conversation_entrypoint" not in source
