# ruff: noqa: E501
from datetime import datetime, timezone

import pytest

from core.cognitive_event_bus import CognitiveEvent, CognitiveEventBus
from core.cross_domain_coordination import CrossDomainCoordinator
from core.global_cognitive_state import GlobalCognitiveStateEngine
from core.llm_provider import LLMRequest
from core.runtime_composition_root import (
    RuntimeCompositionDependencies,
    RuntimeCompositionRoot,
)
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardEntry,
    UnifiedCognitiveBlackboard,
)
from core.unified_cognitive_scheduler import (
    CognitiveScheduleItem,
    UnifiedCognitiveSchedule,
    UnifiedCognitiveScheduler,
    UnifiedCognitiveSchedulerRuntimeContributor,
    UnifiedCognitiveScheduleStatus,
)
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider
from tests.test_m178_runtime_composition_root import (
    InferencePort,
    NeedPort,
    ObservationsPort,
    ReadinessPort,
    WorkloadPort,
)

NOW = datetime(2026, 7, 14, 3, 0, tzinfo=timezone.utc)


def dependencies(**overrides):
    values = dict(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(),
        inference_request_port=InferencePort(),
        local_providers=(RecordingProvider(),),
    )
    values.update(overrides)
    return RuntimeCompositionDependencies(**values)


def stack():
    board = UnifiedCognitiveBlackboard()
    board.publish(
        CognitiveBlackboardEntry(
            owner="Carlos",
            session_id="main",
            domain="conversation",
            kind="signal",
            key="adaptive_conversation_operational_state",
            value="ready",
            confidence=0.9,
            created_at=NOW,
        )
    )
    state = GlobalCognitiveStateEngine(board)
    state.assess(owner="Carlos", session_id="main", now=NOW)
    bus = CognitiveEventBus()
    bus.publish(
        CognitiveEvent(
            owner="Carlos",
            session_id="main",
            event_type="state_changed",
            source_domain="system",
            topic="global_cognitive_state",
            value="stable",
            confidence=0.9,
            created_at=NOW,
        )
    )
    coordinator = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    )
    coordinator.coordinate(owner="Carlos", session_id="main", now=NOW)
    return board, state, bus, coordinator


def test_schedule_identity_is_deterministic_and_validated():
    _, _, _, coordinator = stack()
    first = UnifiedCognitiveScheduler(coordinator).schedule(
        owner="Carlos", session_id="main", now=NOW
    )
    second = UnifiedCognitiveScheduler(coordinator).schedule(
        owner="Carlos", session_id="main", now=NOW
    )
    assert first.schedule_id == second.schedule_id


def test_coordinated_directive_produces_ordered_schedule():
    _, _, _, coordinator = stack()
    result = UnifiedCognitiveScheduler(coordinator).schedule(
        owner="Carlos", session_id="main", now=NOW
    )
    assert result.status is UnifiedCognitiveScheduleStatus.SCHEDULED
    assert result.items[0].sequence == 1
    assert result.items[0].action == "maintain_cross_domain_alignment"


def test_conflicts_produce_attention_required_schedule():
    board, state, bus, _ = stack()
    bus.publish(
        CognitiveEvent(
            owner="Carlos",
            session_id="main",
            event_type="signal_published",
            source_domain="planning",
            topic="next_action",
            value="execute",
            created_at=NOW.replace(microsecond=1),
        )
    )
    bus.publish(
        CognitiveEvent(
            owner="Carlos",
            session_id="main",
            event_type="signal_published",
            source_domain="reasoning",
            topic="next_action",
            value="wait",
            created_at=NOW.replace(microsecond=2),
        )
    )
    coordinator = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    )
    result = UnifiedCognitiveScheduler(coordinator).schedule(
        owner="Carlos", session_id="main", now=NOW
    )
    assert result.status is UnifiedCognitiveScheduleStatus.ATTENTION_REQUIRED
    assert "next_action" in result.constraints
    assert result.items[0].action == "reconcile_conflicting_signals"


def test_idle_coordination_produces_empty_schedule():
    board = UnifiedCognitiveBlackboard()
    state = GlobalCognitiveStateEngine(board)
    bus = CognitiveEventBus()
    coordinator = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    )
    result = UnifiedCognitiveScheduler(coordinator).schedule(
        owner="Other", session_id="secondary", now=NOW
    )
    assert result.status is UnifiedCognitiveScheduleStatus.IDLE
    assert result.items == ()


def test_unbound_scheduler_fails_closed():
    with pytest.raises(RuntimeError, match="not bound"):
        UnifiedCognitiveScheduler().schedule(owner="Carlos", session_id="main", now=NOW)


def test_schedule_rejects_non_contiguous_sequences():
    with pytest.raises(ValueError, match="contiguous"):
        UnifiedCognitiveSchedule(
            owner="Carlos",
            session_id="main",
            status="scheduled",
            items=(
                CognitiveScheduleItem(
                    sequence=2, domain="system", action="x", priority=50
                ),
            ),
            created_at=NOW,
        )


def test_runtime_contributor_publishes_schedule_candidate():
    board, _, _, coordinator = stack()
    contribution = UnifiedCognitiveSchedulerRuntimeContributor(
        UnifiedCognitiveScheduler(), coordinator, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "unified_cognitive_scheduler"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW)
        .latest("unified_cognitive_schedule_status")
        .value
        == "scheduled"
    )


def test_scheduler_is_consultative_and_does_not_mutate_directive():
    _, _, _, coordinator = stack()
    before = coordinator.last_directive
    UnifiedCognitiveScheduler(coordinator).schedule(
        owner="Carlos", session_id="main", now=NOW
    )
    assert coordinator.last_directive == before


def test_official_composition_orders_m205_after_m204():
    board, state, bus, coordinator = stack()
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                global_cognitive_state=state,
                cognitive_event_bus=bus,
                cross_domain_coordinator=coordinator,
                unified_cognitive_scheduler=UnifiedCognitiveScheduler(),
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M205",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-5:] == (
        "unified_cognitive_blackboard",
        "global_cognitive_state",
        "cognitive_event_bus",
        "cross_domain_coordination",
        "unified_cognitive_scheduler",
    )


def test_composition_requires_m201_and_m204():
    with pytest.raises(ValueError, match="requires the unified cognitive blackboard"):
        RuntimeCompositionRoot(
            dependencies(unified_cognitive_scheduler=UnifiedCognitiveScheduler())
        ).compose()
    with pytest.raises(ValueError, match="requires cross-domain coordination"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=UnifiedCognitiveBlackboard(),
                unified_cognitive_scheduler=UnifiedCognitiveScheduler(),
            )
        ).compose()
