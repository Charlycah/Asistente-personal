from datetime import datetime, timezone

import pytest

from core.cognitive_resilience_framework import (
    CognitiveFailureDomain,
    CognitiveResilienceAssessment,
    CognitiveResilienceFramework,
    CognitiveResiliencePosture,
    CognitiveResilienceRuntimeContributor,
    CognitiveResilienceSafeguard,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m210_whole_system_integration import integration_stack

NOW = datetime(2026, 7, 14, 11, 0, tzinfo=timezone.utc)


def resilience_stack(*, blocked=False):
    *stack, integrator = integration_stack(blocked=blocked)
    framework = CognitiveResilienceFramework(integrator)
    return (*stack, integrator, framework)


def test_assessment_identity_is_deterministic():
    *_, framework = resilience_stack()
    first = framework.assess(owner="Carlos", session_id="main", now=NOW)
    second = framework.assess(owner="Carlos", session_id="main", now=NOW)
    assert first.assessment_id == second.assessment_id


def test_ready_system_produces_robust_or_guarded_posture():
    *_, framework = resilience_stack()
    assessment = framework.assess(owner="Carlos", session_id="main", now=NOW)
    assert assessment.posture in {
        CognitiveResiliencePosture.ROBUST,
        CognitiveResiliencePosture.GUARDED,
    }
    assert assessment.safeguards
    assert 0.0 <= assessment.resilience_score <= 1.0


def test_blocked_system_is_contained():
    *_, framework = resilience_stack(blocked=True)
    assessment = framework.assess(owner="Carlos", session_id="main", now=NOW)
    assert assessment.posture in {
        CognitiveResiliencePosture.GUARDED,
        CognitiveResiliencePosture.DEGRADED,
        CognitiveResiliencePosture.CONTAINED,
    }
    assert CognitiveFailureDomain.INTEGRATION in assessment.failure_domains


def test_safeguards_are_priority_ordered():
    *_, framework = resilience_stack(blocked=True)
    assessment = framework.assess(owner="Carlos", session_id="main", now=NOW)
    priorities = tuple(item.priority for item in assessment.safeguards)
    assert priorities == tuple(sorted(priorities, reverse=True))


def test_safeguard_rejects_invalid_priority():
    with pytest.raises(ValueError, match="between 1 and 100"):
        CognitiveResilienceSafeguard(
            "invalid", CognitiveFailureDomain.HEALTH, 0, ("reason",)
        )


def test_assessment_rejects_duplicate_failure_domains():
    safeguard = CognitiveResilienceSafeguard(
        "baseline", CognitiveFailureDomain.INTEGRATION, 10, ("ready",)
    )
    with pytest.raises(ValueError, match="failure domains must be unique"):
        CognitiveResilienceAssessment(
            owner="Carlos",
            session_id="main",
            posture="guarded",
            resilience_score=0.8,
            failure_domains=(
                CognitiveFailureDomain.INTEGRATION,
                CognitiveFailureDomain.INTEGRATION,
            ),
            safeguards=(safeguard,),
            source_reference_ids=("ref",),
            created_at=NOW,
        )


def test_assess_report_does_not_mutate_integration_report():
    *_, integrator, framework = resilience_stack()
    report = integrator.integrate(owner="Carlos", session_id="main", now=NOW)
    framework.assess_report(report)
    assert integrator.last_report == report


def test_runtime_contributor_publishes_resilience_posture():
    board, *_, framework = resilience_stack()
    contribution = CognitiveResilienceRuntimeContributor(framework, board).contribute(
        owner="Carlos",
        session_id="main",
        text="continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "cognitive_resilience_framework"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "cognitive_resilience_posture"
        )
        is not None
    )


def test_official_composition_orders_m211_after_m210():
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
    ) = resilience_stack()
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
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M211",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-2:] == (
        "whole_system_integration",
        "cognitive_resilience_framework",
    )


def test_composition_requires_whole_system_integration():
    board, *_, framework = resilience_stack()
    with pytest.raises(ValueError, match="requires whole-system integration"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                cognitive_resilience_framework=framework,
            )
        ).compose()


def test_framework_has_no_recovery_or_degradation_execution_api():
    *_, framework = resilience_stack()
    assert not hasattr(framework, "recover")
    assert not hasattr(framework, "degrade")
