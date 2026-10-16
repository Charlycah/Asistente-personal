from datetime import datetime, timedelta, timezone

import pytest

from core.document_inbox import (
    DocumentCategory,
    DocumentClassifier,
    DocumentInboxManager,
    DocumentMetadata,
    DocumentRecord,
    DocumentSignal,
    DocumentStatus,
    InMemoryDocumentRepository,
)
from core.household_memory import HouseholdMemoryManager

NOW = datetime(2026, 7, 10, 15, 0, tzinfo=timezone.utc)


def test_metadata_normalizes_tags_and_validates_timestamps() -> None:
    metadata = DocumentMetadata(
        title="Garantía del calefón",
        source_name="garantia.txt",
        tags=("Casa", "garantía", "Casa"),
    )

    assert metadata.normalized_tags == ("casa", "garantía")
    with pytest.raises(ValueError):
        DocumentMetadata(
            title="Documento",
            source_name="documento.txt",
            issued_at=datetime(2026, 7, 10, 15, 0),
        )


def test_record_computes_stable_sha256_hash() -> None:
    record = DocumentRecord(
        metadata=DocumentMetadata(title="Nota", source_name="nota.txt"),
        content="Contenido estable",
        category=DocumentCategory.NOTE,
        created_at=NOW,
        updated_at=NOW,
    )

    assert len(record.effective_hash) == 64
    assert record.to_dict()["content_hash"] == record.effective_hash


def test_classifier_assigns_known_and_unknown_categories() -> None:
    classifier = DocumentClassifier()

    assert (
        classifier.classify("Garantía", "Service oficial por dos años")
        is DocumentCategory.WARRANTY
    )
    assert classifier.classify("Misceláneo", "Texto neutro") is DocumentCategory.OTHER


def test_repository_saves_finds_hash_and_lists_records() -> None:
    repository = InMemoryDocumentRepository()
    record = DocumentRecord(
        metadata=DocumentMetadata(title="Manual", source_name="manual.txt"),
        content="Manual de instrucciones",
        category=DocumentCategory.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )

    repository.save(record)

    assert repository.get(record.document_id) is record
    assert repository.get_by_hash(record.effective_hash) is record
    assert repository.list_all() == (record,)


def test_manager_ingests_classifies_and_recalls_text() -> None:
    manager = DocumentInboxManager()

    record = manager.ingest_text(
        "Garantía y service oficial del calefón.",
        title="Garantía del calefón",
        source_name="garantia.txt",
        tags=("casa",),
        now=NOW,
    )

    assert record.normalized_category is DocumentCategory.WARRANTY
    assert manager.recall("calefón") == (record,)
    assert DocumentSignal.DOCUMENT_INGESTED in manager.snapshot(now=NOW).signals


def test_manager_deduplicates_documents_by_content_hash() -> None:
    manager = DocumentInboxManager()

    first = manager.ingest_text("Contenido único", title="Primero", now=NOW)
    second = manager.ingest_text("Contenido único", title="Segundo", now=NOW)

    assert second.document_id == first.document_id
    assert manager.snapshot(now=NOW).total_documents == 1


def test_manager_blocks_financial_documents() -> None:
    manager = DocumentInboxManager()

    with pytest.raises(PermissionError):
        manager.ingest_text(
            "Transferencia bancaria desde la billetera para pagar una compra.",
            title="Operación financiera",
            now=NOW,
        )


def test_manager_marks_sensitive_documents_for_review() -> None:
    manager = DocumentInboxManager()

    record = manager.ingest_text(
        "Receta médica con dosis del tratamiento.",
        title="Indicaciones médicas",
        now=NOW,
    )

    assert record.normalized_status is DocumentStatus.REVIEW_REQUIRED
    assert manager.snapshot(now=NOW).review_required == 1


def test_manager_ingests_supported_text_path(tmp_path) -> None:
    source = tmp_path / "manual.md"
    source.write_text("# Manual\nInstrucciones del equipo", encoding="utf-8")
    manager = DocumentInboxManager()

    record = manager.ingest_path(source, now=NOW)

    assert record.metadata.source_name == "manual.md"
    assert record.metadata.media_type == "text/markdown"
    assert record.normalized_category is DocumentCategory.MANUAL


def test_manager_rejects_missing_and_unsupported_paths(tmp_path) -> None:
    manager = DocumentInboxManager()

    with pytest.raises(FileNotFoundError):
        manager.ingest_path(tmp_path / "missing.txt", now=NOW)
    binary = tmp_path / "scan.pdf"
    binary.write_bytes(b"%PDF")
    with pytest.raises(ValueError):
        manager.ingest_path(binary, now=NOW)


def test_manager_links_document_to_household_memory() -> None:
    household = HouseholdMemoryManager()
    manager = DocumentInboxManager(household_memory=household)

    record = manager.ingest_text(
        "Garantía del producto por dos años.",
        title="Garantía del calefón",
        source_name="garantia.txt",
        expires_at=NOW + timedelta(days=30),
        link_household_memory=True,
        now=NOW,
    )

    assert record.linked_household_entry_id is not None
    memories = household.recall("Garantía del calefón")
    assert len(memories) == 1
    assert memories[0].due_at == NOW + timedelta(days=30)


def test_manager_archives_and_filters_records() -> None:
    manager = DocumentInboxManager()
    record = manager.ingest_text(
        "Manual de instrucciones.",
        title="Manual",
        now=NOW,
    )

    archived = manager.archive(record.document_id, now=NOW + timedelta(minutes=1))

    assert archived.normalized_status is DocumentStatus.ARCHIVED
    assert manager.recall(status=DocumentStatus.ARCHIVED) == (archived,)


def test_snapshot_exposes_prompt_summary() -> None:
    manager = DocumentInboxManager()
    manager.ingest_text(
        "Manual de instrucciones.",
        title="Manual del equipo",
        now=NOW,
    )

    prompt = "\n".join(manager.snapshot(now=NOW).system_prompt_lines())

    assert "Document Inbox M73" in prompt
    assert "Manual del equipo" in prompt


def test_manager_rejects_invalid_limits_and_unknown_ids() -> None:
    with pytest.raises(ValueError):
        DocumentInboxManager(recent_limit=0)

    manager = DocumentInboxManager()
    with pytest.raises(KeyError):
        manager.archive("missing", now=NOW)
