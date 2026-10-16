from __future__ import annotations

import ast
import inspect
from dataclasses import fields

from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationReport,
    GovernedIndependenceLevel,
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
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedInvestigationAuthorizationReentryResult,
    GovernedInvestigationAuthorizationReentryStatus,
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


def _registry(
    *,
    policy: CapabilityInitiationPolicy = (
        CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS
    ),
    risk: CapabilityRisk = CapabilityRisk.LOW,
    permission: PermissionScope = PermissionScope.READ,
) -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name="local.sensor",
            description="Local read-only evidence provider.",
            risk=risk,
            permission_scope=permission,
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
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("new discriminating observation",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _envelope(step: int) -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=f"level2-read-only-execution-step-{step:02d}-abcdef123456",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=(
            f"independence-authorization-step-{step:02d}-abcdef123456"
        ),
        requirement_id=f"discrimination-requirement-r{step}",
        plan_id=f"evidence-acquisition-plan-step-{step:02d}-abcdef123456",
        capability_name="local.sensor",
        evidence_description="room temperature",
        declared_evidence_output="room_temperature",
        observed_value=22.0 + step,
        observation_source_reference="local:test-reader",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        rationale_codes=("execution:test",),
        source_fingerprint="f" * 64,
    )


def _reentry(step: int) -> GovernedLevel2ReasoningReentryResult:
    envelope = _envelope(step)
    return GovernedLevel2ReasoningReentryResult(
        reentry_id=f"level2-reasoning-reentry-step-{step:02d}-abcdef123456",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        capability_name=envelope.capability_name,
        evidence_id=f"evidence-{step}",
        source_reference=envelope.source_reference,
        world_snapshot_id=envelope.world_snapshot_id,
        reasoning_result=None,
        rationale_codes=("reentry:test",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )


def _planning_reentry(registry: CapabilityRegistryManager):
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, _envelope(1)).state
    state = boundary.record_reentry(state, _reentry(1)).state
    continuation = GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(state, _requirement())
    return GovernedMultiStepInvestigationPlanningReentryV1(
        registry
    ).consume(continuation)


def test_valid_p2_invokes_existing_authorization_once_and_produces_new_a2() -> None:
    registry = _registry()
    planning = _planning_reentry(registry)

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(planning)

    assert (
        result.status
        is GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
    )
    assert result.authorization_invocation_count == 1
    assert result.authorization_product is not None
    assert result.authorization_id not in (
        planning.continuation.resulting_state.authorization_ids
    )


def test_a2_preserves_exact_r2_p2_source_and_snapshot_lineage() -> None:
    registry = _registry()
    planning = _planning_reentry(registry)

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(planning)

    product = result.authorization_product
    assert product is not None
    assert product.requirement_id == planning.requirement_id
    assert product.plan_id == planning.plan_id
    assert product.source_reference == planning.source_reference
    assert product.world_snapshot_id == planning.world_snapshot_id


def test_may_initiate_only_exposes_existing_execution_eligibility() -> None:
    registry = _registry()

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(_planning_reentry(registry))

    assert result.decision is GovernedInitiationDecision.MAY_INITIATE
    assert result.eligible_for_existing_execution
    assert not result.execution_authorized
    assert not result.invokes_execution_gateway
    assert not result.invokes_capabilities


def test_human_approval_decision_does_not_become_execution_eligible() -> None:
    registry = _registry(policy=CapabilityInitiationPolicy.HUMAN_APPROVAL)

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(_planning_reentry(registry))

    assert result.decision is GovernedInitiationDecision.MUST_ASK
    assert not result.eligible_for_existing_execution
    assert not result.creates_questions
    assert not result.emits_conversation


def test_forbidden_policy_does_not_become_execution_eligible() -> None:
    registry = _registry(policy=CapabilityInitiationPolicy.NEVER)

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(_planning_reentry(registry))

    assert result.decision is GovernedInitiationDecision.MUST_ABSTAIN
    assert not result.eligible_for_existing_execution


def test_noneligible_planning_reentry_never_invokes_authorization() -> None:
    registry = CapabilityRegistryManager()
    planning = _planning_reentry(registry)

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(planning)

    assert (
        result.status
        is GovernedInvestigationAuthorizationReentryStatus.NOT_ELIGIBLE
    )
    assert result.authorization_invocation_count == 0
    assert result.authorization_product is None


def test_authorization_failure_fails_closed_without_retry() -> None:
    class FailingBoundary:
        calls = 0

        def evaluate(self, planning_product):
            self.calls += 1
            raise RuntimeError("synthetic authorization failure")

    registry = _registry()
    failing = FailingBoundary()
    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry,
        authorization_boundary=failing,
    ).consume(_planning_reentry(registry))

    assert failing.calls == 1
    assert (
        result.status
        is GovernedInvestigationAuthorizationReentryStatus.REVIEW_REQUIRED
    )
    assert result.authorization_invocation_count == 1
    assert not result.eligible_for_existing_execution


def test_reused_a1_is_rejected() -> None:
    registry = _registry()
    planning = _planning_reentry(registry)
    old_authorization_id = (
        planning.continuation.resulting_state.authorization_ids[0]
    )

    class ReusedBoundary:
        def evaluate(self, planning_product):
            report = planning_product.planning_report
            return GovernedIndependenceAuthorizationReport(
                authorization_id=old_authorization_id,
                decision=GovernedInitiationDecision.MAY_INITIATE,
                independence_level=GovernedIndependenceLevel.LEVEL_2_READ_ONLY,
                requirement_id=report.requirement_id,
                plan_id=report.plan_id,
                capability_name="local.sensor",
                source_reference=report.source_reference,
                world_snapshot_id=report.world_snapshot_id,
                rationale_codes=("authorization:test-reused-a1",),
                source_fingerprint="a" * 64,
            )

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry,
        authorization_boundary=ReusedBoundary(),
    ).consume(planning)

    assert (
        result.status
        is GovernedInvestigationAuthorizationReentryStatus.REVIEW_REQUIRED
    )
    assert result.authorization_product is None
    assert not result.eligible_for_existing_execution


def test_episode_state_remains_unchanged_after_a2() -> None:
    registry = _registry()
    planning = _planning_reentry(registry)
    before = planning.continuation.resulting_state

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(planning)

    assert result.planning_reentry.continuation.resulting_state == before
    assert not result.modifies_episode_state


def test_contract_has_no_execution_reasoning_or_side_effect_authority() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedInvestigationAuthorizationReentryResult)
    }
    for name in (
        "execution_authorized",
        "invokes_execution_gateway",
        "invokes_capabilities",
        "invokes_reasoning",
        "modifies_episode_state",
        "creates_questions",
        "emits_conversation",
        "modifies_memory",
        "modifies_world_model",
        "starts_background_process",
    ):
        assert defaults[name] is False


def test_adapter_contains_no_execution_reasoning_loop_or_retry_calls() -> None:
    source = inspect.getsource(
        GovernedMultiStepInvestigationAuthorizationReentryV1
    )
    tree = ast.parse(source)

    for forbidden in (
        "OfficialCapabilityGateway",
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
                "execute",
                "reason",
                "run",
                "retry",
                "run_episode",
                "run_next_step",
            }
        )
        for node in ast.walk(tree)
    )
