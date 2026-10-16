from datetime import datetime, timezone

from app.household_projects import HouseholdProjectService
from core.household_projects import HouseholdProjectManager, ProjectStatus
from infrastructure.repositories.sqlite_household_project_repository import (
    SQLiteHouseholdProjectRepository,
)

NOW = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


def test_project_lifecycle_persists(tmp_path):
    path = tmp_path / "projects.db"
    manager = HouseholdProjectManager(SQLiteHouseholdProjectRepository(path))
    created = manager.create("Proyecto ROBY", description="Terminar ROBY", now=NOW)
    manager.set_next_step(created.project_id, "Probar la interfaz", now=NOW)
    manager.add_note(created.project_id, "M240 certificado", now=NOW)
    manager.change_status(created.project_id, ProjectStatus.PAUSED, now=NOW)

    restored = HouseholdProjectManager(SQLiteHouseholdProjectRepository(path)).find(
        "ROBY"
    )
    assert restored is not None
    assert restored.next_step == "Probar la interfaz"
    assert restored.notes == ("M240 certificado",)
    assert restored.normalized_status is ProjectStatus.PAUSED


def test_conversation_creates_lists_and_updates_project(tmp_path):
    service = HouseholdProjectService(str(tmp_path / "projects.db"))
    result = service.handle(
        "Creá el proyecto Viaje para organizar las vacaciones", now=NOW
    )
    assert result.handled
    assert "Viaje" in result.response_text

    result = service.handle(
        "El próximo paso del proyecto Viaje es elegir destino", now=NOW
    )
    assert "Actualicé" in result.response_text

    result = service.handle(
        "Agregá una nota al proyecto Viaje: revisar pasaportes", now=NOW
    )
    assert "Agregué" in result.response_text

    detail = service.handle("Detalles del proyecto Viaje", now=NOW)
    assert "elegir destino" in detail.response_text
    assert "revisar pasaportes" in detail.response_text

    listing = service.handle("Qué proyectos tenemos", now=NOW)
    assert "Viaje" in listing.response_text


def test_conversation_changes_status_and_preserves_normal_chat(tmp_path):
    service = HouseholdProjectService(str(tmp_path / "projects.db"))
    service.handle("Creá el proyecto Taller", now=NOW)
    assert "Pausé" in service.handle("Pausá el proyecto Taller", now=NOW).response_text
    assert (
        "Reanudé" in service.handle("Reanudá el proyecto Taller", now=NOW).response_text
    )
    assert (
        "Completé"
        in service.handle("Completá el proyecto Taller", now=NOW).response_text
    )
    assert not service.handle("Hola ROBY", now=NOW).handled
