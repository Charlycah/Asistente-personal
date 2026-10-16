from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_m186_no_longer_imports_historical_console_adapter() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m186_operational_runtime_consolidation.py"
    ).read_text(encoding="utf-8")

    assert "LocalConversationConsole" not in source
    assert "local_conversation_entrypoint" not in source


def test_tool_command_crossing_is_owned_by_input_boundary() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m186_operational_runtime_consolidation.py"
    ).read_text(encoding="utf-8")

    assert "ConsoleInputBoundary" in source
    assert "ConsoleInputKind.CONVERSATION" in source
    assert "boundary.forward" in source


def test_non_tool_commands_are_blocked_by_input_boundary() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m186_operational_runtime_consolidation.py"
    ).read_text(encoding="utf-8")

    assert 'boundary.classify("/status")' in source
    assert "ConsoleInputKind.COMMAND" in source
    assert "assert result is None" in source


def test_supervisor_and_lease_tests_remain_independent() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m186_operational_runtime_consolidation.py"
    ).read_text(encoding="utf-8")

    assert "RuntimeHeartbeatSupervisor" in source
    assert "RuntimeLeaseError" in source
    assert "private_file_is_protected" in source


def test_no_suite_imports_historical_console_adapter() -> None:
    importers = [
        path.name
        for path in (PROJECT_ROOT / "tests").glob("test_*.py")
        if "from app.local_conversation_entrypoint import LocalConversationConsole"
        in path.read_text(encoding="utf-8")
    ]

    assert importers == []


def test_retirement_document_records_operational_input_migration() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Operational input contract migration" in document
    assert "no historical suite" in document
    assert "empty terminal prompt" in document
