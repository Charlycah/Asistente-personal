from datetime import datetime, timezone

import pytest

from core.cognitive_event_bus import CognitiveEvent
from core.cognitive_performance_optimization import (
    CognitiveOptimizationPlan,
    CognitiveOptimizationRecommendation,
    CognitiveOptimizationStatus,
    CognitivePerformanceOptimizationRuntimeContributor,
    CognitivePerformanceOptimizer,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m208_cognitive_health_monitoring import monitor_stack

NOW = datetime(2026, 7, 14, 9, 0, tzinfo=timezone.utc)


def optimizer_stack(*, blocked=False):
    board, state, bus, coordinator, scheduler, arbitrator, fusion, monitor = (
        monitor_stack(blocked=blocked)
    )
    monitor.assess(owner="Carlos", session_id="main", now=NOW)
    optimizer = CognitivePerformanceOptimizer(monitor)
    return (
        board,
        state,
        bus,
        coordinator,
        scheduler,
        arbitrator,
        fusion,
        monitor,
        optimizer,
    )


def test_plan_identity_is_deterministic():
    *_, optimizer = optimizer_stack()
    first = optimizer.optimize(owner="Carlos", session_id="main", now=NOW)
    second = optimizer.optimize(owner="Carlos", session_id="main", now=NOW)
    assert first.plan_id == second.plan_id


def test_healthy_state_maintains_current_profile():
    *_, optimizer = optimizer_stack()
    plan = optimizer.optimize(owner="Carlos", session_id="main", now=NOW)
    assert plan.status in {
        CognitiveOptimizationStatus.OPTIMAL,
        CognitiveOptimizationStatus.TUNE,
    }
    assert plan.recommendations


def test_blocked_state_recommends_constraints_or_deferred_review():
    *_, optimizer = optimizer_stack(blocked=True)
    plan = optimizer.optimize(owner="Carlos", session_id="main", now=NOW)
    actions = {item.action for item in plan.recommendations}
    assert actions & {
        "preserve_constraints_and_limit_parallelism",
        "review_deferred_work",
    }


def test_critical_health_recommends_stabilization():
    *_, bus, _, _, _, fusion, monitor, optimizer = optimizer_stack()
    for microsecond, value in ((1, "direct"), (2, "exploratory")):
        bus.publish(
            CognitiveEvent(
                owner="Carlos",
                session_id="main",
                event_type="signal_published",
                source_domain="reasoning",
                topic="answer_mode",
                value=value,
                created_at=NOW.replace(microsecond=microsecond),
            )
        )
    fusion.fuse(owner="Carlos", session_id="main", now=NOW)
    monitor.assess(owner="Carlos", session_id="main", now=NOW)
    plan = optimizer.optimize(owner="Carlos", session_id="main", now=NOW)
    assert plan.status is CognitiveOptimizationStatus.STABILIZE
    assert plan.recommendations[0].action == "stabilize_conflicted_context"


def test_recommendation_rejects_invalid_priority():
    with pytest.raises(ValueError, match="between one and one hundred"):
        CognitiveOptimizationRecommendation("x", 0, 0.5)


def test_plan_rejects_duplicate_recommendations():
    recommendation = CognitiveOptimizationRecommendation("maintain", 10, 0.2)
    with pytest.raises(ValueError, match="recommendations must be unique"):
        CognitiveOptimizationPlan(
            owner="Carlos",
            session_id="main",
            status="optimal",
            baseline_score=1.0,
            recommendations=(recommendation, recommendation),
            created_at=NOW,
        )


def test_runtime_contributor_publishes_optimization_candidate():
    board, *_, optimizer = optimizer_stack()
    contribution = CognitivePerformanceOptimizationRuntimeContributor(
        optimizer, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "cognitive_performance_optimization"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "cognitive_optimization_status"
        )
        is not None
    )


def test_optimizer_does_not_mutate_health_report():
    *_, monitor, optimizer = optimizer_stack()
    before = monitor.last_report
    optimizer.optimize(owner="Carlos", session_id="main", now=NOW)
    assert monitor.last_report == before


def test_official_composition_orders_m209_after_m208():
    (
        board,
        state,
        bus,
        coordinator,
        scheduler,
        arbitrator,
        fusion,
        monitor,
        optimizer,
    ) = optimizer_stack()
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                global_cognitive_state=state,
                cognitive_event_bus=bus,
                cross_domain_coordinator=coordinator,
                unified_cognitive_scheduler=scheduler,
                executive_arbitrator=arbitrator,
                global_context_fusion=fusion,
                cognitive_health_monitor=monitor,
                cognitive_performance_optimizer=optimizer,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M209",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-9:] == (
        "unified_cognitive_blackboard",
        "global_cognitive_state",
        "cognitive_event_bus",
        "cross_domain_coordination",
        "unified_cognitive_scheduler",
        "executive_arbitration",
        "global_context_fusion",
        "cognitive_health_monitoring",
        "cognitive_performance_optimization",
    )


def test_composition_requires_blackboard_and_health_monitor():
    *_, optimizer = optimizer_stack()
    with pytest.raises(ValueError, match="requires the unified cognitive blackboard"):
        RuntimeCompositionRoot(
            dependencies(cognitive_performance_optimizer=optimizer)
        ).compose()
    board, *_ = optimizer_stack()
    with pytest.raises(ValueError, match="requires cognitive health monitoring"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                cognitive_performance_optimizer=optimizer,
            )
        ).compose()
