from datetime import datetime, timedelta, timezone

from app.goal_project_review import GoalProjectReviewConfig, GoalProjectReviewService
from app.household_goals import HouseholdGoalService
from app.household_projects import HouseholdProjectService

NOW = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


def build_service(tmp_path, *, stale_days=14):
    return GoalProjectReviewService(
        project_db_path=str(tmp_path / "projects.db"),
        goal_db_path=str(tmp_path / "goals.db"),
        config=GoalProjectReviewConfig(stale_days=stale_days),
    )


def test_review_detects_missing_next_steps(tmp_path):
    projects = HouseholdProjectService(str(tmp_path / "projects.db"))
    goals = HouseholdGoalService(str(tmp_path / "goals.db"))
    projects.handle("Creá el proyecto Viaje", now=NOW)
    goals.handle("Creá el objetivo Aprender italiano", now=NOW)

    result = build_service(tmp_path).handle(
        "Revisión de objetivos y proyectos", now=NOW
    )

    assert result.handled
    assert "Proyecto Viaje" in result.response_text
    assert "Objetivo Aprender italiano" in result.response_text
    assert result.response_text.count("falta definir el próximo paso") == 2


def test_review_detects_stale_items_with_steps(tmp_path):
    old = NOW - timedelta(days=20)
    projects = HouseholdProjectService(str(tmp_path / "projects.db"))
    goals = HouseholdGoalService(str(tmp_path / "goals.db"))
    projects.handle("Creá el proyecto Taller", now=old)
    projects.handle("El próximo paso del proyecto Taller es comprar madera", now=old)
    goals.handle("Creá el objetivo Terminar ROBY", now=old)
    goals.handle("El próximo paso del objetivo Terminar ROBY es probar la UI", now=old)
    goals.handle("El objetivo Terminar ROBY va en 70%", now=old)

    text = build_service(tmp_path).generate(now=NOW)

    assert "Proyecto Taller: sin movimiento desde hace 20 días" in text
    assert "Objetivo Terminar ROBY: progreso en 70%" in text


def test_review_ignores_completed_paused_and_recent_items(tmp_path):
    projects = HouseholdProjectService(str(tmp_path / "projects.db"))
    goals = HouseholdGoalService(str(tmp_path / "goals.db"))
    projects.handle("Creá el proyecto Viaje", now=NOW)
    projects.handle("El próximo paso del proyecto Viaje es elegir destino", now=NOW)
    goals.handle("Creá el objetivo Terminar ROBY", now=NOW)
    goals.handle("Completá el objetivo Terminar ROBY", now=NOW)

    text = build_service(tmp_path).generate(now=NOW)

    assert "Todo lo activo" in text
    assert "Terminar ROBY" not in text


def test_review_is_available_for_daily_briefing_and_preserves_normal_chat(tmp_path):
    projects = HouseholdProjectService(str(tmp_path / "projects.db"))
    projects.handle("Creá el proyecto Casa", now=NOW)
    service = build_service(tmp_path)

    assert service.briefing_lines(now=NOW) == (
        "Proyecto Casa: falta definir el próximo paso.",
    )
    assert not service.handle("Hola ROBY", now=NOW).handled
