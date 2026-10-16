from datetime import datetime

import pytest

from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService
from core.mental_state import (
    ActiveGoal,
    MentalEvent,
    MentalMode,
    ROBYMentalState,
    ROBYMentalStateRegistry,
)
from core.provider_router import ProviderRouter


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta con estado mental", provider=self.name)


def test_mental_state_starts_idle_and_serializable():
    state = ROBYMentalState()

    snapshot = state.to_dict()

    assert state.mode is MentalMode.IDLE
    assert state.current_focus is None
    assert not state.active_goals
    assert snapshot["identity"] == "ROBY"
    assert snapshot["mode"] == "idle"
    assert snapshot["active_goals"] == []
    assert snapshot["recent_events"] == []


def test_mental_state_observes_user_input_and_processing():
    state = ROBYMentalState()

    state.observe_user_input("Recordame comprar pan")
    state.begin_processing("daily_assistance")

    assert state.mode is MentalMode.PROCESSING
    assert state.last_user_input == "Recordame comprar pan"
    assert state.current_focus == "daily_assistance"
    assert [event.kind for event in state.recent_events] == [
        "input",
        "focus",
        "processing",
    ]


def test_mental_state_orders_goals_by_priority():
    state = ROBYMentalState()

    state.add_goal(ActiveGoal("Ayudar a Cristina", priority=10, owner="Cristina"))
    state.add_goal(ActiveGoal("Revisar noticias", priority=4, owner="Carlos"))

    assert [goal.title for goal in state.active_goals] == [
        "Ayudar a Cristina",
        "Revisar noticias",
    ]
    assert bool(state.active_goals) is True
    assert state.to_dict()["active_goals"][0]["owner"] == "Cristina"


def test_mental_state_can_complete_goal():
    state = ROBYMentalState()
    state.add_goal(ActiveGoal("Preparar recordatorio", priority=8))

    completed = state.complete_goal("Preparar recordatorio")
    missing = state.complete_goal("No existe")

    assert completed is True
    assert missing is False
    assert state.active_goals == ()


def test_mental_state_limits_recent_events():
    state = ROBYMentalState(max_recent_events=2)

    state.record_event("one", "Primer evento")
    state.record_event("two", "Segundo evento")
    state.record_event("three", "Tercer evento")

    assert [event.kind for event in state.recent_events] == ["two", "three"]


def test_mental_state_system_prompt_lines_include_focus_and_goals():
    state = ROBYMentalState()
    state.set_focus("acompañar a Cristina")
    state.add_goal(ActiveGoal("Recordar medicación", priority=9, owner="Cristina"))

    lines = state.system_prompt_lines()

    assert "Estado mental actual de ROBY:" in lines
    assert "- Modo: idle" in lines
    assert "- Foco actual: acompañar a Cristina" in lines
    assert "- Recordar medicación (prioridad 9)" in lines


def test_mental_state_rejects_invalid_values():
    with pytest.raises(ValueError):
        ActiveGoal(" ")

    with pytest.raises(ValueError):
        ActiveGoal("Objetivo", priority=11)

    with pytest.raises(ValueError):
        MentalEvent(" ", "descripción")

    with pytest.raises(ValueError):
        MentalEvent(
            "event",
            "descripción",
            created_at=datetime(2026, 7, 8),
        )

    with pytest.raises(ValueError):
        ROBYMentalState(max_recent_events=0)


def test_mental_state_registry_returns_default_state():
    registry = ROBYMentalStateRegistry()

    assert registry.state.mode is MentalMode.IDLE
    assert registry.snapshot()["identity"] == "ROBY"


def test_cognitive_pipeline_can_inject_mental_state_into_system_prompt(tmp_path):
    provider = RecordingProvider()
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    mental_state = ROBYMentalState()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
        mental_state=mental_state,
    )

    result = pipeline.process_turn("Ayudame a organizar el día de Cristina")

    assert result.mental_state is mental_state
    assert mental_state.mode is MentalMode.PROCESSING
    assert mental_state.current_focus == "cognitive_pipeline"
    assert mental_state.last_user_input == "Ayudame a organizar el día de Cristina"
    assert "Estado mental actual de ROBY:" in result.system_prompt
    assert "- Modo: processing" in result.system_prompt
    assert "- Foco actual: cognitive_pipeline" in result.system_prompt
    assert provider.requests[0].system_prompt == result.system_prompt
