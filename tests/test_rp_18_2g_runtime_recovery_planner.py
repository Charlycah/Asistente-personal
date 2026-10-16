from __future__ import annotations

import pytest

from app.resident_component_registry import ResidentHealth, ResidentState
from app.runtime_capability_graph import RuntimeCapabilityGraph
from app.runtime_recovery_planner import (
    RuntimeRecoveryAction,
    RuntimeRecoveryPlanner,
    RuntimeRecoveryPlanStatus,
)
from tests.test_rp_18_2e_runtime_health_readiness import _resident, _snapshot
from tests.test_rp_18_2f_runtime_capability_graph import _node


def _graph() -> RuntimeCapabilityGraph:
    return RuntimeCapabilityGraph(
        (
            _node("memory", required_residents=("memory_runtime",)),
            _node(
                "reasoning",
                required_residents=("reasoning_runtime",),
                required_capabilities=("memory",),
            ),
            _node(
                "conversation",
                optional_residents=("voice_runtime",),
                required_capabilities=("reasoning",),
            ),
        )
    )


def test_healthy_requested_capability_needs_no_recovery() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(
            residents=(
                _resident("memory_runtime"),
                _resident("reasoning_runtime"),
                _resident("voice_runtime"),
            )
        ),
        _graph(),
        capabilities=("conversation",),
    )
    assert plan.status is RuntimeRecoveryPlanStatus.NOT_REQUIRED
    assert not plan.required


def test_unknown_requested_capability_is_rejected() -> None:
    with pytest.raises(ValueError, match="no registrada"):
        RuntimeRecoveryPlanner().plan(_snapshot(), _graph(), capabilities=("camera",))


def test_empty_requested_capability_is_rejected() -> None:
    with pytest.raises(ValueError, match="vacíos"):
        RuntimeRecoveryPlanner().plan(_snapshot(), _graph(), capabilities=("",))


def test_duplicate_requested_capabilities_are_normalized() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(), _graph(), capabilities=("Memory", "memory")
    )
    assert plan.requested_capabilities == ("memory",)


def test_missing_required_resident_blocks_plan() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(), _graph(), capabilities=("memory",)
    )
    assert plan.status is RuntimeRecoveryPlanStatus.BLOCKED
    assert not plan.recoverable
    assert plan.steps[0].action is RuntimeRecoveryAction.REGISTER_RESIDENT


def test_missing_optional_resident_does_not_block_plan() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(
            residents=(
                _resident("memory_runtime"),
                _resident("reasoning_runtime"),
            )
        ),
        _graph(),
        capabilities=("conversation",),
    )
    assert plan.status is RuntimeRecoveryPlanStatus.PLANNED
    assert plan.recoverable
    assert plan.steps[0].target_id == "voice_runtime"
    assert not plan.steps[0].required


def test_failed_registered_resident_is_recovered_not_registered() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(
            residents=(
                _resident(
                    "memory_runtime",
                    state=ResidentState.FAILED,
                    health=ResidentHealth.UNAVAILABLE,
                ),
            )
        ),
        _graph(),
        capabilities=("memory",),
    )
    assert plan.steps[0].action is RuntimeRecoveryAction.RECOVER_RESIDENT


def test_plan_includes_transitive_dependency_residents() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(), _graph(), capabilities=("conversation",)
    )
    assert {step.target_id for step in plan.steps} == {
        "memory_runtime",
        "reasoning_runtime",
        "voice_runtime",
    }


def test_registered_residents_follow_startup_order() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(
            residents=(
                _resident(
                    "memory_runtime",
                    state=ResidentState.FAILED,
                    health=ResidentHealth.UNAVAILABLE,
                    startup_order=20,
                ),
                _resident(
                    "reasoning_runtime",
                    state=ResidentState.FAILED,
                    health=ResidentHealth.UNAVAILABLE,
                    startup_order=10,
                ),
            )
        ),
        _graph(),
        capabilities=("reasoning",),
    )
    assert tuple(step.target_id for step in plan.steps) == (
        "reasoning_runtime",
        "memory_runtime",
    )


def test_lifecycle_and_supervisor_are_planned_first() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(lifecycle_running=False, supervisor_running=False),
        _graph(),
        capabilities=("memory",),
    )
    assert tuple(step.action for step in plan.steps[:2]) == (
        RuntimeRecoveryAction.RESTORE_LIFECYCLE,
        RuntimeRecoveryAction.RESTORE_SUPERVISOR,
    )


def test_step_lists_capabilities_it_would_restore() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(), _graph(), capabilities=("conversation",)
    )
    memory = next(step for step in plan.steps if step.target_id == "memory_runtime")
    assert memory.restores_capabilities == ("memory",)


def test_plan_serialization_uses_values_and_iso_time() -> None:
    plan = RuntimeRecoveryPlanner().plan(
        _snapshot(), _graph(), capabilities=("memory",)
    )
    payload = plan.to_dict()
    assert payload["status"] == "blocked"
    assert payload["steps"][0]["action"] == "register_resident"
    assert isinstance(payload["snapshot_generated_at"], str)
