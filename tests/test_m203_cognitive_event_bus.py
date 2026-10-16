from datetime import datetime, timezone

import pytest

from core.adaptive_conversation_intelligence import AdaptiveConversationIntelligence
from core.adaptive_conversation_operational_consolidation import (
    AdaptiveConversationOperationalConsolidation,
)
from core.cognitive_event_bus import (
    CognitiveEvent,
    CognitiveEventBus,
    CognitiveEventBusRuntimeContributor,
    CognitiveEventDeliveryStatus,
    CognitiveEventSubscription,
    CognitiveEventType,
)
from core.conversational_commitment_intelligence import (
    ConversationalCommitmentIntelligence,
)
from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
)
from core.conversational_repair_intelligence import ConversationalRepairIntelligence
from core.global_cognitive_state import GlobalCognitiveStateEngine
from core.llm_provider import LLMRequest
from core.runtime_composition_root import (
    RuntimeCompositionDependencies,
    RuntimeCompositionRoot,
)
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
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

NOW = datetime(2026, 7, 14, 1, 0, tzinfo=timezone.utc)


def event(**overrides):
    values = {
        "owner": "Carlos",
        "session_id": "main",
        "event_type": CognitiveEventType.STATE_CHANGED,
        "source_domain": CognitiveBlackboardDomain.SYSTEM,
        "topic": "global_cognitive_state",
        "value": "stable",
        "confidence": 0.9,
        "created_at": NOW,
    }
    values.update(overrides)
    return CognitiveEvent(**values)


def dependencies(**overrides):
    values = {
        "readiness_port": ReadinessPort(),
        "observations_port": ObservationsPort(),
        "workload_port": WorkloadPort(),
        "knowledge_need_port": NeedPort(),
        "inference_request_port": InferencePort(),
        "local_providers": (RecordingProvider(),),
    }
    values.update(overrides)
    return RuntimeCompositionDependencies(**values)


def conversation_stack():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    grounding = ConversationalGroundingIntelligence(repair)
    commitment = ConversationalCommitmentIntelligence(grounding)
    consolidation = AdaptiveConversationOperationalConsolidation(
        adaptive, repair, grounding, commitment
    )
    return adaptive, repair, grounding, commitment, consolidation


def seed_ready(blackboard: UnifiedCognitiveBlackboard):
    blackboard.publish(
        CognitiveBlackboardEntry(
            owner="Carlos",
            session_id="main",
            domain=CognitiveBlackboardDomain.CONVERSATION,
            kind=CognitiveBlackboardEntryKind.SIGNAL,
            key="adaptive_conversation_operational_state",
            value="ready",
            confidence=0.9,
            created_at=NOW,
        )
    )


def test_event_identity_is_deterministic_and_validated():
    first = event()
    second = event()
    assert first.event_id == second.event_id
    with pytest.raises(ValueError, match="id is inconsistent"):
        event(event_id="invalid")


def test_publish_delivers_to_matching_subscription():
    bus = CognitiveEventBus()
    received = []
    subscription = CognitiveEventSubscription(
        owner="Carlos",
        session_id="main",
        event_types=(CognitiveEventType.STATE_CHANGED,),
        topics=("global_cognitive_state",),
    )
    bus.subscribe(subscription, received.append)
    deliveries = bus.publish(event())
    assert received == [event()]
    assert deliveries[0].status is CognitiveEventDeliveryStatus.DELIVERED


def test_owner_and_session_isolation_prevents_cross_delivery():
    bus = CognitiveEventBus()
    received = []
    bus.subscribe(
        CognitiveEventSubscription(owner="Other", session_id="main"),
        received.append,
    )
    bus.publish(event())
    assert received == []
    assert bus.events(owner="Other", session_id="main") == ()


def test_duplicate_publish_is_idempotent():
    bus = CognitiveEventBus()
    received = []
    bus.subscribe(
        CognitiveEventSubscription(owner="Carlos", session_id="main"),
        received.append,
    )
    item = event()
    bus.publish(item)
    assert bus.publish(item) == ()
    assert received == [item]
    assert bus.events(owner="Carlos", session_id="main") == (item,)


