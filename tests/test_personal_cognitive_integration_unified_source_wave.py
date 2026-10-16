from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from app.always_on_personal_runtime_wiring import (
    build_continuous_cognitive_loop_from_environment,
)
from core.personal_knowledge_base import (
    KnowledgeItem,
    KnowledgeKind,
    KnowledgeSource,
    KnowledgeStatus,
)
from core.task_intelligence import Task, TaskStatus
from domain.reminders import Reminder, ReminderStatus
from infrastructure.calendar.calendar_contract import CalendarEvent, CalendarTimeRange

NOW = datetime(2026, 8, 25, 18, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _disable_agenda_persistence(monkeypatch):
    monkeypatch.setenv("ROBY_COGNITIVE_AGENDA_PERSISTENCE_ENABLED", "0")


def _loop(*, tasks=(), reminders=(), events=(), notes=()):
    return build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=None,
        active_tasks=lambda: tasks,
        pending_reminders=lambda: reminders,
        upcoming_calendar_events=lambda now: events,
        relevant_notes=lambda: notes,
    )


def test_priority_task_projects_read_only_follow_up():
    task = Task(
        title="Revisar presupuesto",
        description="Cerrar revisión antes del viernes",
        importance=9,
        urgency=7,
        status=TaskStatus.PENDING,
        task_id="task-1",
    )
    snapshot = _loop(tasks=(task,)).agenda_manager.refresh(now=NOW)
    item = next(item for item in snapshot.items if item.key == "task:task-1")
    assert item.kind.value == "follow_up"
    assert item.sources == ("resident_tasks",)


def test_completed_or_low_relevance_task_is_not_admitted():
    completed = Task(
        title="Hecha",
        description="Ya finalizada",
        importance=10,
        urgency=10,
        status=TaskStatus.COMPLETED,
        completed_at=NOW,
        task_id="task-done",
    )
    quiet = Task(
        title="Sin urgencia",
        description="No requiere foco ahora",
        importance=3,
        urgency=3,
        status=TaskStatus.PENDING,
        task_id="task-quiet",
    )
    snapshot = _loop(tasks=(completed, quiet)).agenda_manager.refresh(now=NOW)
    assert all(not item.key.startswith("task:") for item in snapshot.items)


def test_due_reminder_projects_awareness_without_mutating_source():
    reminder = Reminder(
        id=uuid4(),
        title="Llamar al médico",
        description=None,
        due_at=NOW + timedelta(hours=2),
        status=ReminderStatus.PENDING,
        recurrence=None,
        created_at=NOW - timedelta(days=1),
        updated_at=NOW - timedelta(days=1),
    )
    snapshot = _loop(reminders=(reminder,)).agenda_manager.refresh(now=NOW)
    assert any(item.key == f"reminder:{reminder.id}" for item in snapshot.items)
    assert reminder.status is ReminderStatus.PENDING


def test_far_reminder_is_not_admitted():
    reminder = Reminder(
        id=uuid4(),
        title="Algo futuro",
        description=None,
        due_at=NOW + timedelta(days=10),
        status=ReminderStatus.PENDING,
        recurrence=None,
        created_at=NOW - timedelta(days=1),
        updated_at=NOW - timedelta(days=1),
    )
    snapshot = _loop(reminders=(reminder,)).agenda_manager.refresh(now=NOW)
    assert all(not item.key.startswith("reminder:") for item in snapshot.items)


def test_upcoming_calendar_event_is_ephemeral_projection():
    event = CalendarEvent(
        event_id="event-1",
        title="Turno médico",
        time_range=CalendarTimeRange(
            starts_at=NOW + timedelta(hours=4),
            ends_at=NOW + timedelta(hours=5),
        ),
    )
    snapshot = _loop(events=(event,)).agenda_manager.refresh(now=NOW)
    item = next(item for item in snapshot.items if item.key == "calendar:event-1")
    assert item.kind.value == "follow_up"
    assert item.expires_at == event.time_range.ends_at


def test_plain_note_is_not_admitted_but_explicit_follow_up_note_is():
    plain = KnowledgeItem(
        title="Receta",
        content="Ingredientes",
        kind=KnowledgeKind.NOTE,
        source=KnowledgeSource.MANUAL_ENTRY,
        tags=("cocina",),
        item_id="note-plain",
    )
    follow_up = KnowledgeItem(
        title="Revisar póliza",
        content="Comparar cobertura",
        kind=KnowledgeKind.NOTE,
        source=KnowledgeSource.MANUAL_ENTRY,
        status=KnowledgeStatus.ACTIVE,
        tags=("seguimiento",),
        item_id="note-follow",
    )
    snapshot = _loop(notes=(plain, follow_up)).agenda_manager.refresh(now=NOW)
    keys = {item.key for item in snapshot.items}
    assert "note:note-plain" not in keys
    assert "note:note-follow" in keys


def test_one_personal_source_failure_does_not_block_other_sources():
    task = Task(
        title="Tarea relevante",
        description="Necesita atención",
        importance=9,
        urgency=9,
        task_id="task-ok",
    )

    def broken_reminders():
        raise RuntimeError("reminders unavailable")

    loop = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=None,
        active_tasks=lambda: (task,),
        pending_reminders=broken_reminders,
    )
    snapshot = loop.agenda_manager.refresh(now=NOW)
    assert any(item.key == "task:task-ok" for item in snapshot.items)
    assert "resident_reminders" in snapshot.operational_health.source_failures


def test_desktop_productively_wires_all_personal_sources():
    source = Path("app/desktop_bootstrap.py").read_text(encoding="utf-8")
    for token in (
        "active_tasks=read_tasks",
        "pending_reminders=read_reminders",
        "upcoming_calendar_events=read_calendar_events",
        "relevant_notes=read_relevant_notes",
    ):
        assert token in source


def test_canonical_managers_expose_read_only_collection_methods():
    from core.personal_knowledge_base import PersonalKnowledgeBaseManager
    from core.task_intelligence import TaskIntelligenceManager

    assert TaskIntelligenceManager().list_tasks() == ()
    assert PersonalKnowledgeBaseManager().list_items() == ()
