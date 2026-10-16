from __future__ import annotations

from types import SimpleNamespace

from app.governed_independence_authorization_boundary import (
    GovernedInitiationDecision,
)
from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_a2_authorization_reentry import (
    GovernedInvestigationA2AuthorizationAdmissionStatus,
    GovernedLongHorizonInvestigationA2AuthorizationReentryV1,
)
from app.governed_long_horizon_investigation_p2_planning_reentry import (
    GovernedInvestigationP2PlanningAdmissionResult,
    GovernedInvestigationP2PlanningAdmissionStatus,
)
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuationV1,
)
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityRegistryManager,
    CapabilityRisk,
    PermissionScope,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

SOURCE = "scenario-123"
SNAPSHOT = "world-1"


def _registry(
    *,
    policy: CapabilityInitiationPolicy = CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
) -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name="local.sensor",
            description="Local read-only evidence provider.",
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.READ,
            evidence_outputs=("new discriminating observation",),
            initiation_policy=policy,
            effect_class=CapabilityEffectClass.READ_ONLY,
            interaction_scope=CapabilityInteractionScope.INTERNAL,
        )
    )
    return registry


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


def _envelope() -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id="level2-read-only-execution-step-01-abcdef123456",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id="independence-authorization-step-01-abcdef123456",
        requirement_id="discrimination-requirement-r1",
        plan_id="evidence-acquisition-plan-step-01-abcdef123456",
        capability_name="local.sensor",
        evidence_description="room temperature",
        declared_evidence_output="room_temperature",
        observed_value=23.0,
        observation_source_reference="local:test-reader",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        rationale_codes=("execution:test",),
        source_fingerprint="f" * 64,
    )


def _reentry() -> GovernedLevel2ReasoningReentryResult:
    envelope = _envelope()
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
        rationale_codes=("reentry:test",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )


def _planning_result(
    registry: CapabilityRegistryManager,
) -> GovernedInvestigationP2PlanningAdmissionResult:
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, _envelope()).state
    state = boundary.record_reentry(state, _reentry()).state
    continuation = GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(state, _requirement())
    planning_reentry = GovernedMultiStepInvestigationPlanningReentryV1(
        registry
    ).consume(continuation)
    return GovernedInvestigationP2PlanningAdmissionResult(
        thread_id="investigation-thread-1",
        checkpoint_id="investigation-checkpoint-1",
        episode_id=planning_reentry.episode_id,
        originating_reasoning_id="reasoning-decision-1",
        requirement_id=planning_reentry.requirement_id,
        source_reference=planning_reentry.source_reference,
        world_snapshot_id=planning_reentry.world_snapshot_id,
        status=GovernedInvestigationP2PlanningAdmissionStatus.PLANNED,
        planning_reentry=planning_reentry,
        plan_id=planning_reentry.plan_id,
        planning_status=planning_reentry.planning_status,
        rationale_codes=("p2-planning:test",),
        planning_invocation_count=1,
        eligible_for_existing_authorization=(
            planning_reentry.eligible_for_authorization
        ),
        invokes_planning=True,
    )


class _AuthorizationSpy:
    def __init__(self, delegate) -> None:
        self._delegate = delegate
        self.calls = 0
        self.received = None

    def consume(self, planning_reentry):
        self.calls += 1
        self.received = planning_reentry
        return self._delegate.consume(planning_reentry)


def test_exact_p2_is_forwarded_once_and_may_initiate_stops_before_e2():
    registry = _registry()
    planning_result = _planning_result(registry)
    spy = _AuthorizationSpy(
        GovernedMultiStepInvestigationAuthorizationReentryV1(registry)
    )

    result = GovernedLongHorizonInvestigationA2AuthorizationReentryV1(
        authorization_reentry=spy
    ).consume(planning_result)

    assert spy.calls == 1
    assert spy.received is planning_result.planning_reentry
    assert result.status is (
        GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED
    )
    assert result.authorization_reentry is not None
    assert result.authorization_product is (
        result.authorization_reentry.authorization_product
    )
    assert result.decision is GovernedInitiationDecision.MAY_INITIATE
    assert result.eligible_for_existing_execution
    assert result.authorization_invocation_count == 1
    assert result.invokes_authorization
    assert not result.invokes_execution
    assert not result.invokes_reasoning
    assert not result.invokes_planning


