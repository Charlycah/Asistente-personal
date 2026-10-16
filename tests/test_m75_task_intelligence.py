from datetime import datetime, timedelta, timezone

import pytest

from core.document_inbox import DocumentInboxManager
from core.household_memory import (
    HouseholdMemoryCategory,
    HouseholdMemoryEntry,
    HouseholdMemoryManager,
    HouseholdMemoryOwner,
)
from core.personal_knowledge_base import (
    KnowledgeKind,
    KnowledgeOwner,
    PersonalKnowledgeBaseManager,
)
from core.task_intelligence import (
    InMemoryTaskRepository,
    Task,
    TaskCandidate,
    TaskDependency,
    TaskIntelligenceManager,
    TaskOrigin,
    TaskOwner,
    TaskSignal,
    TaskStatus,
)

NOW = datetime(2026, 7, 10, 20, 0, tzinfo=timezone.utc)


def test_candidate_validates_and_normalizes_values() -> None:
    candidate = TaskCandidate(
        title="Revisar documentación",
        description="Revisar el documento técnico de ROBY.",
        owner=TaskOwner.CARLOS,
        origin=TaskOrigin.MANUAL,
        tags=("ROBY", "documentación", "ROBY"),
        created_at=NOW,
    )

    assert candidate.normalized_tags == ("roby", "documentación")
    assert candidate.normalized_owner is TaskOwner.CARLOS
    with pytest.raises(ValueError):
        TaskCandidate(
            title="Inválida",
            description="Descripción",
            importance=11,
        )


def test_task_priority_score_accounts_for_deadline_and_status() -> None:
    urgent = Task(
        title="Vence mañana",
        description="Resolver antes del vencimiento.",
        importance=8,
        urgency=8,
        deadline=NOW + timedelta(hours=12),
        created_at=NOW,
        updated_at=NOW,
    )
    later = Task(
        title="Puede esperar",
        description="No tiene vencimiento inmediato.",
        importance=8,
        urgency=8,
        deadline=NOW + timedelta(days=20),
        created_at=NOW,
        updated_at=NOW,
    )

    assert urgent.priority_score(now=NOW) > later.priority_score(now=NOW)
    assert urgent.to_dict(now=NOW)["priority_score"] == urgent.priority_score(now=NOW)


def test_completed_task_requires_completion_timestamp() -> None:
    with pytest.raises(ValueError):
        Task(
            title="Hecha",
            description="Tarea terminada.",
            status=TaskStatus.COMPLETED,
            created_at=NOW,
            updated_at=NOW,
        )


def test_dependency_rejects_self_reference() -> None:
    with pytest.raises(ValueError):
        TaskDependency(task_id="same", depends_on_task_id="same", created_at=NOW)


def test_repository_stores_tasks_and_dependencies() -> None:
    repository = InMemoryTaskRepository()
    first = Task(
        title="Primera",
        description="Primera tarea.",
        created_at=NOW,
        updated_at=NOW,
    )
    second = Task(
        title="Segunda",
        description="Segunda tarea.",
        created_at=NOW + timedelta(seconds=1),
        updated_at=NOW + timedelta(seconds=1),
    )
    repository.save_task(first)
    repository.save_task(second)
    dependency = repository.save_dependency(
        TaskDependency(
            task_id=second.task_id,
            depends_on_task_id=first.task_id,
            created_at=NOW,
        )
    )

    assert repository.get_task(first.task_id) is first
    assert repository.get_by_fingerprint(first.fingerprint) is first
    assert repository.list_tasks() == (first, second)
    assert repository.list_dependencies() == (dependency,)


def test_manager_creates_manual_task() -> None:
    manager = TaskIntelligenceManager()

    task = manager.create_task(
        title="Ordenar documentos",
        description="Clasificar los documentos pendientes.",
        owner=TaskOwner.SHARED,
        importance=7,
        urgency=6,
        tags=("documentos",),
        now=NOW,
    )

    assert task.normalized_status is TaskStatus.PENDING
    assert task.normalized_origin is TaskOrigin.MANUAL
    assert TaskSignal.TASK_STORED in manager.snapshot(now=NOW).signals


def test_manager_requires_review_for_system_suggestion() -> None:
    manager = TaskIntelligenceManager()
    candidate = manager.create_candidate(
        title="Sugerencia",
        description="Tarea propuesta automáticamente.",
        origin=TaskOrigin.SYSTEM_SUGGESTION,
        now=NOW,
    )

    assert candidate.requires_review is True
    with pytest.raises(PermissionError):
        manager.approve(candidate, now=NOW)
    approved = manager.approve(candidate, reviewed=True, now=NOW)
    assert approved.normalized_status is TaskStatus.PENDING


def test_manager_blocks_financial_task() -> None:
    manager = TaskIntelligenceManager()

    with pytest.raises(PermissionError):
        manager.create_task(
            title="Transferencia bancaria",
            description="Mover dinero para pagar una compra.",
            now=NOW,
        )


def test_manager_deduplicates_tasks() -> None:
    manager = TaskIntelligenceManager()
    first = manager.create_task(
        title="Revisar garantía",
        description="Verificar la fecha de vencimiento.",
        now=NOW,
    )
    second = manager.create_task(
        title="Revisar garantía",
        description="Verificar la fecha de vencimiento.",
        now=NOW + timedelta(seconds=1),
    )

    assert first.task_id == second.task_id
    assert TaskSignal.DUPLICATE_REUSED in manager.snapshot(now=NOW).signals


