from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_m182_observability_no_longer_imports_historical_adapter() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m182_development_console_observability.py"
    ).read_text(encoding="utf-8")

    assert "LocalConversationConsole" not in source
    assert "local_conversation_entrypoint" not in source


def test_independent_observer_retains_metadata_and_privacy_evidence() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m182_development_console_observability.py"
    ).read_text(encoding="utf-8")

    assert "DevelopmentConsoleObserver" in source
    assert "DevelopmentConsoleRenderer" in source
    assert "does_not_render_conversation_text" in source
    assert "does_not_call_provider_again" in source


def test_retired_terminal_diagnostic_commands_are_archived() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m182_development_console_observability.py"
    ).read_text(encoding="utf-8")

    for retired_command_test in (
        "test_console_status_command",
        "test_console_last_reports",
        "test_console_trace_command",
        "test_console_can_observe_each_turn",
    ):
        assert retired_command_test not in source


def test_desktop_diagnostics_use_unified_brain_metadata_only() -> None:
    source = (
        PROJECT_ROOT
        / "tests"
        / "architecture"
        / "test_m383_2_desktop_diagnostic_migration.py"
    ).read_text(encoding="utf-8")

    assert "desktop.diagnostics" in source
    assert "fully_observed" in source
    assert "never_contains_conversation_content" in source
    assert "DevelopmentConsoleObserver" in source
    assert 'assert "DevelopmentConsoleObserver" not in source' in source


def test_no_historical_console_importers_remain() -> None:
    importers = [
        path
        for path in (PROJECT_ROOT / "tests").glob("test_*.py")
        if "from app.local_conversation_entrypoint import LocalConversationConsole"
        in path.read_text(encoding="utf-8")
    ]

    assert importers == []


def test_retirement_document_records_observability_migration() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Observability contract migration" in document
    assert "Seven terminal-command tests" in document
    assert "no historical suite" in document
    assert "prompt-reveal behavior remains retired" in document
