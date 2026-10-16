from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_local_conversation_factory_has_a_dedicated_module() -> None:
    source = (
        PROJECT_ROOT / "app" / "local_conversation_factory.py"
    ).read_text(encoding="utf-8")

    assert "def build_local_conversation_from_environment" in source
    assert "EndToEndLocalConversation(" in source
    assert "class LocalConversationConsole" not in source


def test_console_module_is_physically_absent() -> None:
    assert not (PROJECT_ROOT / "app" / "local_conversation_entrypoint.py").exists()


def test_official_runtime_imports_the_ui_independent_factory() -> None:
    source = (
        PROJECT_ROOT / "app" / "official_runtime_composition.py"
    ).read_text(encoding="utf-8")

    assert "from .local_conversation_factory import" in source
    assert "from .local_conversation_entrypoint import" not in source


def test_execution_inventory_declares_the_new_canonical_factory_path() -> None:
    source = (
        PROJECT_ROOT / "app" / "runtime_execution_inventory.py"
    ).read_text(encoding="utf-8")

    assert "app.local_conversation_factory:" in source
    assert "app.local_conversation_entrypoint:" not in source


def test_no_compatibility_alias_recreates_the_old_factory_path() -> None:
    for relative in (
        "app/local_conversation_factory.py",
        "app/official_runtime_composition.py",
    ):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "local_conversation_entrypoint import build_local" not in source


def test_retirement_document_records_factory_separation() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Local-conversation factory separation" in document
    assert "local_conversation_factory.py" in document
    assert "no compatibility alias" in document
