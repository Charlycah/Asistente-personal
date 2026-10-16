from datetime import datetime
from pathlib import Path

import pytest

from core.attention import AttentionManager
from core.cognitive_cycle import (
    CognitiveCycleContext,
    CognitiveCycleManager,
    CognitiveCyclePhase,
    CognitiveCycleResult,
    CognitiveCycleStatus,
    CognitiveCycleStep,
)
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.knowledge_gateway import (
    KnowledgeGatewayManager,
    KnowledgeRequest,
    KnowledgeSourceKind,
    KnowledgeSourceResult,
)
from core.learning import ExperientialLearningManager
from core.mental_state import MentalMode, ROBYMentalState
from core.planning import PlanningManager
from core.reasoning import ReasoningManager
from core.reflection import ReflectionManager
from core.working_memory import WorkingMemoryManager


class StaticKnowledgeProvider:
    def __init__(self) -> None:
        self.name = "cycle-provider"
        self.source_kind = KnowledgeSourceKind.LLM
        self.requests: list[KnowledgeRequest] = []

    def retrieve(self, request: KnowledgeRequest) -> KnowledgeSourceResult:
        self.requests.append(request)
        return KnowledgeSourceResult(
            "Conocimiento externo controlado para el ciclo cognitivo.",
            provider=self.name,
            source_kind=self.source_kind,
            confidence=0.91,
        )


def make_full_context() -> CognitiveCycleContext:
    return CognitiveCycleContext(
        input_text="ROBY, ayudame a organizar una tarea para Cristina",
        identity=ROBYIdentity(),
        mental_state=ROBYMentalState(),
        attention=AttentionManager(),
        working_memory=WorkingMemoryManager(),
        reasoning=ReasoningManager(),
        planning=PlanningManager(),
        learning=ExperientialLearningManager(),
        knowledge_gateway=KnowledgeGatewayManager(
            providers=(StaticKnowledgeProvider(),)
        ),
        reflection=ReflectionManager(),
    )


def test_cycle_context_validates_required_fields():
    with pytest.raises(ValueError):
        CognitiveCycleContext(" ")

    with pytest.raises(ValueError):
        CognitiveCycleContext("hola", source=" ")

    with pytest.raises(ValueError):
        CognitiveCycleContext(
            "hola",
            created_at=datetime(2026, 7, 8),
        )


def test_cycle_step_validates_description_and_timestamp():
    with pytest.raises(ValueError):
        CognitiveCycleStep(CognitiveCyclePhase.ATTENTION, " ")

    with pytest.raises(ValueError):
        CognitiveCycleStep(
            CognitiveCyclePhase.ATTENTION,
            "ok",
            created_at=datetime(2026, 7, 8),
        )


def test_cycle_result_validates_steps_and_timestamps():
    step = CognitiveCycleStep(CognitiveCyclePhase.COMPLETION, "cerrado")

    with pytest.raises(ValueError):
        CognitiveCycleResult("hola", CognitiveCycleStatus.COMPLETED, ())

    with pytest.raises(ValueError):
        CognitiveCycleResult(
            "hola",
            CognitiveCycleStatus.COMPLETED,
            (step,),
            started_at=datetime(2026, 7, 8),
        )


def test_manager_runs_complete_cognitive_cycle():
    manager = CognitiveCycleManager()
    context = make_full_context()

    result = manager.run(context)

    assert result.normalized_status is CognitiveCycleStatus.COMPLETED
    assert result.is_complete is True
    assert result.reasoning_result is not None
    assert result.plan is not None
    assert result.knowledge_answer is not None
    assert result.learned_experience is not None
    assert result.reflection_result is not None
    assert manager.last_result is result
    assert len(manager.history) == 1
    assert context.mental_state is not None
    assert context.mental_state.mode is MentalMode.WAITING


def test_cycle_records_expected_phase_order():
    result = CognitiveCycleManager().run(make_full_context())

    phases = [step.normalized_phase for step in result.steps]

    assert phases[0] is CognitiveCyclePhase.IDENTITY
    assert CognitiveCyclePhase.ATTENTION in phases
    assert CognitiveCyclePhase.WORKING_MEMORY in phases
    assert CognitiveCyclePhase.REASONING in phases
    assert CognitiveCyclePhase.PLANNING in phases
    assert CognitiveCyclePhase.LEARNING in phases
    assert CognitiveCyclePhase.REFLECTION in phases
    assert phases[-1] is CognitiveCyclePhase.COMPLETION


def test_cycle_can_run_partially_without_optional_managers():
    manager = CognitiveCycleManager()

    result = manager.run(
        CognitiveCycleContext("Solo observar", identity=ROBYIdentity())
    )

    assert result.normalized_status is CognitiveCycleStatus.PARTIAL
    assert result.is_complete is False
    assert result.reasoning_result is None
    assert result.plan is None
    assert result.completed_phases == (
        CognitiveCyclePhase.IDENTITY,
        CognitiveCyclePhase.COMPLETION,
    )


def test_cycle_system_prompt_lines_describe_last_result():
    manager = CognitiveCycleManager()

    empty_lines = manager.system_prompt_lines()
    manager.run(make_full_context())
    lines = manager.system_prompt_lines()

    assert empty_lines == ("Ciclo cognitivo M50: sin ejecución reciente.",)
    assert "Ciclo cognitivo M50:" in lines
    assert any("completed" in line for line in lines)
    assert any("Reflexión" in line for line in lines)


def test_cycle_result_to_dict_is_auditable():
    result = CognitiveCycleManager().run(make_full_context())

    data = result.to_dict()

    assert data["status"] == "completed"
    assert data["is_complete"] is True
    assert data["reasoning"] is not None
    assert data["plan"] is not None
    assert data["learned_experience"] is not None
    assert data["reflection"] is not None
    assert len(data["steps"]) == len(result.steps)


def test_cognitive_pipeline_can_run_full_cycle(tmp_path: Path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    cycle = CognitiveCycleManager()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        identity=ROBYIdentity(),
        mental_state=ROBYMentalState(),
        attention=AttentionManager(),
        working_memory=WorkingMemoryManager(),
        reasoning=ReasoningManager(),
        planning=PlanningManager(),
        learning=ExperientialLearningManager(),
        knowledge_gateway=KnowledgeGatewayManager(
            providers=(StaticKnowledgeProvider(),)
        ),
        reflection=ReflectionManager(),
        cognitive_cycle=cycle,
    )

    result = pipeline.process_turn(
        "ROBY, planifiquemos una ayuda para Cristina",
        call_llm=False,
    )

    assert result.cognitive_cycle is cycle
    assert cycle.last_result is not None
    assert cycle.last_result.is_complete is True
    assert "Ciclo cognitivo M50:" in result.system_prompt
    assert result.skipped_llm_reason == "llm_call_disabled"
