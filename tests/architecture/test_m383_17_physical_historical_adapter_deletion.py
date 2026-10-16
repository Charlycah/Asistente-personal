from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_historical_console_adapter_is_physically_absent() -> None:
    assert not (PROJECT_ROOT / "app" / "local_conversation_entrypoint.py").exists()


def test_no_production_module_references_removed_adapter() -> None:
    for package in ("app", "application", "core", "domain", "infrastructure"):
        for path in (PROJECT_ROOT / package).rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            assert "local_conversation_entrypoint" not in source
            assert "LocalConversationConsole" not in source


def test_conversation_factory_and_official_composition_remain_connected() -> None:
    factory = (
        PROJECT_ROOT / "app" / "local_conversation_factory.py"
    ).read_text(encoding="utf-8")
    composition = (
        PROJECT_ROOT / "app" / "official_runtime_composition.py"
    ).read_text(encoding="utf-8")

    assert "def build_local_conversation_from_environment" in factory
    assert "from .local_conversation_factory import" in composition


def test_migrated_input_and_observability_components_remain_present() -> None:
    assert (PROJECT_ROOT / "app" / "console_input.py").exists()
    assert (
        PROJECT_ROOT / "core" / "development_console_observability"
    ).is_dir()


def test_current_refinement_documents_contain_no_retired_adapter_path() -> None:
    for relative in (
        "docs/refinement/RP_18_2A_EXECUTION_ROOT_INVENTORY.md",
        "docs/refinement/RP_18_8_SINGLE_EXECUTION_CERTIFICATION.md",
    ):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert "app.local_conversation_entrypoint" not in source
        assert "LocalConversationConsole" not in source


def test_retirement_document_records_physical_adapter_deletion() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "Physical historical-adapter deletion" in document
    assert "local_conversation_entrypoint.py` was physically removed" in document
    assert "M383 console retirement is complete" in document
