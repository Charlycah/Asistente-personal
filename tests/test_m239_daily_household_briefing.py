from datetime import datetime, timezone

from app.daily_household_briefing import (
    DailyHouseholdBriefingConfig,
    DailyHouseholdBriefingService,
)
from application.reminders.natural_language import ReminderConversationService

NOW = datetime(2026, 7, 15, 8, 0, tzinfo=timezone.utc)


class Battery:
    def read(self):
        return type("Snapshot", (), {"percent": 82.0, "plugged": False})()


class LowBattery:
    def read(self):
        return type("Snapshot", (), {"percent": 9.0, "plugged": False})()


class Gmail:
    def announce(self):
        return type("Result", (), {"text": "Hay 3 correos no leídos."})()


def _store(path):
    service = ReminderConversationService(path)
    service.handle(
        owner="Familia",
        text="Recordame llamar al médico hoy a las 10",
        now=NOW,
    )
    service.handle(
        owner="Familia",
        text="Recordame regar las plantas todos los días a las 12",
        now=NOW,
    )


def test_briefing_composes_official_household_sources(tmp_path):
    db = tmp_path / "reminders.db"
    _store(db)
    text = DailyHouseholdBriefingService(
        reminder_db_path=db,
        battery_sensor=Battery(),
        gmail_announcer=Gmail(),
    ).generate(now=NOW)
    assert "Buen día" in text
    assert "Recordatorio: Hoy a las 10:00: llamar al médico." in text
    assert "Rutina: Hoy a las 12:00: regar las plantas." in text
    assert "Batería" not in text
    assert "Tengo algunas cosas importantes" in text
    assert "3 correos no leídos" in text


def test_briefing_excludes_items_outside_horizon(tmp_path):
    db = tmp_path / "reminders.db"
    ReminderConversationService(db).handle(
        owner="Familia",
        text="Recordame revisar el techo en 3 días",
        now=NOW,
    )
    text = DailyHouseholdBriefingService(
        reminder_db_path=db,
        config=DailyHouseholdBriefingConfig(horizon_hours=24),
    ).generate(now=NOW)
    assert "revisar el techo" not in text
    assert text in {
        "Buen día. ¿Cómo estás?",
        "Buen día. ¿Todo bien?",
        "Buen día. ¿Cómo va todo?",
    }


def test_briefing_degrades_when_optional_sources_fail(tmp_path):
    class Broken:
        def read(self):
            raise OSError("offline")

        def announce(self):
            raise OSError("offline")

    text = DailyHouseholdBriefingService(
        reminder_db_path=tmp_path / "reminders.db",
        battery_sensor=Broken(),
        gmail_announcer=Broken(),
    ).generate(now=NOW)
    assert text in {
        "Buen día. ¿Cómo estás?",
        "Buen día. ¿Todo bien?",
        "Buen día. ¿Cómo va todo?",
    }


def test_briefing_mentions_only_actionable_low_battery(tmp_path):
    text = DailyHouseholdBriefingService(
        reminder_db_path=tmp_path / "reminders.db",
        battery_sensor=LowBattery(),
    ).generate(now=NOW)
    assert "Tengo algo importante" in text
    assert "batería está en 9%" in text
    assert "conectar el equipo pronto" in text


def test_briefing_does_not_warn_when_low_battery_is_plugged(tmp_path):
    class PluggedLowBattery:
        def read(self):
            return type("Snapshot", (), {"percent": 7.0, "plugged": True})()

    text = DailyHouseholdBriefingService(
        reminder_db_path=tmp_path / "reminders.db",
        battery_sensor=PluggedLowBattery(),
    ).generate(now=NOW)
    assert text in {
        "Buen día. ¿Cómo estás?",
        "Buen día. ¿Todo bien?",
        "Buen día. ¿Cómo va todo?",
    }


def test_single_reminder_uses_forget_me_not_wording_and_weekday(tmp_path):
    db = tmp_path / "reminders.db"
    now = datetime(2026, 7, 16, 9, 0, tzinfo=timezone.utc)
    ReminderConversationService(db).handle(
        owner="Familia",
        text="Recordame que el viernes tengo reunión con Laura a las 15.30",
        now=now,
    )

    text = DailyHouseholdBriefingService(
        reminder_db_path=db,
        config=DailyHouseholdBriefingConfig(horizon_hours=48),
    ).generate(now=now)

    assert "No te olvides:" in text
    assert "Tengo una novedad" not in text
    assert "el viernes a las 15:30 tenés reunión con laura." in text.casefold()
    assert "hoy a las 12:00" not in text


def test_first_person_reminder_uses_structured_due_time(tmp_path):
    db = tmp_path / "reminders.db"
    now = datetime(2026, 7, 16, 9, 0, tzinfo=timezone.utc)
    ReminderConversationService(db).handle(
        owner="Familia",
        text="Recordame que el viernes tengo reunión con Laura a las 15.30",
        now=now,
    )

    text = DailyHouseholdBriefingService(
        reminder_db_path=db,
        config=DailyHouseholdBriefingConfig(horizon_hours=48),
    ).generate(now=now)

    assert "tenés reunión con laura" in text.casefold()
    assert "tengo reunión" not in text.casefold()
    assert "el viernes a las 15:30 tenés reunión con laura." in text.casefold()


def test_old_temporal_tail_is_removed_from_spoken_reminder_title():
    title = DailyHouseholdBriefingService._spoken_reminder_title(
        "tengo reunión con Laura, hoy a las 12:00"
    )

    assert title == "tenés reunión con Laura"


def test_briefing_renders_structured_turno_without_duplicate_temporal_text(tmp_path):
    db = tmp_path / "reminders.db"
    now = datetime(2026, 7, 16, 9, 0, tzinfo=timezone.utc)
    service = ReminderConversationService(db)
    service.handle(
        owner="Carlos",
        text="recordame que el viernes tengo turno con el dentista a las 12",
        now=now,
    )

    text = DailyHouseholdBriefingService(
        reminder_db_path=db,
        config=DailyHouseholdBriefingConfig(horizon_hours=48),
    ).generate(now=now)

    assert "El viernes a las 12:00 tenés turno con el dentista." in text
    assert "hoy a las 12:00: el viernes" not in text.casefold()
