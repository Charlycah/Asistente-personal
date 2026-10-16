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
from core.planning import (
    Plan,
    PlanGoal,
    PlanningContext,
    PlanningEngine,
    PlanningManager,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from core.provider_router import ProviderRouter
from core.reasoning import ReasoningContext, ReasoningManager
from core.working_memory import WorkingMemoryKind, WorkingMemoryManager


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta planificada", provider=self.name)


def test_plan_goal_validates_description_owner_and_priority():
    with pytest.raises(ValueError):
        PlanGoal(" ")

    with pytest.raises(ValueError):
        PlanGoal("Organizar vacaciones", owner=" ")

    with pytest.raises(ValueError):
        PlanGoal("Organizar vacaciones", priority=11)


def test_plan_step_validates_description_priority_and_status():
    with pytest.raises(ValueError):
        PlanStep(" ")

    with pytest.raises(ValueError):
        PlanStep("Revisar calendario", priority=0)

    with pytest.raises(ValueError):
        PlanStep("Revisar calendario", status="unknown")


def test_planning_context_validates_required_fields():
    with pytest.raises(ValueError):
        PlanningContext(goal=" ")

    with pytest.raises(ValueError):
        PlanningContext(goal="x", owner=" ")

    with pytest.raises(ValueError):
        PlanningContext(goal="x", created_at=datetime(2026, 7, 8))


def test_plan_requires_steps_and_timezone_aware_timestamp():
    goal = PlanGoal("Organizar la casa")

    with pytest.raises(ValueError):
        Plan(goal=goal, steps=())

    with pytest.raises(ValueError):
        Plan(
            goal=goal,
            steps=(PlanStep("Definir objetivo"),),
            created_at=datetime(2026, 7, 8),
        )


def test_planning_engine_creates_ordered_plan_from_context():
    memory = WorkingMemoryManager()
    memory.capture_user_input("Carlos quiere organizar vacaciones")
    reasoning = ReasoningManager()
    reasoning.reason(
        ReasoningContext(
            query="Organizar vacaciones",
            identity=ROBYIdentity(),
            working_memory=memory,
        )
    )
    context = PlanningContext(
        goal="Organizar vacaciones con Cristina",
        identity=ROBYIdentity(),
        working_memory=memory,
        reasoning=reasoning,
    )

    plan = PlanningEngine().create_plan(context)

    assert plan.goal.description == "Organizar vacaciones con Cristina"
    assert plan.goal.priority >= 6
    assert plan.progress == 0
    assert plan.next_step is not None
    assert plan.next_step.description.startswith("Definir el objetivo")
    assert "razonamiento previo" in plan.rationale
    assert any(step.depends_on for step in plan.steps)
    assert memory.memory.current_focus is not None
    assert memory.memory.current_focus.normalized_kind is WorkingMemoryKind.PLAN_STEP


def test_plan_updates_step_status_and_progress():
    first = PlanStep("Definir destino", priority=10)
    second = PlanStep("Consultar clima", priority=9, depends_on=(first.step_id,))
    plan = Plan(goal=PlanGoal("Viaje"), steps=(first, second))

    updated = plan.update_step(first.step_id, PlanStepStatus.DONE)

    assert updated.progress == 0.5
    assert updated.next_step is not None
    assert updated.next_step.step_id == second.step_id

    with pytest.raises(KeyError):
        updated.update_step("missing", PlanStepStatus.DONE)


def test_planning_manager_controls_plan_lifecycle():
    manager = PlanningManager()
    plan = manager.create_plan(PlanningContext(goal="Preparar recordatorios"))

    assert manager.last_plan is plan
    assert manager.activate().normalized_status is PlanStatus.ACTIVE
    assert manager.pause().normalized_status is PlanStatus.PAUSED
    assert manager.complete().normalized_status is PlanStatus.COMPLETED
    assert manager.cancel().normalized_status is PlanStatus.CANCELLED


def test_planning_manager_requires_active_plan_for_updates():
    manager = PlanningManager()

    with pytest.raises(ValueError):
        manager.activate()

    with pytest.raises(ValueError):
        manager.update_step("missing", PlanStepStatus.DONE)


def test_planning_system_prompt_lines_and_snapshot_are_serializable():
    manager = PlanningManager()
    empty_lines = manager.system_prompt_lines()
    plan = manager.create_plan(PlanningContext(goal="Coordinar compras"))
    lines = manager.system_prompt_lines()
    snapshot = manager.to_dict()

    assert empty_lines == ("Planificación cognitiva de ROBY: sin plan activo",)
    assert "Plan cognitivo activo de ROBY:" in lines
    assert any("Objetivo: Coordinar compras" in line for line in lines)
    assert snapshot["last_plan"]["goal"]["description"] == "Coordinar compras"
    assert snapshot["last_plan"]["steps"]
    assert plan.to_dict()["next_step"] is not None


def test_planning_prioritizes_cristina_and_attention():
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

    plan = PlanningEngine().create_plan(
        PlanningContext(
            goal="Ayudar a Cristina con medicación urgente",
            attention=attention,
        )
    )

    assert plan.goal.priority == 10
    assert "atención" in plan.rationale


def test_cognitive_pipeline_can_inject_planning_into_system_prompt(tmp_path):
    provider = RecordingProvider()
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    identity = ROBYIdentity()
    mental_state = ROBYMentalState()
    attention = AttentionManager()
    working_memory = WorkingMemoryManager()
    reasoning = ReasoningManager()
    planning = PlanningManager()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
        identity=identity,
        mental_state=mental_state,
        attention=attention,
        working_memory=working_memory,
        reasoning=reasoning,
        planning=planning,
    )

    result = pipeline.process_turn("Necesito planificar los próximos pasos")

    assert result.planning is planning
    assert planning.last_plan is not None
    assert "Plan cognitivo activo de ROBY:" in result.system_prompt
    assert "Próximo paso" in result.system_prompt
    assert provider.requests[0].system_prompt == result.system_prompt
