from __future__ import annotations

from datetime import datetime, timezone

from application.reminders import ReminderConversationService

NOW = datetime(2026, 7, 15, 20, 0, tzinfo=timezone.utc)


def test_carlos_and_cristina_share_reminders(tmp_path):
    service = ReminderConversationService(tmp_path / "reminders.db")
    service.handle(
        owner="Carlos",
        text="recordame comprar pan mañana a las 10",
        now=NOW,
    )

    listed = service.handle(
        owner="Cristina",
        text="qué recordatorios tengo",
        now=NOW,
    )

    assert "comprar pan" in listed.response_text


def test_explicit_person_name_does_not_create_private_scope(tmp_path):
    service = ReminderConversationService(tmp_path / "reminders.db")
    service.handle(
        owner="Carlos",
        text="recordame llamar al médico mañana a las 10 para Cristina",
        now=NOW,
    )

    cancelled = service.handle(
        owner="Carlos",
        text="cancelá el recordatorio llamar al médico",
        now=NOW,
    )

    assert "Cancelé" in cancelled.response_text
