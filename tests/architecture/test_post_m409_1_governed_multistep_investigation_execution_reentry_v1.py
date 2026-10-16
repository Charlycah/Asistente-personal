from __future__ import annotations

import ast
import inspect
from dataclasses import fields
from datetime import datetime, timezone

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeStatus,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryResult,
    GovernedInvestigationExecutionReentryStatus,
    GovernedMultiStepInvestigationExecutionReentryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuationV1,
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
    def __init__(self, *, fail: bool = False):
        self.calls = 0
        self.fail = fail

    def read_evidence(self, request, *, now):
        self.calls += 1
        if self.fail:
            raise RuntimeError("synthetic read failure")
        return GovernedReadOnlyEvidenceObservation(
            evidence_output="new discriminating observation",
            value=24.5,
            source_reference="local-reader:e2",
            rationale_codes=("reader:local_read_only",),
        )


def _runtime(*, reader=None, scope=CapabilityInteractionScope.INTERNAL):
    manager = CapabilityRegistryManager()
    runtime = OfficialRuntimeCapabilityRegistry(manager)
    reader = reader or _Reader()
    runtime.register(
        name="local.sensor",
        description="Local deterministic evidence reader.",
        interceptor=_NoopInterceptor(),
        evidence_reader=reader,
        evidence_outputs=("new discriminating observation",),
        initiation_policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=scope,
        permission_scope=PermissionScope.READ,
    )
    return manager, runtime, reader


