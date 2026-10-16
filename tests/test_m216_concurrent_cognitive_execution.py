from datetime import datetime, timezone
from threading import Barrier

import pytest

from core.concurrent_cognitive_execution import (
    ConcurrentCognitiveExecution,
    ConcurrentCognitiveExecutor,
    ConcurrentExecutionStatus,
    ConcurrentTaskResult,
    ConcurrentTaskStatus,
)
from core.high_load_cognitive_scheduling import (
    HighLoadCognitiveSchedule,
    HighLoadScheduleItem,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m215_long_running_stability import stability_stack

NOW = datetime(2026, 7, 14, 20, 0, tzinfo=timezone.utc)


def concurrent_stack(*, blocked=False, capacity=4, workers=4, interval=25):
    *stack, high_load, monitor = stability_stack(
        blocked=blocked, capacity=capacity, interval=interval
    )
    executor = ConcurrentCognitiveExecutor(monitor, max_workers=workers)
    return (*stack, high_load, monitor, executor)


def assessment_with_actions(monitor, actions, *, demand=2):
    base = monitor.scheduler.schedule(
        owner="Carlos", session_id="main", demand_units=demand, now=NOW
    )
    schedule = HighLoadCognitiveSchedule(
        base.owner,
        base.session_id,
        base.load_band,
        demand,
        max(demand, 2),
        tuple(
            HighLoadScheduleItem(index, action, "admit", 100 - index, ("test",))
            for index, action in enumerate(actions, 1)
        ),
        base.source_reference_ids,
        NOW,
    )
    monitor.scheduler.last_schedule = schedule
    return monitor.assess_schedule(schedule)


def test_executes_admitted_tasks_and_preserves_logical_order():
    *_, monitor, executor = concurrent_stack(workers=2)
    assessment = assessment_with_actions(monitor, ("first", "second"))
    result = executor.execute_assessment(
        assessment, {"first": lambda: "one", "second": lambda: "two"}
    )
    assert result.status is ConcurrentExecutionStatus.COMPLETED
    assert tuple(item.value for item in result.results) == ("one", "two")


def test_execution_is_genuinely_parallel_with_two_workers():
    *_, monitor, executor = concurrent_stack(workers=2)
    assessment = assessment_with_actions(monitor, ("first", "second"))
    barrier = Barrier(2, timeout=2)

    def work():
        barrier.wait()
        return "done"

    result = executor.execute_assessment(assessment, {"first": work, "second": work})
    assert result.status is ConcurrentExecutionStatus.COMPLETED


def test_task_failure_is_isolated_as_partial_result():
    *_, monitor, executor = concurrent_stack(workers=2)
    assessment = assessment_with_actions(monitor, ("good", "bad"))

    def fail():
        raise RuntimeError("boom")

    result = executor.execute_assessment(
        assessment, {"good": lambda: "ok", "bad": fail}
    )
    assert result.status is ConcurrentExecutionStatus.PARTIAL
    assert result.results[0].status is ConcurrentTaskStatus.COMPLETED
    assert result.results[1].status is ConcurrentTaskStatus.FAILED
    assert "RuntimeError: boom" == result.results[1].error


def test_guarded_stability_blocks_handlers():
    *_, monitor, executor = concurrent_stack(capacity=1)
    assessment = assessment_with_actions(monitor, ("work",), demand=3)
    called = False

    def work():
        nonlocal called
        called = True
        return "no"

    result = executor.execute_assessment(assessment, {"work": work})
    assert result.status is ConcurrentExecutionStatus.BLOCKED
    assert result.results[0].status is ConcurrentTaskStatus.SKIPPED
    assert called is False


def test_missing_handlers_produce_idle_execution():
    *_, monitor, executor = concurrent_stack()
    assessment = assessment_with_actions(monitor, ("work",))
    result = executor.execute_assessment(assessment, {})
    assert result.status is ConcurrentExecutionStatus.IDLE
    assert result.results == ()


def test_worker_limit_is_bounded_by_config_and_task_count():
    *_, monitor, executor = concurrent_stack(workers=8)
    assessment = assessment_with_actions(monitor, ("one", "two"))
    result = executor.execute_assessment(
        assessment, {"one": lambda: 1, "two": lambda: 2}
    )
    assert result.worker_limit == 2


def test_checkpoint_state_reduces_worker_limit_to_one():
    *_, high_load, monitor, executor = concurrent_stack(workers=4, interval=2)
    first = high_load.schedule(owner="Carlos", session_id="main", now=NOW)
    monitor.assess_schedule(first)
    assessment = assessment_with_actions(monitor, ("work",))
    result = executor.execute_assessment(assessment, {"work": lambda: "ok"})
    assert result.worker_limit == 1


def test_executor_rejects_invalid_worker_limit():
    *_, monitor = stability_stack()
    with pytest.raises(ValueError, match="max workers"):
        ConcurrentCognitiveExecutor(monitor, max_workers=0)


def test_failed_result_requires_error():
    with pytest.raises(ValueError, match="requires an error"):
        ConcurrentTaskResult(1, "work", "failed")


def test_execution_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        ConcurrentCognitiveExecution(
            "Carlos", "main", "idle", 1, (), (), (), datetime(2026, 1, 1)
        )


def test_execution_rejects_result_order_mismatch():
    result = ConcurrentTaskResult(2, "work", "completed", value="ok")
    with pytest.raises(ValueError, match="preserve task order"):
        ConcurrentCognitiveExecution(
            "Carlos", "main", "completed", 1, (), (result,), (), NOW
        )


def test_runtime_contributor_publishes_execution_status():
    board, *_, executor = concurrent_stack()
    contribution = executor_runtime(executor, board).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "concurrent_cognitive_execution"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "concurrent_cognitive_execution"
        )
        is not None
    )


def executor_runtime(executor, board):
    from core.concurrent_cognitive_execution import (
        ConcurrentCognitiveExecutionRuntimeContributor,
    )

    return ConcurrentCognitiveExecutionRuntimeContributor(executor, board)


def test_official_composition_orders_m216_after_m215():
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
        executor,
    ) = concurrent_stack()
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
                concurrent_cognitive_executor=executor,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M216",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-2:] == (
        "long_running_stability",
        "concurrent_cognitive_execution",
    )


def test_composition_requires_long_running_stability():
    board, *_, executor = concurrent_stack()
    with pytest.raises(ValueError, match="requires long-running stability"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                concurrent_cognitive_executor=executor,
            )
        ).compose()


def test_execution_identity_is_deterministic_for_same_inputs():
    *_, monitor, executor = concurrent_stack()
    assessment = assessment_with_actions(monitor, ("work",))
    first = executor.execute_assessment(assessment, {"work": lambda: "ok"})
    second = executor.execute_assessment(assessment, {"work": lambda: "ok"})
    assert first.execution_id == second.execution_id


def test_executor_has_no_provider_restart_or_infrastructure_api():
    *_, executor = concurrent_stack()
    assert not hasattr(executor, "restart_provider")
    assert not hasattr(executor, "scale_cluster")
    assert not hasattr(executor, "mutate_infrastructure")
