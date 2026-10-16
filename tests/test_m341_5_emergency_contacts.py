from datetime import datetime
from pathlib import Path

from app.emergency_contacts import EmergencyContactRepository, EmergencyContactService
from app.health_orchestrator import HealthOrchestratorService
from app.medical_consultation_preparation import MedicalConsultationPreparationService
from app.secure_health_checkups import HealthCheckupRepository
from app.secure_medication_registry import MedicationRegistryRepository

NOW = datetime(2026, 7, 28, 17, 0)


def _service(tmp_path: Path) -> EmergencyContactService:
    repository = EmergencyContactRepository(tmp_path / "emergency.json")
    return EmergencyContactService(repository)


def _register(service: EmergencyContactService, person: str = "Carlos") -> None:
    service.prepare(
        f"registrar contacto de emergencia de {person}: nombre=Ana | "
        "relación=hermana | teléfono=1111 | prioridad=1"
    )
    service.prepare("confirmar emergencia")


def test_ignores_unrelated_request(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("Contame las noticias").handled


def test_contact_requires_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    result = service.prepare(
        "registrar contacto de emergencia de Carlos: nombre=Ana | "
        "relación=hermana | teléfono=1111 | prioridad=2"
    )
    assert result.handled
    assert service.repository.load_contacts() == []
    service.prepare("confirmar emergencia")
    contact = service.repository.load_contacts()[0]
    assert contact.relationship == "hermana"
    assert contact.priority == 2


def test_requires_name_phone_and_valid_priority(tmp_path: Path) -> None:
    service = _service(tmp_path)
    assert not service.prepare(
        "registrar contacto de emergencia de Carlos: nombre=Ana | prioridad=10"
    ).handled


def test_sessions_and_profiles_are_independent(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar contacto de emergencia de Carlos: nombre=Ana | teléfono=1",
        session_id="a",
    )
    service.prepare(
        "registrar contacto de emergencia de Cristina: nombre=Luis | teléfono=2",
        session_id="b",
    )
    service.prepare("cancelar emergencia", session_id="a")
    service.prepare("confirmar emergencia", session_id="b")
    assert [item.person for item in service.repository.load_contacts()] == ["Cristina"]


def test_lists_by_priority_and_person(tmp_path: Path) -> None:
    service = _service(tmp_path)
    for session, command in (
        (
            "a",
            "registrar contacto de emergencia de Carlos: "
            "nombre=Dos | teléfono=2 | prioridad=2",
        ),
        (
            "b",
            "registrar contacto de emergencia de Carlos: "
            "nombre=Uno | teléfono=1 | prioridad=1",
        ),
        ("c", "registrar contacto de emergencia de Cristina: nombre=Otro | teléfono=3"),
    ):
        service.prepare(command, session_id=session)
        service.prepare("confirmar emergencia", session_id=session)
    response = service.prepare("contactos de emergencia de Carlos").response
    assert response.index("Uno") < response.index("Dos")
    assert "Otro" not in response


def test_coverage_replaces_previous_after_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar cobertura de emergencia de Carlos: prestador=OS Uno | "
        "plan=A | afiliado=123 | teléfono=0800"
    )
    service.prepare("confirmar emergencia")
    service.prepare(
        "registrar cobertura de emergencia de Carlos: prestador=OS Dos | teléfono=0810"
    )
    service.prepare("confirmar emergencia")
    records = service.repository.load_coverages()
    assert len(records) == 1
    assert records[0].provider == "OS Dos"


def test_archive_requires_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _register(service)
    contact = service.repository.load_contacts()[0]
    service.prepare(f"archivar contacto de emergencia {contact.contact_id}")
    assert not service.repository.load_contacts()[0].archived
    service.prepare("confirmar emergencia")
    assert service.repository.load_contacts()[0].archived


def test_emergency_summary_includes_coverage_and_safety_limit(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _register(service)
    service.prepare(
        "registrar cobertura de emergencia de Carlos: prestador=OS Uno | teléfono=0800"
    )
    service.prepare("confirmar emergencia")
    response = service.prepare("ficha de emergencia de Carlos").response
    assert "Ana" in response
    assert "OS Uno" in response
    assert "no realiza llamadas" in response


def test_orchestrator_and_consultation_include_contacts(tmp_path: Path) -> None:
    repository = EmergencyContactRepository(tmp_path / "emergency.json")
    service = EmergencyContactService(repository)
    _register(service)
    medications = MedicationRegistryRepository(tmp_path / "medications.json")
    checkups = HealthCheckupRepository(tmp_path / "checkups.json")
    orchestrator = HealthOrchestratorService(
        medications, checkups, now=lambda: NOW, emergency_repository=repository
    )
    assert "Ana" in orchestrator.prepare("resumen de salud de Carlos").response
    consultation = MedicalConsultationPreparationService(
        medications, checkups, now=lambda: NOW, emergency_repository=repository
    )
    assert "Ana" in consultation.prepare(
        "preparar resumen para consulta de Carlos"
    ).response


def test_desktop_routes_emergency_contact(tmp_path: Path) -> None:
    from app.desktop_ui import DesktopConversationController
    from app.ui_adapter import UIResponse

    class Adapter:
        def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
            return UIResponse(text="fallback")

    controller = DesktopConversationController(Adapter())
    controller.emergency_contacts = _service(tmp_path)
    messages = controller.submit(
        "registrar contacto de emergencia de Carlos: nombre=Ana | teléfono=1111"
    )
    assert "Confirmá el contacto" in messages[-1].text
