from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_reserved_input_authority_is_independent_from_console_adapter() -> None:
    source = (PROJECT_ROOT / "app" / "console_input.py").read_text(encoding="utf-8")

    assert "class ConsoleInputBoundary" in source
    assert "ConsoleInputKind.CONVERSATION" in source
    assert "LocalConversationConsole" not in source


def test_independent_boundary_survives_historical_adapter_removal() -> None:
    source = (PROJECT_ROOT / "app" / "console_input.py").read_text(encoding="utf-8")

    assert not (PROJECT_ROOT / "app" / "local_conversation_entrypoint.py").exists()
    assert "class ConsoleInputBoundary" in source
    assert "def classify" in source
    assert "def forward" in source


def test_reserved_input_suite_no_longer_imports_console_adapter() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m225_4_reserved_console_input.py"
    ).read_text(encoding="utf-8")

    assert "ConsoleInputBoundary" in source
    assert "LocalConversationConsole" not in source
    assert "local_conversation_entrypoint" not in source


def test_boundary_refuses_every_non_conversation_classification() -> None:
    source = (PROJECT_ROOT / "app" / "console_input.py").read_text(encoding="utf-8")

    assert "parsed.kind is not ConsoleInputKind.CONVERSATION" in source
    assert "return None" in source


def test_no_historical_console_importers_remain() -> None:
    importers = [
        path
        for path in (PROJECT_ROOT / "tests").glob("test_*.py")
        if "from app.local_conversation_entrypoint import LocalConversationConsole"
        in path.read_text(encoding="utf-8")
    ]

    assert importers == []


def test_retirement_document_records_reserved_input_migration() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Reserved-input boundary migration" in document
    assert "ConsoleInputBoundary" in document
    assert "five historical suites" in document
