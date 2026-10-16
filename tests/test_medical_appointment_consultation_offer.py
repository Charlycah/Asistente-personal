from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.medical_appointment_consultation_offer import (
    MedicalAppointmentConsultationOffer,
)
from core.always_on_personal_runtime.reminder_awareness import (
    IntelligentReminderPolicy,
    ReminderAwarenessService,
)
from domain.reminders import Reminder, ReminderStatus


class Source:
    def __init__(self, reminder):
        self.reminder = reminder
        self.advance = set()

    def list_due(self, *, now):
        return []

    def was_notified(self, reminder_id, *, due_at):
        return False

    def mark_notified(self, reminder_id, *, due_at, notified_at):
        return None

    def list_upcoming(self, *, now, until):
        return [self.reminder]

    def was_advance_notified(self, reminder_id, *, due_at, stage):
        return stage in self.advance

    def mark_advance_notified(
        self, reminder_id, *, due_at, stage, notified_at
    ):
        self.advance.add(stage)


def _reminder(title, *, now):
    return Reminder(
        id=uuid4(),
        title=title,
        description=None,
        due_at=now + timedelta(days=1),
        status=ReminderStatus.PENDING,
        recurrence=None,
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1),
    )


def test_medical_reminder_for_named_household_member_gets_opt_in_offer():
    now = datetime(2026, 9, 11, 16, tzinfo=timezone.utc)
    reminder = _reminder(
        "Cristina tiene turno con el cardiólogo",
        now=now,
    )
    offer = MedicalAppointmentConsultationOffer()

    message = offer.enhance(reminder, "Mañana a las 16:00 tenés el turno.")

    assert "resumen preconsulta de Cristina" in message
    assert "Si querés" in message


def test_non_medical_life_event_is_not_enriched():
    now = datetime(2026, 9, 11, 16, tzinfo=timezone.utc)
    reminder = _reminder("Cristina tiene concierto", now=now)
    offer = MedicalAppointmentConsultationOffer()

    assert offer.enhance(reminder, "Mañana tenés concierto.") == (
        "Mañana tenés concierto."
    )


def test_ambiguous_person_is_fail_closed():
    now = datetime(2026, 9, 11, 16, tzinfo=timezone.utc)
    reminder = _reminder("turno con el cardiólogo", now=now)
    offer = MedicalAppointmentConsultationOffer()

    assert offer.recognize(reminder) is None


def test_reminder_awareness_can_offer_without_accessing_health_data():
    now = datetime(2026, 9, 11, 16, tzinfo=timezone.utc)
    reminder = _reminder(
        "Carlos tiene consulta con la doctora Pérez",
        now=now,
    )
    source = Source(reminder)
    messages = []
    awareness = ReminderAwarenessService(
        source,
        notify=messages.append,
        intelligent_policy=IntelligentReminderPolicy(),
        enhance_notice=MedicalAppointmentConsultationOffer().enhance,
    )

    result = awareness.check_once(now=now)

    assert len(result) == 1
    assert "resumen preconsulta de Carlos" in result[0]
    assert messages == list(result)
