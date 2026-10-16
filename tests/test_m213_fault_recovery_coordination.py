from datetime import datetime, timezone

import pytest

from core.fault_recovery_coordination import (
    FaultRecoveryCoordinator,
    FaultRecoveryDisposition,
    FaultRecoveryPlan,
    FaultRecoveryRuntimeContributor,
    FaultRecoveryState,
    FaultRecoveryStep,
)
from core.graceful_degradation_engine import CognitiveDegradationMode
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m212_graceful_degradation_engine import assessment, degradation_stack

NOW = datetime(2026, 7, 14, 15, 0, tzinfo=timezone.utc)


def recovery_stack(*, blocked=False):
    *stack, engine = degradation_stack(blocked=blocked)
    coordinator = FaultRecoveryCoordinator(engine)
    return (*stack, engine, coordinator)


def decision(mode):
    *_, engine = degradation_stack()
    posture = {
        CognitiveDegradationMode.FULL: "robust",
        CognitiveDegradationMode.CONSERVATIVE: "guarded",
        CognitiveDegradationMode.ESSENTIAL: "degraded",
        CognitiveDegradationMode.CONTAINED: "contained",
    }[mode]
    return engine.activate_assessment(assessment(posture))


def test_plan_identity_is_deterministic():
    *_, coordinator = recovery_stack()
    first = coordinator.coordinate(owner="Carlos", session_id="main", now=NOW)
    second = coordinator.coordinate(owner="Carlos", session_id="main", now=NOW)
    assert first.plan_id == second.plan_id


@pytest.mark.parametrize(
    ("mode", "state"),
    (
        (CognitiveDegradationMode.FULL, FaultRecoveryState.STABLE),
        (CognitiveDegradationMode.CONSERVATIVE, FaultRecoveryState.OBSERVING),
        (CognitiveDegradationMode.ESSENTIAL, FaultRecoveryState.STABILIZING),
        (CognitiveDegradationMode.CONTAINED, FaultRecoveryState.HELD),
    ),
)
def test_mode_maps_to_expected_recovery_state(mode, state):
    *_, coordinator = recovery_stack()
    assert coordinator.coordinate_decision(decision(mode)).state is state


def test_stable_state_verifies_baseline_only():
    *_, coordinator = recovery_stack()
    plan = coordinator.coordinate_decision(decision(CognitiveDegradationMode.FULL))
    assert plan.steps[0].disposition is FaultRecoveryDisposition.VERIFY
    assert plan.held_capabilities == ()


def test_essential_mode_retries_restricted_capabilities():
    *_, coordinator = recovery_stack()
    plan = coordinator.coordinate_decision(decision(CognitiveDegradationMode.ESSENTIAL))
    assert plan.state is FaultRecoveryState.STABILIZING
    assert all(
        item.disposition is FaultRecoveryDisposition.RETRY for item in plan.steps
    )
    assert plan.held_capabilities


def test_contained_mode_holds_restricted_capabilities():
    *_, coordinator = recovery_stack()
    plan = coordinator.coordinate_decision(decision(CognitiveDegradationMode.CONTAINED))
    assert all(item.disposition is FaultRecoveryDisposition.HOLD for item in plan.steps)
    assert "conversation_continuity" not in plan.held_capabilities


def test_step_rejects_nonpositive_sequence():
    with pytest.raises(ValueError, match="sequence must be positive"):
        FaultRecoveryStep(0, "reasoning", "verify", ("reason",))


def test_plan_rejects_noncontiguous_steps():
    step = FaultRecoveryStep(2, "reasoning", "verify", ("reason",))
    with pytest.raises(ValueError, match="steps must be contiguous"):
        FaultRecoveryPlan(
            owner="Carlos",
            session_id="main",
            state="stable",
            steps=(step,),
            restored_capabilities=(),
            held_capabilities=(),
            source_reference_ids=("decision",),
            created_at=NOW,
        )


def test_runtime_contributor_publishes_recovery_state():
    board, *_, coordinator = recovery_stack()
    contribution = FaultRecoveryRuntimeContributor(coordinator, board).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "fault_recovery_coordination"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "fault_recovery_state"
        )
        is not None
    )


def test_official_composition_orders_m213_after_m212():
    (
        board,
        state,
        bus,
        domain_coordinator,
        scheduler,
        arbitrator,
        fusion,
        monitor,
        optimizer,
        integrator,
        framework,
        engine,
        recovery,
    ) = recovery_stack()
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                global_cognitive_state=state,
                cognitive_event_bus=bus,
                cross_domain_coordinator=domain_coordinator,
                unified_cognitive_scheduler=scheduler,
                executive_arbitrator=arbitrator,
                global_context_fusion=fusion,
                cognitive_health_monitor=monitor,
                cognitive_performance_optimizer=optimizer,
                whole_system_integrator=integrator,
                cognitive_resilience_framework=framework,
                graceful_degradation_engine=engine,
                fault_recovery_coordinator=recovery,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M213",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-3:] == (
        "cognitive_resilience_framework",
        "graceful_degradation_engine",
        "fault_recovery_coordination",
    )


def test_composition_requires_graceful_degradation():
    board, *_, recovery = recovery_stack()
    with pytest.raises(ValueError, match="requires graceful degradation"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                fault_recovery_coordinator=recovery,
            )
        ).compose()


def test_coordinator_has_no_external_repair_api():
    *_, coordinator = recovery_stack()
    assert not hasattr(coordinator, "restart_provider")
    assert not hasattr(coordinator, "mutate_platform")
