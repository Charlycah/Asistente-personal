from __future__ import annotations

import inspect
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.document_inbox import DocumentInboxManager


def _sqlite_document_repository_class():
    from infrastructure.repositories.sqlite_document_repository import (
        SQLiteDocumentRepository,
    )

    return SQLiteDocumentRepository


def test_document_repository_has_durable_sqlite_adapter() -> None:
    repository_class = _sqlite_document_repository_class()
    assert repository_class.__name__ == "SQLiteDocumentRepository"


def test_durable_repository_preserves_identity_and_provenance_across_restart(
    tmp_path: Path,
) -> None:
    repository_class = _sqlite_document_repository_class()
    db_path = tmp_path / "documents.db"
    now = datetime(2026, 9, 2, 10, 0, tzinfo=timezone.utc)

    first = DocumentInboxManager(repository=repository_class(db_path))
    record = first.ingest_text(
        "Contrato privado de prueba durable.",
        title="Contrato",
        source_name="contrato.txt",
        now=now,
    )

    restarted = DocumentInboxManager(repository=repository_class(db_path))
    restored = restarted.repository.get(record.document_id)

    assert restored is not None
    assert restored.document_id == record.document_id
    assert restored.effective_hash == record.effective_hash
    assert restored.metadata == record.metadata
    assert restored.content == record.content
    assert restored.created_at == record.created_at


def test_durable_repository_preserves_hash_deduplication_across_restart(
    tmp_path: Path,
) -> None:
    repository_class = _sqlite_document_repository_class()
    db_path = tmp_path / "documents.db"
    now = datetime(2026, 9, 2, 10, 0, tzinfo=timezone.utc)

    first = DocumentInboxManager(repository=repository_class(db_path))
    original = first.ingest_text(
        "Documento privado estable.",
        title="Primero",
        now=now,
    )

    restarted = DocumentInboxManager(repository=repository_class(db_path))
    duplicate = restarted.ingest_text(
        "Documento privado estable.",
        title="Segundo",
        now=now,
    )

    assert duplicate.document_id == original.document_id
    assert len(restarted.repository.list_all()) == 1


def test_official_runtime_exposes_document_inbox_builder() -> None:
    from app import runtime_environment_wiring

    builder = getattr(
        runtime_environment_wiring, "build_document_inbox_from_environment"
    )
    assert callable(builder)


def test_official_document_inbox_builder_uses_durable_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app import runtime_environment_wiring

    monkeypatch.setenv("ROBY_DOCUMENT_INBOX_ENABLED", "1")
    monkeypatch.setenv("ROBY_DOCUMENT_INBOX_DB_PATH", str(tmp_path / "documents.db"))
    inbox = runtime_environment_wiring.build_document_inbox_from_environment()

    assert isinstance(inbox, DocumentInboxManager)
    assert inbox.repository.__class__.__name__ == "SQLiteDocumentRepository"


def test_personal_knowledge_builder_accepts_existing_shared_document_inbox() -> None:
    from app.runtime_environment_wiring import build_personal_knowledge_from_environment

    parameters = inspect.signature(build_personal_knowledge_from_environment).parameters
    assert "document_inbox" in parameters


def test_task_intelligence_builder_accepts_existing_shared_document_inbox() -> None:
    from app.runtime_environment_wiring import build_task_intelligence_from_environment

    parameters = inspect.signature(build_task_intelligence_from_environment).parameters
    assert "document_inbox" in parameters


def test_same_document_inbox_instance_is_injected_into_existing_consumers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app import runtime_environment_wiring

    monkeypatch.setenv("ROBY_DOCUMENT_INBOX_ENABLED", "1")
    monkeypatch.setenv(
        "ROBY_DOCUMENT_INBOX_DB_PATH", str(tmp_path / "documents.db")
    )
    monkeypatch.setenv(
        "ROBY_PERSONAL_KNOWLEDGE_DB_PATH", str(tmp_path / "knowledge.db")
    )
    monkeypatch.setenv("ROBY_TASK_DB_PATH", str(tmp_path / "tasks.db"))

    inbox = runtime_environment_wiring.build_document_inbox_from_environment()
    knowledge_port = (
        runtime_environment_wiring.build_personal_knowledge_from_environment(
            document_inbox=inbox
        )
    )
    task_port = runtime_environment_wiring.build_task_intelligence_from_environment(
        document_inbox=inbox
    )

    knowledge_manager = knowledge_port.manager
    task_manager = task_port.manager
    assert knowledge_manager.document_inbox is inbox
    assert task_manager.document_inbox is inbox


def test_contract_does_not_introduce_parallel_document_authority() -> None:
    import core.document_inbox as document_inbox

    source = inspect.getsource(document_inbox)
    assert source.count("class DocumentInboxManager") == 1
    assert "PersonalDocumentsManager" not in source
    assert "DocumentSourceManager" not in source
