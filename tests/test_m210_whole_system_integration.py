from datetime import datetime, timezone

import pytest

from core.cognitive_event_bus import CognitiveEvent
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from core.whole_system_integration import (
    WholeSystemComponentState,
    WholeSystemIntegrationReport,
    WholeSystemIntegrationRuntimeContributor,
    WholeSystemIntegrationStatus,
    WholeSystemIntegrator,
)
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m209_cognitive_performance_optimization import optimizer_stack

NOW = datetime(2026, 7, 14, 10, 0, tzinfo=timezone.utc)


def integration_stack(*, blocked=False):
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
    ) = optimizer_stack(blocked=blocked)
    integrator = WholeSystemIntegrator(optimizer)
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
        integrator,
    )


def test_report_identity_is_deterministic():
    *_, integrator = integration_stack()
    first = integrator.integrate(owner="Carlos", session_id="main", now=NOW)
    second = integrator.integrate(owner="Carlos", session_id="main", now=NOW)
    assert first.report_id == second.report_id


def test_healthy_stack_is_operationally_ready():
    *_, integrator = integration_stack()
    report = integrator.integrate(owner="Carlos", session_id="main", now=NOW)
    assert report.status in {
        WholeSystemIntegrationStatus.READY,
        WholeSystemIntegrationStatus.CONSTRAINED,
    }
    assert report.operational_ready is True
    assert len(report.components) == 9


def test_blocked_stack_is_not_operationally_ready():
    *_, integrator = integration_stack(blocked=True)
    report = integrator.integrate(owner="Carlos", session_id="main", now=NOW)
    assert report.status in {
        WholeSystemIntegrationStatus.CONSTRAINED,
        WholeSystemIntegrationStatus.DEGRADED,
        WholeSystemIntegrationStatus.BLOCKED,
    }
    assert report.constraints


def test_conflicted_context_blocks_whole_system():
    _, _, bus, _, _, _, fusion, monitor, optimizer, integrator = integration_stack()
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
    optimizer.optimize(owner="Carlos", session_id="main", now=NOW)
    report = integrator.integrate(owner="Carlos", session_id="main", now=NOW)
    assert report.status is WholeSystemIntegrationStatus.BLOCKED
    assert report.operational_ready is False


def test_component_state_requires_complete_values():
    with pytest.raises(ValueError, match="must be complete"):
        WholeSystemComponentState("", "available", "ref")


def test_report_rejects_duplicate_components():
    component = WholeSystemComponentState("m201", "available", "ref")
    with pytest.raises(ValueError, match="components must be unique"):
        WholeSystemIntegrationReport(
            owner="Carlos",
            session_id="main",
            status="ready",
            operational_ready=True,
            score=1.0,
            components=(component, component),
            created_at=NOW,
        )


def test_runtime_contributor_publishes_whole_system_health():
    board, *_, integrator = integration_stack()
    contribution = WholeSystemIntegrationRuntimeContributor(
        integrator, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "whole_system_integration"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "whole_system_integration_status"
        )
        is not None
    )


def test_integration_does_not_mutate_optimization_plan():
    *_, optimizer, integrator = integration_stack()
    before = optimizer.optimize(owner="Carlos", session_id="main", now=NOW)
    integrator.integrate(owner="Carlos", session_id="main", now=NOW)
    assert optimizer.last_plan == before


def test_official_composition_orders_m210_after_m209():
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
        integrator,
    ) = integration_stack()
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
                whole_system_integrator=integrator,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M210",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-10:] == (
        "unified_cognitive_blackboard",
        "global_cognitive_state",
        "cognitive_event_bus",
        "cross_domain_coordination",
        "unified_cognitive_scheduler",
        "executive_arbitration",
        "global_context_fusion",
        "cognitive_health_monitoring",
        "cognitive_performance_optimization",
        "whole_system_integration",
    )


def test_composition_requires_blackboard_and_optimizer():
    *_, integrator = integration_stack()
    with pytest.raises(ValueError, match="requires the unified cognitive blackboard"):
        RuntimeCompositionRoot(
            dependencies(whole_system_integrator=integrator)
        ).compose()
    board, *_ = integration_stack()
    with pytest.raises(ValueError, match="requires cognitive performance optimization"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board, whole_system_integrator=integrator
            )
        ).compose()
