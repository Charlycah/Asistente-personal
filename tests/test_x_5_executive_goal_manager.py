from datetime import datetime, timezone

from app.executive_goal_manager import ExecutiveGoalManager
from app.executive_working_memory import ExecutiveWorkingMemory
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime.now(timezone.utc)


def request(text: str, session_id: str = "household-main"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


def test_manager_keeps_multiple_goals_and_one_active_focus():
    manager = ExecutiveGoalManager()
    manager.observe(request("Quiero organizar un viaje"), now=NOW)
    manager.observe(request("Necesito preparar la compra de una notebook"), now=NOW)

    result = manager.intercept(request("Objetivos ejecutivos"), now=NOW)

    assert result is not None
    assert "organizar un viaje" in result.response_text
    assert "preparar la compra de una notebook" in result.response_text
    assert manager.active_goal(owner="Carlos", session_id="household-main").name == (
        "preparar la compra de una notebook"
    )


def test_manager_can_switch_and_prioritize_a_goal():
    manager = ExecutiveGoalManager()
    manager.observe(request("Quiero organizar un viaje"), now=NOW)
    manager.observe(request("Necesito preparar la compra de una notebook"), now=NOW)

    switched = manager.intercept(
        request("Cambiar al objetivo organizar un viaje"), now=NOW
    )
    prioritized = manager.intercept(
        request("Prioridad alta para organizar un viaje"), now=NOW
    )

    assert switched is not None
    assert prioritized is not None
    active = manager.active_goal(owner="Carlos", session_id="household-main")
    assert active is not None
    assert active.name == "organizar un viaje"
    assert active.priority.value == "high"


def test_completed_goal_leaves_another_open_goal_active():
    manager = ExecutiveGoalManager()
    manager.observe(request("Quiero organizar un viaje"), now=NOW)
    manager.observe(request("Necesito preparar la compra de una notebook"), now=NOW)

    result = manager.intercept(
        request("Completar objetivo ejecutivo preparar la compra de una notebook"),
        now=NOW,
    )

    assert result is not None
    active = manager.active_goal(owner="Carlos", session_id="household-main")
    assert active is not None
    assert active.name == "organizar un viaje"


def test_working_memory_uses_the_same_goal_manager():
    manager = ExecutiveGoalManager()
    memory = ExecutiveWorkingMemory(manager)
    memory.intercept(request("Quiero organizar un viaje"), now=NOW)

    goal = manager.active_goal(owner="Carlos", session_id="household-main")
    status = memory.intercept(request("En que estabamos"), now=NOW)

    assert goal is not None
    assert status is not None
    assert goal.name in status.response_text


def test_registry_runs_goal_manager_before_working_memory():
    manager = ExecutiveGoalManager()
    memory = ExecutiveWorkingMemory(manager)
    registry = OfficialRuntimeCapabilityRegistry()
    registry.set_goal_manager(manager)
    registry.set_working_memory(memory)
    registry.intercept(request("Quiero organizar un viaje"), now=NOW)

    result = registry.intercept(request("Objetivos ejecutivos"), now=NOW)

    assert result is not None
    assert result.rationale == "executive_goal_manager_list_completed"
