from datetime import datetime, timezone

import pytest

from core.cognitive_event_bus import CognitiveEvent
from core.cognitive_health_monitoring import (
    CognitiveHealthDimension,
    CognitiveHealthMonitor,
    CognitiveHealthMonitoringRuntimeContributor,
    CognitiveHealthReport,
    CognitiveHealthStatus,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m207_global_context_fusion import fusion_stack

NOW = datetime(2026, 7, 14, 7, 0, tzinfo=timezone.utc)


def monitor_stack(*, conflict=False, blocked=False):
    board, state, bus, coordinator, scheduler, arbitrator, fusion = fusion_stack(
        conflict=conflict, blocked=blocked
    )
    monitor = CognitiveHealthMonitor(fusion)
    return board, state, bus, coordinator, scheduler, arbitrator, fusion, monitor


def test_report_identity_is_deterministic():
    *_, monitor = monitor_stack()
    first = monitor.assess(owner="Carlos", session_id="main", now=NOW)
    second = monitor.assess(owner="Carlos", session_id="main", now=NOW)
    assert first.report_id == second.report_id


def test_coherent_context_is_healthy_or_watch():
    *_, monitor = monitor_stack()
    report = monitor.assess(owner="Carlos", session_id="main", now=NOW)
    assert report.status in {CognitiveHealthStatus.HEALTHY, CognitiveHealthStatus.WATCH}
    assert report.score >= 0.65


def test_blocked_context_produces_alerts():
    *_, monitor = monitor_stack(blocked=True)
    report = monitor.assess(owner="Carlos", session_id="main", now=NOW)
    assert report.alerts
    assert report.status is not CognitiveHealthStatus.HEALTHY


def test_conflicting_context_is_critical():
    *_, bus, _, _, _, fusion, monitor = monitor_stack()
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
    report = monitor.assess(owner="Carlos", session_id="main", now=NOW)
    assert report.status is CognitiveHealthStatus.CRITICAL
    assert "context_conflict_detected" in report.alerts


def test_dimension_rejects_invalid_score():
    with pytest.raises(ValueError, match="between zero and one"):
        CognitiveHealthDimension("coherence", 2.0)


def test_report_rejects_duplicate_dimensions():
    dimension = CognitiveHealthDimension("coherence", 1.0)
    with pytest.raises(ValueError, match="dimensions must be unique"):
        CognitiveHealthReport(
            owner="Carlos",
            session_id="main",
            status="healthy",
            score=1.0,
            dimensions=(dimension, dimension),
            created_at=NOW,
        )


def test_runtime_contributor_publishes_health():
    board, *_, monitor = monitor_stack()
    contribution = CognitiveHealthMonitoringRuntimeContributor(
        monitor, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "cognitive_health_monitoring"
    latest = board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
        "cognitive_health_status"
    )
    assert latest is not None


def test_monitor_does_not_mutate_fused_context():
    *_, fusion, monitor = monitor_stack()
    before = fusion.fuse(owner="Carlos", session_id="main", now=NOW)
    monitor.assess(owner="Carlos", session_id="main", now=NOW)
    assert fusion.last_context == before


def test_official_composition_orders_m208_after_m207():
    board, state, bus, coordinator, scheduler, arbitrator, fusion, monitor = (
        monitor_stack()
    )
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
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M208",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-8:] == (
        "unified_cognitive_blackboard",
        "global_cognitive_state",
        "cognitive_event_bus",
        "cross_domain_coordination",
        "unified_cognitive_scheduler",
        "executive_arbitration",
        "global_context_fusion",
        "cognitive_health_monitoring",
    )


def test_composition_requires_blackboard_and_fusion():
    *_, monitor = monitor_stack()
    with pytest.raises(ValueError, match="requires the unified cognitive blackboard"):
        RuntimeCompositionRoot(dependencies(cognitive_health_monitor=monitor)).compose()
    board, *_ = monitor_stack()
    with pytest.raises(ValueError, match="requires global context fusion"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                cognitive_health_monitor=monitor,
            )
        ).compose()
