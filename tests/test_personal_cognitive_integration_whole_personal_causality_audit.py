from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.always_on_personal_runtime_wiring import (
    build_continuous_cognitive_loop_from_environment,
)
from app.continuous_internal_cognitive_loop import CognitiveFocus
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


def test_task_change_causally_changes_resident_deliberation():
    tasks = [
        Task(
            title="Revisar contrato",
            description="Necesita atención",
            importance=9,
            urgency=9,
            status=TaskStatus.PENDING,
            task_id="task-causal",
        )
    ]
    loop = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=None,
        active_tasks=lambda: tuple(tasks),
    )
    before = loop.tick(now=NOW)
    assert before.focus is CognitiveFocus.COGNITIVE_AGENDA
    assert before.agenda.effective_focus.key == "task:task-causal"
    assert before.deliberation.agenda_key == "task:task-causal"

    tasks[0] = Task(
        title="Revisar contrato",
        description="Terminado",
        importance=9,
        urgency=9,
        status=TaskStatus.COMPLETED,
        completed_at=NOW + timedelta(minutes=1),
        task_id="task-causal",
    )
    after = loop.tick(now=NOW + timedelta(minutes=1))
    assert all(item.key != "task:task-causal" for item in after.agenda.items)


def test_reminder_relevance_reaches_reasoning_without_mutation():
    reminder = Reminder(
        id=uuid4(),
        title="Llamar al médico",
        description=None,
        due_at=NOW + timedelta(hours=1),
        status=ReminderStatus.PENDING,
        recurrence=None,
        created_at=NOW - timedelta(days=1),
        updated_at=NOW - timedelta(days=1),
    )
    loop = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=None,
        pending_reminders=lambda: (reminder,),
    )
    state = loop.tick(now=NOW)
    assert state.agenda.effective_focus.key == f"reminder:{reminder.id}"
    assert state.deliberation.agenda_key == f"reminder:{reminder.id}"
    assert reminder.status is ReminderStatus.PENDING


def test_calendar_projection_expires_and_leaves_resident_focus():
    event = CalendarEvent(
        event_id="event-causal",
        title="Reunión",
        time_range=CalendarTimeRange(
            starts_at=NOW + timedelta(minutes=30),
            ends_at=NOW + timedelta(hours=1),
        ),
    )
    events = [event]
    loop = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=None,
        upcoming_calendar_events=lambda now: tuple(events),
    )
    before = loop.tick(now=NOW)
    assert before.agenda.effective_focus.key == "calendar:event-causal"
    assert before.deliberation.agenda_key == "calendar:event-causal"

    events.clear()
    after = loop.tick(now=NOW + timedelta(hours=2))
    assert all(item.key != "calendar:event-causal" for item in after.agenda.items)


def test_explicit_follow_up_note_reaches_reasoning_plain_note_does_not():
    notes = [
        KnowledgeItem(
            title="Receta",
            content="Ingredientes",
            kind=KnowledgeKind.NOTE,
            source=KnowledgeSource.MANUAL_ENTRY,
            tags=("cocina",),
            item_id="plain",
        ),
        KnowledgeItem(
            title="Revisar póliza",
            content="Comparar cobertura",
            kind=KnowledgeKind.NOTE,
            source=KnowledgeSource.MANUAL_ENTRY,
            status=KnowledgeStatus.ACTIVE,
            tags=("seguimiento",),
            item_id="follow",
        ),
    ]
    loop = build_continuous_cognitive_loop_from_environment(
        latest_self_analysis=None,
        relevant_notes=lambda: tuple(notes),
    )
    state = loop.tick(now=NOW)
    keys = {item.key for item in state.agenda.items}
    assert "note:plain" not in keys
    assert "note:follow" in keys
    assert state.deliberation.agenda_key == "note:follow"
