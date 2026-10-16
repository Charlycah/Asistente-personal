from datetime import datetime, timezone

import pytest

from core.final_architecture_certification import (
    AcceptanceCriterion,
    FinalAcceptanceStatus,
    FinalArchitectureCertificationRuntimeContributor,
    ROBYArchitectureCertificate,
    ROBYArchitectureCertifier,
)
from core.llm_provider import LLMRequest
from core.production_readiness_assessment import (
    ProductionReadinessAssessor,
    ProductionReadinessStatus,
)
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m219_production_readiness_assessment import (
    certified_evidence,
    readiness_stack,
)

NOW = datetime(2026, 7, 15, 1, 0, tzinfo=timezone.utc)


def acceptance_stack(**kwargs):
    *stack, validator, certifier, assessor = readiness_stack(**kwargs)
    architecture = ROBYArchitectureCertifier(assessor)
    return (*stack, validator, certifier, assessor, architecture)


def ready_evidence(validator, certifier, assessor, *, session_id="main"):
    certificate = certified_evidence(validator, certifier, session_id=session_id)
    return assessor.assess(
        owner="Carlos", session_id=session_id, certificate=certificate, now=NOW
    )


def test_ready_assessment_is_finally_accepted():
    *_, validator, certifier, assessor, architecture = acceptance_stack(capacity=4)
    result = architecture.certify(
        owner="Carlos",
        session_id="main",
        assessment=ready_evidence(validator, certifier, assessor),
        now=NOW,
    )
    assert result.status is FinalAcceptanceStatus.ACCEPTED
    assert result.version == "ROBY v1"
    assert all(item.passed for item in result.criteria)


def test_certifier_uses_last_m219_assessment_by_default():
    *_, validator, certifier, assessor, architecture = acceptance_stack(capacity=4)
    assessment = ready_evidence(validator, certifier, assessor)
    result = architecture.certify(owner="Carlos", session_id="main", now=NOW)
    assert result.readiness_assessment_id == assessment.assessment_id


def test_certifier_requires_m219_evidence():
    *_, architecture = acceptance_stack()
    with pytest.raises(ValueError, match="requires M219 evidence"):
        architecture.certify(owner="Carlos", session_id="main", now=NOW)


def test_certifier_rejects_identity_mismatch():
    *_, validator, certifier, assessor, architecture = acceptance_stack(capacity=4)
    assessment = ready_evidence(validator, certifier, assessor, session_id="other")
    with pytest.raises(ValueError, match="identity"):
        architecture.certify(
            owner="Carlos", session_id="main", assessment=assessment, now=NOW
        )


def test_conditional_readiness_is_conditional_under_strict_policy():
    *stack, validator, certifier, _assessor, _architecture = acceptance_stack(
        capacity=4
    )
    assessor = ProductionReadinessAssessor(certifier, require_full_certification=False)
    architecture = ROBYArchitectureCertifier(assessor)
    certificate = certified_evidence(validator, certifier)
    assessment = assessor.assess(
        owner="Carlos", session_id="main", certificate=certificate, now=NOW
    )
    object.__setattr__(assessment, "status", ProductionReadinessStatus.CONDITIONAL)
    result = architecture.certify(
        owner="Carlos", session_id="main", assessment=assessment, now=NOW
    )
    assert result.status is FinalAcceptanceStatus.CONDITIONAL


def test_relaxed_policy_allows_conditional_acceptance():
    *_, validator, certifier, assessor, _ = acceptance_stack(capacity=4)
    assessment = ready_evidence(validator, certifier, assessor)
    object.__setattr__(assessment, "status", ProductionReadinessStatus.CONDITIONAL)
    architecture = ROBYArchitectureCertifier(assessor, require_ready=False)
    result = architecture.certify(
        owner="Carlos", session_id="main", assessment=assessment, now=NOW
    )
    assert result.status is FinalAcceptanceStatus.CONDITIONAL


def test_acceptance_criterion_rejects_blank_fields():
    with pytest.raises(ValueError, match="must not be blank"):
        AcceptanceCriterion(" ", True, "ok", "required")


def test_certificate_rejects_duplicate_criterion_names():
    criterion = AcceptanceCriterion("same", True, "ok", "required")
    with pytest.raises(ValueError, match="unique"):
        ROBYArchitectureCertificate(
            "Carlos",
            "main",
            "accepted",
            "ROBY v1",
            (criterion, criterion),
            "assessment",
            ("source",),
            NOW,
        )


def test_certificate_rejects_naive_timestamp():
    criterion = AcceptanceCriterion("one", True, "ok", "required")
    with pytest.raises(ValueError, match="timezone-aware"):
        ROBYArchitectureCertificate(
            "Carlos",
            "main",
            "accepted",
            "ROBY v1",
            (criterion,),
            "assessment",
            ("source",),
            datetime(2026, 1, 1),
        )


def test_certificate_identity_is_deterministic():
    *_, validator, certifier, assessor, architecture = acceptance_stack(capacity=4)
    assessment = ready_evidence(validator, certifier, assessor)
    first = architecture.certify(
        owner="Carlos", session_id="main", assessment=assessment, now=NOW
    )
    second = architecture.certify(
        owner="Carlos", session_id="main", assessment=assessment, now=NOW
    )
    assert first.certificate_id == second.certificate_id


def test_runtime_contributor_publishes_final_status():
    board, *_, validator, certifier, assessor, architecture = acceptance_stack(
        capacity=4
    )
    ready_evidence(validator, certifier, assessor)
    contribution = FinalArchitectureCertificationRuntimeContributor(
        architecture, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="certifica",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "final_architecture_certification"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "final_architecture_certification"
        )
        is not None
    )


def test_official_composition_orders_m220_after_m219():
    (
        board,
        state,
        bus,
        coordinator,
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
        architecture,
    ) = acceptance_stack(capacity=4)
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
                roby_architecture_certifier=architecture,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M220",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-2:] == (
        "production_readiness_assessment",
        "final_architecture_certification",
    )


def test_composition_requires_production_readiness():
    board, *_, architecture = acceptance_stack()
    with pytest.raises(ValueError, match="requires production readiness"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                roby_architecture_certifier=architecture,
            )
        ).compose()


def test_certifier_tracks_last_certificate():
    *_, validator, certifier, assessor, architecture = acceptance_stack(capacity=4)
    result = architecture.certify(
        owner="Carlos",
        session_id="main",
        assessment=ready_evidence(validator, certifier, assessor),
        now=NOW,
    )
    assert architecture.last_certificate is result


def test_certifier_has_no_deployment_or_runtime_mutation_authority():
    *_, architecture = acceptance_stack()
    assert not hasattr(architecture, "deploy")
    assert not hasattr(architecture, "restart_provider")
    assert not hasattr(architecture, "mutate_runtime")


def test_certificate_preserves_m219_lineage():
    *_, validator, certifier, assessor, architecture = acceptance_stack(capacity=4)
    assessment = ready_evidence(validator, certifier, assessor)
    result = architecture.certify(
        owner="Carlos", session_id="main", assessment=assessment, now=NOW
    )
    assert result.source_reference_ids[0] == assessment.assessment_id
    assert set(assessment.source_reference_ids).issubset(result.source_reference_ids)