def test_must_ask_is_preserved_without_existing_execution_eligibility():
    registry = _registry(policy=CapabilityInitiationPolicy.HUMAN_APPROVAL)
    result = GovernedLongHorizonInvestigationA2AuthorizationReentryV1(registry).consume(
        _planning_result(registry)
    )

    assert result.status is (
        GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED
    )
    assert result.decision is GovernedInitiationDecision.MUST_ASK
    assert not result.eligible_for_existing_execution
    assert result.authorization_product is not None


def test_must_abstain_is_preserved_without_existing_execution_eligibility():
    registry = _registry(policy=CapabilityInitiationPolicy.NEVER)
    result = GovernedLongHorizonInvestigationA2AuthorizationReentryV1(registry).consume(
        _planning_result(registry)
    )

    assert result.status is (
        GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED
    )
    assert result.decision is GovernedInitiationDecision.MUST_ABSTAIN
    assert not result.eligible_for_existing_execution
    assert result.authorization_product is not None


def test_nonplannable_p2_stops_before_existing_a2_owner():
    planning_result = _planning_result(CapabilityRegistryManager())
    spy = _AuthorizationSpy(
        GovernedMultiStepInvestigationAuthorizationReentryV1(_registry())
    )

    result = GovernedLongHorizonInvestigationA2AuthorizationReentryV1(
        authorization_reentry=spy
    ).consume(planning_result)

    assert result.status is (
        GovernedInvestigationA2AuthorizationAdmissionStatus.NOT_ELIGIBLE
    )
    assert spy.calls == 0
    assert result.authorization_reentry is None
    assert result.authorization_invocation_count == 0
    assert not result.eligible_for_existing_execution


def test_existing_a2_owner_failure_becomes_review_without_retry():
    registry = _registry()
    planning_result = _planning_result(registry)

    class _FailingOwner:
        calls = 0

        def consume(self, planning_reentry):
            self.calls += 1
            assert planning_reentry is planning_result.planning_reentry
            raise RuntimeError("synthetic A2 failure")

    owner = _FailingOwner()
    result = GovernedLongHorizonInvestigationA2AuthorizationReentryV1(
        authorization_reentry=owner
    ).consume(planning_result)

    assert owner.calls == 1
    assert result.status is (
        GovernedInvestigationA2AuthorizationAdmissionStatus.REVIEW_REQUIRED
    )
    assert result.authorization_invocation_count == 1
    assert result.authorization_reentry is None
    assert not result.eligible_for_existing_execution
    assert not result.permits_retry


def test_forged_a2_lineage_is_review_required_and_never_exposes_product():
    registry = _registry()
    planning_result = _planning_result(registry)
    canonical = GovernedMultiStepInvestigationAuthorizationReentryV1(registry).consume(
        planning_result.planning_reentry
    )
    forged = SimpleNamespace(
        **{
            **canonical.__dict__,
            "plan_id": "forged-plan-id",
        }
    )

    class _ForgingOwner:
        def consume(self, planning_reentry):
            assert planning_reentry is planning_result.planning_reentry
            return forged

    result = GovernedLongHorizonInvestigationA2AuthorizationReentryV1(
        authorization_reentry=_ForgingOwner()
    ).consume(planning_result)

    assert result.status is (
        GovernedInvestigationA2AuthorizationAdmissionStatus.REVIEW_REQUIRED
    )
    assert result.authorization_reentry is forged
    assert result.authorization_product is None
    assert result.authorization_id is None
    assert result.decision is None
    assert not result.eligible_for_existing_execution
    assert not result.permits_retry
