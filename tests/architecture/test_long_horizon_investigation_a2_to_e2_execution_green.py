from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_a2_authorization_reentry import (
    GovernedInvestigationA2AuthorizationAdmissionResult,
    GovernedInvestigationA2AuthorizationAdmissionStatus,
)
from app.governed_long_horizon_investigation_e2_execution_reentry import (
    GovernedInvestigationE2ExecutionAdmissionStatus,
    GovernedLongHorizonInvestigationE2ExecutionReentryV1,
)
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeStatus,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
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

SOURCE = "scenario-123"
SNAPSHOT = "world-1"
NOW = datetime(2026, 8, 29, 21, 0, tzinfo=timezone.utc)


class _NoopInterceptor:
    def intercept(self, request, *, now):
        return None


class _Reader:
    def __init__(self, *, fail: bool = False) -> None:
        self.calls = 0
        self.fail = fail

    def read_evidence(self, request, *, now):
        self.calls += 1
        if self.fail:
            raise RuntimeError("synthetic E2 read failure")
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


def _requirement() -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-r2",
        hypothesis_ids=("h1", "h2"),
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("new discriminating observation",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _e1() -> GovernedAcquiredEvidenceEnvelope:
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
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        rationale_codes=("execution:test-e1",),
        source_fingerprint="f" * 64,
    )


def _r1_reentry() -> GovernedLevel2ReasoningReentryResult:
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
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        reasoning_result=None,
        rationale_codes=("reentry:test-r1",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )


def _a2(manager: CapabilityRegistryManager):
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, _e1()).state
    state = boundary.record_reentry(state, _r1_reentry()).state
    continuation = GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(state, _requirement())
    planning = GovernedMultiStepInvestigationPlanningReentryV1(manager).consume(
        continuation
    )
    authorization = GovernedMultiStepInvestigationAuthorizationReentryV1(
        manager
    ).consume(planning)
    return GovernedInvestigationA2AuthorizationAdmissionResult(
        thread_id="investigation-thread-1",
        checkpoint_id="investigation-checkpoint-1",
        episode_id=authorization.episode_id,
        originating_reasoning_id="reasoning-decision-1",
        requirement_id=authorization.requirement_id,
        plan_id=authorization.plan_id,
        source_reference=authorization.source_reference,
        world_snapshot_id=authorization.world_snapshot_id,
        status=GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED,
        authorization_reentry=authorization,
        authorization_product=authorization.authorization_product,
        authorization_id=authorization.authorization_id,
        decision=authorization.decision,
        rationale_codes=("test:canonical-a2",),
        authorization_invocation_count=1,
        eligible_for_existing_execution=authorization.eligible_for_existing_execution,
        invokes_authorization=True,
    )


class _ExecutionSpy:
    def __init__(self, delegate) -> None:
        self._delegate = delegate
        self.calls = 0
        self.received = None
        self.received_now = None

    def consume(self, authorization_reentry, *, now):
        self.calls += 1
        self.received = authorization_reentry
        self.received_now = now
        return self._delegate.consume(authorization_reentry, now=now)


def test_exact_a2_and_now_are_forwarded_once_and_e2_is_preserved():
    manager, runtime, reader = _runtime()
    a2 = _a2(manager)
    from app.governed_multistep_investigation_execution_reentry import (
        GovernedMultiStepInvestigationExecutionReentryV1,
    )

    spy = _ExecutionSpy(GovernedMultiStepInvestigationExecutionReentryV1(runtime))
    result = GovernedLongHorizonInvestigationE2ExecutionReentryV1(
        execution_reentry=spy
    ).consume(a2, now=NOW)

    assert spy.calls == 1
    assert spy.received is a2.authorization_reentry
    assert spy.received_now is NOW
    assert reader.calls == 1
    assert result.status is GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED
    assert result.execution_reentry is not None
    assert result.evidence_envelope is result.execution_reentry.evidence_envelope
    assert result.resulting_episode_state is (
        result.execution_reentry.resulting_episode_state
    )
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1


def test_acquired_e2_exhausts_budget_and_only_enables_second_reasoning_reentry():
    manager, runtime, _ = _runtime()
    result = GovernedLongHorizonInvestigationE2ExecutionReentryV1(runtime).consume(
        _a2(manager), now=NOW
    )

    assert result.status is GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED
    assert result.resulting_episode_state is not None
    assert result.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
    )
    assert result.resulting_episode_state.remaining_acquisitions == 0
    assert result.eligible_for_existing_reasoning_reentry
    assert not result.invokes_reasoning
    assert not result.invokes_planning
    assert not result.invokes_authorization