def _requirement():
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-r2",
        hypothesis_ids=("h1", "h2"),
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("new discriminating observation",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _e1():
    return GovernedAcquiredEvidenceEnvelope(
        execution_id="level2-read-only-execution-step-01-abcdef123456",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id="independence-authorization-step-01-abcdef123456",
        requirement_id="discrimination-requirement-r1",
        plan_id="evidence-acquisition-plan-step-01-abcdef123456",
        capability_name="local.sensor",
        evidence_description="first evidence",
        declared_evidence_output="first_evidence",
        observed_value=22.0,
        observation_source_reference="local-reader:e1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        rationale_codes=("execution:test-e1",),
        source_fingerprint="f" * 64,
    )


def _r1_reentry():
    envelope = _e1()
    return GovernedLevel2ReasoningReentryResult(
        reentry_id="level2-reasoning-reentry-step-01-abcdef123456",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        capability_name=envelope.capability_name,
        evidence_id="evidence-1",
        source_reference=envelope.source_reference,
        world_snapshot_id=envelope.world_snapshot_id,
        reasoning_result=None,
        rationale_codes=("reentry:test-r1",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )


def _authorization_reentry(manager):
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, _e1()).state
    state = boundary.record_reentry(state, _r1_reentry()).state
    continuation = GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(state, _requirement())
    planning = GovernedMultiStepInvestigationPlanningReentryV1(
        manager
    ).consume(continuation)
    return GovernedMultiStepInvestigationAuthorizationReentryV1(
        manager
    ).consume(planning)


def test_valid_a2_executes_existing_gateway_once_and_records_new_e2():
    manager, runtime, reader = _runtime()
    authorization = _authorization_reentry(manager)
    before = runtime.gateway.snapshot.executions

    result = GovernedMultiStepInvestigationExecutionReentryV1(
        runtime
    ).consume(authorization, now=datetime.now(timezone.utc))

    assert result.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.execution_id not in (
        authorization.planning_reentry.continuation.resulting_state.execution_ids
    )
    assert reader.calls == 1
    assert runtime.gateway.snapshot.executions == before + 1


def test_e2_preserves_r2_p2_a2_source_and_snapshot_lineage():
    manager, runtime, _ = _runtime()
    authorization = _authorization_reentry(manager)

    result = GovernedMultiStepInvestigationExecutionReentryV1(
        runtime
    ).consume(authorization, now=datetime.now(timezone.utc))

    envelope = result.evidence_envelope
    assert envelope is not None
    assert envelope.authorization_id == authorization.authorization_id
    assert envelope.plan_id == authorization.plan_id
    assert envelope.requirement_id == authorization.requirement_id
    assert envelope.source_reference == authorization.source_reference
    assert envelope.world_snapshot_id == authorization.world_snapshot_id


def test_acquired_e2_consumes_second_slot_and_only_enables_reasoning_reentry():
    manager, runtime, _ = _runtime()

    result = GovernedMultiStepInvestigationExecutionReentryV1(
        runtime
    ).consume(
        _authorization_reentry(manager),
        now=datetime.now(timezone.utc),
    )

    assert result.resulting_episode_state.consumed_acquisitions == 2
    assert result.remaining_acquisitions == 0
    assert (
        result.resulting_episode_state.status
        is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
    )
    assert result.eligible_for_reasoning_reentry
    assert not result.invokes_reasoning


def test_noneligible_a2_never_invokes_execution_gateway():
    manager, runtime, reader = _runtime()
    authorization = _authorization_reentry(manager)
    object.__setattr__(authorization, "eligible_for_existing_execution", False)

    result = GovernedMultiStepInvestigationExecutionReentryV1(
        runtime
    ).consume(authorization, now=datetime.now(timezone.utc))

    assert result.status is GovernedInvestigationExecutionReentryStatus.NOT_ELIGIBLE
    assert result.execution_invocation_count == 0
    assert result.episode_record_invocation_count == 0
    assert reader.calls == 0


def test_device_scope_is_denied_and_enters_review_without_retry():
    manager, runtime, reader = _runtime(
        scope=CapabilityInteractionScope.DEVICE
    )

    result = GovernedMultiStepInvestigationExecutionReentryV1(
        runtime
    ).consume(
        _authorization_reentry(manager),
        now=datetime.now(timezone.utc),
    )

    assert (
        result.status
        is GovernedInvestigationExecutionReentryStatus.REVIEW_REQUIRED
    )
    assert result.execution_status is GovernedLevel2ExecutionStatus.DENIED
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert reader.calls == 0
    assert not result.eligible_for_reasoning_reentry
    assert not result.permits_retry


def test_failed_e2_is_single_attempt_and_closes_episode_without_retry():
    reader = _Reader(fail=True)
    manager, runtime, _ = _runtime(reader=reader)

    result = GovernedMultiStepInvestigationExecutionReentryV1(
        runtime
    ).consume(
        _authorization_reentry(manager),
        now=datetime.now(timezone.utc),
    )

    assert result.status is GovernedInvestigationExecutionReentryStatus.STOPPED
    assert result.execution_status is GovernedLevel2ExecutionStatus.FAILED
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert reader.calls == 1
    assert not result.permits_retry
    assert not result.eligible_for_reasoning_reentry


def test_gateway_exception_fails_closed_without_episode_record():
    class FailingGateway:
        calls = 0

        def execute(self, authorization, planning, *, now):
            self.calls += 1
            raise RuntimeError("synthetic gateway failure")

    manager, runtime, _ = _runtime()
    gateway = FailingGateway()

    result = GovernedMultiStepInvestigationExecutionReentryV1(
        runtime,
        execution_gateway=gateway,
    ).consume(
        _authorization_reentry(manager),
        now=datetime.now(timezone.utc),
    )

    assert gateway.calls == 1
    assert (
        result.status
        is GovernedInvestigationExecutionReentryStatus.REVIEW_REQUIRED
    )
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 0
    assert not result.eligible_for_reasoning_reentry


def test_reused_e1_is_rejected_before_episode_record():
    manager, runtime, _ = _runtime()
    authorization = _authorization_reentry(manager)
    e1 = authorization.planning_reentry.continuation.resulting_state.execution_ids[0]

    class ReusedGateway:
        def execute(self, auth, planning, *, now):
            return GovernedAcquiredEvidenceEnvelope(
                execution_id=e1,
                status=GovernedLevel2ExecutionStatus.ACQUIRED,
                authorization_id=auth.authorization_id,
                requirement_id=auth.requirement_id,
                plan_id=auth.plan_id,
                capability_name=auth.capability_name,
                evidence_description="new discriminating observation",
                declared_evidence_output="new discriminating observation",
                observed_value=24.5,
                observation_source_reference="local-reader:reused",
                source_reference=auth.source_reference,
                world_snapshot_id=auth.world_snapshot_id,
                rationale_codes=("execution:synthetic-reuse",),
                source_fingerprint="d" * 64,
            )

    result = GovernedMultiStepInvestigationExecutionReentryV1(
        runtime,
        execution_gateway=ReusedGateway(),
    ).consume(authorization, now=datetime.now(timezone.utc))

    assert (
        result.status
        is GovernedInvestigationExecutionReentryStatus.REVIEW_REQUIRED
    )
    assert result.episode_record_invocation_count == 0
    assert not result.eligible_for_reasoning_reentry


def test_contract_has_no_reasoning_retry_or_side_effect_authority():
    defaults = {
        field.name: field.default
        for field in fields(GovernedInvestigationExecutionReentryResult)
    }
    for name in (
        "invokes_reasoning",
        "creates_questions",
        "emits_conversation",
        "modifies_memory",
        "modifies_world_model",
        "permits_retry",
        "starts_background_process",
    ):
        assert defaults[name] is False


def test_adapter_contains_no_reasoning_planning_authorization_or_loop_calls():
    source = inspect.getsource(GovernedMultiStepInvestigationExecutionReentryV1)
    tree = ast.parse(source)

    for forbidden in (
        "GovernedMultiStepInvestigationPlanningReentryV1",
        "GovernedMultiStepInvestigationAuthorizationReentryV1",
        "OfficialGovernedReasoningRuntimeGateway",
        "OfficialMemoryGateway",
        "OfficialConversationGateway",
        "GovernedEpistemicCuriosity",
        "subprocess",
        "requests.",
        "socket.",
    ):
        assert forbidden not in source

    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name
            in {
                "reason",
                "plan",
                "authorize",
                "retry",
                "run",
                "run_episode",
                "run_next_step",
            }
        )
        for node in ast.walk(tree)
    )
