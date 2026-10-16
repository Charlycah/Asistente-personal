from datetime import datetime, timezone

import pytest

from core.llm_provider import LLMRequest
from core.operational_reliability_certification import OperationalReliabilityCertifier
from core.production_readiness_assessment import (
    ProductionReadinessAssessment,
    ProductionReadinessAssessmentRuntimeContributor,
    ProductionReadinessAssessor,
    ProductionReadinessStatus,
    ReadinessCriterion,
)
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m218_operational_reliability_certification import (
    certification_stack,
    nominal_report,
)

NOW = datetime(2026, 7, 14, 23, 0, tzinfo=timezone.utc)


def readiness_stack(**kwargs):
    *stack, validator, certifier = certification_stack(**kwargs)
    assessor = ProductionReadinessAssessor(certifier)
    return (*stack, validator, certifier, assessor)


def certified_evidence(validator, certifier, *, session_id="main"):
    report = nominal_report(validator, session_id=session_id)
    return certifier.certify(
        owner="Carlos", session_id=session_id, report=report, now=NOW
    )


def test_certified_reliability_evidence_is_ready():
    *_, validator, certifier, assessor = readiness_stack(capacity=4)
    assessment = assessor.assess(
        owner="Carlos",
        session_id="main",
        certificate=certified_evidence(validator, certifier),
        now=NOW,
    )
    assert assessment.status is ProductionReadinessStatus.READY
    assert all(item.passed for item in assessment.criteria)


def test_assessor_uses_last_m218_certificate_by_default():
    *_, validator, certifier, assessor = readiness_stack(capacity=4)
    certificate = certified_evidence(validator, certifier)
    assessment = assessor.assess(owner="Carlos", session_id="main", now=NOW)
    assert assessment.reliability_certificate_id == certificate.certificate_id


def test_assessor_requires_m218_evidence():
    *_, assessor = readiness_stack()
    with pytest.raises(ValueError, match="requires M218 certification evidence"):
        assessor.assess(owner="Carlos", session_id="main", now=NOW)


def test_assessor_rejects_identity_mismatch():
    *_, validator, certifier, assessor = readiness_stack(capacity=4)
    certificate = certified_evidence(validator, certifier, session_id="other")
    with pytest.raises(ValueError, match="identity"):
        assessor.assess(
            owner="Carlos", session_id="main", certificate=certificate, now=NOW
        )


def test_conditional_certificate_is_not_ready_by_default():
    *stack, validator, _, _ = readiness_stack(capacity=4)
    certifier = OperationalReliabilityCertifier(validator, minimum_cycles=4)
    assessor = ProductionReadinessAssessor(certifier)
    report = nominal_report(validator)
    certificate = certifier.certify(
        owner="Carlos", session_id="main", report=report, now=NOW
    )
    assessment = assessor.assess(
        owner="Carlos", session_id="main", certificate=certificate, now=NOW
    )
    assert assessment.status is ProductionReadinessStatus.NOT_READY


def test_relaxed_policy_accepts_conditional_certificate_conditionally():
    *_, validator, _ = certification_stack(capacity=4)
    certifier = OperationalReliabilityCertifier(validator, minimum_cycles=4)
    assessor = ProductionReadinessAssessor(certifier, require_full_certification=False)
    certificate = certifier.certify(
        owner="Carlos",
        session_id="main",
        report=nominal_report(validator),
        now=NOW,
    )
    assessment = assessor.assess(
        owner="Carlos", session_id="main", certificate=certificate, now=NOW
    )
    assert assessment.status is ProductionReadinessStatus.CONDITIONAL


def test_readiness_criterion_rejects_blank_fields():
    with pytest.raises(ValueError, match="must not be blank"):
        ReadinessCriterion(" ", True, "ok", "required")


