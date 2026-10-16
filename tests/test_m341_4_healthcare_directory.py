from datetime import datetime
from pathlib import Path

from app.health_orchestrator import HealthOrchestratorService
from app.healthcare_directory import (
    HealthcareDirectoryRepository,
    HealthcareDirectoryService,
)
from app.medical_consultation_preparation import MedicalConsultationPreparationService
from app.secure_health_checkups import HealthCheckupRepository
from app.secure_medication_registry import MedicationRegistryRepository
from app.structured_symptom_registry import SymptomRepository
from app.vital_sign_history import VitalSignRepository

NOW = datetime(2026, 7, 28, 17, 0)


def _service(tmp_path: Path) -> HealthcareDirectoryService:
    return HealthcareDirectoryService(
        HealthcareDirectoryRepository(tmp_path / "directory.json")
    )


def test_ignores_unrelated_request(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("Contame las noticias").handled


def test_professional_requires_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    result = service.prepare(
        "registrar profesional de Carlos: nombre=Dra. Pérez | "
        "especialidad=cardiología | matrícula=MN 123 | teléfono=5555"
    )
    assert result.handled
    assert service.repository.load_professionals() == []
    service.prepare("confirmar directorio médico")
    record = service.repository.load_professionals()[0]
    assert record.person == "Carlos"
    assert record.specialty == "cardiología"


def test_center_requires_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar centro de salud de Cristina: nombre=Clínica Central | "
        "tipo=clínica | dirección=Calle 1 | teléfono=4444"
    )
    service.prepare("confirmar directorio medico")
    record = service.repository.load_centers()[0]
    assert record.person == "Cristina"
    assert record.address == "Calle 1"


def test_sessions_and_profiles_are_independent(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar profesional de Carlos: nombre=Dr. Uno", session_id="one"
    )
    service.prepare(
        "registrar profesional de Cristina: nombre=Dra. Dos", session_id="two"
    )
    service.prepare("cancelar directorio médico", session_id="one")
    service.prepare("confirmar directorio médico", session_id="two")
    assert [item.person for item in service.repository.load_professionals()] == [
        "Cristina"
    ]


def test_lists_only_requested_person(tmp_path: Path) -> None:
    service = _service(tmp_path)
    for session, command in (
        ("a", "registrar profesional de Carlos: nombre=Dr. Carlos"),
        ("b", "registrar profesional de Cristina: nombre=Dra. Cristina"),
    ):
        service.prepare(command, session_id=session)
        service.prepare("confirmar directorio médico", session_id=session)
    response = service.prepare("profesionales de Cristina").response
    assert "Dra. Cristina" in response
    assert "Dr. Carlos" not in response


def test_links_professional_and_center_after_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare("registrar profesional de Carlos: nombre=Dr. López")
    service.prepare("confirmar directorio médico")
    service.prepare("registrar centro de salud de Carlos: nombre=Hospital Sur")
    service.prepare("confirmar directorio médico")
    professional = service.repository.load_professionals()[0]
    center = service.repository.load_centers()[0]
    service.prepare(
        f"vincular profesional {professional.professional_id} "
        f"con centro {center.center_id}"
    )
    service.prepare("confirmar directorio médico")
    assert service.repository.load_professionals()[0].center_ids == (
        center.center_id,
    )


def test_rejects_cross_profile_link(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare("registrar profesional de Carlos: nombre=Dr. López")
    service.prepare("confirmar directorio médico")
    service.prepare("registrar centro de salud de Cristina: nombre=Hospital Sur")
    service.prepare("confirmar directorio médico")
    professional = service.repository.load_professionals()[0]
    center = service.repository.load_centers()[0]
    response = service.prepare(
        f"vincular profesional {professional.professional_id} "
        f"con centro {center.center_id}"
    ).response
    assert "personas diferentes" in response


def test_archive_is_confirmed(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare("registrar profesional de Carlos: nombre=Dr. López")
    service.prepare("confirmar directorio médico")
    record = service.repository.load_professionals()[0]
    service.prepare(f"archivar profesional {record.professional_id}")
    assert not service.repository.load_professionals()[0].archived
    service.prepare("confirmar directorio médico")
    assert service.repository.load_professionals()[0].archived


def test_orchestrator_includes_directory(tmp_path: Path) -> None:
    directory = HealthcareDirectoryRepository(tmp_path / "directory.json")
    service = HealthcareDirectoryService(directory)
    service.prepare(
        "registrar profesional de Carlos: nombre=Dra. Pérez | "
        "especialidad=cardiología"
    )
    service.prepare("confirmar directorio médico")
    orchestrator = HealthOrchestratorService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        now=lambda: NOW,
        vital_repository=VitalSignRepository(tmp_path / "vitals.json"),
        symptom_repository=SymptomRepository(tmp_path / "symptoms.json"),
        directory_repository=directory,
    )
    response = orchestrator.prepare("resumen de salud de Carlos").response
    assert "Equipo y centros de salud" in response
    assert "Dra. Pérez" in response


def test_consultation_and_desktop_route_directory(tmp_path: Path) -> None:
    from app.desktop_ui import DesktopConversationController
    from app.ui_adapter import UIResponse

    directory = HealthcareDirectoryRepository(tmp_path / "directory.json")
    service = HealthcareDirectoryService(directory)
    service.prepare(
        "registrar profesional de Cristina: nombre=Dra. Gómez | "
        "especialidad=neumonología"
    )
    service.prepare("confirmar directorio médico")
    consultation = MedicalConsultationPreparationService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        VitalSignRepository(tmp_path / "vitals.json"),
        now=lambda: NOW,
        directory_repository=directory,
    )
    response = consultation.prepare(
        "preparar resumen para consulta de Cristina con la Dra. Gómez"
    ).response
    assert "Dra. Gómez" in response
    assert "profesional indicado" in response

    class Adapter:
        def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
            return UIResponse(text="fallback")

    controller = DesktopConversationController(Adapter())
    controller.healthcare_directory = _service(tmp_path / "desktop")
    messages = controller.submit(
        "registrar centro de salud de Carlos: nombre=Clínica Norte"
    )
    assert "Confirmá el centro" in messages[-1].text
