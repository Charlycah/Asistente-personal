# ruff: noqa: E501
from datetime import datetime, timezone

import pytest

from core.cognitive_event_bus import (
    CognitiveEvent,
    CognitiveEventBus,
    CognitiveEventType,
)
from core.cross_domain_coordination import (
    CrossDomainCoordinationRuntimeContributor,
    CrossDomainCoordinationStatus,
    CrossDomainCoordinator,
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
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider
from tests.test_m178_runtime_composition_root import (
    InferencePort,
    NeedPort,
    ObservationsPort,
    ReadinessPort,
    WorkloadPort,
)

NOW = datetime(2026, 7, 14, 2, 0, tzinfo=timezone.utc)


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
    return board, state, bus


def test_directive_identity_is_deterministic_and_validated():
    board, state, bus = stack()
    first = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    ).coordinate(owner="Carlos", session_id="main", now=NOW)
    second = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    ).coordinate(owner="Carlos", session_id="main", now=NOW)
    assert first.directive_id == second.directive_id


def test_stable_domains_produce_coordinated_directive():
    board, state, bus = stack()
    result = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    ).coordinate(owner="Carlos", session_id="main", now=NOW)
    assert result.status is CrossDomainCoordinationStatus.COORDINATED
    assert "maintain_cross_domain_alignment" in result.priorities


def test_conflicting_event_values_require_attention():
    board, state, bus = stack()
    bus.publish(
        CognitiveEvent(
            owner="Carlos",
            session_id="main",
            event_type="signal_published",
            source_domain="planning",
            topic="next_action",
            value="execute",
            created_at=NOW,
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
            created_at=NOW.replace(microsecond=1),
        )
    )
    result = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    ).coordinate(owner="Carlos", session_id="main", now=NOW)
    assert result.status is CrossDomainCoordinationStatus.ATTENTION_REQUIRED
    assert result.conflicts == ("next_action",)


def test_constraint_events_are_prioritized():
    board, state, bus = stack()
    bus.publish(
        CognitiveEvent(
            owner="Carlos",
            session_id="main",
            event_type=CognitiveEventType.CONSTRAINT_RAISED,
            source_domain="system",
            topic="scope",
            value="review",
            created_at=NOW.replace(microsecond=2),
        )
    )
    result = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    ).coordinate(owner="Carlos", session_id="main", now=NOW)
    assert result.priorities[0] == "resolve_constraints"


def test_owner_and_session_isolation_is_preserved():
    board, state, bus = stack()
    result = CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    ).coordinate(owner="Other", session_id="secondary", now=NOW)
    assert result.participating_domains == ()
    assert result.status is CrossDomainCoordinationStatus.IDLE


def test_unbound_coordinator_fails_closed():
    with pytest.raises(RuntimeError, match="not bound"):
        CrossDomainCoordinator().coordinate(owner="Carlos", session_id="main", now=NOW)


def test_runtime_contributor_publishes_candidate_to_blackboard():
    board, state, bus = stack()
    contribution = CrossDomainCoordinationRuntimeContributor(
        CrossDomainCoordinator(), board, bus, state
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "cross_domain_coordination"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW)
        .latest("cross_domain_coordination_status")
        .value
        == "coordinated"
    )


def test_coordination_is_consultative_and_does_not_publish_events():
    board, state, bus = stack()
    before = bus.events(owner="Carlos", session_id="main")
    CrossDomainCoordinator(
        blackboard=board, event_bus=bus, state_engine=state
    ).coordinate(owner="Carlos", session_id="main", now=NOW)
    assert bus.events(owner="Carlos", session_id="main") == before


def test_official_composition_orders_m204_after_m203():
    board, state, bus = stack()
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                global_cognitive_state=state,
                cognitive_event_bus=bus,
                cross_domain_coordinator=CrossDomainCoordinator(),
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M204",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-4:] == (
        "unified_cognitive_blackboard",
        "global_cognitive_state",
        "cognitive_event_bus",
        "cross_domain_coordination",
    )


def test_composition_requires_m201_m202_and_m203():
    with pytest.raises(ValueError, match="requires the unified cognitive blackboard"):
        RuntimeCompositionRoot(
            dependencies(cross_domain_coordinator=CrossDomainCoordinator())
        ).compose()
    with pytest.raises(ValueError, match="requires the global cognitive state"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=UnifiedCognitiveBlackboard(),
                cross_domain_coordinator=CrossDomainCoordinator(),
            )
        ).compose()
    with pytest.raises(ValueError, match="requires the cognitive event bus"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=UnifiedCognitiveBlackboard(),
                global_cognitive_state=GlobalCognitiveStateEngine(),
                cross_domain_coordinator=CrossDomainCoordinator(),
            )
        ).compose()