def test_noneligible_a2_stops_before_existing_e2_owner():
    manager, runtime, reader = _runtime()
    canonical = _a2(manager)
    a2 = GovernedInvestigationA2AuthorizationAdmissionResult(
        thread_id=canonical.thread_id,
        checkpoint_id=canonical.checkpoint_id,
        episode_id=canonical.episode_id,
        originating_reasoning_id=canonical.originating_reasoning_id,
        requirement_id=canonical.requirement_id,
        plan_id=canonical.plan_id,
        source_reference=canonical.source_reference,
        world_snapshot_id=canonical.world_snapshot_id,
        status=GovernedInvestigationA2AuthorizationAdmissionStatus.NOT_ELIGIBLE,
        authorization_reentry=None,
        authorization_product=None,
        authorization_id=None,
        decision=None,
        rationale_codes=("test:not-execution-eligible",),
        authorization_invocation_count=0,
        eligible_for_existing_execution=False,
        invokes_authorization=False,
    )

    class _NeverCalled:
        calls = 0

        def consume(self, authorization_reentry, *, now):
            self.calls += 1
            raise AssertionError("E2 owner must not be called")

    owner = _NeverCalled()
    result = GovernedLongHorizonInvestigationE2ExecutionReentryV1(
        execution_reentry=owner
    ).consume(a2, now=NOW)

    assert owner.calls == 0
    assert reader.calls == 0
    assert result.status is (
        GovernedInvestigationE2ExecutionAdmissionStatus.NOT_ELIGIBLE
    )
    assert result.execution_invocation_count == 0
    assert result.episode_record_invocation_count == 0


def test_existing_e2_owner_exception_becomes_review_without_retry():
    manager, _, _ = _runtime()
    a2 = _a2(manager)

    class _FailingOwner:
        calls = 0

        def consume(self, authorization_reentry, *, now):
            self.calls += 1
            assert authorization_reentry is a2.authorization_reentry
            assert now is NOW
            raise RuntimeError("synthetic owner failure")

    owner = _FailingOwner()
    result = GovernedLongHorizonInvestigationE2ExecutionReentryV1(
        execution_reentry=owner
    ).consume(a2, now=NOW)

    assert owner.calls == 1
    assert result.status is (
        GovernedInvestigationE2ExecutionAdmissionStatus.REVIEW_REQUIRED
    )
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 0
    assert not result.permits_retry
    assert not result.eligible_for_existing_reasoning_reentry


def test_failed_e2_is_preserved_as_stopped_without_reasoning_eligibility():
    reader = _Reader(fail=True)
    manager, runtime, _ = _runtime(reader=reader)
    result = GovernedLongHorizonInvestigationE2ExecutionReentryV1(runtime).consume(
        _a2(manager), now=NOW
    )

    assert result.status is GovernedInvestigationE2ExecutionAdmissionStatus.STOPPED
    assert result.execution_status is GovernedLevel2ExecutionStatus.FAILED
    assert result.execution_reentry is not None
    assert result.evidence_envelope is result.execution_reentry.evidence_envelope
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert not result.eligible_for_existing_reasoning_reentry
    assert not result.permits_retry


def test_forged_recorded_e2_lineage_is_review_and_not_exposed_as_trusted_evidence():
    manager, runtime, _ = _runtime()
    a2 = _a2(manager)
    from app.governed_multistep_investigation_execution_reentry import (
        GovernedMultiStepInvestigationExecutionReentryV1,
    )

    canonical = GovernedMultiStepInvestigationExecutionReentryV1(runtime).consume(
        a2.authorization_reentry,
        now=NOW,
    )
    forged_envelope = replace(
        canonical.evidence_envelope,
        plan_id="evidence-acquisition-plan-forged-abcdef123456",
    )
    forged = replace(canonical, evidence_envelope=forged_envelope)

    class _ForgingOwner:
        def consume(self, authorization_reentry, *, now):
            assert authorization_reentry is a2.authorization_reentry
            return forged

    result = GovernedLongHorizonInvestigationE2ExecutionReentryV1(
        execution_reentry=_ForgingOwner()
    ).consume(a2, now=NOW)

    assert result.status is (
        GovernedInvestigationE2ExecutionAdmissionStatus.REVIEW_REQUIRED
    )
    assert result.execution_reentry is forged
    assert result.evidence_envelope is None
    assert result.execution_id is None
    assert not result.eligible_for_existing_reasoning_reentry
    assert not result.permits_retry
