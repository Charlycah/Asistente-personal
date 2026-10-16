from datetime import datetime
from pathlib import Path

from app.allergy_registry import AllergyRecord, AllergyRepository
from app.chronic_condition_registry import (
    ChronicConditionRecord,
    ChronicConditionRepository,
)
from app.conversational_health_guidance import ConversationalHealthGuidanceService
from app.desktop_ui import DesktopConversationController, DesktopMessagePresenter
from app.emergency_contacts import EmergencyContactRepository
from app.secure_medication_registry import (
    MedicationRecord,
    MedicationRegistryRepository,
)
from app.structured_symptom_registry import SymptomEpisode, SymptomRepository
from app.ui_adapter import UIResponse

NOW = datetime(2026, 7, 28, 12, 0)


class _Adapter:
    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        return UIResponse(text=f"fallback:{text}")


def _service(tmp_path: Path) -> ConversationalHealthGuidanceService:
    return ConversationalHealthGuidanceService(
        medication_repository=MedicationRegistryRepository(
            tmp_path / "medications.json"
        ),
        symptom_repository=SymptomRepository(tmp_path / "symptoms.json"),
        allergy_repository=AllergyRepository(tmp_path / "allergies.json"),
        chronic_repository=ChronicConditionRepository(tmp_path / "chronic.json"),
        emergency_repository=EmergencyContactRepository(tmp_path / "emergency.json"),
        now=lambda: NOW,
    )


def test_ignores_unrelated_request(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("decime el clima").handled


def test_supports_three_conversational_commands(tmp_path: Path) -> None:
    service = _service(tmp_path)
    assert service.prepare("guía de salud de Carlos").handled
    assert service.prepare("orientame sobre la salud de Cristina").handled
    assert service.prepare("qué debería revisar de salud de Carlos").handled


def test_returns_informative_level_without_priorities(tmp_path: Path) -> None:
    response = _service(tmp_path).prepare("guía de salud de Carlos").response
    assert "Informativo:" in response
    assert "Preventiva:" in response
    assert "No diagnostica" in response


def test_uses_urgent_level_for_explicit_alarm_symptom(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.symptom_repository.save(
        [SymptomEpisode("s1", "Carlos", "dolor de pecho", "2026-07-28T10:00")]
    )
    response = service.prepare("orientame sobre la salud de Carlos").response
    assert "Urgente:" in response
    assert "asistencia médica inmediata" in response


def test_uses_precaution_level_for_high_intensity_symptom(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.symptom_repository.save(
        [SymptomEpisode("s1", "Cristina", "cefalea", "2026-07-28T10:00", 8)]
    )
    response = service.prepare("guía de salud de Cristina").response
    assert "Precaución:" in response
    assert "intensidad registrada de 7/10 o más" in response


def test_uses_precaution_level_for_severe_allergy(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.allergy_repository.save(
        [AllergyRecord("a1", "Carlos", "Penicilina", "medicamento", severity="grave")]
    )
    response = service.prepare("guía de salud de Carlos").response
    assert "Precaución:" in response
    assert "alergia(s) con gravedad alta o grave" in response


def test_reports_pending_medication_followup(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [MedicationRecord("m1", "Carlos", "Losartán", "50 mg", ["08:00"])]
    )
    response = service.prepare("guía de salud de Carlos").response
    assert "Seguimiento:" in response
    assert "confirmar 1 toma(s)" in response


def test_reports_chronic_condition_followup(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.chronic_repository.save(
        [ChronicConditionRecord("c1", "Cristina", "Hipertensión")]
    )
    response = service.prepare("guía de salud de Cristina").response
    assert "revisar el seguimiento documentado de 1 condición(es)" in response


def test_keeps_people_strictly_separate(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.symptom_repository.save(
        [SymptomEpisode("s1", "Cristina", "dolor de pecho", "2026-07-28T10:00")]
    )
    response = service.prepare("guía de salud de Carlos").response
    assert "Urgente:" not in response


def test_desktop_controller_routes_guidance_before_fallback(tmp_path: Path) -> None:
    controller = DesktopConversationController(_Adapter(), DesktopMessagePresenter())
    controller.health_guidance = _service(tmp_path)
    messages = controller.submit("guía de salud de Carlos")
    assert len(messages) == 2
    assert messages[1].text.startswith("Guía conversacional de salud de Carlos")
