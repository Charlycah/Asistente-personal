from datetime import datetime, timezone

from application.reminders.natural_language import parse_create_reminder
from domain.reminders import RecurrenceFrequency, RecurrenceRule


def test_parse_recordame_a_las_cinco() -> None:
    now = datetime(2026, 7, 3, 14, 0, tzinfo=timezone.utc)

    command = parse_create_reminder(
        "ROBY recordame a las cinco comprar leche",
        now=now,
    )

    assert command.title == "comprar leche"
    assert command.due_at == datetime(2026, 7, 3, 17, 0, tzinfo=timezone.utc)


def test_parse_haceme_acordar_a_las_5() -> None:
    now = datetime(2026, 7, 3, 14, 0, tzinfo=timezone.utc)

    command = parse_create_reminder(
        "ROBY haceme acordar que a las 5 tengo gimnasia",
        now=now,
    )

    assert command.title == "gimnasia"
    assert command.due_at == datetime(2026, 7, 3, 17, 0, tzinfo=timezone.utc)


def test_if_5_pm_already_passed_schedule_tomorrow() -> None:
    now = datetime(2026, 7, 3, 20, 0, tzinfo=timezone.utc)

    command = parse_create_reminder(
        "recordame a las 5 comprar leche",
        now=now,
    )

    assert command.due_at == datetime(2026, 7, 4, 17, 0, tzinfo=timezone.utc)


def test_parse_haceme_acordar_concierto_con_fecha_absoluta() -> None:
    now = datetime(2026, 9, 11, 10, 0, tzinfo=timezone.utc)

    command = parse_create_reminder(
        "ROBY haceme acordar que el 20/10 a las 21 tengo concierto",
        now,
    )

    assert command.title == "concierto"
    assert command.due_at == datetime(2026, 10, 20, 21, 0, tzinfo=timezone.utc)


def test_parse_haceme_acordar_viaje_con_fecha_natural() -> None:
    now = datetime(2026, 9, 11, 10, 0, tzinfo=timezone.utc)

    command = parse_create_reminder(
        "haceme acordar que el 3 de noviembre a las 8 tengo viaje a Córdoba",
        now,
    )

    assert command.title == "viaje a córdoba"
    assert command.due_at == datetime(2026, 11, 3, 8, 0, tzinfo=timezone.utc)


def test_parse_haceme_acordar_cumpleanos_anual() -> None:
    now = datetime(2026, 9, 11, 10, 0, tzinfo=timezone.utc)

    command = parse_create_reminder(
        "haceme acordar todos los años el 15 de marzo a las 9 "
        "el cumpleaños de Ana",
        now,
    )

    assert command.title == "el cumpleaños de ana"
    assert command.due_at == datetime(2027, 3, 15, 9, 0, tzinfo=timezone.utc)
    assert command.recurrence == RecurrenceRule(
        frequency=RecurrenceFrequency.YEARLY,
        interval=1,
    )
