from datetime import datetime, timezone

import pytest

from core.cognitive_resilience_framework import (
    CognitiveFailureDomain,
    CognitiveResilienceAssessment,
    CognitiveResiliencePosture,
    CognitiveResilienceSafeguard,
)
from core.graceful_degradation_engine import (
    CognitiveCapabilityDisposition,
    CognitiveCapabilityPolicy,
    CognitiveDegradationDecision,
    CognitiveDegradationMode,
    GracefulDegradationEngine,
    GracefulDegradationRuntimeContributor,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m211_cognitive_resilience_framework import resilience_stack

NOW = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def degradation_stack(*, blocked=False):
    *stack, framework = resilience_stack(blocked=blocked)
    engine = GracefulDegradationEngine(framework)
    return (*stack, framework, engine)


def assessment(posture: CognitiveResiliencePosture):
    safeguard = CognitiveResilienceSafeguard(
        "baseline", CognitiveFailureDomain.INTEGRATION, 10, ("traceable",)
    )
    return CognitiveResilienceAssessment(
        owner="Carlos",
        session_id="main",
        posture=posture,
        resilience_score=0.8,
        failure_domains=(),
        safeguards=(safeguard,),
        source_reference_ids=("report",),
        created_at=NOW,
    )


def test_decision_identity_is_deterministic():
    *_, engine = degradation_stack()
    first = engine.activate(owner="Carlos", session_id="main", now=NOW)
    second = engine.activate(owner="Carlos", session_id="main", now=NOW)
    assert first.decision_id == second.decision_id


@pytest.mark.parametrize(
    ("posture", "mode"),
    (
        (CognitiveResiliencePosture.ROBUST, CognitiveDegradationMode.FULL),
        (CognitiveResiliencePosture.GUARDED, CognitiveDegradationMode.CONSERVATIVE),
        (CognitiveResiliencePosture.DEGRADED, CognitiveDegradationMode.ESSENTIAL),
        (CognitiveResiliencePosture.CONTAINED, CognitiveDegradationMode.CONTAINED),
    ),
)
def test_posture_maps_to_expected_mode(posture, mode):
    *_, engine = degradation_stack()
    assert engine.activate_assessment(assessment(posture)).mode is mode


def test_conversation_continuity_is_always_preserved():
    *_, engine = degradation_stack(blocked=True)
    decision = engine.activate(owner="Carlos", session_id="main", now=NOW)
    policy = next(
        item
        for item in decision.policies
        if item.capability == "conversation_continuity"
    )
    assert policy.disposition is CognitiveCapabilityDisposition.PRESERVE


def test_conservative_mode_limits_nonessential_work():
    *_, engine = degradation_stack()
    decision = engine.activate_assessment(
        assessment(CognitiveResiliencePosture.GUARDED)
    )
    policies = {item.capability: item.disposition for item in decision.policies}
    assert policies["background_cognition"] is CognitiveCapabilityDisposition.LIMIT
    assert policies["tool_expansion"] is CognitiveCapabilityDisposition.LIMIT


def test_contained_mode_suspends_everything_except_conversation():
    *_, engine = degradation_stack()
    decision = engine.activate_assessment(
        assessment(CognitiveResiliencePosture.CONTAINED)
    )
    assert all(
        item.disposition is CognitiveCapabilityDisposition.SUSPEND
        for item in decision.policies
        if item.capability != "conversation_continuity"
    )


def test_policy_rejects_blank_capability():
    with pytest.raises(ValueError, match="must not be blank"):
        CognitiveCapabilityPolicy(" ", "preserve", ("reason",))


def test_decision_rejects_duplicate_capabilities():
    policy = CognitiveCapabilityPolicy("reasoning", "preserve", ("reason",))
    with pytest.raises(ValueError, match="capabilities must be unique"):
        CognitiveDegradationDecision(
            owner="Carlos",
            session_id="main",
            mode="full",
            policies=(policy, policy),
            triggers=("posture:robust",),
            source_reference_ids=("assessment",),
            created_at=NOW,
        )


def test_runtime_contributor_publishes_effective_mode():
    board, *_, engine = degradation_stack()
    contribution = GracefulDegradationRuntimeContributor(engine, board).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "graceful_degradation_engine"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "cognitive_degradation_mode"
        )
        is not None
    )


def test_official_composition_orders_m212_after_m211():
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
        framework,
        engine,
    ) = degradation_stack()
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
                cognitive_resilience_framework=framework,
                graceful_degradation_engine=engine,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M212",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-2:] == (
        "cognitive_resilience_framework",
        "graceful_degradation_engine",
    )


def test_composition_requires_cognitive_resilience():
    board, *_, engine = degradation_stack()
    with pytest.raises(ValueError, match="requires cognitive resilience"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                graceful_degradation_engine=engine,
            )
        ).compose()


def test_engine_has_no_fault_recovery_api():
    *_, engine = degradation_stack()
    assert not hasattr(engine, "recover")
    assert not hasattr(engine, "repair")
