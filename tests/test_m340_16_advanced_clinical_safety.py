from datetime import datetime
from pathlib import Path

from app.advanced_clinical_safety import (
    AdvancedClinicalSafetyService,
    ClinicalSafetyRepository,
)
from app.desktop_ui import DesktopConversationController
from app.secure_medication_registry import (
    MedicationRecord,
    MedicationRegistryRepository,
)
from app.ui_adapter import UIResponse

NOW = datetime(2026, 7, 28, 17, 0)


class _Adapter:
    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        return UIResponse(text="fallback")


def _service(tmp_path: Path) -> AdvancedClinicalSafetyService:
    return AdvancedClinicalSafetyService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        ClinicalSafetyRepository(tmp_path / "clinical_safety.json"),
        now=lambda: NOW,
    )


def test_ignores_unrelated_requests(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("hola Roby").handled


def test_empty_report_is_factual(tmp_path: Path) -> None:
    response = _service(tmp_path).prepare("seguridad clínica de Carlos").response

    assert "Seguridad clínica de Carlos" in response
    assert response.count("sin hallazgos") == 5
    assert "No suspendas" in response


def test_detects_duplicates_expired_and_upcoming_end_dates(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [
            MedicationRecord("dup00001", "Carlos", "Med A", "5 mg", ["08:00"]),
            MedicationRecord("dup00002", "Carlos", "Med A", "5 mg", ["20:00"]),
            MedicationRecord(
                "expired1",
                "Carlos",
                "Med vencido",
                "1",
                ["09:00"],
                end_date="2026-07-20",
            ),
            MedicationRecord(
                "renew001",
                "Carlos",
                "Med próximo",
                "1",
                ["10:00"],
                end_date="2026-08-10",
            ),
        ]
    )

    response = service.prepare("control de seguridad de Carlos").response

    assert "Med A · registros dup00001, dup00002" in response
    assert "Med vencido · finalizó 2026-07-20" in response
    assert "Med próximo · finaliza 2026-08-10" in response


def test_registers_confirmed_interaction_and_matches_active_medications(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [
            MedicationRecord("a0000001", "Cristina", "Med A", "1", ["08:00"]),
            MedicationRecord("b0000001", "Cristina", "Med B", "1", ["20:00"]),
        ]
    )
    draft = service.prepare(
        "registrar interacción potencial: medicamento a=Med A | "
        "medicamento b=Med B | nota=verificar combinación | fuente=Dra. Pérez",
        session_id="s",
    )
    confirmed = service.prepare("confirmar seguridad", session_id="s")

    assert draft.handled
    assert "Guardé la regla" in confirmed.response
    response = service.prepare("seguridad clínica de Cristina").response
    assert "Med A + Med B" in response
    assert "Dra. Pérez" in response


def test_interactions_do_not_cross_people(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.medication_repository.save(
        [
            MedicationRecord("a0000001", "Carlos", "Med A", "1", ["08:00"]),
            MedicationRecord("b0000001", "Cristina", "Med B", "1", ["20:00"]),
        ]
    )
    service.prepare(
        "registrar interacción potencial: medicamento a=Med A | "
        "medicamento b=Med B | nota=revisar | fuente=profesional",
        session_id="s",
    )
    service.prepare("confirmar seguridad", session_id="s")

    assert "Med A + Med B" not in service.prepare(
        "seguridad clínica de Carlos"
    ).response


def test_registers_overdue_and_upcoming_study_controls(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar control de Carlos: estudio=Laboratorio | vence=2026-07-20 | "
        "profesional=Dra. Pérez",
        session_id="a",
    )
    service.prepare("confirmar seguridad", session_id="a")
    service.prepare(
        "registrar control de Carlos: estudio=Cardiología | vence=2026-08-15",
        session_id="b",
    )
    service.prepare("confirmar seguridad", session_id="b")

    response = service.prepare("seguridad clínica de Carlos").response

    assert "Laboratorio · vencido · 2026-07-20" in response
    assert "Cardiología · próximo · 2026-08-15" in response


def test_requires_confirmation_and_supports_cancel(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar control de Cristina: estudio=Ecografía | vence=2026-08-01",
        session_id="s",
    )
    result = service.prepare("cancelar seguridad", session_id="s")

    assert "Cancelé" in result.response
    assert service.repository.load_controls() == []


def test_desktop_routes_clinical_safety_without_fallback(tmp_path: Path) -> None:
    controller = DesktopConversationController(adapter=_Adapter())
    controller.clinical_safety = _service(tmp_path)

    messages = controller.submit("seguridad clínica de Cristina")

    assert messages[-1].text.startswith("Seguridad clínica de Cristina")
    assert messages[-1].text != "fallback"
