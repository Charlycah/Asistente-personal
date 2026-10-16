from datetime import UTC, datetime
from inspect import signature

from app.memory_consolidation import (
    GovernedLearningTemporalIntrospectionView,
    OfficialMemoryGateway,
)
from app.roby_config import DEFAULT_CONFIG, environment_values
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


class RecordingLearningRuntime:
    def __init__(self, views=()):
        self.views = tuple(views)
        self.calls = []

    def governed_learning_temporal_introspection(self, **kwargs):
        self.calls.append(kwargs)
        return self.views



def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos y Cristina",
        session_id="intel-g2.1-contract-red",
        text=text,
    )



def _gateway(runtime: RecordingLearningRuntime) -> OfficialMemoryGateway:
    gateway = OfficialMemoryGateway(runtime, owner="Carlos y Cristina")
    gateway.household_timezone = "America/Argentina/Buenos_Aires"
    return gateway



def _view(content: str) -> GovernedLearningTemporalIntrospectionView:
    return GovernedLearningTemporalIntrospectionView(
        memory_id=7,
        content=content,
        category="stable_knowledge",
        confidence=0.91,
        created_at="2026-09-04T15:00:00+00:00",
        metadata=(("source", "governed_reasoning"),),
    )



def test_intel_g21_config_projects_canonical_household_timezone() -> None:
    values = environment_values(DEFAULT_CONFIG)

    assert values["ROBY_HOUSEHOLD_TIMEZONE"] == (
        "America/Argentina/Buenos_Aires"
    )



def test_intel_g21_official_memory_gateway_accepts_explicit_household_timezone() -> (
    None
):
    parameters = signature(OfficialMemoryGateway.__init__).parameters

    assert "household_timezone" in parameters



def test_intel_g21_today_uses_household_civil_day_and_intel_g2_projection() -> None:
    runtime = RecordingLearningRuntime((_view("conocimiento de hoy"),))
    gateway = _gateway(runtime)

    result = gateway.intercept(
        _request("¿Qué aprendiste hoy?"),
        now=datetime(2026, 9, 5, 1, 30, tzinfo=UTC),
    )

    assert runtime.calls == [
        {
            "owner": "Carlos y Cristina",
            "created_at_from": "2026-09-04T03:00:00+00:00",
            "created_at_before": "2026-09-05T03:00:00+00:00",
            "limit": 20,
        }
    ]
    assert result is not None
    assert result.rationale == "governed_learning_temporal_today_inspection"
    assert "conocimiento de hoy" in result.response_text



def test_intel_g21_yesterday_uses_previous_household_civil_day() -> None:
    runtime = RecordingLearningRuntime((_view("conocimiento de ayer"),))
    gateway = _gateway(runtime)

    result = gateway.intercept(
        _request("Que aprendiste ayer?"),
        now=datetime(2026, 9, 5, 1, 30, tzinfo=UTC),
    )

    assert runtime.calls == [
        {
            "owner": "Carlos y Cristina",
            "created_at_from": "2026-09-03T03:00:00+00:00",
            "created_at_before": "2026-09-04T03:00:00+00:00",
            "limit": 20,
        }
    ]
    assert result is not None
    assert result.rationale == "governed_learning_temporal_yesterday_inspection"
    assert "conocimiento de ayer" in result.response_text



def test_intel_g21_empty_interval_is_honest_and_remains_read_only() -> None:
    runtime = RecordingLearningRuntime()
    gateway = _gateway(runtime)

    result = gateway.intercept(
        _request("Qué aprendiste hoy"),
        now=datetime(2026, 9, 4, 18, 0, tzinfo=UTC),
    )

    assert len(runtime.calls) == 1
    assert result is not None
    assert result.rationale == "governed_learning_temporal_today_inspection"
    assert "no" in result.response_text.casefold()
    assert "aprendiz" in result.response_text.casefold()
