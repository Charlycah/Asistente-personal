from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

from core.daily_briefing import BriefingPeriod, DailyBriefing, DailyBriefingSignal
from core.document_inbox import (
    DocumentCategory,
    DocumentMetadata,
    DocumentRecord,
    DocumentStatus,
)
from core.governed_reasoning import (
    DocumentEvidenceAdapter,
    EvidenceBundle,
    EvidenceKind,
    EvidenceReference,
    EvidenceRegistry,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
)
from core.household_memory import (
    HouseholdMemoryCategory,
    HouseholdMemoryEntry,
    HouseholdMemoryOwner,
    HouseholdMemoryStatus,
)
from core.personal_knowledge_base import (
    KnowledgeItem,
    KnowledgeKind,
    KnowledgeOwner,
    KnowledgeSource,
    KnowledgeStatus,
)
from core.task_intelligence import Task, TaskOrigin, TaskOwner, TaskStatus

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)
HASH = sha256(b"evidence").hexdigest()


def test_reference_requires_source_id() -> None:
    with pytest.raises(ValueError):
        EvidenceReference(
            source_type=EvidenceSourceType.DOCUMENT,
            source_id="",
            kind=EvidenceKind.DOCUMENT,
            owner="shared",
            status=EvidenceStatus.ACTIVE,
            sensitivity=EvidenceSensitivity.PERSONAL,
            observed_at=NOW,
            fingerprint=HASH,
            summary="Documento",
        )


def test_reference_requires_aware_timestamps() -> None:
    with pytest.raises(ValueError):
        EvidenceReference(
            source_type=EvidenceSourceType.DOCUMENT,
            source_id="doc-1",
            kind=EvidenceKind.DOCUMENT,
            owner="shared",
            status=EvidenceStatus.ACTIVE,
            sensitivity=EvidenceSensitivity.PERSONAL,
            observed_at=datetime(2026, 7, 10),
            fingerprint=HASH,
            summary="Documento",
        )


def test_reference_requires_sha256_fingerprint() -> None:
    with pytest.raises(ValueError):
        EvidenceReference(
            source_type=EvidenceSourceType.DOCUMENT,
            source_id="doc-1",
            kind=EvidenceKind.DOCUMENT,
            owner="shared",
            status=EvidenceStatus.ACTIVE,
            sensitivity=EvidenceSensitivity.PERSONAL,
            observed_at=NOW,
            fingerprint="not-a-hash",
            summary="Documento",
        )


def test_reference_id_is_stable() -> None:
    first = _reference("doc-1")
    second = _reference("doc-1")
    assert first.evidence_id == second.evidence_id
    assert len(first.evidence_id) == 64


def test_reference_rejects_inconsistent_explicit_id() -> None:
    with pytest.raises(ValueError):
        EvidenceReference(
            source_type=EvidenceSourceType.DOCUMENT,
            source_id="doc-1",
            kind=EvidenceKind.DOCUMENT,
            owner="shared",
            status=EvidenceStatus.ACTIVE,
            sensitivity=EvidenceSensitivity.PERSONAL,
            observed_at=NOW,
            fingerprint=HASH,
            summary="Documento",
            evidence_id="0" * 64,
        )


def test_bundle_rejects_duplicate_references() -> None:
    reference = _reference("doc-1")
    with pytest.raises(ValueError):
        EvidenceBundle((reference, reference), created_at=NOW)


def test_bundle_orders_references_deterministically() -> None:
    bundle = EvidenceBundle(
        (_reference("z"), _reference("a")),
        created_at=NOW,
    )
    assert [item.source_id for item in bundle.references] == ["a", "z"]


def test_household_memory_is_normalized_with_household_sensitivity() -> None:
    entry = HouseholdMemoryEntry(
        title="Garantía heladera",
        details="Vence en agosto",
        category=HouseholdMemoryCategory.WARRANTY,
        owner=HouseholdMemoryOwner.SHARED,
        status=HouseholdMemoryStatus.ACTIVE,
        due_at=NOW + timedelta(days=30),
        created_at=NOW,
        updated_at=NOW,
        entry_id="household-1",
    )
    reference = EvidenceRegistry().normalize(entry)
    assert reference.normalized_source_type is EvidenceSourceType.HOUSEHOLD_MEMORY
    assert reference.normalized_sensitivity is EvidenceSensitivity.HOUSEHOLD
    assert reference.valid_until == entry.due_at
    assert reference.source_id == entry.entry_id


def test_medical_document_is_never_downgraded_from_sensitive() -> None:
    record = _document(category=DocumentCategory.MEDICAL)
    reference = DocumentEvidenceAdapter().adapt(record)
    assert reference.normalized_sensitivity is EvidenceSensitivity.SENSITIVE
    assert reference.fingerprint == record.effective_hash


def test_archived_document_preserves_archived_status() -> None:
    record = _document(status=DocumentStatus.ARCHIVED)
    reference = EvidenceRegistry().normalize(record)
    assert reference.normalized_status is EvidenceStatus.ARCHIVED


