from datetime import datetime, timezone

from app.executive_goal_manager import ExecutiveGoalManager
from app.operational_intelligence_runtime import OperationalIntelligenceRuntime
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


def request(text: str):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="household-main",
        text=text,
    )


def test_observes_success_degradation_and_failure():
    runtime = OperationalIntelligenceRuntime(ExecutiveGoalManager())
    runtime.observe_result(
        request("clima"),
        GovernedOperationalInterception(
            response_text="Todo bien.",
            rationale="weather_completed",
        ),
        now=NOW,
    )
    runtime.observe_result(
        request("correo"),
        GovernedOperationalInterception(
            response_text="La funcion no esta disponible.",
            rationale="mail_unavailable",
        ),
        now=NOW,
    )
    runtime.observe_result(
        request("camara"),
        GovernedOperationalInterception(
            response_text="No se pudo completar.",
            rationale="camera_failure",
        ),
        now=NOW,
    )
    assert runtime.snapshot.successes == 1
    assert runtime.snapshot.degradations == 1
    assert runtime.snapshot.failures == 1


def test_recommends_high_priority_active_goal():
    goals = ExecutiveGoalManager()
    goals.start(request("objetivo"), "organizar un viaje", now=NOW)
    goals.set_priority(request("objetivo"), "organizar un viaje", "alta", now=NOW)
    runtime = OperationalIntelligenceRuntime(goals)
    result = runtime.intercept(request("que conviene priorizar"), now=NOW)
    assert result is not None
    assert "organizar un viaje" in result.response_text


def test_reports_repeated_degradation_without_persisting():
    runtime = OperationalIntelligenceRuntime(ExecutiveGoalManager())
    for _ in range(2):
        runtime.observe_result(
            request("correo"),
            GovernedOperationalInterception(
                response_text="No esta disponible.",
                rationale="mail_unavailable",
            ),
            now=NOW,
        )
    result = runtime.intercept(request("estado operativo"), now=NOW)
    assert result is not None
    assert "problemas repetidos" in result.response_text
    assert (
        len(runtime.observations_for(owner="Carlos", session_id="household-main")) == 2
    )


def test_ordinary_messages_stay_in_the_normal_runtime():
    runtime = OperationalIntelligenceRuntime(ExecutiveGoalManager())
    assert runtime.intercept(request("hola roby"), now=NOW) is None
