import json
from datetime import datetime
from pathlib import Path

from app.desktop_ui import DesktopConversationController
from app.secure_medication_registry import (
    MedicationRegistryRepository,
    SecureMedicationRegistryService,
)
from app.ui_adapter import UIResponse

NOW = datetime(2026, 7, 27, 7, 30)


def _service(tmp_path: Path) -> SecureMedicationRegistryService:
    repository = MedicationRegistryRepository(tmp_path / "medications.json")
    return SecureMedicationRegistryService(repository, now=lambda: NOW)


def _register(
    service: SecureMedicationRegistryService,
    person: str = "Carlos",
    schedules: str = "08:00;20:00",
) -> str:
    service.prepare(
        f"registrar medicamento de {person}: medicamento=Ejemplo Agenda | "
        f"dosis=1 comprimido | horarios={schedules}",
        session_id=person,
    )
    service.prepare("confirmar medicamento", session_id=person)
    return service.repository.load()[0].record_id


class RecordingAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.calls += 1
        return UIResponse(text="respuesta", status="success", session_id="s")


def test_m340_12_agenda_lists_today_occurrences(tmp_path: Path) -> None:
    service = _service(tmp_path)
    record_id = _register(service)

    result = service.prepare("agenda de medicación de Carlos")

    assert "08:00 · Ejemplo Agenda" in result.response
    assert "20:00 · Ejemplo Agenda" in result.response
    assert f"ID {record_id}" in result.response
    assert "pendiente" in result.response


def test_m340_12_taken_intake_is_persisted_and_reported(tmp_path: Path) -> None:
    service = _service(tmp_path)
    record_id = _register(service)

    result = service.prepare(f"marcar toma {record_id} 08:00 como tomada")
    state = service.prepare(f"estado de toma {record_id} 08:00")

    assert "Registré como tomada" in result.response
    assert "figura como tomado" in state.response
    intake = service.repository.load_intakes()[0]
    assert intake.person == "Carlos"
    assert intake.scheduled_date == "2026-07-27"
    assert intake.status == "tomado"


def test_m340_12_postpone_preserves_master_schedule(tmp_path: Path) -> None:
    service = _service(tmp_path)
    record_id = _register(service)

    result = service.prepare(f"postergar toma {record_id} 08:00 10 minutos")

    assert "hasta las 07:40" in result.response
    assert "horario indicado sigue siendo 08:00" in result.response
    assert service.repository.load()[0].schedules == ["08:00", "20:00"]
    assert service.repository.load_intakes()[0].due_at.endswith("07:40:00")


def test_m340_12_omitted_intake_appears_in_history(tmp_path: Path) -> None:
    service = _service(tmp_path)
    record_id = _register(service, person="Cristina", schedules="07:00")

    service.prepare(f"marcar toma {record_id} 07:00 como omitida")
    history = service.prepare("historial de medicación de Cristina hoy")

    assert "Ejemplo Agenda" in history.response
    assert "omitido" in history.response
    assert "Carlos" not in history.response


def test_m340_12_rejects_time_not_in_confirmed_prescription(tmp_path: Path) -> None:
    service = _service(tmp_path)
    record_id = _register(service)

    result = service.prepare(f"marcar toma {record_id} 09:00 como tomada")

    assert "no está registrado" in result.response
    assert service.repository.load_intakes() == []


def test_m340_12_paused_medication_is_excluded(tmp_path: Path) -> None:
    service = _service(tmp_path)
    record_id = _register(service)
    service.prepare(f"marcar medicamento {record_id} como pausado", session_id="c")
    service.prepare("confirmar medicamento", session_id="c")

    agenda = service.prepare("agenda de medicación de Carlos")
    intake = service.prepare(f"marcar toma {record_id} 08:00 como tomada")

    assert "No hay tomas activas" in agenda.response
    assert "no está activo" in intake.response


def test_m340_12_intake_replaces_same_daily_occurrence(tmp_path: Path) -> None:
    service = _service(tmp_path)
    record_id = _register(service)

    service.prepare(f"postergar toma {record_id} 08:00 10 minutos")
    service.prepare(f"marcar toma {record_id} 08:00 como tomada")

    intakes = service.repository.load_intakes()
    assert len(intakes) == 1
    assert intakes[0].status == "tomado"


def test_m340_12_repository_keeps_records_and_intakes(tmp_path: Path) -> None:
    service = _service(tmp_path)
    record_id = _register(service)
    service.prepare(f"marcar toma {record_id} 08:00 como tomada")

    payload = json.loads(service.repository.path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert len(payload["records"]) == 1
    assert len(payload["intakes"]) == 1


def test_m340_12_desktop_routes_agenda_without_provider(tmp_path: Path) -> None:
    adapter = RecordingAdapter()
    controller = DesktopConversationController(adapter=adapter)
    controller.medications = _service(tmp_path)
    _register(controller.medications)

    messages = controller.submit("agenda de medicación de Carlos")

    assert adapter.calls == 0
    assert "Agenda de medicación" in messages[1].text
