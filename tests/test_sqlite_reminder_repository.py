from datetime import datetime, timedelta, timezone
from uuid import uuid4

from domain.reminders import (
    RecurrenceFrequency,
    RecurrenceRule,
    Reminder,
    ReminderStatus,
)
from infrastructure.persistence.sqlite import (
    SQLiteReminderRepository,
    create_connection,
    init_reminders_schema,
)


def make_repository(tmp_path):
    db_path = tmp_path / "test_reminders.db"
    connection = create_connection(db_path)
    init_reminders_schema(connection)
    return SQLiteReminderRepository(connection)


def make_reminder(
    *,
    title: str = "Comprar pan",
    status: ReminderStatus = ReminderStatus.PENDING,
    recurrence: RecurrenceRule | None = None,
) -> Reminder:
    now = datetime(2026, 7, 3, 10, 0, tzinfo=timezone.utc)

    return Reminder(
        id=uuid4(),
        title=title,
        description="Pasar por la panadería",
        due_at=now + timedelta(hours=1),
        status=status,
        recurrence=recurrence,
        created_at=now,
        updated_at=now,
    )


def test_save_and_get_reminder_by_id(tmp_path) -> None:
    repository = make_repository(tmp_path)
    reminder = make_reminder()

    repository.save(reminder)

    saved = repository.get_by_id(reminder.id)

    assert saved is not None
    assert saved.id == reminder.id
    assert saved.title == reminder.title
    assert saved.description == reminder.description
    assert saved.due_at == reminder.due_at
    assert saved.status == reminder.status
    assert saved.created_at == reminder.created_at
    assert saved.updated_at == reminder.updated_at


def test_get_missing_reminder_returns_none(tmp_path) -> None:
    repository = make_repository(tmp_path)

    result = repository.get_by_id(uuid4())

    assert result is None


def test_save_updates_existing_reminder(tmp_path) -> None:
    repository = make_repository(tmp_path)
    reminder = make_reminder()

    repository.save(reminder)

    updated_at = reminder.updated_at + timedelta(minutes=10)
    reminder.title = "Comprar leche"
    reminder.updated_at = updated_at

    repository.save(reminder)

    saved = repository.get_by_id(reminder.id)

    assert saved is not None
    assert saved.title == "Comprar leche"
    assert saved.updated_at == updated_at


def test_list_pending_returns_only_pending_reminders(tmp_path) -> None:
    repository = make_repository(tmp_path)

    pending = make_reminder(title="Pendiente", status=ReminderStatus.PENDING)
    completed = make_reminder(title="Completado", status=ReminderStatus.COMPLETED)
    cancelled = make_reminder(title="Cancelado", status=ReminderStatus.CANCELLED)

    repository.save(pending)
    repository.save(completed)
    repository.save(cancelled)

    result = repository.list_pending()

    assert result == [pending]


def test_delete_reminder(tmp_path) -> None:
    repository = make_repository(tmp_path)
    reminder = make_reminder()

    repository.save(reminder)
    repository.delete(reminder.id)

    assert repository.get_by_id(reminder.id) is None


def test_save_and_get_reminder_with_recurrence(tmp_path) -> None:
    repository = make_repository(tmp_path)
    recurrence = RecurrenceRule(
        frequency=RecurrenceFrequency.WEEKLY,
        interval=2,
    )
    reminder = make_reminder(recurrence=recurrence)

    repository.save(reminder)

    saved = repository.get_by_id(reminder.id)

    assert saved is not None
    assert saved.recurrence == recurrence
