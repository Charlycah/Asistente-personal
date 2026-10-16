from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_m180_no_longer_imports_historical_console_adapter() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m180_end_to_end_local_conversation.py"
    ).read_text(encoding="utf-8")

    assert "LocalConversationConsole" not in source
    assert "local_conversation_entrypoint" not in source


def test_completed_turn_presentation_uses_productive_desktop_adapter() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m180_end_to_end_local_conversation.py"
    ).read_text(encoding="utf-8")

    assert "LocalConversationUIAdapter(item)" in source
    assert "ConversationOrigin.DESKTOP_TEXT" in source
    assert 'response.status == "completed"' in source


def test_blank_and_failed_output_contracts_use_desktop_adapter() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m180_end_to_end_local_conversation.py"
    ).read_text(encoding="utf-8")

    assert "rejects_blank_text_without_starting_runtime" in source
    assert 'response.status == "needs_information"' in source
    assert "non_deliverable_desktop_output_is_explicit" in source
    assert 'response.text == "[failed]"' in source


def test_terminal_eof_and_render_tests_are_archived() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m180_end_to_end_local_conversation.py"
    ).read_text(encoding="utf-8")

    assert "test_console_stops_on_eof" not in source
    assert "test_non_deliverable_console_output" not in source
    assert "read=lambda" not in source


def test_no_test_suite_imports_historical_console_adapter() -> None:
    importers = [
        path
        for path in (PROJECT_ROOT / "tests").glob("test_*.py")
        if "from app.local_conversation_entrypoint import LocalConversationConsole"
        in path.read_text(encoding="utf-8")
    ]

    assert importers == []


def test_retirement_document_records_final_suite_migration() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")
    normalized_document = " ".join(document.split())

    assert "Final console-suite migration" in document
    assert "no historical suite" in document
    assert "physical adapter deletion" in normalized_document
