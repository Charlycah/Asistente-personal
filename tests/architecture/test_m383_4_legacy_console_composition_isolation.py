from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_main_no_longer_owns_console_runtime_composition() -> None:
    source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    for retired_detail in (
        "build_battery_awareness_from_environment",
        "build_reminder_awareness_from_environment",
        "def _runtime_owner",
    ):
        assert retired_detail not in source
    assert "from app.official_runtime_composition import" not in source
    assert "LEGACY_CONSOLE_CERTIFICATION_MARKERS" not in source
    assert "run_embedded_console_compatibility" not in source


def test_retired_composition_module_has_been_physically_removed() -> None:
    assert not (PROJECT_ROOT / "app" / "legacy_console_compatibility.py").exists()


def test_desktop_and_brain_cannot_import_legacy_console_compatibility() -> None:
    for relative in (
        "app/desktop_bootstrap.py",
        "app/desktop_ui.py",
        "app/runtime_ui_adapter.py",
        "app/unified_brain.py",
    ):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "legacy_console_compatibility" not in source


def test_main_does_not_import_legacy_compatibility_module() -> None:
    source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    assert "--console" not in source
    assert "legacy_console_compatibility" not in source


def test_legacy_module_removal_is_documented() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Physical compatibility-bridge removal" in document
    assert "physically removed" in document
