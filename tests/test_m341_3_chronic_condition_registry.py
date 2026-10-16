from datetime import datetime
from pathlib import Path

from app.chronic_condition_registry import (
    ChronicConditionRecord,
    ChronicConditionRegistryService,
    ChronicConditionRepository,
)
from app.health_orchestrator import HealthOrchestratorService
from app.medical_consultation_preparation import (
    MedicalConsultationPreparationService,
)
from app.secure_health_checkups import HealthCheckupRepository
from app.secure_medication_registry import (
    MedicationRecord,
    MedicationRegistryRepository,
)
from app.structured_symptom_registry import SymptomEpisode, SymptomRepository
from app.vital_sign_history import VitalSignRecord, VitalSignRepository

NOW = datetime(2026, 7, 28, 17, 0)


def _service(tmp_path: Path) -> ChronicConditionRegistryService:
    return ChronicConditionRegistryService(
        ChronicConditionRepository(tmp_path / "conditions.json"),
        MedicationRegistryRepository(tmp_path / "medications.json"),
        VitalSignRepository(tmp_path / "vitals.json"),
        SymptomRepository(tmp_path / "symptoms.json"),
    )


def test_ignores_unrelated_requests(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("Contame las noticias").handled


def test_requires_confirmation_and_stores_structured_condition(tmp_path: Path) -> None:
    service = _service(tmp_path)
    prepared = service.prepare(
        "registrar condición de Carlos: nombre=hipertensión | "
        "diagnóstico=2020-05 | estado=activa | profesional=Dra. Pérez | "
        "centro=Clínica Central | medicación=Losartán | "
        "seguimiento=presión arterial, frecuencia cardíaca | "
        "controles=cardiología semestral | objetivos=objetivo indicado | "
        "notas=registro confirmado",
        session_id="carlos",
    )
    assert prepared.handled
    assert service.repository.load() == []
    service.prepare("confirmar condición", session_id="carlos")
    records = service.repository.load()
    assert len(records) == 1
    assert records[0].person == "Carlos"
    assert records[0].name == "hipertensión"
    assert records[0].monitoring_metrics == (
        "presión arterial",
        "frecuencia cardíaca",
    )


def test_rejects_missing_name_and_unknown_status(tmp_path: Path) -> None:
    service = _service(tmp_path)
    assert not service.prepare(
        "registrar condición de Carlos: estado=activa"
    ).handled
    assert not service.prepare(
        "registrar condición de Carlos: nombre=asma | estado=inventado"
    ).handled


def test_cancellation_and_sessions_are_independent(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar condición de Carlos: nombre=hipertensión",
        session_id="one",
    )
    service.prepare(
        "registrar condición de Cristina: nombre=asma",
        session_id="two",
    )
    service.prepare("cancelar condición", session_id="one")
    service.prepare("confirmar condición", session_id="two")
    assert [item.person for item in service.repository.load()] == ["Cristina"]


def test_lists_only_requested_person_and_non_archived_records(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            ChronicConditionRecord("carlos01", "Carlos", "hipertensión"),
            ChronicConditionRecord("cristi01", "Cristina", "asma"),
            ChronicConditionRecord(
                "cristi02",
                "Cristina",
                "artrosis",
                status="archivada",
                archived=True,
            ),
        ]
    )
    response = service.prepare("enfermedades crónicas de Cristina").response
    assert "asma" in response
    assert "hipertensión" not in response
    assert "artrosis" not in response


def test_updates_status_and_archives_after_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [ChronicConditionRecord("abcd1234", "Carlos", "hipertensión")]
    )
    service.prepare("actualizar condición abcd1234: estado=controlada")
    assert service.repository.load()[0].status == "activa"
    service.prepare("confirmar condición")
    assert service.repository.load()[0].status == "controlada"
    service.prepare("archivar condición abcd1234")
    service.prepare("confirmar condición")
    assert service.repository.load()[0].archived


def test_specific_followup_integrates_confirmed_local_data(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            ChronicConditionRecord(
                "cond0001",
                "Carlos",
                "hipertensión",
                professional="Dra. Pérez",
                health_center="Clínica Central",
                related_medications=("Losartán",),
                monitoring_metrics=("presión arterial",),
                followups=("cardiología semestral",),
                professional_goals=("meta indicada por profesional",),
            )
        ]
    )
    service.medication_repository.save(
        [
            MedicationRecord(
                record_id="med00001",
                person="Carlos",
                name="Losartán",
                dosage="50 mg",
                schedules=("08:00",),
                status="activo",
            )
        ]
    )
    service.vital_repository.save(
        [
            VitalSignRecord(
                record_id="vit00001",
                person="Carlos",
                measured_at="2026-07-28T09:00",
                blood_pressure="128/82",
            )
        ]
    )
    service.symptom_repository.save(
        [
            SymptomEpisode(
                episode_id="sym00001",
                person="Carlos",
                symptom="mareo",
                started_at="2026-07-28T10:00",
            )
        ]
    )
    response = service.prepare("seguimiento de hipertensión de Carlos").response
    assert "Losartán (50 mg)" in response
    assert "128/82 mmHg" in response
    assert "mareo" in response
    assert "No determina" in response


def test_orchestrator_includes_non_archived_conditions(tmp_path: Path) -> None:
    chronic = ChronicConditionRepository(tmp_path / "conditions.json")
    chronic.save(
        [
            ChronicConditionRecord("active01", "Cristina", "asma"),
            ChronicConditionRecord(
                "old00001",
                "Cristina",
                "artrosis",
                status="archivada",
                archived=True,
            ),
        ]
    )
    service = HealthOrchestratorService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        now=lambda: NOW,
        vital_repository=VitalSignRepository(tmp_path / "vitals.json"),
        symptom_repository=SymptomRepository(tmp_path / "symptoms.json"),
        chronic_repository=chronic,
    )
    response = service.prepare("resumen de salud de Cristina").response
    assert "Condiciones crónicas" in response
    assert "asma" in response
    assert "artrosis" not in response


def test_consultation_summary_includes_chronic_conditions(tmp_path: Path) -> None:
    chronic = ChronicConditionRepository(tmp_path / "conditions.json")
    chronic.save(
        [
            ChronicConditionRecord(
                "cond0001",
                "Carlos",
                "diabetes",
                status="en estudio",
                professional="Dr. López",
                health_center="Hospital Central",
            )
        ]
    )
    service = MedicalConsultationPreparationService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        VitalSignRepository(tmp_path / "vitals.json"),
        now=lambda: NOW,
        chronic_repository=chronic,
    )
    response = service.prepare("preparar resumen para consulta de Carlos").response
    assert "Condiciones crónicas" in response
    assert "diabetes" in response
    assert "en estudio" in response
    assert "Dr. López" in response


def test_desktop_controller_routes_condition_commands(
    tmp_path: Path,
) -> None:
    from app.desktop_ui import DesktopConversationController
    from app.ui_adapter import UIResponse

    class Adapter:
        def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
            return UIResponse(text="fallback")

    controller = DesktopConversationController(Adapter())
    controller.chronic_conditions = _service(tmp_path)
    result = controller.submit(
        "registrar condición de Carlos: nombre=hipertensión"
    )
    assert "Confirmá la condición" in result[-1].text
