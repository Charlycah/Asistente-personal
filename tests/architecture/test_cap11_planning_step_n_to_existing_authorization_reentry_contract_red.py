from __future__ import annotations

import ast
import inspect

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
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedInvestigationAuthorizationReentryStatus,
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedInvestigationPlanningReentryStatus,
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

SOURCE = "scenario-cap11-step-n-authorization"
SNAPSHOT = "world-cap11-step-n-authorization"
HARD_CAP = 4


def _registry() -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name="local.sensor",
            description="Local read-only evidence provider.",
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.READ,
            evidence_outputs=("next discriminating observation",),
            initiation_policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
            effect_class=CapabilityEffectClass.READ_ONLY,
            interaction_scope=CapabilityInteractionScope.INTERNAL,
        )
    )
    return registry


def _requirement(step: int) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id=f"discrimination-requirement-r{step}-cap11-auth-n",
        hypothesis_ids=("h1", "h2"),
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("next discriminating observation",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _envelope(step: int) -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=f"level2-read-only-execution-step-{step:02d}-cap11authn",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=f"independence-authorization-step-{step:02d}-cap11authn",
        requirement_id=_requirement(step).requirement_id,
        plan_id=f"evidence-acquisition-plan-step-{step:02d}-cap11authn",
        capability_name="local.sensor",
        evidence_description="next discriminating observation",
        declared_evidence_output="next discriminating observation",
        observed_value=20.0 + step,
        observation_source_reference=f"local:test-reader:{step}",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        rationale_codes=("execution:cap11-auth-n",),
        source_fingerprint="f" * 64,
    )


def _reentry(step: int) -> GovernedLevel2ReasoningReentryResult:
    envelope = _envelope(step)
    return GovernedLevel2ReasoningReentryResult(
        reentry_id=f"level2-reasoning-reentry-step-{step:02d}-cap11authn",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        capability_name=envelope.capability_name,
        evidence_id=f"evidence-{step}-cap11authn",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        reasoning_result=None,
        rationale_codes=("reentry:cap11-auth-n",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )


def _planning_to(step: int, *, budget: int = HARD_CAP):
    registry = _registry()
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-cap11-auth-n",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id=_requirement(1).requirement_id,
        max_acquisitions=budget,
    ).state
    for acquisition_step in range(1, step):
        if acquisition_step > 1:
            state = boundary.evaluate_continuation(
                state,
                _requirement(acquisition_step),
            ).state
        state = boundary.record_acquisition(state, _envelope(acquisition_step)).state
        state = boundary.record_reentry(state, _reentry(acquisition_step)).state

    requirement = _requirement(step)
    continuation = GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(state, requirement)
    planning = GovernedMultiStepInvestigationPlanningReentryV1(registry).consume(
        continuation
    )
    assert planning.status is GovernedInvestigationPlanningReentryStatus.PLANNED
    return registry, planning, requirement


def test_red_step_three_planning_reenters_existing_authorization_once() -> None:
    registry, planning, requirement = _planning_to(3)
    prior_authorization_ids = planning.continuation.resulting_state.authorization_ids

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(planning)

    assert result.status is GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
    assert result.authorization_invocation_count == 1
    assert result.authorization_product is not None
    assert result.requirement_id == requirement.requirement_id
    assert result.plan_id == planning.plan_id
    assert result.current_step == 3
    assert result.remaining_acquisitions == 2
    assert result.authorization_id not in prior_authorization_ids


def test_red_step_four_planning_reenters_existing_authorization_once() -> None:
    registry, planning, requirement = _planning_to(4)
    prior_authorization_ids = planning.continuation.resulting_state.authorization_ids

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(planning)

    assert result.status is GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
    assert result.authorization_invocation_count == 1
    assert result.authorization_product is not None
    assert result.requirement_id == requirement.requirement_id
    assert result.plan_id == planning.plan_id
    assert result.current_step == 4
    assert result.remaining_acquisitions == 1
    assert result.authorization_id not in prior_authorization_ids


def test_red_authorized_step_three_only_exposes_execution_eligibility() -> None:
    registry, planning, _ = _planning_to(3)

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(planning)

    assert result.status is GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
    assert result.decision is GovernedInitiationDecision.MAY_INITIATE
    assert result.eligible_for_existing_execution
    assert not result.execution_authorized
    assert not result.invokes_execution_gateway
    assert not result.invokes_capabilities
    assert not result.invokes_reasoning
    assert not result.modifies_episode_state


def test_legacy_p2_a2_budget_two_remains_exactly_supported() -> None:
    registry, planning, requirement = _planning_to(2, budget=2)

    result = GovernedMultiStepInvestigationAuthorizationReentryV1(
        registry
    ).consume(planning)

    assert planning.current_step == 2
    assert planning.remaining_acquisitions == 1
    assert result.status is GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
    assert result.authorization_invocation_count == 1
    assert result.requirement_id == requirement.requirement_id
    assert result.plan_id == planning.plan_id


def test_red_generalization_removes_step_two_guards_without_new_authority() -> None:
    source = inspect.getsource(GovernedMultiStepInvestigationAuthorizationReentryV1)
    tree = ast.parse(source)

    assert "current_step != 2" not in source
    assert "remaining_acquisitions != 1" not in source
    assert "step_two_required" not in source
    assert "single_remaining_budget_required" not in source

    for forbidden in (
        "GovernedLevel2ReadOnlyExecutionGatewayV1",
        "OfficialCapabilityGateway",
        "GovernedLevel2ReasoningReentryFoundationV1",
        "OfficialMemoryGateway",
        "ResearchLoop",
        "HorizonManager",
    ):
        assert forbidden not in source

    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name in {"execute", "reason", "retry", "run_episode"}
        )
        for node in ast.walk(tree)
    )
