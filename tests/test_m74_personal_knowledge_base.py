from datetime import datetime, timedelta, timezone

import pytest

from core.document_inbox import DocumentInboxManager
from core.personal_knowledge_base import (
    InMemoryPersonalKnowledgeRepository,
    KnowledgeCandidate,
    KnowledgeItem,
    KnowledgeKind,
    KnowledgeOwner,
    KnowledgeRelation,
    KnowledgeRelationType,
    KnowledgeSignal,
    KnowledgeSource,
    KnowledgeStatus,
    PersonalKnowledgeBaseManager,
)

NOW = datetime(2026, 7, 10, 18, 0, tzinfo=timezone.utc)


def test_candidate_validates_and_normalizes_values() -> None:
    candidate = KnowledgeCandidate(
        title="Arquitectura ROBY",
        content="ROBY prioriza contratos explícitos.",
        kind=KnowledgeKind.CONCEPT,
        source=KnowledgeSource.MANUAL_ENTRY,
        tags=("ROBY", "arquitectura", "ROBY"),
        created_at=NOW,
    )

    assert candidate.normalized_tags == ("roby", "arquitectura")
    assert candidate.normalized_owner is KnowledgeOwner.SHARED
    with pytest.raises(ValueError):
        KnowledgeCandidate(
            title="Inválido",
            content="Contenido",
            kind=KnowledgeKind.NOTE,
            source=KnowledgeSource.MANUAL_ENTRY,
            confidence=1.1,
        )


def test_item_exposes_stable_fingerprint_and_dictionary() -> None:
    item = KnowledgeItem(
        title="Principio",
        content="La arquitectura debe permanecer verificable.",
        kind=KnowledgeKind.CONCLUSION,
        source=KnowledgeSource.MANUAL_ENTRY,
        created_at=NOW,
        updated_at=NOW,
    )

    assert len(item.fingerprint) == 64
    assert item.to_dict()["kind"] == "conclusion"
    assert item.to_dict()["fingerprint"] == item.fingerprint


def test_relation_rejects_self_reference() -> None:
    with pytest.raises(ValueError):
        KnowledgeRelation(
            source_item_id="same",
            target_item_id="same",
            relation_type=KnowledgeRelationType.RELATED_TO,
        )


def test_repository_stores_items_relations_and_fingerprints() -> None:
    repository = InMemoryPersonalKnowledgeRepository()
    first = KnowledgeItem(
        title="Primero",
        content="Contenido primero",
        kind=KnowledgeKind.NOTE,
        source=KnowledgeSource.MANUAL_ENTRY,
        created_at=NOW,
        updated_at=NOW,
    )
    second = KnowledgeItem(
        title="Segundo",
        content="Contenido segundo",
        kind=KnowledgeKind.NOTE,
        source=KnowledgeSource.MANUAL_ENTRY,
        created_at=NOW + timedelta(seconds=1),
        updated_at=NOW + timedelta(seconds=1),
    )
    repository.save_item(first)
    repository.save_item(second)
    relation = repository.save_relation(
        KnowledgeRelation(
            source_item_id=first.item_id,
            target_item_id=second.item_id,
            relation_type=KnowledgeRelationType.RELATED_TO,
            created_at=NOW,
        )
    )

    assert repository.get_item(first.item_id) is first
    assert repository.get_by_fingerprint(first.fingerprint) is first
    assert repository.list_items() == (first, second)
    assert repository.list_relations() == (relation,)


def test_manager_creates_and_approves_manual_knowledge() -> None:
    manager = PersonalKnowledgeBaseManager()

    item = manager.remember(
        title="Preferencia de documentación",
        content="La documentación técnica se prefiere en español.",
        kind=KnowledgeKind.PREFERENCE,
        owner=KnowledgeOwner.CARLOS,
        tags=("documentación", "idioma"),
        now=NOW,
    )

    assert item.normalized_status is KnowledgeStatus.ACTIVE
    assert manager.recall("español") == (item,)
    assert KnowledgeSignal.KNOWLEDGE_STORED in manager.snapshot(now=NOW).signals


def test_manager_requires_review_for_low_confidence_candidate() -> None:
    manager = PersonalKnowledgeBaseManager(automatic_approval_threshold=0.85)
    candidate = manager.create_candidate(
        title="Hipótesis",
        content="Este dato todavía necesita confirmación.",
        kind=KnowledgeKind.CONCLUSION,
        source=KnowledgeSource.SYSTEM_GENERATED,
        confidence=0.6,
        now=NOW,
    )

    assert candidate.requires_review is True
    with pytest.raises(PermissionError):
        manager.approve(candidate, now=NOW)
    approved = manager.approve(candidate, reviewed=True, now=NOW)
    assert approved.normalized_status is KnowledgeStatus.ACTIVE


def test_manager_blocks_financial_knowledge() -> None:
    manager = PersonalKnowledgeBaseManager()

    with pytest.raises(PermissionError):
        manager.remember(
            title="Transferencia bancaria",
            content="Mover dinero desde una billetera para pagar una compra.",
            kind=KnowledgeKind.PROCEDURE,
            now=NOW,
        )


def test_manager_deduplicates_approved_knowledge() -> None:
    manager = PersonalKnowledgeBaseManager()

    first = manager.remember(
        title="Dato estable",
        content="El mismo contenido.",
        kind=KnowledgeKind.FACT,
        now=NOW,
    )
    second = manager.remember(
        title="Dato estable",
        content="El mismo contenido.",
        kind=KnowledgeKind.FACT,
        now=NOW + timedelta(seconds=1),
    )

    assert second.item_id == first.item_id
    assert manager.snapshot(now=NOW).total_items == 1
    assert KnowledgeSignal.DUPLICATE_REUSED in manager.snapshot(now=NOW).signals


