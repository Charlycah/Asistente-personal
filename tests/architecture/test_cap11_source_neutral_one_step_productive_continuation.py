from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.governed_cap11_one_step_continuation import (
    GovernedCAP11OneStepContinuationCoordinatorV1,
    GovernedCAP11OneStepContinuationStatus,
)
from app.governed_independence_authorization_boundary import GovernedInitiationDecision
from app.governed_long_horizon_investigation_reassessment_requirement_admission import (
    GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.capability_registry import (
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityRegistryManager,
    CapabilityRisk,
    PermissionScope,
)
from core.governed_read_only_evidence import GovernedReadOnlyEvidenceObservation
from tests.architecture import (
    test_cap11_rr_n_to_discriminant_requirement_n_plus_1_contract_red as rrn_contract,
)

NOW = datetime(2026, 9, 12, 18, 0, tzinfo=timezone.utc)


class _NoopInterceptor:
    pass


class _Reader:
    def __init__(self) -> None:
        self.calls = 0

    def read_evidence(self, request, *, now):
        self.calls += 1
        assert now is NOW
        return GovernedReadOnlyEvidenceObservation(
            evidence_output=request.declared_evidence_output,
            value=42.0,
            source_reference="local-reader:cap11-one-step",
            rationale_codes=("reader:cap11-one-step",),
        )


class _EvidenceRegistry:
    def __init__(self) -> None:
        self.references = []

    def register_reference(self, reference, *, source):
        self.references.append((reference, source))


class _ReasoningGateway:
    def __init__(self) -> None:
        self.registry = _EvidenceRegistry()
        self.orchestrator = SimpleNamespace(
            context_assembler=SimpleNamespace(evidence_registry=self.registry)
        )
        self.calls = 0

    def reason(self, query, *, now):
        self.calls += 1
        assert now is NOW
        return SimpleNamespace(
            decision=SimpleNamespace(decision_id=f"reasoning-decision-{self.calls}")
        )


def _admission():
    return GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1().consume(
        rrn_contract._closure(2),
        rrn_contract._report(2),
    )


def _runtime(
    *,
    risk=CapabilityRisk.LOW,
    requires_confirmation=False,
    initiation_policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
):
    admission = _admission()
    manager = CapabilityRegistryManager()
    runtime = OfficialRuntimeCapabilityRegistry(manager)
    reader = _Reader()
    runtime.register(
        name="local.sensor",
        description="Local deterministic governed evidence reader.",
        interceptor=_NoopInterceptor(),
        evidence_reader=reader,
        evidence_outputs=tuple(
            item.upper()
            for item in admission.source_requirement.missing_evidence_descriptions
        ),
        initiation_policy=initiation_policy,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=CapabilityInteractionScope.INTERNAL,
        permission_scope=PermissionScope.READ,
        risk=risk,
        requires_confirmation=requires_confirmation,
    )
    reasoning = _ReasoningGateway()
    coordinator = GovernedCAP11OneStepContinuationCoordinatorV1(
        capability_registry=manager,
        runtime_registry=runtime,
        reasoning_gateway=reasoning,
    )
    return admission, coordinator, reader, reasoning


def test_may_initiate_runs_exactly_one_productive_step_and_stops_at_reasoning():
    admission, coordinator, reader, reasoning = _runtime()

    result = coordinator.consume(admission, now=NOW)

    assert result.status is GovernedCAP11OneStepContinuationStatus.REASONING_COMPLETED
    assert result.planning is not None
    assert result.authorization is not None
    assert result.authorization.decision is GovernedInitiationDecision.MAY_INITIATE
    assert result.execution is not None
    assert result.reasoning is not None
    assert result.planning_invocation_count == 1
    assert result.authorization_invocation_count == 1
    assert result.execution_invocation_count == 1
    assert result.reasoning_invocation_count == 1
    assert reader.calls == 1
    assert reasoning.calls == 1
    assert not result.derives_next_requirement
    assert not result.recursive_continuation


def test_must_ask_stops_before_execution():
    admission, coordinator, reader, reasoning = _runtime(
        risk=CapabilityRisk.MEDIUM,
    )

    result = coordinator.consume(admission, now=NOW)

    assert result.status is GovernedCAP11OneStepContinuationStatus.AUTHORIZATION_STOPPED
    assert result.authorization is not None
    assert result.authorization.decision is GovernedInitiationDecision.MUST_ASK
    assert result.execution is None
    assert result.reasoning is None
    assert reader.calls == 0
    assert reasoning.calls == 0


def test_required_confirmation_stops_before_execution():
    admission, coordinator, reader, reasoning = _runtime(
        requires_confirmation=True,
    )

    result = coordinator.consume(admission, now=NOW)

    assert result.status is GovernedCAP11OneStepContinuationStatus.AUTHORIZATION_STOPPED
    assert result.authorization is not None
    assert result.authorization.decision is GovernedInitiationDecision.MUST_ASK
    assert result.execution is None
    assert result.reasoning is None
    assert reader.calls == 0
    assert reasoning.calls == 0


def test_never_policy_must_abstain_and_stops_before_execution():
    admission, coordinator, reader, reasoning = _runtime(
        initiation_policy=CapabilityInitiationPolicy.NEVER,
    )

    result = coordinator.consume(admission, now=NOW)

    assert result.status is GovernedCAP11OneStepContinuationStatus.AUTHORIZATION_STOPPED
    assert result.authorization is not None
    assert result.authorization.decision is GovernedInitiationDecision.MUST_ABSTAIN
    assert result.execution is None
    assert result.reasoning is None
    assert reader.calls == 0
    assert reasoning.calls == 0


def test_undeclared_policy_requires_review_and_stops_before_execution():
    admission, coordinator, reader, reasoning = _runtime(
        initiation_policy=CapabilityInitiationPolicy.UNDECLARED,
    )

    result = coordinator.consume(admission, now=NOW)

    assert result.status is GovernedCAP11OneStepContinuationStatus.AUTHORIZATION_STOPPED
    assert result.authorization is not None
    assert result.authorization.decision is GovernedInitiationDecision.REVIEW_REQUIRED
    assert result.execution is None
    assert result.reasoning is None
    assert reader.calls == 0
    assert reasoning.calls == 0


def test_non_admitted_result_fails_closed_without_planning():
    admission_owner = (
        GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    )
    admission = admission_owner.consume(
        rrn_contract._closure(4),
        rrn_contract._report(4),
    )
    manager = CapabilityRegistryManager()
    runtime = OfficialRuntimeCapabilityRegistry(manager)
    reasoning = _ReasoningGateway()
    coordinator = GovernedCAP11OneStepContinuationCoordinatorV1(
        capability_registry=manager,
        runtime_registry=runtime,
        reasoning_gateway=reasoning,
    )

    result = coordinator.consume(admission, now=NOW)

    assert result.status is GovernedCAP11OneStepContinuationStatus.NOT_ELIGIBLE
    assert result.planning is None
    assert result.authorization is None
    assert result.execution is None
    assert result.reasoning is None
    assert result.planning_invocation_count == 0
    assert reasoning.calls == 0
