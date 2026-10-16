from datetime import datetime, timezone

from app.actionable_follow_up import (
    ActionableFollowUpService,
    build_actionable_follow_up_from_environment,
)
from app.household_goals import HouseholdGoalService
from app.household_projects import HouseholdProjectService
from app.runtime_root_factory import (
    ActionableFollowUpConversationInterceptionPort,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


def build_service(tmp_path):
    return ActionableFollowUpService(
        project_db_path=str(tmp_path / "projects.db"),
        goal_db_path=str(tmp_path / "goals.db"),
    )


def test_project_follow_up_reuses_official_next_step_mutation(tmp_path):
    projects = HouseholdProjectService(str(tmp_path / "projects.db"))
    projects.handle("Creá el proyecto Viaje", now=NOW)

    result = build_service(tmp_path).handle(
        "Dale seguimiento al proyecto Viaje: reservar hotel", now=NOW
    )

    assert result.handled
    assert result.response_text == "Actualicé el próximo paso de Viaje."
    detail = projects.handle("Detalle del proyecto Viaje", now=NOW)
    assert "Próximo paso: reservar hotel" in detail.response_text


def test_goal_follow_up_reuses_official_next_step_mutation(tmp_path):
    goals = HouseholdGoalService(str(tmp_path / "goals.db"))
    goals.handle("Creá el objetivo Aprender italiano", now=NOW)

    result = build_service(tmp_path).handle(
        "Da seguimiento al objetivo Aprender italiano "
        "con el próximo paso practicar 20 minutos",
        now=NOW,
    )

    assert result.handled
    assert result.response_text == "Actualicé el próximo paso de Aprender italiano."
    detail = goals.handle("Detalle del objetivo Aprender italiano", now=NOW)
    assert "Próximo paso: practicar 20 minutos" in detail.response_text


def test_meta_alias_is_supported(tmp_path):
    goals = HouseholdGoalService(str(tmp_path / "goals.db"))
    goals.handle("Creá la meta Correr 10K", now=NOW)

    result = build_service(tmp_path).handle(
        "Dá seguimiento a el meta Correr 10K: caminar cinco kilómetros", now=NOW
    )

    assert result.handled
    assert "Actualicé el próximo paso" in result.response_text


def test_unknown_project_returns_official_not_found_response(tmp_path):
    result = build_service(tmp_path).handle(
        "Dale seguimiento al proyecto Inexistente: hacer algo", now=NOW
    )

    assert result.handled
    assert result.response_text == "No encontré ese proyecto."


def test_unknown_goal_returns_official_not_found_response(tmp_path):
    result = build_service(tmp_path).handle(
        "Dale seguimiento al objetivo Inexistente: hacer algo", now=NOW
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
    port = ActionableFollowUpConversationInterceptionPort(build_service(tmp_path))
    request = GovernedConversationPipelineRequest(
        owner="Familia",
        session_id="session",
        text="Dale seguimiento al proyecto Casa: pintar",
    )

    result = port.intercept(request, now=NOW)

    assert result is not None
    assert result.rationale == "actionable_follow_up_conversation_completed"
    assert result.response_text == "Actualicé el próximo paso de Casa."


def test_environment_builder_can_be_disabled(monkeypatch):
    monkeypatch.setenv("ROBY_ACTIONABLE_FOLLOW_UP_ENABLED", "false")
    assert build_actionable_follow_up_from_environment() is None


def test_environment_builder_uses_shared_official_stores(tmp_path, monkeypatch):
    project_db = tmp_path / "projects.db"
    goal_db = tmp_path / "goals.db"
    monkeypatch.setenv("ROBY_ACTIONABLE_FOLLOW_UP_ENABLED", "true")
    monkeypatch.setenv("ROBY_HOUSEHOLD_PROJECTS_DB_PATH", str(project_db))
    monkeypatch.setenv("ROBY_HOUSEHOLD_GOALS_DB_PATH", str(goal_db))
    HouseholdProjectService(str(project_db)).handle("Creá el proyecto ROBY", now=NOW)

    service = build_actionable_follow_up_from_environment()

    assert service is not None
    result = service.handle(
        "Dale seguimiento al proyecto ROBY: ejecutar pruebas", now=NOW
    )
    assert result.handled
    detail = HouseholdProjectService(str(project_db)).handle(
        "Detalle del proyecto ROBY", now=NOW
    )
    assert "Próximo paso: ejecutar pruebas" in detail.response_text
