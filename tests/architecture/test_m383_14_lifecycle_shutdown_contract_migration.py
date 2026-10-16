from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_m224_5_no_longer_imports_historical_console_adapter() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m224_5_graceful_runtime_shutdown.py"
    ).read_text(encoding="utf-8")

    assert "LocalConversationConsole" not in source
    assert "local_conversation_entrypoint" not in source


def test_exit_commands_are_owned_by_independent_input_boundary() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m224_5_graceful_runtime_shutdown.py"
    ).read_text(encoding="utf-8")

    assert "ConsoleInputBoundary" in source
    assert "ConsoleInputKind.EXIT" in source
    assert "boundary.forward" in source


def test_lease_release_is_certified_on_lifecycle_authority() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m224_5_graceful_runtime_shutdown.py"
    ).read_text(encoding="utf-8")

    assert "LongLivedRuntimeLifecycle" in source
    assert "managed.stop()" in source
    assert "not lease_path.exists()" in source


def test_desktop_runtime_owns_service_startup_and_shutdown() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_m224_5_graceful_runtime_shutdown.py"
    ).read_text(encoding="utf-8")

    assert "DesktopPersonalRuntime" in source
    assert "desktop.start()" in source
    assert "desktop.stop()" in source
    assert "stop:lifecycle" in source


def test_no_historical_console_importers_remain() -> None:
    importers = [
        path
        for path in (PROJECT_ROOT / "tests").glob("test_*.py")
        if "from app.local_conversation_entrypoint import LocalConversationConsole"
        in path.read_text(encoding="utf-8")
    ]

    assert importers == []


def test_retirement_document_records_lifecycle_shutdown_migration() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Lifecycle and shutdown contract migration" in document
    assert "LongLivedRuntimeLifecycle" in document
    assert "DesktopPersonalRuntime" in document
    assert "no historical suite" in document