def test_consumer_failure_is_contained():
    bus = CognitiveEventBus()

    def broken(_event):
        raise RuntimeError("boom")

    subscription = CognitiveEventSubscription(owner="Carlos", session_id="main")
    bus.subscribe(subscription, broken)
    deliveries = bus.publish(event())
    assert deliveries[0].status is CognitiveEventDeliveryStatus.FAILED
    assert deliveries[0].error == "RuntimeError"
    assert bus.events(owner="Carlos", session_id="main")


def test_retention_and_filters_are_bounded():
    bus = CognitiveEventBus(maximum_events_per_session=2)
    bus.publish(event(topic="one", value="1"))
    bus.publish(event(topic="two", value="2"))
    bus.publish(event(topic="three", value="3"))
    stored_topics = tuple(
        item.topic for item in bus.events(owner="Carlos", session_id="main")
    )
    assert stored_topics == ("two", "three")
    assert tuple(
        item.topic
        for item in bus.events(owner="Carlos", session_id="main", topics=("three",))
    ) == ("three",)


def test_runtime_contributor_eventizes_global_state_and_publishes_receipt():
    blackboard = UnifiedCognitiveBlackboard()
    seed_ready(blackboard)
    engine = GlobalCognitiveStateEngine(blackboard)
    engine.assess(owner="Carlos", session_id="main", now=NOW)
    bus = CognitiveEventBus()
    contribution = CognitiveEventBusRuntimeContributor(
        bus, engine, blackboard
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert bus.last_event.event_type is CognitiveEventType.STATE_CHANGED
    assert contribution.reference_ids
    assert (
        blackboard.snapshot(owner="Carlos", session_id="main", now=NOW)
        .latest("cognitive_event_bus_last_event")
        .value
        == "state_changed"
    )


def test_constraints_are_emitted_as_constraint_events():
    blackboard = UnifiedCognitiveBlackboard()
    seed_ready(blackboard)
    blackboard.publish(
        CognitiveBlackboardEntry(
            owner="Carlos",
            session_id="main",
            domain=CognitiveBlackboardDomain.SYSTEM,
            kind=CognitiveBlackboardEntryKind.CONSTRAINT,
            key="scope",
            value="human_review_required",
            created_at=NOW,
        )
    )
    engine = GlobalCognitiveStateEngine(blackboard)
    bus = CognitiveEventBus()
    CognitiveEventBusRuntimeContributor(bus, engine, blackboard).contribute(
        owner="Carlos",
        session_id="main",
        text="Continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert bus.last_event.event_type is CognitiveEventType.CONSTRAINT_RAISED


def test_official_composition_orders_m203_after_m202():
    adaptive, repair, grounding, commitment, consolidation = conversation_stack()
    blackboard = UnifiedCognitiveBlackboard()
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                adaptive_conversation_intelligence=adaptive,
                conversational_repair_intelligence=repair,
                conversational_grounding_intelligence=grounding,
                conversational_commitment_intelligence=commitment,
                adaptive_conversation_operational_consolidation=consolidation,
                unified_cognitive_blackboard=blackboard,
                global_cognitive_state=GlobalCognitiveStateEngine(),
                cognitive_event_bus=CognitiveEventBus(),
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M203",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-3:] == (
        "unified_cognitive_blackboard",
        "global_cognitive_state",
        "cognitive_event_bus",
    )


def test_composition_requires_m201_and_m202_for_event_bus():
    with pytest.raises(ValueError, match="requires the unified cognitive blackboard"):
        RuntimeCompositionRoot(
            dependencies(cognitive_event_bus=CognitiveEventBus())
        ).compose()
    with pytest.raises(ValueError, match="requires the global cognitive state"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=UnifiedCognitiveBlackboard(),
                cognitive_event_bus=CognitiveEventBus(),
            )
        ).compose()
