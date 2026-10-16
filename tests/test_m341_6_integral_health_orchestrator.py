from datetime import datetime
from pathlib import Path

from app.allergy_registry import AllergyRecord, AllergyRepository
from app.chronic_condition_registry import (
    ChronicConditionRecord,
    ChronicConditionRepository,
)
from app.emergency_contacts import (
    EmergencyContact,
    EmergencyContactRepository,
)
from app.health_orchestrator import HealthOrchestratorService
from app.healthcare_directory import HealthcareDirectoryRepository
from app.secure_health_checkups import HealthCheckupRepository
from app.secure_medication_registry import (
    MedicationRecord,
    MedicationRegistryRepository,
)
from app.structured_symptom_registry import SymptomEpisode, SymptomRepository
from app.vital_sign_history import VitalSignRepository

NOW = datetime(2026, 7, 28, 12, 0)


def _service(tmp_path: Path) -> HealthOrchestratorService:
    return HealthOrchestratorService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        now=lambda: NOW,
        vital_repository=VitalSignRepository(tmp_path / "vitals.json"),
        symptom_repository=SymptomRepository(tmp_path / "symptoms.json"),
        allergy_repository=AllergyRepository(tmp_path / "allergies.json"),
        chronic_repository=ChronicConditionRepository(tmp_path / "chronic.json"),
        directory_repository=HealthcareDirectoryRepository(tmp_path / "directory.json"),
        emergency_repository=EmergencyContactRepository(tmp_path / "emergency.json"),
    )


def test_ignores_unrelated_request(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("decime el clima").handled


def test_builds_empty_integral_panorama(tmp_path: Path) -> None:
    response = _service(tmp_path).prepare(
        "orquestador integral de salud de Carlos"
    ).response
    assert "Orquestador integral de salud de Carlos" in response
    assert "Prioridades registradas" in response
    assert "Preventiva" in response


def test_supports_integral_command_aliases(tmp_path: Path) -> None:
    service = _service(tmp_path)
    assert service.prepare("panorama integral de Cristina").handled
    assert service.prepare("prioridades de salud de Carlos").handled


def test_prioritizes_high_intensity_active_symptoms(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.symptom_repository.save([
        SymptomEpisode("s1", "Carlos", "dolor", "2026-07-28T10:00", intensity=8)
    ])
    response = service.prepare("panorama integral de Carlos").response
    assert "Alta: 1 síntoma(s) activo(s)" in response
    assert "intensidad 8/10" in response


def test_prioritizes_severe_documented_allergy(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.allergy_repository.save([
        AllergyRecord("a1", "Cristina", "Penicilina", "medicamento", severity="grave")
    ])
    response = service.prepare("prioridades de salud de Cristina").response
    assert "Alta: 1 alergia(s) activa(s)" in response


def test_reports_pending_medication_followup(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save([
        MedicationRecord("m1", "Carlos", "Losartán", "50 mg", ["08:00"])
    ])
    response = service.prepare("panorama integral de Carlos").response
    assert "1 toma(s) de hoy pendientes de confirmar" in response


def test_reports_chronic_condition_followup(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.chronic_repository.save([
        ChronicConditionRecord("c1", "Carlos", "Hipertensión")
    ])
    response = service.prepare("orquestador integral de salud de Carlos").response
    assert "1 condición(es) crónica(s) registrada(s)" in response
    assert "Hipertensión" in response


def test_emergency_contact_removes_missing_data_priority(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.emergency_repository.save(
        [EmergencyContact("e1", "Carlos", "Ana", "hermana", "1111")],
        [],
    )
    response = service.prepare("panorama integral de Carlos").response
    assert "no hay contactos ni cobertura" not in response
    assert "Ana" in response


def test_keeps_people_strictly_separate(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.symptom_repository.save([
        SymptomEpisode("s1", "Cristina", "mareo", "2026-07-28T09:00", intensity=5)
    ])
    response = service.prepare("panorama integral de Carlos").response
    assert "mareo" not in response


def test_preserves_legacy_health_summary_contract(tmp_path: Path) -> None:
    response = _service(tmp_path).prepare("resumen de salud de Carlos").response
    assert response.startswith("Resumen de salud de Carlos")
    assert "Este resumen reúne datos confirmados" in response
