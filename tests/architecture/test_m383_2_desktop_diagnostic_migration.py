from __future__ import annotations

from pathlib import Path

from app.desktop_ui import ROBYDesktopApp
from app.runtime_ui_adapter import (
    ConversationalPersonalityUIAdapter,
    LocalConversationUIAdapter,
    OptionalServiceGuardUIAdapter,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Turn:
    response_text = "respuesta"
    status = "completed"
    session_id = "familia"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False


class ConversationRuntimeStub:
    def converse(self, text: str) -> Turn:
        return Turn()


def _desktop() -> ROBYDesktopApp:
    adapter = ConversationalPersonalityUIAdapter(
        OptionalServiceGuardUIAdapter(
            LocalConversationUIAdapter(ConversationRuntimeStub()),
            weather_enabled=False,
        )
    )
    return ROBYDesktopApp(adapter=adapter)


def test_desktop_exposes_the_same_brain_diagnostics_through_all_adapters() -> None:
    desktop = _desktop()

    desktop.adapter.submit_text("contenido privado", session_id="familia")
    diagnostics = desktop.diagnostics

    assert diagnostics == desktop.adapter.diagnostics
    assert diagnostics is not None
    assert diagnostics.conversation.processed_messages == 1
    assert diagnostics.reflection.observed_turns == 1
    assert diagnostics.fully_observed is True


def test_desktop_diagnostics_never_contains_conversation_content() -> None:
    desktop = _desktop()

    desktop.adapter.submit_text("dato familiar reservado")

    assert "dato familiar reservado" not in repr(desktop.diagnostics)
    assert "respuesta" not in repr(desktop.diagnostics)


def test_desktop_diagnostic_path_does_not_import_console_observers() -> None:
    for relative in (
        "app/runtime_ui_adapter.py",
        "app/desktop_ui.py",
        "app/unified_brain.py",
    ):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "DevelopmentConsoleObserver" not in source
        assert "DevelopmentConsoleRenderer" not in source
        assert "reveal_prompt" not in source


def test_desktop_already_owns_residents_and_lifecycle_without_console() -> None:
    source = (PROJECT_ROOT / "app" / "desktop_bootstrap.py").read_text(
        encoding="utf-8"
    )

    for dependency in (
        "build_gmail_startup_announcer_from_environment",
        "build_battery_awareness_from_environment",
        "build_reminder_awareness_from_environment",
        "on_start=",
        "on_stop=",
    ):
        assert dependency in source
    assert "LocalConversationConsole" not in source


def test_console_prompt_reveal_is_explicitly_excluded_from_migration() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert (
        "ability to reveal provider prompts is deliberately not migrated" in document
    )
    assert "metadata-only" in document