def test_manager_prioritizes_overdue_and_important_tasks() -> None:
    manager = TaskIntelligenceManager()
    low = manager.create_task(
        title="Lectura opcional",
        description="Leer cuando haya tiempo.",
        importance=2,
        urgency=2,
        now=NOW,
    )
    high = manager.create_task(
        title="Turno mañana",
        description="Preparar documentación para el turno.",
        importance=9,
        urgency=9,
        deadline=NOW + timedelta(hours=10),
        now=NOW,
    )

    assert manager.prioritize(now=NOW) == (high, low)


def test_manager_handles_dependencies_and_ready_tasks() -> None:
    manager = TaskIntelligenceManager()
    prerequisite = manager.create_task(
        title="Sacar turno",
        description="Solicitar un turno.",
        now=NOW,
    )
    dependent = manager.create_task(
        title="Asistir al trámite",
        description="Presentarse con la documentación.",
        now=NOW,
    )
    manager.add_dependency(dependent.task_id, prerequisite.task_id, now=NOW)

    assert prerequisite in manager.ready_tasks(now=NOW)
    assert dependent not in manager.ready_tasks(now=NOW)
    manager.complete(prerequisite.task_id, now=NOW + timedelta(minutes=1))
    assert dependent in manager.ready_tasks(now=NOW + timedelta(minutes=1))


def test_manager_rejects_dependency_cycles() -> None:
    manager = TaskIntelligenceManager()
    first = manager.create_task(
        title="Primera",
        description="Primera tarea.",
        now=NOW,
    )
    second = manager.create_task(
        title="Segunda",
        description="Segunda tarea.",
        now=NOW,
    )
    manager.add_dependency(second.task_id, first.task_id, now=NOW)

    with pytest.raises(ValueError):
        manager.add_dependency(first.task_id, second.task_id, now=NOW)


def test_manager_completes_tasks_and_updates_snapshot() -> None:
    manager = TaskIntelligenceManager()
    task = manager.create_task(
        title="Completar revisión",
        description="Cerrar revisión documental.",
        now=NOW,
    )

    completed = manager.complete(task.task_id, now=NOW + timedelta(minutes=5))
    snapshot = manager.snapshot(now=NOW + timedelta(minutes=5))

    assert completed.normalized_status is TaskStatus.COMPLETED
    assert completed.completed_at == NOW + timedelta(minutes=5)
    assert snapshot.completed_tasks == 1


def test_candidate_from_household_memory() -> None:
    memory = HouseholdMemoryManager()
    entry = memory.remember(
        HouseholdMemoryEntry(
            title="Renovar garantía",
            details="Revisar la garantía del equipo.",
            category=HouseholdMemoryCategory.WARRANTY,
            owner=HouseholdMemoryOwner.SHARED,
            due_at=NOW + timedelta(days=3),
            created_at=NOW,
            updated_at=NOW,
        )
    )
    manager = TaskIntelligenceManager(household_memory=memory)

    candidate = manager.candidate_from_household_memory(entry.entry_id, now=NOW)

    assert candidate.normalized_origin is TaskOrigin.HOUSEHOLD_MEMORY
    assert candidate.deadline == entry.due_at
    assert candidate.source_reference == entry.entry_id


def test_candidate_from_document() -> None:
    documents = DocumentInboxManager()
    document = documents.ingest_text(
        "Manual del equipo para revisar.",
        title="Manual del equipo",
        tags=("manual",),
        now=NOW,
    )
    manager = TaskIntelligenceManager(document_inbox=documents)

    candidate = manager.candidate_from_document(document.document_id, now=NOW)

    assert candidate.normalized_origin is TaskOrigin.DOCUMENT
    assert candidate.source_reference == document.document_id


def test_candidate_from_knowledge() -> None:
    knowledge = PersonalKnowledgeBaseManager()
    item = knowledge.remember(
        title="Procedimiento seguro",
        content="Revisar el manual antes de reiniciar.",
        kind=KnowledgeKind.PROCEDURE,
        owner=KnowledgeOwner.CARLOS,
        tags=("manual",),
        now=NOW,
    )
    manager = TaskIntelligenceManager(personal_knowledge_base=knowledge)

    candidate = manager.candidate_from_knowledge(item.item_id, now=NOW)

    assert candidate.normalized_origin is TaskOrigin.KNOWLEDGE
    assert candidate.normalized_owner is TaskOwner.CARLOS
    assert candidate.source_reference == item.item_id


def test_manager_converts_task_and_dependencies_to_plan() -> None:
    manager = TaskIntelligenceManager()
    prerequisite = manager.create_task(
        title="Preparar papeles",
        description="Reunir documentación.",
        now=NOW,
    )
    task = manager.create_task(
        title="Realizar trámite",
        description="Completar el trámite.",
        now=NOW,
    )
    manager.add_dependency(task.task_id, prerequisite.task_id, now=NOW)

    plan = manager.to_plan(task.task_id, now=NOW)

    assert plan.goal.description == task.title
    assert len(plan.steps) == 2
    assert plan.steps[-1].metadata["task_id"] == task.task_id


def test_snapshot_exposes_prompt_context() -> None:
    manager = TaskIntelligenceManager()
    manager.create_task(
        title="Tarea visible",
        description="Aparece en el contexto del pipeline.",
        now=NOW,
    )

    lines = manager.snapshot(now=NOW).system_prompt_lines()

    assert lines[0] == "Task Intelligence M75:"
    assert any("Tarea visible" in line for line in lines)
