from __future__ import annotations

from datetime import datetime, timezone

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumptionV1,
)
from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
)
from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumptionV1,
)
from app.governed_level2_read_only_execution_gateway import (
    GovernedLevel2ExecutionStatus,
    GovernedLevel2ReadOnlyExecutionGatewayV1,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.capability_registry import (
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityRegistryManager,
    PermissionScope,
)
from core.governed_read_only_evidence import GovernedReadOnlyEvidenceObservation
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


class _NoopInterceptor:
    def intercept(self, request, *, now):
        return None


class _Reader:
    def __init__(self, *, value=22.4, fail=False, output="room temperature"):
        self.calls = 0
        self.value = value
        self.fail = fail
        self.output = output

    def read_evidence(self, request, *, now):
        self.calls += 1
        if self.fail:
            raise RuntimeError("read failed")
        return GovernedReadOnlyEvidenceObservation(
            evidence_output=self.output,
            value=self.value,
            source_reference="local-reader:room-temperature",
            rationale_codes=("reader:local_read_only",),
        )


def _requirement():
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-1234567890abcdef",
        hypothesis_ids=("h1", "h2"),
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        known_elements=("fact-shared",),
        missing_evidence_descriptions=("room temperature",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _setup(*, reader=None, scope=CapabilityInteractionScope.INTERNAL):
    manager = CapabilityRegistryManager()
    runtime = OfficialRuntimeCapabilityRegistry(manager)
    reader = reader or _Reader()
    runtime.register(
        name="local.temperature.read",
        description="Local deterministic temperature reader",
        interceptor=_NoopInterceptor(),
        evidence_reader=reader,
        evidence_outputs=("room temperature",),
        initiation_policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=scope,
        permission_scope=PermissionScope.READ,
    )
    planning = GovernedEvidenceAcquisitionProductiveConsumptionV1(manager).consume(
        _requirement()
    )
    boundary = GovernedIndependenceAuthorizationBoundaryV1(manager).evaluate(planning)
    authorization = GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(
        boundary
    )
    return runtime, planning, authorization, reader


def test_level2_exec_uses_official_gateway_once_and_returns_evidence_envelope():
    runtime, planning, authorization, reader = _setup()
    before = runtime.gateway.snapshot.executions
    result = GovernedLevel2ReadOnlyExecutionGatewayV1(runtime).execute(
        authorization,
        planning,
        now=datetime.now(timezone.utc),
    )
    assert result.status is GovernedLevel2ExecutionStatus.ACQUIRED
    assert result.observed_value == 22.4
    assert result.declared_evidence_output == "room temperature"
    assert result.requirement_id == planning.requirement_id
    assert result.plan_id == planning.planning_report.plan_id
    assert result.authorization_id == authorization.authorization_id
    assert result.canonical_execution_gateway == "OfficialCapabilityGateway"
    assert reader.calls == 1
    assert runtime.gateway.snapshot.executions == before + 1
    assert not result.establishes_truth
    assert not result.permits_retry
    assert not result.triggers_reasoning_reentry


def test_unavailable_reader_fails_closed_without_gateway_execution():
    runtime, planning, authorization, _ = _setup()
    registration = runtime.registration_for("local.temperature.read")
    object.__setattr__(registration, "evidence_reader", None)
    before = runtime.gateway.snapshot.executions
    result = GovernedLevel2ReadOnlyExecutionGatewayV1(runtime).execute(
        authorization,
        planning,
        now=datetime.now(timezone.utc),
    )
    assert result.status is GovernedLevel2ExecutionStatus.UNAVAILABLE
    assert runtime.gateway.snapshot.executions == before


def test_failed_read_is_single_attempt_with_no_retry():
    reader = _Reader(fail=True)
    runtime, planning, authorization, _ = _setup(reader=reader)
    result = GovernedLevel2ReadOnlyExecutionGatewayV1(runtime).execute(
        authorization,
        planning,
        now=datetime.now(timezone.utc),
    )
    assert result.status is GovernedLevel2ExecutionStatus.FAILED
    assert reader.calls == 1
    assert not result.permits_retry


def test_device_scope_is_not_executable_in_v1_even_if_authorized_level2():
    runtime, planning, authorization, reader = _setup(
        scope=CapabilityInteractionScope.DEVICE
    )
    result = GovernedLevel2ReadOnlyExecutionGatewayV1(runtime).execute(
        authorization,
        planning,
        now=datetime.now(timezone.utc),
    )
    assert result.status is GovernedLevel2ExecutionStatus.DENIED
    assert reader.calls == 0


def test_observation_output_mismatch_is_review_required_not_evidence():
    reader = _Reader(output="different output")
    runtime, planning, authorization, _ = _setup(reader=reader)
    result = GovernedLevel2ReadOnlyExecutionGatewayV1(runtime).execute(
        authorization,
        planning,
        now=datetime.now(timezone.utc),
    )
    assert result.status is GovernedLevel2ExecutionStatus.REVIEW_REQUIRED
    assert result.observed_value is None
    assert reader.calls == 1
