from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_CONSOLE_TESTS: set[str] = set()


def test_historical_console_adapter_has_no_production_importers() -> None:
    for package in ("app", "application", "core", "domain", "infrastructure"):
        for path in (PROJECT_ROOT / package).rglob("*.py"):
            if path.name == "local_conversation_entrypoint.py":
                continue
            source = path.read_text(encoding="utf-8")
            assert "from app.local_conversation_entrypoint import" not in source
            assert "import app.local_conversation_entrypoint" not in source


def test_console_adapter_has_no_remaining_test_suite_importers() -> None:
    importers = {
        path.name
        for path in (PROJECT_ROOT / "tests").glob("test_*.py")
        if "from app.local_conversation_entrypoint import LocalConversationConsole"
        in path.read_text(encoding="utf-8")
    }

    assert importers == HISTORICAL_CONSOLE_TESTS


def test_console_input_policy_is_an_independent_component() -> None:
    source = (PROJECT_ROOT / "app" / "console_input.py").read_text(encoding="utf-8")

    assert "class ConsoleInputParser" in source
    assert "LocalConversationConsole" not in source
    assert "local_conversation_entrypoint" not in source


def test_process_inventory_no_longer_calls_main_a_development_console() -> None:
    source = (
        PROJECT_ROOT / "app" / "runtime_execution_inventory.py"
    ).read_text(encoding="utf-8")

    assert 'key="roby_process_entrypoint"' in source
    assert 'key="development_console"' not in source
    assert "Único punto de entrada de proceso para ROBY Desktop." in source


def test_desktop_replacements_for_diagnostics_and_lifecycle_are_certified() -> None:
    diagnostics = (
        PROJECT_ROOT
        / "tests"
        / "architecture"
        / "test_m383_2_desktop_diagnostic_migration.py"
    ).read_text(encoding="utf-8")
    lifecycle = (
        PROJECT_ROOT / "tests" / "test_m235_unified_desktop_personal_runtime.py"
    ).read_text(encoding="utf-8")

    assert "desktop.diagnostics" in diagnostics
    assert "desktop_already_owns_residents_and_lifecycle" in diagnostics
    assert "starts_and_stops_official_services" in lifecycle


def test_retirement_document_classifies_every_remaining_contract_group() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Remaining console-contract inventory" in document
    for contract in (
        "Input classification",
        "Conversation routing",
        "Diagnostics",
        "Lifecycle and shutdown",
        "Rendering",
    ):
        assert contract in document
    assert "no historical suite" in document
