from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_single_route_suite_no_longer_imports_historical_console() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_rp_18_4_single_conversation_route.py"
    ).read_text(encoding="utf-8")

    assert "LocalConversationConsole" not in source
    assert "local_conversation_entrypoint" not in source


def test_single_route_suite_targets_productive_ui_adapter() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_rp_18_4_single_conversation_route.py"
    ).read_text(encoding="utf-8")

    assert "LocalConversationUIAdapter(runtime)" in source
    assert "isinstance(adapter.runtime, OfficialConversationGateway)" in source


def test_gateway_remains_the_only_origin_tracking_boundary() -> None:
    source = (
        PROJECT_ROOT / "app" / "official_conversation_gateway.py"
    ).read_text(encoding="utf-8")

    assert "class OfficialConversationGateway" in source
    assert "last_origin" in source
    assert "submitted_turns" in source


def test_desktop_text_and_voice_share_the_same_gateway() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_rp_18_4_single_conversation_route.py"
    ).read_text(encoding="utf-8")

    assert "ConversationOrigin.DESKTOP_TEXT" in source
    assert "ConversationOrigin.DESKTOP_VOICE" in source
    assert "uses_same_gateway_with_voice_origin" in source


def test_no_historical_console_importers_remain() -> None:
    importers = [
        path
        for path in (PROJECT_ROOT / "tests").glob("test_*.py")
        if "from app.local_conversation_entrypoint import LocalConversationConsole"
        in path.read_text(encoding="utf-8")
    ]

    assert importers == []


def test_retirement_document_records_single_route_migration() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Single conversation-route migration" in document
    assert "OfficialConversationGateway" in document
    assert "no historical suite" in document