def test_assessment_rejects_duplicate_criterion_names():
    criterion = ReadinessCriterion("same", True, "ok", "required")
    with pytest.raises(ValueError, match="unique"):
        ProductionReadinessAssessment(
            "Carlos",
            "main",
            "ready",
            (criterion, criterion),
            "certificate",
            ("source",),
            NOW,
        )


def test_assessment_rejects_naive_timestamp():
    criterion = ReadinessCriterion("one", True, "ok", "required")
    with pytest.raises(ValueError, match="timezone-aware"):
        ProductionReadinessAssessment(
            "Carlos",
            "main",
            "ready",
            (criterion,),
            "certificate",
            ("source",),
            datetime(2026, 1, 1),
        )


def test_assessment_identity_is_deterministic():
    *_, validator, certifier, assessor = readiness_stack(capacity=4)
    certificate = certified_evidence(validator, certifier)
    first = assessor.assess(
        owner="Carlos", session_id="main", certificate=certificate, now=NOW
    )
    second = assessor.assess(
        owner="Carlos", session_id="main", certificate=certificate, now=NOW
    )
    assert first.assessment_id == second.assessment_id


def test_runtime_contributor_publishes_readiness_status():
    board, *_, validator, certifier, assessor = readiness_stack(capacity=4)
    certified_evidence(validator, certifier)
    contribution = ProductionReadinessAssessmentRuntimeContributor(
        assessor, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="evalúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "production_readiness_assessment"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "production_readiness_assessment"
        )
        is not None
    )


def test_official_composition_orders_m219_after_m218():
    (
        board,
        state,
        bus,
        domain_coordinator,
        scheduler,
        arbitrator,
        fusion,
        health,
        optimizer,
        integrator,
        framework,
        engine,
        recovery,
        high_load,
        monitor,
        executor,
        validator,
        certifier,
        assessor,
    ) = readiness_stack(capacity=4)
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                global_cognitive_state=state,
                cognitive_event_bus=bus,
                cross_domain_coordinator=domain_coordinator,
                unified_cognitive_scheduler=scheduler,
                executive_arbitrator=arbitrator,
                global_context_fusion=fusion,
                cognitive_health_monitor=health,
                cognitive_performance_optimizer=optimizer,
                whole_system_integrator=integrator,
                cognitive_resilience_framework=framework,
                graceful_degradation_engine=engine,
                fault_recovery_coordinator=recovery,
                high_load_cognitive_scheduler=high_load,
                long_running_stability_monitor=monitor,
                concurrent_cognitive_executor=executor,
                end_to_end_stress_validator=validator,
                operational_reliability_certifier=certifier,
                production_readiness_assessor=assessor,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M219",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-2:] == (
        "operational_reliability_certification",
        "production_readiness_assessment",
    )


def test_composition_requires_reliability_certification():
    board, *_, assessor = readiness_stack()
    with pytest.raises(ValueError, match="requires reliability certification"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                production_readiness_assessor=assessor,
            )
        ).compose()


def test_assessor_tracks_last_assessment():
    *_, validator, certifier, assessor = readiness_stack(capacity=4)
    assessment = assessor.assess(
        owner="Carlos",
        session_id="main",
        certificate=certified_evidence(validator, certifier),
        now=NOW,
    )
    assert assessor.last_assessment is assessment


def test_assessor_has_no_deployment_or_acceptance_authority():
    *_, assessor = readiness_stack()
    assert not hasattr(assessor, "deploy")
    assert not hasattr(assessor, "approve_release")
    assert not hasattr(assessor, "certify_architecture")


def test_assessment_preserves_m218_lineage():
    *_, validator, certifier, assessor = readiness_stack(capacity=4)
    certificate = certified_evidence(validator, certifier)
    assessment = assessor.assess(
        owner="Carlos", session_id="main", certificate=certificate, now=NOW
    )
    assert assessment.source_reference_ids[0] == certificate.certificate_id
    assert set(certificate.source_reference_ids).issubset(
        assessment.source_reference_ids
    )
