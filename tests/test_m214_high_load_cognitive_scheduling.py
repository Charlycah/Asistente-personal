from datetime import datetime, timezone

import pytest

from core.high_load_cognitive_scheduling import (
    CognitiveAdmissionDisposition,
    CognitiveLoadBand,
    HighLoadCognitiveSchedule,
    HighLoadCognitiveScheduler,
    HighLoadCognitiveSchedulingRuntimeContributor,
    HighLoadScheduleItem,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m213_fault_recovery_coordination import recovery_stack

NOW = datetime(2026, 7, 14, 18, 0, tzinfo=timezone.utc)


def high_load_stack(*, blocked=False, capacity=4):
    *stack, recovery = recovery_stack(blocked=blocked)
    scheduler = stack[4]
    high_load = HighLoadCognitiveScheduler(scheduler, recovery, capacity_units=capacity)
    return (*stack, recovery, high_load)


def test_schedule_identity_is_deterministic():
    *_, scheduler = high_load_stack()
    first = scheduler.schedule(
        owner="Carlos", session_id="main", demand_units=8, now=NOW
    )
    second = scheduler.schedule(
        owner="Carlos", session_id="main", demand_units=8, now=NOW
    )
    assert first.schedule_id == second.schedule_id


@pytest.mark.parametrize(
    ("demand", "capacity", "band"),
    ((4, 4, "nominal"), (5, 4, "elevated"), (8, 4, "high"), (9, 4, "saturated")),
)
def test_load_ratio_maps_to_expected_band(demand, capacity, band):
    *_, scheduler = high_load_stack(capacity=capacity)
    result = scheduler.schedule(
        owner="Carlos", session_id="main", demand_units=demand, now=NOW
    )
    assert result.load_band is CognitiveLoadBand(band)


def test_nominal_capacity_admits_available_work():
    *_, scheduler = high_load_stack(capacity=4)
    result = scheduler.schedule(
        owner="Carlos", session_id="main", demand_units=4, now=NOW
    )
    assert result.items
    assert result.items[0].disposition is CognitiveAdmissionDisposition.ADMIT


def test_elevated_load_defers_over_capacity_work():
    *_, scheduler = high_load_stack(capacity=1)
    result = scheduler.schedule(
        owner="Carlos", session_id="main", demand_units=2, now=NOW
    )
    assert (
        any(
            item.disposition is CognitiveAdmissionDisposition.DEFER
            for item in result.items[1:]
        )
        or len(result.items) == 1
    )


def test_saturated_load_sheds_over_capacity_work():
    *_, scheduler = high_load_stack(capacity=1)
    result = scheduler.schedule(
        owner="Carlos", session_id="main", demand_units=3, now=NOW
    )
    assert result.load_band is CognitiveLoadBand.SATURATED
    if len(result.items) > 1:
        assert result.items[1].disposition is CognitiveAdmissionDisposition.SHED


def test_held_recovery_restricts_admission_to_one():
    *_, scheduler = high_load_stack(blocked=True, capacity=8)
    result = scheduler.schedule(
        owner="Carlos", session_id="main", demand_units=8, now=NOW
    )
    assert (
        sum(
            item.disposition is CognitiveAdmissionDisposition.ADMIT
            for item in result.items
        )
        <= 1
    )


def test_schedule_item_rejects_nonpositive_sequence():
    with pytest.raises(ValueError, match="sequence must be positive"):
        HighLoadScheduleItem(0, "reason", "admit", 90, ("load",))


def test_schedule_rejects_noncontiguous_items():
    item = HighLoadScheduleItem(2, "reason", "admit", 90, ("load",))
    with pytest.raises(ValueError, match="items must be contiguous"):
        HighLoadCognitiveSchedule(
            "Carlos", "main", "nominal", 1, 1, (item,), ("source",), NOW
        )


def test_scheduler_rejects_invalid_capacity():
    *stack, recovery = recovery_stack()
    with pytest.raises(ValueError, match="capacity must be positive"):
        HighLoadCognitiveScheduler(stack[4], recovery, capacity_units=0)


def test_runtime_contributor_publishes_load_band():
    board, *_, scheduler = high_load_stack()
    contribution = HighLoadCognitiveSchedulingRuntimeContributor(
        scheduler, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "high_load_cognitive_scheduling"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "high_load_cognitive_schedule"
        )
        is not None
    )


def test_official_composition_orders_m214_after_m213():
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
        high_load,
    ) = high_load_stack()
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
                high_load_cognitive_scheduler=high_load,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M214",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-4:] == (
        "cognitive_resilience_framework",
        "graceful_degradation_engine",
        "fault_recovery_coordination",
        "high_load_cognitive_scheduling",
    )


def test_composition_requires_fault_recovery():
    board, *_, high_load = high_load_stack()
    with pytest.raises(ValueError, match="requires fault recovery"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                high_load_cognitive_scheduler=high_load,
            )
        ).compose()


def test_scheduler_has_no_concurrent_execution_api():
    *_, scheduler = high_load_stack()
    assert not hasattr(scheduler, "execute_concurrently")
    assert not hasattr(scheduler, "spawn_worker")
