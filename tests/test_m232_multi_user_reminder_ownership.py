from __future__ import annotations

from datetime import datetime, timezone

from application.reminders import ReminderConversationService
from infrastructure.persistence.sqlite import SQLiteReminderRuntimeStore

NOW = datetime(2026, 7, 15, 20, 0, tzinfo=timezone.utc)


def create(service, owner: str, text: str) -> None:
    result = service.handle(owner=owner, text=text, now=NOW)
    assert result.handled is True
    assert "Listo" in result.response_text


def test_historical_profile_labels_share_one_household_view(tmp_path):
    service = ReminderConversationService(tmp_path / "reminders.db")
    create(service, "Carlos", "recordame comprar café mañana a las 10")
    create(service, "Cristina", "recordame llamar a Ana mañana a las 11")

    carlos = service.handle(owner="Carlos", text="qué recordatorios tengo", now=NOW)
    cristina = service.handle(owner="Cristina", text="qué recordatorios tengo", now=NOW)

    assert "comprar café" in carlos.response_text
    assert "llamar a ana" in carlos.response_text.casefold()
    assert "llamar a ana" in cristina.response_text.casefold()
    assert "comprar café" in cristina.response_text


def test_owner_can_create_for_other_household_profile(tmp_path):
    service = ReminderConversationService(tmp_path / "reminders.db")
    create(
        service,
        "Carlos",
        "recordame llamar al médico mañana a las 10 para Cristina",
    )

    carlos = service.handle(owner="Carlos", text="qué recordatorios tengo", now=NOW)
    cristina = service.handle(owner="Cristina", text="qué recordatorios tengo", now=NOW)

    assert "llamar al médico" in carlos.response_text
    assert "llamar al médico" in cristina.response_text


def test_shared_household_reminder_is_visible_to_both_profiles(tmp_path):
    service = ReminderConversationService(tmp_path / "reminders.db")
    create(
        service,
        "Carlos",
        "recordame pagar internet mañana a las 10 para todos",
    )

    for owner in ("Carlos", "Cristina"):
        listed = service.handle(owner=owner, text="qué recordatorios tengo", now=NOW)
        assert "pagar internet" in listed.response_text


def test_either_household_name_can_cancel_any_household_reminder(tmp_path):
    service = ReminderConversationService(tmp_path / "reminders.db")
    create(service, "Cristina", "recordame comprar té mañana a las 10")

    result = service.handle(
        owner="Carlos",
        text="cancelá el recordatorio comprar té",
        now=NOW,
    )

    assert "Cancelé" in result.response_text
    listed = service.handle(owner="Cristina", text="qué recordatorios tengo", now=NOW)
    assert "No tenés" in listed.response_text


def test_resident_runtime_delivers_all_household_reminders(tmp_path):
    service = ReminderConversationService(tmp_path / "reminders.db")
    create(service, "Carlos", "recordame café hoy a las 21")
    create(service, "Cristina", "recordame té hoy a las 21")
    create(service, "Carlos", "recordame cerrar puertas hoy a las 21 para todos")
    due = datetime(2026, 7, 15, 22, 0, tzinfo=timezone.utc)

    carlos = SQLiteReminderRuntimeStore(
        tmp_path / "reminders.db", owner="Carlos"
    ).list_due(now=due)
    cristina = SQLiteReminderRuntimeStore(
        tmp_path / "reminders.db", owner="Cristina"
    ).list_due(now=due)

    expected = {"café", "té", "cerrar puertas"}
    assert {item.title for item in carlos} == expected
    assert {item.title for item in cristina} == expected