def test_manager_filters_by_kind_owner_status_and_tags() -> None:
    manager = PersonalKnowledgeBaseManager()
    item = manager.remember(
        title="Procedimiento doméstico",
        content="Revisar el manual antes de reiniciar el equipo.",
        kind=KnowledgeKind.PROCEDURE,
        owner=KnowledgeOwner.SHARED,
        tags=("equipo", "manual"),
        now=NOW,
    )
    manager.remember(
        title="Idea personal",
        content="Otra entrada diferente.",
        kind=KnowledgeKind.IDEA,
        owner=KnowledgeOwner.CARLOS,
        now=NOW,
    )

    result = manager.recall(
        kind=KnowledgeKind.PROCEDURE,
        owner=KnowledgeOwner.SHARED,
        status=KnowledgeStatus.ACTIVE,
        tags=("manual",),
    )
    assert result == (item,)


def test_manager_creates_and_queries_relations() -> None:
    manager = PersonalKnowledgeBaseManager()
    source = manager.remember(
        title="Contrato explícito",
        content="Los módulos colaboran mediante contratos.",
        kind=KnowledgeKind.CONCEPT,
        now=NOW,
    )
    target = manager.remember(
        title="Bajo acoplamiento",
        content="Los contratos reducen el acoplamiento.",
        kind=KnowledgeKind.CONCLUSION,
        now=NOW,
    )

    relation = manager.relate(
        target.item_id,
        source.item_id,
        KnowledgeRelationType.DERIVED_FROM,
        rationale="La conclusión deriva del principio.",
        now=NOW,
    )

    assert manager.relations_for(source.item_id) == (relation,)
    assert relation.normalized_type is KnowledgeRelationType.DERIVED_FROM


def test_manager_supersedes_old_knowledge_and_records_replacement() -> None:
    manager = PersonalKnowledgeBaseManager()
    old = manager.remember(
        title="Versión de ROBY",
        content="ROBY tiene 768 tests.",
        kind=KnowledgeKind.FACT,
        now=NOW,
    )
    replacement = manager.remember(
        title="Versión de ROBY actualizada",
        content="ROBY tiene una suite posterior a M74.",
        kind=KnowledgeKind.FACT,
        now=NOW + timedelta(minutes=1),
    )

    superseded = manager.supersede(
        old.item_id,
        replacement.item_id,
        now=NOW + timedelta(minutes=2),
    )

    assert superseded.normalized_status is KnowledgeStatus.SUPERSEDED
    assert superseded.superseded_by == replacement.item_id
    relations = manager.relations_for(old.item_id)
    assert relations[0].normalized_type is KnowledgeRelationType.REPLACES


def test_manager_archives_items() -> None:
    manager = PersonalKnowledgeBaseManager()
    item = manager.remember(
        title="Nota temporal",
        content="Contenido que luego será archivado.",
        kind=KnowledgeKind.NOTE,
        now=NOW,
    )

    archived = manager.archive(item.item_id, now=NOW + timedelta(minutes=1))

    assert archived.normalized_status is KnowledgeStatus.ARCHIVED
    assert manager.recall(status=KnowledgeStatus.ARCHIVED) == (archived,)


def test_manager_builds_candidate_from_document_inbox() -> None:
    documents = DocumentInboxManager()
    document = documents.ingest_text(
        "Manual de instrucciones para reiniciar el equipo de forma segura.",
        title="Manual del equipo",
        tags=("equipo",),
        now=NOW,
    )
    manager = PersonalKnowledgeBaseManager(document_inbox=documents)

    candidate = manager.candidate_from_document(
        document.document_id,
        kind=KnowledgeKind.PROCEDURE,
        now=NOW,
    )
    item = manager.approve(candidate, now=NOW)

    assert item.normalized_source is KnowledgeSource.DOCUMENT
    assert item.source_reference == f"document:{document.document_id}"
    assert "documento" in item.normalized_tags


def test_document_candidate_requires_configured_inbox_and_known_id() -> None:
    manager = PersonalKnowledgeBaseManager()
    with pytest.raises(RuntimeError):
        manager.candidate_from_document("missing", now=NOW)

    configured = PersonalKnowledgeBaseManager(document_inbox=DocumentInboxManager())
    with pytest.raises(KeyError):
        configured.candidate_from_document("missing", now=NOW)


def test_snapshot_exposes_prompt_summary() -> None:
    manager = PersonalKnowledgeBaseManager()
    manager.remember(
        title="Arquitectura de ROBY",
        content="ROBY usa contratos explícitos.",
        kind=KnowledgeKind.CONCEPT,
        now=NOW,
    )

    prompt = "\n".join(manager.system_prompt_lines())

    assert "Personal Knowledge Base M74" in prompt
    assert "Arquitectura de ROBY" in prompt
    assert "Elementos activos: 1" in prompt


def test_manager_rejects_invalid_configuration_and_unknown_ids() -> None:
    with pytest.raises(ValueError):
        PersonalKnowledgeBaseManager(recent_limit=0)
    with pytest.raises(ValueError):
        PersonalKnowledgeBaseManager(automatic_approval_threshold=1.2)

    manager = PersonalKnowledgeBaseManager()
    with pytest.raises(KeyError):
        manager.archive("missing", now=NOW)
    with pytest.raises(ValueError):
        manager.archive("", now=NOW)
