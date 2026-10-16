from datetime import datetime, timezone

from app.household_goals import HouseholdGoalService
from app.household_projects import HouseholdProjectService
from app.progress_check_in import (
    ProgressCheckInService,
    build_progress_check_in_from_environment,
)
from app.runtime_root_factory import ProgressCheckInConversationInterceptionPort
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, 19, 0, tzinfo=timezone.utc)


def build_service(tmp_path):
    return ProgressCheckInService(
        project_db_path=str(tmp_path / "projects.db"),
        goal_db_path=str(tmp_path / "goals.db"),
    )


def test_project_check_in_reuses_official_note_mutation(tmp_path):
    projects = HouseholdProjectService(str(tmp_path / "projects.db"))
    projects.handle("Creá el proyecto Viaje", now=NOW)

    result = build_service(tmp_path).handle(
        "Registrá el avance del proyecto Viaje: hotel reservado", now=NOW
    )

    assert result.handled
    assert result.response_text == "Agregué una nota a Viaje."
    detail = projects.handle("Detalle del proyecto Viaje", now=NOW)
    assert "hotel reservado" in detail.response_text


def test_goal_check_in_reuses_official_progress_mutation(tmp_path):
    goals = HouseholdGoalService(str(tmp_path / "goals.db"))
    goals.handle("Creá el objetivo Aprender italiano", now=NOW)

    result = build_service(tmp_path).handle(
        "Actualizá el avance del objetivo Aprender italiano: 40%", now=NOW
    )

    assert result.handled
    assert result.response_text == "Actualicé Aprender italiano al 40%."
    detail = goals.handle("Detalle del objetivo Aprender italiano", now=NOW)
    assert "Progreso: 40%" in detail.response_text


def test_meta_alias_is_supported(tmp_path):
    goals = HouseholdGoalService(str(tmp_path / "goals.db"))
    goals.handle("Creá la meta Correr 10K", now=NOW)

    result = build_service(tmp_path).handle(
        "Registra avance de la meta Correr 10K: 55%", now=NOW
    )

    assert result.handled
    assert result.response_text == "Actualicé Correr 10K al 55%."


def test_invalid_goal_progress_reuses_official_validation(tmp_path):
    goals = HouseholdGoalService(str(tmp_path / "goals.db"))
    goals.handle("Creá el objetivo Leer más", now=NOW)

    result = build_service(tmp_path).handle(
        "Registrá avance del objetivo Leer más: 120%", now=NOW
    )

    assert result.handled
    assert result.response_text == "El progreso debe estar entre 0 y 100%."


def test_unknown_project_returns_official_not_found_response(tmp_path):
    result = build_service(tmp_path).handle(
        "Anotá avance del proyecto Inexistente: primera prueba", now=NOW
    )

    assert result.handled
    assert result.response_text == "No encontré ese proyecto."


def test_unknown_goal_returns_official_not_found_response(tmp_path):
    result = build_service(tmp_path).handle(
        "Registrá avance del objetivo Inexistente: 10%", now=NOW
    )

    assert result.handled
    assert result.response_text == "No encontré ese objetivo."


def test_unrelated_conversation_is_not_intercepted(tmp_path):
    result = build_service(tmp_path).handle("Hola ROBY", now=NOW)
    assert not result.handled
    assert result.response_text == ""


def test_official_interception_rationale(tmp_path):
    projects = HouseholdProjectService(str(tmp_path / "projects.db"))
    projects.handle("Creá el proyecto Casa", now=NOW)
    port = ProgressCheckInConversationInterceptionPort(build_service(tmp_path))
    request = GovernedConversationPipelineRequest(
        owner="Familia",
        session_id="session",
        text="Registrá avance del proyecto Casa: primera pared pintada",
    )

    result = port.intercept(request, now=NOW)

    assert result is not None
    assert result.rationale == "progress_check_in_conversation_completed"
    assert result.response_text == "Agregué una nota a Casa."


def test_environment_builder_can_be_disabled(monkeypatch):
    monkeypatch.setenv("ROBY_PROGRESS_CHECK_IN_ENABLED", "false")
    assert build_progress_check_in_from_environment() is None


def test_environment_builder_uses_shared_official_stores(tmp_path, monkeypatch):
    project_db = tmp_path / "projects.db"
    goal_db = tmp_path / "goals.db"
    monkeypatch.setenv("ROBY_PROGRESS_CHECK_IN_ENABLED", "true")
    monkeypatch.setenv("ROBY_HOUSEHOLD_PROJECTS_DB_PATH", str(project_db))
    monkeypatch.setenv("ROBY_HOUSEHOLD_GOALS_DB_PATH", str(goal_db))
    HouseholdGoalService(str(goal_db)).handle("Creá el objetivo ROBY", now=NOW)

    service = build_progress_check_in_from_environment()

    assert service is not None
    result = service.handle("Registrá avance del objetivo ROBY: 75%", now=NOW)
    assert result.handled
    detail = HouseholdGoalService(str(goal_db)).handle(
        "Detalle del objetivo ROBY", now=NOW
    )
    assert "Progreso: 75%" in detail.response_text
