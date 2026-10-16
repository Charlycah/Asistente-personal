from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_obsolete_compatibility_bridge_is_physically_absent() -> None:
    assert not (PROJECT_ROOT / "app" / "legacy_console_compatibility.py").exists()


def test_obsolete_console_configuration_is_physically_absent() -> None:
    source = (
        PROJECT_ROOT / "app" / "development_console.py"
    ).read_text(encoding="utf-8")

    assert "class DevelopmentConsoleConfig" not in source
    assert "def banner" not in source
    assert "observe_each_turn" not in source
    assert "use_lifecycle" not in source


def test_no_python_module_imports_the_removed_bridge() -> None:
    paths = [PROJECT_ROOT / "main.py"]
    for package in ("app", "application", "core", "domain", "infrastructure"):
        paths.extend((PROJECT_ROOT / package).rglob("*.py"))

    for path in paths:
        source = path.read_text(encoding="utf-8")
        assert "from app.legacy_console_compatibility import" not in source
        assert "import app.legacy_console_compatibility" not in source


def test_obsolete_bridge_behavior_tests_are_archived() -> None:
    for relative in (
        "tests/test_m221_hal_development_console.py",
        "tests/test_m228_2_gmail_startup_runtime_wiring.py",
    ):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "run_embedded_console_compatibility" not in source
        assert "DevelopmentConsoleConfig" not in source


def test_local_console_was_removed_after_separate_migration() -> None:
    assert not (PROJECT_ROOT / "app" / "local_conversation_entrypoint.py").exists()
    assert (PROJECT_ROOT / "app" / "local_conversation_factory.py").exists()


def test_retirement_document_records_bounded_physical_removal() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Physical compatibility-bridge removal" in document
    assert "Physical historical-adapter deletion" in document
    assert "separate migration" in document
