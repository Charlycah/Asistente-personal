# ruff: noqa: E501
from datetime import datetime, timezone

import pytest

from core.cognitive_event_bus import CognitiveEvent, CognitiveEventBus
from core.cross_domain_coordination import CrossDomainCoordinator
from core.executive_arbitration import (
    ExecutiveArbitrationDecision,
    ExecutiveArbitrationRuntimeContributor,
    ExecutiveArbitrationStatus,
    ExecutiveArbitrator,
    ExecutiveTaskDecision,
    ExecutiveTaskDisposition,
)
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
)
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider
from tests.test_m178_runtime_composition_root import (
    InferencePort,
    NeedPort,
    ObservationsPort,
    ReadinessPort,
    WorkloadPort,
)

NOW = datetime(2026, 7, 14, 4, 0, tzinfo=timezone.utc)


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


def stack(*, conflict=False, blocked=False):
    board = UnifiedCognitiveBlackboard()
    value = "blocked" if blocked else "ready"
    board.publish(
        CognitiveBlackboardEntry(
            owner="Carlos",
            session_id="main",
            domain="conversation",
            kind="signal",
            key="adaptive_conversation_operational_state",
            value=value,
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
            value="blocked" if blocked else "stable",
            confidence=0.9,
            created_at=NOW,
        )
    )
    if conflict:
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
    coordinator.coordinate(owner="Carlos", session_id="main", now=NOW)
    scheduler = UnifiedCognitiveScheduler(coordinator)
    scheduler.schedule(owner="Carlos", session_id="main", now=NOW)
    return board, state, bus, coordinator, scheduler


def test_authorized_decision_identity_is_deterministic():
    *_, scheduler = stack()
    first = ExecutiveArbitrator(scheduler).arbitrate(
        owner="Carlos", session_id="main", now=NOW
    )
    second = ExecutiveArbitrator(scheduler).arbitrate(
        owner="Carlos", session_id="main", now=NOW
    )
    assert first.decision_id == second.decision_id
    assert first.status is ExecutiveArbitrationStatus.AUTHORIZED


def test_attention_schedule_authorizes_repair_and_defers_other_work():
    *_, scheduler = stack(conflict=True)
    result = ExecutiveArbitrator(scheduler).arbitrate(
        owner="Carlos", session_id="main", now=NOW
    )
    assert result.status in {
        ExecutiveArbitrationStatus.AUTHORIZED,
        ExecutiveArbitrationStatus.PARTIALLY_AUTHORIZED,
    }
    assert result.task_decisions[0].disposition is ExecutiveTaskDisposition.AUTHORIZE


def test_blocked_schedule_rejects_all_tasks():
    scheduler = UnifiedCognitiveScheduler()
    scheduler.last_schedule = UnifiedCognitiveSchedule(
        owner="Carlos",
        session_id="main",
        status="blocked",
        items=(
            CognitiveScheduleItem(
                sequence=1,
                domain="system",
                action="preserve_blocking_boundary",
                priority=100,
            ),
        ),
        constraints=("clarification_required",),
        created_at=NOW,
    )
    result = ExecutiveArbitrator(scheduler).arbitrate(
        owner="Carlos", session_id="main", now=NOW
    )
    assert result.status is ExecutiveArbitrationStatus.REJECTED
    assert all(
        item.disposition is ExecutiveTaskDisposition.REJECT
        for item in result.task_decisions
    )


def test_idle_schedule_produces_idle_decision():
    board = UnifiedCognitiveBlackboard()
    state = GlobalCognitiveStateEngine(board)
    bus = CognitiveEventBus()
    coordinator = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    )
    scheduler = UnifiedCognitiveScheduler(coordinator)
    result = ExecutiveArbitrator(scheduler).arbitrate(
        owner="Other", session_id="secondary", now=NOW
    )
    assert result.status is ExecutiveArbitrationStatus.IDLE
    assert result.task_decisions == ()


def test_unbound_arbitrator_fails_closed():
    with pytest.raises(RuntimeError, match="not bound"):
        ExecutiveArbitrator().arbitrate(owner="Carlos", session_id="main", now=NOW)


def test_decision_rejects_non_contiguous_sequences():
    with pytest.raises(ValueError, match="contiguous"):
        ExecutiveArbitrationDecision(
            owner="Carlos",
            session_id="main",
            status="authorized",
            task_decisions=(
                ExecutiveTaskDecision(
                    sequence=2, domain="system", action="x", disposition="authorize"
                ),
            ),
            created_at=NOW,
        )


def test_runtime_contributor_publishes_executive_decision():
    board, *_, scheduler = stack()
    contribution = ExecutiveArbitrationRuntimeContributor(
        ExecutiveArbitrator(), scheduler, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "executive_arbitration"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW)
        .latest("executive_arbitration_status")
        .value
        == "authorized"
    )


def test_arbitration_is_non_executing_and_does_not_mutate_schedule():
    *_, scheduler = stack()
    before = scheduler.last_schedule
    ExecutiveArbitrator(scheduler).arbitrate(owner="Carlos", session_id="main", now=NOW)
    assert scheduler.last_schedule == before


def test_official_composition_orders_m206_after_m205():
    board, state, bus, coordinator, scheduler = stack()
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                global_cognitive_state=state,
                cognitive_event_bus=bus,
                cross_domain_coordinator=coordinator,
                unified_cognitive_scheduler=scheduler,
                executive_arbitrator=ExecutiveArbitrator(),
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M206",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-6:] == (
        "unified_cognitive_blackboard",
        "global_cognitive_state",
        "cognitive_event_bus",
        "cross_domain_coordination",
        "unified_cognitive_scheduler",
        "executive_arbitration",
    )


def test_composition_requires_m201_and_m205():
    with pytest.raises(ValueError, match="requires the unified cognitive blackboard"):
        RuntimeCompositionRoot(
            dependencies(executive_arbitrator=ExecutiveArbitrator())
        ).compose()
    with pytest.raises(ValueError, match="requires the unified cognitive scheduler"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=UnifiedCognitiveBlackboard(),
                executive_arbitrator=ExecutiveArbitrator(),
            )
        ).compose()
