from datetime import datetime

import pytest

from core.attention import AttentionManager, AttentionSignal
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService
from core.mental_state import ROBYMentalState
from core.provider_router import ProviderRouter
from core.reasoning import (
    ReasoningContext,
    ReasoningEngine,
    ReasoningManager,
    ReasoningMode,
    ReasoningResult,
    ReasoningStep,
    ReasoningStepKind,
)
from core.working_memory import WorkingMemoryManager


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta razonada", provider=self.name)


def test_reasoning_context_validates_required_fields():
    with pytest.raises(ValueError):
        ReasoningContext(query=" ")

    with pytest.raises(ValueError):
        ReasoningContext(query="x", goal=" ")

    with pytest.raises(ValueError):
        ReasoningContext(query="x", created_at=datetime(2026, 7, 8))


def test_reasoning_step_validates_description_and_confidence():
    with pytest.raises(ValueError):
        ReasoningStep(ReasoningStepKind.OBSERVE, " ")

    with pytest.raises(ValueError):
        ReasoningStep(ReasoningStepKind.OBSERVE, "x", confidence=1.2)


def test_reasoning_result_validates_required_fields():
    step = ReasoningStep(ReasoningStepKind.OBSERVE, "observar")

    with pytest.raises(ValueError):
        ReasoningResult(
            query=" ",
            conclusion="x",
            justification="x",
            confidence=0.5,
            mode=ReasoningMode.DIRECT,
            steps=(step,),
        )

    with pytest.raises(ValueError):
        ReasoningResult(
            query="x",
            conclusion=" ",
            justification="x",
            confidence=0.5,
            mode=ReasoningMode.DIRECT,
            steps=(step,),
        )


def test_reasoning_engine_uses_identity_and_working_memory():
    memory = WorkingMemoryManager()
    memory.capture_user_input("Carlos pregunta por vacaciones")
    context = ReasoningContext(
        query="Conviene viajar en octubre?",
        identity=ROBYIdentity(),
        working_memory=memory,
    )

    result = ReasoningEngine().reason(context)

    assert result.used_identity is True
    assert result.used_working_memory is True
    assert result.mode is ReasoningMode.DELIBERATIVE
    assert result.confidence > 0.7
    assert any(step.evidence for step in result.steps)
    assert memory.memory.current_focus is not None
    assert memory.memory.current_focus.source == "reasoning"


def test_reasoning_engine_selects_information_mode_for_questions():
    result = ReasoningEngine().reason(
        ReasoningContext(query="Qué superficie tiene Júpiter?")
    )

    assert result.mode is ReasoningMode.INFORMATIONAL
    assert "consultar fuentes" in result.conclusion.lower()
    assert any(
        "Consultar conocimiento externo" in alternative
        for alternative in result.alternatives
    )


def test_reasoning_engine_prioritizes_interrupting_attention():
    attention = AttentionManager()
    attention.submit(
        AttentionSignal(
            "Cristina tiene un recordatorio urgente",
            person="Cristina",
            urgency=10,
            importance=10,
            source="reminders",
        )
    )

    result = ReasoningEngine().reason(
        ReasoningContext(query="Podemos hablar de noticias?", attention=attention)
    )

    assert result.used_attention is True
    assert result.mode is ReasoningMode.SAFETY
    assert "Atender primero" in result.conclusion


def test_reasoning_manager_exposes_last_result_for_prompts():
    manager = ReasoningManager()

    empty_lines = manager.system_prompt_lines()
    result = manager.reason(ReasoningContext(query="Necesito decidir algo"))
    lines = manager.system_prompt_lines()

    assert empty_lines == ("Razonamiento estructurado de ROBY: sin resultado activo",)
    assert manager.last_result is result
    assert "Razonamiento estructurado de ROBY:" in lines
    assert any("Conclusión" in line for line in lines)


def test_reasoning_result_snapshot_is_serializable():
    result = ReasoningEngine().reason(ReasoningContext(query="Necesito decidir algo"))

    snapshot = result.to_dict()

    assert snapshot["query"] == "Necesito decidir algo"
    assert snapshot["steps"][0]["kind"] == "observe"
    assert snapshot["mode"] == result.mode.value


def test_cognitive_pipeline_can_inject_reasoning_into_system_prompt(tmp_path):
    provider = RecordingProvider()
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    identity = ROBYIdentity()
    mental_state = ROBYMentalState()
    attention = AttentionManager()
    working_memory = WorkingMemoryManager()
    reasoning = ReasoningManager()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
        identity=identity,
        mental_state=mental_state,
        attention=attention,
        working_memory=working_memory,
        reasoning=reasoning,
    )

    result = pipeline.process_turn("Necesito razonar antes de responder")

    assert result.reasoning is reasoning
    assert reasoning.last_result is not None
    assert "Razonamiento estructurado de ROBY:" in result.system_prompt
    assert "Conclusión" in result.system_prompt
    assert provider.requests[0].system_prompt == result.system_prompt
