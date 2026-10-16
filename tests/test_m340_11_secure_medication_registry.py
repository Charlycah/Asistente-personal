import json
from pathlib import Path

from app.desktop_ui import DesktopConversationController
from app.secure_medication_registry import (
    MedicationRegistryRepository,
    SecureMedicationRegistryService,
)
from app.ui_adapter import UIResponse


def _service(tmp_path: Path) -> SecureMedicationRegistryService:
    repository = MedicationRegistryRepository(tmp_path / "medications.json")
    return SecureMedicationRegistryService(repository)


class RecordingAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.calls += 1
        return UIResponse(text="respuesta", status="success", session_id="s")


def test_m340_11_ordinary_conversation_is_not_intercepted(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("contame una historia")

    assert result.handled is False


def test_m340_11_registration_requires_explicit_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)

    result = service.prepare(
        "registrar medicamento de Carlos: medicamento=Ejemplo A | "
        "presentación=10 mg | dosis=1 comprimido | horarios=08:00;20:00 | "
        "momentos=mañana;noche | comidas=después de comer",
        session_id="carlos",
    )

    assert result.handled is True
    assert "confirmar medicamento" in result.response
    assert "Dosis informada: 1 comprimido" in result.response
    assert service.repository.load() == []


def test_m340_11_confirmation_persists_structured_record(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar medicamento de Cristina: medicamento=Ejemplo B | "
        "dosis=media tableta | horarios=21:30 | momento=noche | "
        "profesional=Dra. Ejemplo | fuente=receta",
        session_id="cristina",
    )

    confirmation = service.prepare(
        "confirmar medicamento",
        session_id="cristina",
    )
    record = service.repository.load()[0]

    assert "no validé ni modifiqué" in confirmation.response
    assert record.person == "Cristina"
    assert record.name == "Ejemplo B"
    assert record.schedules == ["21:30"]
    assert record.moments == ["noche"]
    assert record.source == "receta"


def test_m340_11_profiles_are_never_mixed(tmp_path: Path) -> None:
    service = _service(tmp_path)
    for person, medicine in (("Carlos", "Ejemplo C"), ("Cristina", "Ejemplo D")):
        service.prepare(
            f"registrar medicamento de {person}: medicamento={medicine} | "
            "dosis=1 unidad | horarios=09:00",
            session_id=person,
        )
        service.prepare("confirmar medicamento", session_id=person)

    result = service.prepare("mostrar medicamentos de Carlos")

    assert "Ejemplo C" in result.response
    assert "Ejemplo D" not in result.response
    assert "Cristina" not in result.response


def test_m340_11_update_requires_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar medicamento de Carlos: medicamento=Ejemplo E | "
        "dosis=1 unidad | horarios=08:00",
        session_id="carlos",
    )
    service.prepare("confirmar medicamento", session_id="carlos")
    record_id = service.repository.load()[0].record_id

    pending = service.prepare(
        f"actualizar medicamento {record_id}: horarios=09:00 | momento=mañana",
        session_id="carlos",
    )

    assert "actualizar" in pending.response
    assert service.repository.load()[0].schedules == ["08:00"]

    service.prepare("confirmar medicamento", session_id="carlos")
    assert service.repository.load()[0].schedules == ["09:00"]


def test_m340_11_status_and_archive_are_confirmed_changes(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar medicamento de Cristina: medicamento=Ejemplo F | "
        "dosis=1 unidad | horarios=22:00",
        session_id="cristina",
    )
    service.prepare("confirmar medicamento", session_id="cristina")
    record_id = service.repository.load()[0].record_id

    service.prepare(
        f"marcar medicamento {record_id} como pausado",
        session_id="cristina",
    )
    assert service.repository.load()[0].status == "activo"
    service.prepare("confirmar medicamento", session_id="cristina")
    assert service.repository.load()[0].status == "pausado"

    service.prepare(f"archivar medicamento {record_id}", session_id="cristina")
    service.prepare("confirmar medicamento", session_id="cristina")
    listed = service.prepare("listar medicamentos de Cristina")
    assert "No hay medicamentos" in listed.response


def test_m340_11_invalid_or_incomplete_registration_is_not_captured(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    missing_dose = service.prepare(
        "registrar medicamento de Carlos: medicamento=Ejemplo G | horarios=08:00"
    )
    invalid_time = service.prepare(
        "registrar medicamento de Carlos: medicamento=Ejemplo G | "
        "dosis=1 unidad | horarios=por la mañana"
    )

    assert missing_dose.handled is False
    assert invalid_time.handled is False


def test_m340_11_repository_uses_versioned_local_json(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar medicamento de Carlos: medicamento=Ejemplo H | "
        "dosis=1 unidad | horarios=07:00",
        session_id="carlos",
    )
    service.prepare("confirmar medicamento", session_id="carlos")

    payload = json.loads(service.repository.path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert len(payload["records"]) == 1


def test_m340_11_desktop_routes_medication_without_provider(tmp_path: Path) -> None:
    adapter = RecordingAdapter()
    controller = DesktopConversationController(adapter=adapter)
    controller.medications = _service(tmp_path)

    messages = controller.submit(
        "registrar medicamento de Carlos: medicamento=Ejemplo I | "
        "dosis=1 unidad | horarios=08:00",
        session_id="carlos",
    )

    assert adapter.calls == 0
    assert "confirmar medicamento" in messages[1].text
