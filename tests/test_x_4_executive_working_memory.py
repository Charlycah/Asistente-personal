from datetime import datetime, timezone

from app.executive_working_memory import ExecutiveWorkingMemory
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from app.runtime_root_factory import EnvironmentInferenceRequestPort
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def request(text: str, *, session_id: str = "household-main"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


def test_working_memory_starts_and_reports_a_travel_objective():
    memory = ExecutiveWorkingMemory()
    now = datetime.now(timezone.utc)

    assert (
        memory.intercept(
            request("Estoy organizando un viaje para la semana que viene"),
            now=now,
        )
        is None
    )
    result = memory.intercept(request("En que estabamos"), now=now)

    assert result is not None
    assert "organizando un viaje" in result.response_text
    assert "alojamiento" in result.response_text
    assert memory.snapshot.objectives_started == 1


def test_working_memory_is_isolated_by_conversation():
    memory = ExecutiveWorkingMemory()
    now = datetime.now(timezone.utc)
    memory.intercept(
        request("Quiero planificar vacaciones", session_id="one"),
        now=now,
    )

    result = memory.intercept(
        request("Que falta", session_id="two"),
        now=now,
    )

    assert result is not None
    assert result.response_text == "No hay un objetivo de trabajo activo."


def test_working_memory_context_is_added_to_the_llm_fallback_prompt():
    memory = ExecutiveWorkingMemory()
    now = datetime.now(timezone.utc)
    original = request("Necesito preparar un viaje a Cordoba")
    memory.intercept(original, now=now)
    port = EnvironmentInferenceRequestPort(memory)

    llm_request = port.build(request("Y el hotel?"))

    assert "Contexto ejecutivo temporal" in llm_request.prompt
    assert "preparar un viaje a Cordoba" in llm_request.prompt
    assert "Mensaje actual: Y el hotel?" in llm_request.prompt


def test_registry_runs_working_memory_before_the_director():
    registry = OfficialRuntimeCapabilityRegistry()
    memory = ExecutiveWorkingMemory()
    registry.set_working_memory(memory)
    now = datetime.now(timezone.utc)
    registry.intercept(
        request("Quiero organizar un viaje"),
        now=now,
    )

    result = registry.intercept(request("Cual es el objetivo"), now=now)

    assert result is not None
    assert result.rationale == "executive_working_memory_status_completed"


def test_working_memory_can_close_the_active_objective():
    memory = ExecutiveWorkingMemory()
    now = datetime.now(timezone.utc)
    memory.intercept(request("Quiero organizar un viaje"), now=now)

    closed = memory.intercept(request("Cerrar objetivo"), now=now)
    status = memory.intercept(request("En que estabamos"), now=now)

    assert closed is not None
    assert closed.response_text == "Objetivo de trabajo cerrado."
    assert status is not None
    assert status.response_text == "No hay un objetivo de trabajo activo."
    assert memory.snapshot.objectives_closed == 1