def test_knowledge_draft_requires_review() -> None:
    item = KnowledgeItem(
        title="Dato pendiente",
        content="Debe verificarse",
        kind=KnowledgeKind.FACT,
        source=KnowledgeSource.MANUAL_ENTRY,
        owner=KnowledgeOwner.CARLOS,
        status=KnowledgeStatus.DRAFT,
        created_at=NOW,
        updated_at=NOW,
        item_id="knowledge-1",
    )
    reference = EvidenceRegistry().normalize(item)
    assert reference.normalized_status is EvidenceStatus.REVIEW_REQUIRED
    assert dict(reference.metadata)["kind"] == "fact"


def test_superseded_knowledge_preserves_status() -> None:
    item = KnowledgeItem(
        title="Dato viejo",
        content="Contenido anterior",
        kind=KnowledgeKind.NOTE,
        source=KnowledgeSource.MANUAL_ENTRY,
        status=KnowledgeStatus.SUPERSEDED,
        superseded_by="knowledge-2",
        created_at=NOW,
        updated_at=NOW,
        item_id="knowledge-1",
    )
    reference = EvidenceRegistry().normalize(item)
    assert reference.normalized_status is EvidenceStatus.SUPERSEDED


def test_blocked_task_requires_review() -> None:
    task = Task(
        title="Trámite",
        description="Esperar documentación",
        owner=TaskOwner.CARLOS,
        origin=TaskOrigin.DOCUMENT,
        status=TaskStatus.BLOCKED,
        created_at=NOW,
        updated_at=NOW,
        task_id="task-1",
    )
    reference = EvidenceRegistry().normalize(task)
    assert reference.normalized_kind is EvidenceKind.TASK_STATE
    assert reference.normalized_status is EvidenceStatus.REVIEW_REQUIRED
    assert reference.owner == "carlos"


def test_completed_task_preserves_completion_status() -> None:
    task = Task(
        title="Trámite",
        description="Finalizado",
        status=TaskStatus.COMPLETED,
        created_at=NOW,
        updated_at=NOW,
        completed_at=NOW,
        task_id="task-1",
    )
    reference = EvidenceRegistry().normalize(task)
    assert reference.normalized_status is EvidenceStatus.COMPLETED


def test_daily_briefing_is_marked_as_derived_summary() -> None:
    briefing = DailyBriefing(
        period=BriefingPeriod.MORNING,
        owner=TaskOwner.SHARED,
        items=(),
        signals=(DailyBriefingSignal.EMPTY,),
        generated_at=NOW,
        briefing_id="briefing-1",
    )
    reference = EvidenceRegistry().normalize(briefing)
    assert reference.normalized_kind is EvidenceKind.SUMMARY
    assert dict(reference.metadata)["derived_summary"] == "true"


def test_registry_rejects_unsupported_source() -> None:
    with pytest.raises(TypeError):
        EvidenceRegistry().normalize(object())


def test_registry_rejects_duplicate_source_type_adapters() -> None:
    adapter = DocumentEvidenceAdapter()
    with pytest.raises(ValueError):
        EvidenceRegistry((adapter, adapter))


def test_registry_can_resolve_original_source_without_copying_it() -> None:
    record = _document()
    registry = EvidenceRegistry()
    reference = registry.normalize(record)
    assert registry.resolve_source(reference) is record


def test_registry_deduplicates_same_source_version_in_bundle() -> None:
    record = _document()
    registry = EvidenceRegistry()
    bundle = registry.normalize_many((record, record), now=NOW)
    assert len(bundle.references) == 1
    assert len(registry.list_all()) == 1


def test_registry_rejects_naive_bundle_timestamp() -> None:
    with pytest.raises(ValueError):
        EvidenceRegistry().normalize_many((), now=datetime(2026, 7, 10))


def test_serialization_keeps_provenance_fields() -> None:
    payload = EvidenceRegistry().normalize(_document()).to_dict()
    assert payload["source_type"] == "document"
    assert payload["source_id"] == "document-1"
    assert payload["metadata"]["source_name"] == "test.txt"


def _reference(source_id: str) -> EvidenceReference:
    return EvidenceReference(
        source_type=EvidenceSourceType.DOCUMENT,
        source_id=source_id,
        kind=EvidenceKind.DOCUMENT,
        owner="shared",
        status=EvidenceStatus.ACTIVE,
        sensitivity=EvidenceSensitivity.PERSONAL,
        observed_at=NOW,
        fingerprint=HASH,
        summary="Documento de prueba",
    )


def _document(
    *,
    category: DocumentCategory = DocumentCategory.NOTE,
    status: DocumentStatus = DocumentStatus.INGESTED,
) -> DocumentRecord:
    return DocumentRecord(
        metadata=DocumentMetadata(
            title="Documento de prueba",
            source_name="test.txt",
            issued_at=NOW,
            expires_at=NOW + timedelta(days=30),
        ),
        content="Contenido verificable",
        category=category,
        status=status,
        created_at=NOW,
        updated_at=NOW,
        document_id="document-1",
    )
