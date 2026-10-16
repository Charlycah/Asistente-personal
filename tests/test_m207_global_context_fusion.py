from datetime import datetime, timezone

import pytest

from core.cognitive_event_bus import CognitiveEvent
from core.executive_arbitration import ExecutiveArbitrator
from core.global_context_fusion import (
    FusedContextDomain,
    GlobalContextFusionEngine,
    GlobalContextFusionRuntimeContributor,
    GlobalContextFusionStatus,
    GlobalContextView,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies, stack

NOW = datetime(2026, 7, 14, 5, 0, tzinfo=timezone.utc)


def fusion_stack(*, conflict=False, blocked=False):
    board, state, bus, coordinator, scheduler = stack(
        conflict=conflict, blocked=blocked
    )
    arbitrator = ExecutiveArbitrator(scheduler)
    arbitrator.arbitrate(owner="Carlos", session_id="main", now=NOW)
    fusion = GlobalContextFusionEngine(
        blackboard=board,
        state_engine=state,
        event_bus=bus,
        arbitrator=arbitrator,
    )
    return board, state, bus, coordinator, scheduler, arbitrator, fusion


def test_context_identity_is_deterministic():
    *_, fusion = fusion_stack()
    first = fusion.fuse(owner="Carlos", session_id="main", now=NOW)
    second = fusion.fuse(owner="Carlos", session_id="main", now=NOW)
    assert first.context_id == second.context_id


def test_fusion_collects_domains_and_authorized_actions():
    *_, fusion = fusion_stack()
    result = fusion.fuse(owner="Carlos", session_id="main", now=NOW)
    assert result.status is GlobalContextFusionStatus.COHERENT
    assert result.domains
    assert result.authorized_actions


def test_fusion_preserves_constraints():
    *_, fusion = fusion_stack(blocked=True)
    result = fusion.fuse(owner="Carlos", session_id="main", now=NOW)
    assert result.status is GlobalContextFusionStatus.CONSTRAINED
    assert result.constraints or result.deferred_actions


def test_conflicting_events_remain_visible():
    *_, bus, _, _, _, fusion = fusion_stack()
    bus.publish(
        CognitiveEvent(
            owner="Carlos",
            session_id="main",
            event_type="signal_published",
            source_domain="reasoning",
            topic="answer_mode",
            value="direct",
            created_at=NOW.replace(microsecond=1),
        )
    )
    bus.publish(
        CognitiveEvent(
            owner="Carlos",
            session_id="main",
            event_type="signal_published",
            source_domain="reasoning",
            topic="answer_mode",
            value="exploratory",
            created_at=NOW.replace(microsecond=2),
        )
    )
    result = fusion.fuse(owner="Carlos", session_id="main", now=NOW)
    assert result.status is GlobalContextFusionStatus.CONFLICTED


def test_context_rejects_duplicate_domains():
    domain = FusedContextDomain(domain="system", facts=("x=y",))
    with pytest.raises(ValueError, match="domains must be unique"):
        GlobalContextView(
            owner="Carlos",
            session_id="main",
            status="coherent",
            domains=(domain, domain),
            created_at=NOW,
        )


def test_domain_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="between zero and one"):
        FusedContextDomain(domain="system", confidence=2.0)


def test_runtime_contributor_publishes_context():
    board, *_, fusion = fusion_stack()
    contribution = GlobalContextFusionRuntimeContributor(fusion, board).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "global_context_fusion"
    latest = board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
        "global_context_fusion_status"
    )
    assert latest is not None


def test_fusion_does_not_mutate_arbitration():
    *_, arbitrator, fusion = fusion_stack()
    before = arbitrator.last_decision
    fusion.fuse(owner="Carlos", session_id="main", now=NOW)
    assert arbitrator.last_decision == before


def test_official_composition_orders_m207_after_m206():
    board, state, bus, coordinator, scheduler, arbitrator, fusion = fusion_stack()
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
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M207",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-7:] == (
        "unified_cognitive_blackboard",
        "global_cognitive_state",
        "cognitive_event_bus",
        "cross_domain_coordination",
        "unified_cognitive_scheduler",
        "executive_arbitration",
        "global_context_fusion",
    )


def test_composition_requires_blackboard_and_arbitration():
    *_, fusion = fusion_stack()
    with pytest.raises(ValueError, match="requires the unified cognitive blackboard"):
        RuntimeCompositionRoot(dependencies(global_context_fusion=fusion)).compose()
    board, *_ = fusion_stack()
    with pytest.raises(ValueError, match="requires executive arbitration"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                global_context_fusion=fusion,
            )
        ).compose()
