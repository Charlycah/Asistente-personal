from datetime import datetime, timezone

from app.household_goals import HouseholdGoalService
from core.household_goals import GoalStatus, HouseholdGoalManager
from infrastructure.repositories.sqlite_household_goal_repository import (
    SQLiteHouseholdGoalRepository,
)

NOW = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


def test_goal_lifecycle_persists(tmp_path):
    path = tmp_path / "goals.db"
    manager = HouseholdGoalManager(SQLiteHouseholdGoalRepository(path))
    created = manager.create("Terminar ROBY", description="Completar el plan", now=NOW)
    manager.set_progress(created.goal_id, 35, now=NOW)
    manager.set_next_step(created.goal_id, "Probar la interfaz", now=NOW)
    manager.link_project(created.goal_id, "Proyecto ROBY", now=NOW)
    manager.link_routine(created.goal_id, "Revisión semanal", now=NOW)
    manager.add_note(created.goal_id, "M241 certificado", now=NOW)

    restored = HouseholdGoalManager(SQLiteHouseholdGoalRepository(path)).find("ROBY")
    assert restored is not None
    assert restored.progress_percent == 35
    assert restored.next_step == "Probar la interfaz"
    assert restored.linked_project == "Proyecto ROBY"
    assert restored.linked_routine == "Revisión semanal"
    assert restored.notes == ("M241 certificado",)


def test_conversation_creates_updates_and_lists_goal(tmp_path):
    service = HouseholdGoalService(str(tmp_path / "goals.db"))
    created = service.handle(
        "Creá el objetivo Aprender italiano para mantener una conversación", now=NOW
    )
    assert created.handled
    assert "Aprender italiano" in created.response_text

    assert (
        "40%"
        in service.handle(
            "El objetivo Aprender italiano va en 40%", now=NOW
        ).response_text
    )
    assert (
        "próximo paso"
        in service.handle(
            (
                "El próximo paso del objetivo Aprender italiano es "
                "practicar todos los días"
            ),
            now=NOW,
        ).response_text
    )
    assert (
        "Vinculé"
        in service.handle(
            "Vinculá el objetivo Aprender italiano con la rutina práctica diaria",
            now=NOW,
        ).response_text
    )

    detail = service.handle("Detalles del objetivo Aprender italiano", now=NOW)
    assert "40%" in detail.response_text
    assert "practicar todos los días" in detail.response_text
    assert "práctica diaria" in detail.response_text
    assert (
        "Aprender italiano"
        in service.handle("Qué objetivos tenemos", now=NOW).response_text
    )


def test_completion_sets_full_progress_and_normal_chat_is_preserved(tmp_path):
    service = HouseholdGoalService(str(tmp_path / "goals.db"))
    service.handle("Creá la meta Ordenar la casa", now=NOW)
    result = service.handle("Completá la meta Ordenar la casa", now=NOW)
    assert "Completé" in result.response_text
    goal = service.manager.find("Ordenar")
    assert goal is not None
    assert goal.normalized_status is GoalStatus.COMPLETED
    assert goal.progress_percent == 100
    assert not service.handle("Hola ROBY", now=NOW).handled
