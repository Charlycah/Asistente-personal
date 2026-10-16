from datetime import datetime
from pathlib import Path

from app.health_orchestrator import HealthOrchestratorService
from app.secure_health_checkups import (
    HealthCheckup,
    HealthCheckupRepository,
)
from app.secure_medication_registry import (
    MedicationIntake,
    MedicationRecord,
    MedicationRegistryRepository,
)

NOW = datetime(2026, 7, 27, 10, 30)


def _service(tmp_path: Path) -> HealthOrchestratorService:
    return HealthOrchestratorService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "health_checkups.json"),
        now=lambda: NOW,
    )


def test_ignores_unrelated_requests(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("Contame las noticias")

    assert not result.handled
    assert result.response == ""


def test_reports_empty_confirmed_health_snapshot(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("resumen de salud de Carlos hoy")

    assert result.handled
    assert "Resumen de salud de Carlos para 2026-07-27" in result.response
    assert "no hay tomas activas programadas" in result.response
    assert "no hay registros activos" in result.response


def test_combines_today_medication_and_recent_checkups(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [
            MedicationRecord(
                record_id="a1b2c3d4",
                person="Cristina",
                name="Medicamento A",
                dosage="1 comprimido",
                schedules=["08:00", "20:00"],
            )
        ],
        [
            MedicationIntake(
                intake_id="i1",
                medication_id="a1b2c3d4",
                person="Cristina",
                scheduled_date="2026-07-27",
                scheduled_time="08:00",
                status="tomado",
                recorded_at="2026-07-27T08:05:00",
            )
        ],
    )
    service.checkup_repository.save(
        [
            HealthCheckup(
                record_id="11111111",
                person="Cristina",
                study_type="Laboratorio general",
                performed_on="2026-07-20",
                category="laboratorio",
            )
        ]
    )

    result = service.prepare("estado de salud de Cristina")

    assert "08:00 · Medicamento A · 1 comprimido · tomado" in result.response
    assert (
        "20:00 · Medicamento A · 1 comprimido · pendiente de confirmar"
        in result.response
    )
    assert "2026-07-20 · Laboratorio general · ID 11111111" in result.response


def test_excludes_inactive_archived_and_out_of_date_records(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [
            MedicationRecord(
                record_id="paused01",
                person="Carlos",
                name="Pausado",
                dosage="1",
                schedules=["09:00"],
                status="pausado",
            ),
            MedicationRecord(
                record_id="future01",
                person="Carlos",
                name="Futuro",
                dosage="1",
                schedules=["09:00"],
                start_date="2026-08-01",
            ),
        ]
    )
    service.checkup_repository.save(
        [
            HealthCheckup(
                record_id="archived",
                person="Carlos",
                study_type="Archivado",
                performed_on="2026-07-01",
                category="informe",
                archived=True,
            )
        ]
    )

    result = service.prepare("ver resumen de salud de Carlos")

    assert "Pausado" not in result.response
    assert "Futuro" not in result.response
    assert "Archivado" not in result.response


def test_limits_checkups_to_three_most_recent(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.checkup_repository.save(
        [
            HealthCheckup(
                record_id=f"0000000{index}",
                person="Carlos",
                study_type=f"Estudio {index}",
                performed_on=f"2026-07-{index:02d}",
                category="informe",
            )
            for index in range(1, 5)
        ]
    )

    response = service.prepare("mostrar estado de salud de Carlos hoy").response

    assert "Estudio 4" in response
    assert "Estudio 3" in response
    assert "Estudio 2" in response
    assert "Estudio 1" not in response


def test_keeps_carlos_and_cristina_separate(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [
            MedicationRecord(
                record_id="carlos01",
                person="Carlos",
                name="Solo Carlos",
                dosage="1",
                schedules=["08:00"],
            ),
            MedicationRecord(
                record_id="crist01",
                person="Cristina",
                name="Solo Cristina",
                dosage="1",
                schedules=["09:00"],
            ),
        ]
    )

    response = service.prepare("resumen de salud de Cristina").response

    assert "Solo Cristina" in response
    assert "Solo Carlos" not in response


def test_renders_postponed_due_time(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [
            MedicationRecord(
                record_id="postpone",
                person="Carlos",
                name="Medicamento B",
                dosage="5 mg",
                schedules=["10:00"],
            )
        ],
        [
            MedicationIntake(
                intake_id="i2",
                medication_id="postpone",
                person="Carlos",
                scheduled_date="2026-07-27",
                scheduled_time="10:00",
                status="postergado",
                recorded_at="2026-07-27T10:05:00",
                due_at="2026-07-27T11:00:00",
            )
        ],
    )

    response = service.prepare("resumen de salud de Carlos").response

    assert "postergado hasta 11:00" in response
