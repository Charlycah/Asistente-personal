from datetime import datetime, timezone

import pytest

from core.end_to_end_stress_validation import StressScenario
from core.llm_provider import LLMRequest
from core.operational_reliability_certification import (
    OperationalReliabilityCertificate,
    OperationalReliabilityCertificationRuntimeContributor,
    OperationalReliabilityCertifier,
    ReliabilityCertificationStatus,
    ReliabilityCriterion,
)
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m217_end_to_end_stress_validation import stress_stack

NOW = datetime(2026, 7, 14, 22, 0, tzinfo=timezone.utc)


def certification_stack(**kwargs):
    *stack, validator = stress_stack(**kwargs)
    certifier = OperationalReliabilityCertifier(
        validator,
        minimum_cycles=3,
        maximum_failure_rate=0.10,
    )
    return (*stack, validator, certifier)


def nominal_report(validator, *, session_id="main"):
    return validator.validate(
        owner="Carlos",
        session_id=session_id,
        scenarios=(StressScenario("nominal", (1, 2, 3)),),
        now=NOW,
    )


def test_nominal_stress_evidence_is_certified():
    *_, validator, certifier = certification_stack(capacity=4)
    certificate = certifier.certify(
        owner="Carlos",
        session_id="main",
        report=nominal_report(validator),
        now=NOW,
    )
    assert certificate.status is ReliabilityCertificationStatus.CERTIFIED
    assert all(item.passed for item in certificate.criteria)


def test_certifier_uses_last_m217_report_by_default():
    *_, validator, certifier = certification_stack(capacity=4)
    report = nominal_report(validator)
    certificate = certifier.certify(owner="Carlos", session_id="main", now=NOW)
    assert certificate.stress_report_id == report.report_id


def test_certifier_rejects_when_no_m217_evidence_exists():
    *_, certifier = certification_stack()
    with pytest.raises(ValueError, match="requires M217 evidence"):
        certifier.certify(owner="Carlos", session_id="main", now=NOW)


def test_certifier_rejects_identity_mismatch():
    *_, validator, certifier = certification_stack()
    report = nominal_report(validator, session_id="other")
    with pytest.raises(ValueError, match="identity"):
        certifier.certify(owner="Carlos", session_id="main", report=report, now=NOW)


def test_insufficient_cycle_coverage_is_conditional():
    *_, validator = stress_stack(capacity=4)
    certifier = OperationalReliabilityCertifier(validator, minimum_cycles=4)
    report = nominal_report(validator)
    certificate = certifier.certify(
        owner="Carlos", session_id="main", report=report, now=NOW
    )
    assert certificate.status is ReliabilityCertificationStatus.CONDITIONAL
    assert not certificate.criteria[0].passed


def test_failed_stress_evidence_is_rejected():
    *_, validator, certifier = certification_stack(capacity=1)
    report = validator.validate(
        owner="Carlos",
        session_id="main",
        scenarios=(StressScenario("blocked", (10, 10, 10)),),
        now=NOW,
    )
    certificate = certifier.certify(
        owner="Carlos", session_id="main", report=report, now=NOW
    )
    assert certificate.status is ReliabilityCertificationStatus.REJECTED


def test_injected_failure_above_threshold_is_conditional():
    *_, validator = stress_stack()
    certifier = OperationalReliabilityCertifier(
        validator, minimum_cycles=1, maximum_failure_rate=0.0
    )
    report = validator.validate(
        owner="Carlos",
        session_id="main",
        scenarios=(
            StressScenario(
                "failure",
                (1,),
                ("maintain_cross_domain_alignment",),
            ),
        ),
        now=NOW,
    )
    certificate = certifier.certify(
        owner="Carlos", session_id="main", report=report, now=NOW
    )
    assert certificate.status is ReliabilityCertificationStatus.CONDITIONAL


def test_criterion_rejects_blank_fields():
    with pytest.raises(ValueError, match="must not be blank"):
        ReliabilityCriterion(" ", True, "ok", "required")


def test_certificate_rejects_duplicate_criterion_names():
    criterion = ReliabilityCriterion("same", True, "ok", "required")
    with pytest.raises(ValueError, match="unique"):
        OperationalReliabilityCertificate(
            "Carlos",
            "main",
            "certified",
            (criterion, criterion),
            "report",
            ("source",),
            NOW,
        )


def test_certificate_rejects_naive_timestamp():
    criterion = ReliabilityCriterion("one", True, "ok", "required")
    with pytest.raises(ValueError, match="timezone-aware"):
        OperationalReliabilityCertificate(
            "Carlos",
            "main",
            "certified",
            (criterion,),
            "report",
            ("source",),
            datetime(2026, 1, 1),
        )


def test_certificate_identity_is_deterministic():
    *_, validator, certifier = certification_stack(capacity=4)
    report = nominal_report(validator)
    first = certifier.certify(owner="Carlos", session_id="main", report=report, now=NOW)
    second = certifier.certify(
        owner="Carlos", session_id="main", report=report, now=NOW
    )
    assert first.certificate_id == second.certificate_id


def test_runtime_contributor_publishes_certification_status():
    board, *_, validator, certifier = certification_stack(capacity=4)
    nominal_report(validator)
    contribution = OperationalReliabilityCertificationRuntimeContributor(
        certifier, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="certifica",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "operational_reliability_certification"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "operational_reliability_certification"
        )
        is not None
    )


def test_official_composition_orders_m218_after_m217():
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
    ) = certification_stack(capacity=4)
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
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M218",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-2:] == (
        "end_to_end_stress_validation",
        "operational_reliability_certification",
    )


def test_composition_requires_stress_validation():
    board, *_, certifier = certification_stack()
    with pytest.raises(ValueError, match="requires end-to-end stress validation"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                operational_reliability_certifier=certifier,
            )
        ).compose()


def test_certifier_tracks_last_certificate():
    *_, validator, certifier = certification_stack(capacity=4)
    certificate = certifier.certify(
        owner="Carlos",
        session_id="main",
        report=nominal_report(validator),
        now=NOW,
    )
    assert certifier.last_certificate is certificate


def test_certifier_has_no_production_or_infrastructure_authority():
    *_, certifier = certification_stack()
    assert not hasattr(certifier, "deploy")
    assert not hasattr(certifier, "scale_cluster")
    assert not hasattr(certifier, "approve_production")
