from datetime import datetime
from pathlib import Path

from app.health_orchestrator import HealthOrchestratorService
from app.secure_health_checkups import HealthCheckupRepository
from app.secure_medication_registry import MedicationRegistryRepository
from app.vital_sign_history import (
    VitalSignHistoryService,
    VitalSignRecord,
    VitalSignRepository,
)

NOW = datetime(2026, 7, 28, 17, 0)


def _service(tmp_path: Path) -> VitalSignHistoryService:
    return VitalSignHistoryService(
        VitalSignRepository(tmp_path / "vital_signs.json"),
        now=lambda: NOW,
    )


def test_ignores_unrelated_requests(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("Contame las noticias")

    assert not result.handled


def test_requires_confirmation_before_persisting(tmp_path: Path) -> None:
    service = _service(tmp_path)

    prepared = service.prepare(
        "registrar signos de Carlos: fecha=2026-07-28T09:00 | "
        "presión=128/82 | glucemia=101 | peso=76,5 | saturación=97 | "
        "temperatura=36,4 | pulso=68"
    )

    assert prepared.handled
    assert service.repository.load() == []
    confirmed = service.prepare("confirmar signos")
    records = service.repository.load()
    assert "Guardé el control" in confirmed.response
    assert len(records) == 1
    assert records[0].person == "Carlos"
    assert records[0].blood_pressure == "128/82"
    assert records[0].weight == 76.5


def test_cancellation_does_not_store_data(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare("registrar signos de Cristina: peso=61")

    result = service.prepare("cancelar signos")

    assert result.handled
    assert service.repository.load() == []


def test_keeps_people_separate_in_history(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            VitalSignRecord("c1", "Carlos", "2026-07-27T09:00", weight=76),
            VitalSignRecord("c2", "Cristina", "2026-07-27T10:00", weight=61),
        ]
    )

    response = service.prepare("historial de signos de Cristina").response

    assert "peso 61 kg" in response
    assert "peso 76 kg" not in response


def test_describes_numeric_trend_without_clinical_interpretation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            VitalSignRecord("a", "Carlos", "2026-07-01T09:00", weight=78),
            VitalSignRecord("b", "Carlos", "2026-07-28T09:00", weight=76.5),
        ]
    )

    response = service.prepare("tendencia de peso de Carlos").response

    assert "78 a 76.5 kg" in response
    assert "variación -1.5" in response
    assert "no se interpreta clínicamente" in response


def test_describes_blood_pressure_trend(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            VitalSignRecord(
                "a", "Cristina", "2026-07-20T09:00", blood_pressure="135/85"
            ),
            VitalSignRecord(
                "b", "Cristina", "2026-07-28T09:00", blood_pressure="130/80"
            ),
        ]
    )

    response = service.prepare("tendencia de presión de Cristina").response

    assert "135/85 a 130/80" in response
    assert "variación -5/-5 mmHg" in response


def test_weekly_summary_calculates_descriptive_averages(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            VitalSignRecord(
                "a", "Carlos", "2026-07-25T09:00", heart_rate=70, weight=77
            ),
            VitalSignRecord(
                "b", "Carlos", "2026-07-28T09:00", heart_rate=74, weight=76
            ),
        ]
    )

    response = service.prepare("resumen semanal de signos de Carlos").response

    assert "peso: promedio 76.5 kg; 2 registros" in response
    assert "frecuencia cardíaca: promedio 72.0 lpm; 2 registros" in response
    assert "sin diagnóstico ni alertas clínicas" in response


def test_excludes_archived_and_old_records(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            VitalSignRecord("old", "Carlos", "2026-06-01T09:00", weight=90),
            VitalSignRecord(
                "archived",
                "Carlos",
                "2026-07-28T09:00",
                weight=80,
                archived=True,
            ),
            VitalSignRecord("active", "Carlos", "2026-07-27T09:00", weight=76),
        ]
    )

    response = service.prepare(
        "historial de signos de Carlos de los últimos 7 días"
    ).response

    assert "peso 76 kg" in response
    assert "peso 90 kg" not in response
    assert "peso 80 kg" not in response


def test_health_orchestrator_includes_latest_vital_control(tmp_path: Path) -> None:
    vital_repository = VitalSignRepository(tmp_path / "vital_signs.json")
    vital_repository.save(
        [
            VitalSignRecord("old", "Cristina", "2026-07-20T09:00", weight=62),
            VitalSignRecord(
                "new",
                "Cristina",
                "2026-07-28T09:00",
                blood_pressure="128/79",
                oxygen_saturation=98,
            ),
        ]
    )
    service = HealthOrchestratorService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        now=lambda: NOW,
        vital_repository=vital_repository,
    )

    response = service.prepare("resumen de salud de Cristina").response

    assert "Último control de signos" in response
    assert "2026-07-28T09:00" in response
    assert "presión 128/79 mmHg" in response
    assert "saturación 98 %" in response
    assert "peso 62 kg" not in response
