from datetime import datetime
from pathlib import Path

from app.advanced_clinical_safety import AdvancedClinicalSafetyService
from app.allergy_registry import (
    AllergyRecord,
    AllergyRegistryService,
    AllergyRepository,
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
from app.structured_symptom_registry import SymptomRepository
from app.vital_sign_history import VitalSignRepository

NOW = datetime(2026, 7, 28, 17, 0)


def _service(tmp_path: Path) -> AllergyRegistryService:
    return AllergyRegistryService(AllergyRepository(tmp_path / "allergies.json"))


def test_ignores_unrelated_requests(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("Contame las noticias").handled


def test_requires_confirmation_and_stores_structured_allergy(tmp_path: Path) -> None:
    service = _service(tmp_path)
    prepared = service.prepare(
        "registrar alergia de Cristina: alérgeno=penicilina | "
        "tipo=medicamento | reacción=urticaria | gravedad=moderada | "
        "fecha=2024-03 | confirmada=sí | profesional=Dra. Pérez | "
        "institución=Clínica Central | notas=evitar exposición",
        session_id="cristina",
    )

    assert prepared.handled
    assert service.repository.load() == []
    confirmed = service.prepare("confirmar alergia", session_id="cristina")
    records = service.repository.load()
    assert "Guardé la alergia" in confirmed.response
    assert len(records) == 1
    assert records[0].person == "Cristina"
    assert records[0].allergen == "penicilina"
    assert records[0].professional_confirmed


def test_rejects_unknown_type_and_status(tmp_path: Path) -> None:
    service = _service(tmp_path)
    assert not service.prepare(
        "registrar alergia de Carlos: alérgeno=polen | tipo=desconocida"
    ).handled
    assert not service.prepare(
        "registrar alergia de Carlos: alérgeno=polen | estado=inventado"
    ).handled


def test_cancellation_and_sessions_are_independent(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar alergia de Carlos: alérgeno=polen | tipo=ambiental",
        session_id="one",
    )
    service.prepare(
        "registrar alergia de Cristina: alérgeno=maní | tipo=alimento",
        session_id="two",
    )
    service.prepare("cancelar alergia", session_id="one")
    service.prepare("confirmar alergia", session_id="two")
    assert [item.person for item in service.repository.load()] == ["Cristina"]


def test_lists_only_active_allergies_for_requested_person(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            AllergyRecord("carlos01", "Carlos", "polen", "ambiental"),
            AllergyRecord("cristi01", "Cristina", "maní", "alimento"),
            AllergyRecord(
                "cristi02",
                "Cristina",
                "látex",
                "material",
                status="archivada",
                archived=True,
            ),
        ]
    )
    response = service.prepare("alergias activas de Cristina").response
    assert "maní" in response
    assert "polen" not in response
    assert "látex" not in response


def test_updates_status_and_archives_after_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [AllergyRecord("abcd1234", "Carlos", "polen", "ambiental")]
    )
    service.prepare("actualizar alergia abcd1234: estado=descartada")
    assert service.repository.load()[0].status == "activa"
    service.prepare("confirmar alergia")
    assert service.repository.load()[0].status == "descartada"

    service.prepare("archivar alergia abcd1234")
    service.prepare("confirmar alergia")
    assert service.repository.load()[0].archived


def test_exact_medication_match_is_reported_without_family_inference(
    tmp_path: Path,
) -> None:
    medications = MedicationRegistryRepository(tmp_path / "medications.json")
    medications.save(
        [
            MedicationRecord(
                record_id="med00001",
                person="Cristina",
                name="Penicilina",
                dosage="500 mg",
                schedules=("08:00",),
                status="activo",
            ),
            MedicationRecord(
                record_id="med00002",
                person="Cristina",
                name="Amoxicilina",
                dosage="500 mg",
                schedules=("20:00",),
                status="activo",
            ),
        ]
    )
    allergies = AllergyRepository(tmp_path / "allergies.json")
    allergies.save(
        [AllergyRecord("all00001", "Cristina", "penicilina", "medicamento")]
    )
    service = AdvancedClinicalSafetyService(
        medication_repository=medications,
        allergy_repository=allergies,
        now=lambda: NOW,
    )
    response = service.prepare("seguridad clínica de Cristina").response
    assert "Penicilina coincide exactamente" in response
    assert "Amoxicilina coincide exactamente" not in response
    assert "revisar con profesional" in response


def test_orchestrator_includes_only_active_allergies(tmp_path: Path) -> None:
    allergies = AllergyRepository(tmp_path / "allergies.json")
    allergies.save(
        [
            AllergyRecord(
                "active01",
                "Cristina",
                "maní",
                "alimento",
                reaction="urticaria",
            ),
            AllergyRecord(
                "closed01",
                "Cristina",
                "látex",
                "material",
                status="descartada",
            ),
        ]
    )
    service = HealthOrchestratorService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        now=lambda: NOW,
        vital_repository=VitalSignRepository(tmp_path / "vitals.json"),
        symptom_repository=SymptomRepository(tmp_path / "symptoms.json"),
        allergy_repository=allergies,
    )
    response = service.prepare("resumen de salud de Cristina").response
    assert "Alergias activas" in response
    assert "maní" in response
    assert "urticaria" in response
    assert "látex" not in response


def test_consultation_summary_includes_allergies(tmp_path: Path) -> None:
    allergies = AllergyRepository(tmp_path / "allergies.json")
    allergies.save(
        [
            AllergyRecord(
                "all00001",
                "Carlos",
                "ibuprofeno",
                "medicamento",
                reaction="hinchazón",
                severity="alta",
            )
        ]
    )
    service = MedicalConsultationPreparationService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        VitalSignRepository(tmp_path / "vitals.json"),
        now=lambda: NOW,
        allergy_repository=allergies,
    )
    response = service.prepare("preparar resumen para consulta de Carlos").response
    assert "Alergias activas" in response
    assert "ibuprofeno" in response
    assert "hinchazón" in response
    assert "gravedad alta" in response


def test_desktop_controller_routes_allergy_commands(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from app.desktop_ui import DesktopConversationController
    from app.ui_adapter import UIResponse

    class Adapter:
        def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
            return UIResponse(text="fallback")

    controller = DesktopConversationController(Adapter())
    controller.allergies = _service(tmp_path)
    result = controller.submit(
        "registrar alergia de Carlos: alérgeno=polen | tipo=ambiental"
    )
    assert "Confirmá la alergia" in result[-1].text
