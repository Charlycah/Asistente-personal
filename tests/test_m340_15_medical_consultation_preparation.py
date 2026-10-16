from datetime import datetime
from pathlib import Path

from app.medical_consultation_preparation import (
    MedicalConsultationPreparationService,
)
from app.secure_health_checkups import HealthCheckup, HealthCheckupRepository
from app.secure_medication_registry import (
    MedicationIntake,
    MedicationRecord,
    MedicationRegistryRepository,
)
from app.vital_sign_history import VitalSignRecord, VitalSignRepository

NOW = datetime(2026, 7, 28, 17, 0)


def _service(tmp_path: Path) -> MedicalConsultationPreparationService:
    return MedicalConsultationPreparationService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        VitalSignRepository(tmp_path / "vital_signs.json"),
        now=lambda: NOW,
    )


def test_ignores_unrelated_requests(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("Contame las noticias").handled


def test_builds_empty_factual_summary(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("preparar resumen para consulta de Carlos")

    assert result.handled
    assert "Resumen preconsulta de Carlos · 2026-07-28" in result.response
    assert "no hay medicamentos activos" in result.response
    assert "no hay controles activos" in result.response
    assert "no hay estudios activos" in result.response
    assert "No diagnostica" in result.response


def test_accepts_professional_context(tmp_path: Path) -> None:
    response = _service(tmp_path).prepare(
        "preparame informe para consulta de Cristina con la cardióloga"
    ).response

    assert "para cardióloga" in response


def test_keeps_people_separate_and_excludes_inactive_data(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [
            MedicationRecord(
                "carlos01", "Carlos", "Solo Carlos", "5 mg", ["08:00"]
            ),
            MedicationRecord(
                "crist01", "Cristina", "Solo Cristina", "10 mg", ["09:00"]
            ),
            MedicationRecord(
                "paused01",
                "Cristina",
                "Pausado",
                "1",
                ["10:00"],
                status="pausado",
            ),
        ]
    )

    response = service.prepare(
        "generar resumen preconsulta de Cristina"
    ).response

    assert "Solo Cristina" in response
    assert "Solo Carlos" not in response
    assert "Pausado" not in response


def test_includes_recent_medication_changes_and_adherence(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [
            MedicationRecord(
                "med00001",
                "Carlos",
                "Medicamento A",
                "5 mg",
                ["08:00"],
                start_date="2026-07-20",
                reviewed_on="2026-07-25",
            )
        ],
        [
            MedicationIntake(
                "i1",
                "med00001",
                "Carlos",
                "2026-07-27",
                "08:00",
                "tomado",
                "2026-07-27T08:05:00",
            ),
            MedicationIntake(
                "i2",
                "med00001",
                "Carlos",
                "2026-07-28",
                "08:00",
                "omitido",
                "2026-07-28T08:30:00",
            ),
        ],
    )

    response = service.prepare(
        "mostrar informe para consulta de Carlos"
    ).response

    assert "inicio documentada" in response
    assert "revisión documentada" in response
    assert "omitido: 1" in response
    assert "tomado: 1" in response


def test_includes_vital_signs_and_recent_studies(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.vital_repository.save(
        [
            VitalSignRecord("v1", "Cristina", "2026-07-10T09:00", weight=62),
            VitalSignRecord(
                "v2",
                "Cristina",
                "2026-07-28T09:00",
                blood_pressure="128/79",
                oxygen_saturation=98,
            ),
        ]
    )
    service.checkup_repository.save(
        [
            HealthCheckup(
                "study001",
                "Cristina",
                "Laboratorio general",
                "2026-07-24",
                "laboratorio",
                institution="Clínica Central",
            )
        ]
    )

    response = service.prepare(
        "prepará resumen para la consulta de Cristina"
    ).response

    assert "2 control(es)" in response
    assert "presión 128/79 mmHg" in response
    assert "Laboratorio general" in response
    assert "Clínica Central" in response


def test_limits_studies_to_five_and_excludes_archived(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.checkup_repository.save(
        [
            HealthCheckup(
                f"study{index}",
                "Carlos",
                f"Estudio {index}",
                f"2026-07-{index:02d}",
                "informe",
            )
            for index in range(1, 7)
        ]
        + [
            HealthCheckup(
                "archived",
                "Carlos",
                "Archivado",
                "2026-07-28",
                "informe",
                archived=True,
            )
        ]
    )

    response = service.prepare(
        "preparar informe preconsulta de Carlos"
    ).response

    assert "Estudio 6" in response
    assert "Estudio 2" in response
    assert "Estudio 1" not in response
    assert "Archivado" not in response
