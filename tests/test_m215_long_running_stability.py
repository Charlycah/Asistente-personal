from datetime import datetime, timedelta, timezone

import pytest

from core.llm_provider import LLMRequest
from core.long_running_stability import (
    LongRunningStabilityAssessment,
    LongRunningStabilityMonitor,
    LongRunningStabilityRuntimeContributor,
    LongRunningStabilityState,
    StabilityDirective,
    StabilityObservation,
)
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m214_high_load_cognitive_scheduling import high_load_stack

NOW = datetime(2026, 7, 14, 19, 0, tzinfo=timezone.utc)


def stability_stack(*, blocked=False, capacity=4, interval=25, history_limit=32):
    *stack, high_load = high_load_stack(blocked=blocked, capacity=capacity)
    monitor = LongRunningStabilityMonitor(
        high_load,
        checkpoint_interval=interval,
        history_limit=history_limit,
    )
    return (*stack, high_load, monitor)


def test_first_nominal_cycle_is_stable():
    *_, monitor = stability_stack()
    result = monitor.assess(owner="Carlos", session_id="main", demand_units=4, now=NOW)
    assert result.state is LongRunningStabilityState.STABLE
    assert result.directive is StabilityDirective.CONTINUE
    assert result.drift_score == 0


def test_assessment_identity_is_deterministic_for_same_input_state():
    *_, high_load, _ = stability_stack()
    schedule = high_load.schedule(
        owner="Carlos", session_id="main", demand_units=4, now=NOW
    )
    first = LongRunningStabilityMonitor(high_load).assess_schedule(schedule)
    second = LongRunningStabilityMonitor(high_load).assess_schedule(schedule)
    assert first.assessment_id == second.assessment_id


def test_elevated_load_enters_observing_state():
    *_, monitor = stability_stack(capacity=4)
    result = monitor.assess(owner="Carlos", session_id="main", demand_units=5, now=NOW)
    assert result.state is LongRunningStabilityState.OBSERVING
    assert result.directive is StabilityDirective.OBSERVE


def test_checkpoint_interval_requests_checkpoint():
    *_, monitor = stability_stack(interval=2)
    monitor.assess(owner="Carlos", session_id="main", demand_units=4, now=NOW)
    result = monitor.assess(
        owner="Carlos",
        session_id="main",
        demand_units=4,
        now=NOW + timedelta(seconds=1),
    )
    assert result.checkpoint_due is True
    assert result.state is LongRunningStabilityState.CHECKPOINT_REQUIRED
    assert result.directive is StabilityDirective.CHECKPOINT


def test_shedding_enters_guarded_state():
    *_, monitor = stability_stack(capacity=1)
    result = monitor.assess(owner="Carlos", session_id="main", demand_units=3, now=NOW)
    assert result.state is LongRunningStabilityState.GUARDED
    assert result.directive is StabilityDirective.STABILIZE


def test_abrupt_load_change_produces_drift():
    *_, monitor = stability_stack(capacity=4)
    monitor.assess(owner="Carlos", session_id="main", demand_units=4, now=NOW)
    result = monitor.assess(
        owner="Carlos",
        session_id="main",
        demand_units=9,
        now=NOW + timedelta(seconds=1),
    )
    assert result.drift_score >= 70
    assert result.state is LongRunningStabilityState.GUARDED


def test_history_is_bounded():
    *_, monitor = stability_stack(history_limit=2)
    for offset in range(3):
        result = monitor.assess(
            owner="Carlos",
            session_id="main",
            demand_units=4,
            now=NOW + timedelta(seconds=offset),
        )
    assert result.cycle_count == 3
    assert len(result.observations) == 2
    assert tuple(item.sequence for item in result.observations) == (2, 3)


def test_sessions_have_independent_cycle_counts():
    *_, monitor = stability_stack()
    first = monitor.assess(owner="Carlos", session_id="one", now=NOW)
    second = monitor.assess(owner="Carlos", session_id="two", now=NOW)
    assert first.cycle_count == second.cycle_count == 1


def test_monitor_rejects_invalid_configuration():
    *_, high_load = high_load_stack()
    with pytest.raises(ValueError, match="checkpoint interval"):
        LongRunningStabilityMonitor(high_load, checkpoint_interval=1)
    with pytest.raises(ValueError, match="history limit"):
        LongRunningStabilityMonitor(high_load, history_limit=1)


def test_observation_rejects_naive_time():
    with pytest.raises(ValueError, match="timezone-aware"):
        StabilityObservation(1, "nominal", 1, 0, 0, datetime(2026, 1, 1))


def test_assessment_rejects_unbounded_drift():
    observation = StabilityObservation(1, "nominal", 1, 0, 0, NOW)
    with pytest.raises(ValueError, match="drift score"):
        LongRunningStabilityAssessment(
            "Carlos",
            "main",
            "stable",
            "continue",
            1,
            101,
            False,
            (observation,),
            ("source",),
            NOW,
        )


def test_runtime_contributor_publishes_stability_state():
    board, *_, monitor = stability_stack()
    contribution = LongRunningStabilityRuntimeContributor(monitor, board).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "long_running_stability"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "long_running_stability"
        )
        is not None
    )


def test_official_composition_orders_m215_after_m214():
    (
        board,
        state,
        bus,
        domain_coordinator,
        scheduler,
        arbitrator,
        fusion,
        health,
        optimizer,
        integrator,
        framework,
        engine,
        recovery,
        high_load,
        monitor,
    ) = stability_stack()
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
                cognitive_health_monitor=health,
                cognitive_performance_optimizer=optimizer,
                whole_system_integrator=integrator,
                cognitive_resilience_framework=framework,
                graceful_degradation_engine=engine,
                fault_recovery_coordinator=recovery,
                high_load_cognitive_scheduler=high_load,
                long_running_stability_monitor=monitor,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M215",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-5:] == (
        "cognitive_resilience_framework",
        "graceful_degradation_engine",
        "fault_recovery_coordination",
        "high_load_cognitive_scheduling",
        "long_running_stability",
    )


def test_composition_requires_high_load_scheduling():
    board, *_, monitor = stability_stack()
    with pytest.raises(ValueError, match="requires high-load scheduling"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                long_running_stability_monitor=monitor,
            )
        ).compose()


def test_monitor_has_no_concurrent_execution_or_repair_api():
    *_, monitor = stability_stack()
    assert not hasattr(monitor, "execute_concurrently")
    assert not hasattr(monitor, "spawn_worker")
    assert not hasattr(monitor, "restart_provider")
