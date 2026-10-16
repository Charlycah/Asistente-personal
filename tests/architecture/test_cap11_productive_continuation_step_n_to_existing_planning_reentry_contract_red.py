from __future__ import annotations

import ast
import inspect

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeStatus,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedInvestigationPlanningReentryStatus,
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuationV1,
)
from core.capability_registry import CapabilityDescriptor, CapabilityRegistryManager
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

SOURCE = "scenario-cap11-step-n-planning"
SNAPSHOT = "world-cap11-step-n-planning"
HARD_CAP = 4


def _registry() -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name="local.sensor",
            description="Local read-only evidence provider.",
            evidence_outputs=("next discriminating observation",),
        )
    )
    return registry


def _requirement(step: int) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id=f"discrimination-requirement-r{step}-cap11-step-n",
        hypothesis_ids=("h1", "h2"),
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("next discriminating observation",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _envelope(step: int) -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=f"level2-read-only-execution-step-{step:02d}-cap11n",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=f"independence-authorization-step-{step:02d}-cap11n",
        requirement_id=_requirement(step).requirement_id,
        plan_id=f"evidence-acquisition-plan-step-{step:02d}-cap11n",
        capability_name="local.sensor",
        evidence_description="next discriminating observation",
        declared_evidence_output="next discriminating observation",
        observed_value=20.0 + step,
        observation_source_reference=f"local:test-reader:{step}",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        rationale_codes=("execution:cap11-step-n",),
        source_fingerprint="f" * 64,
    )


def _reentry(step: int) -> GovernedLevel2ReasoningReentryResult:
    envelope = _envelope(step)
    return GovernedLevel2ReasoningReentryResult(
        reentry_id=f"level2-reasoning-reentry-step-{step:02d}-cap11n",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        capability_name=envelope.capability_name,
        evidence_id=f"evidence-{step}-cap11n",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        reasoning_result=None,
        rationale_codes=("reentry:cap11-step-n",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )


def _awaiting_requirement_after(step: int, *, budget: int = HARD_CAP):
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-cap11-step-n",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id=_requirement(1).requirement_id,
        max_acquisitions=budget,
    ).state
    for acquisition_step in range(1, step + 1):
        if acquisition_step > 1:
            state = boundary.evaluate_continuation(
                state,
                _requirement(acquisition_step),
            ).state
        state = boundary.record_acquisition(state, _envelope(acquisition_step)).state
        state = boundary.record_reentry(state, _reentry(acquisition_step)).state
    return boundary, state


def _continuation_to(step: int, *, budget: int = HARD_CAP):
    boundary, state = _awaiting_requirement_after(step - 1, budget=budget)
    assert state.status is GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
    requirement = _requirement(step)
    continuation = GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(state, requirement)
    return continuation, requirement


def test_red_step_three_productive_continuation_is_planning_eligible() -> None:
    continuation, requirement = _continuation_to(3)

    assert continuation.source_requirement is requirement
    assert continuation.current_step == 3
    assert continuation.remaining_acquisitions == 2
    assert continuation.resulting_state.consumed_acquisitions == 2
    assert continuation.eligible_for_existing_planning


def test_red_step_four_productive_continuation_is_planning_eligible() -> None:
    continuation, requirement = _continuation_to(4)

    assert continuation.source_requirement is requirement
    assert continuation.current_step == 4
    assert continuation.remaining_acquisitions == 1
    assert continuation.resulting_state.consumed_acquisitions == 3
    assert continuation.eligible_for_existing_planning


def test_red_step_three_reenters_existing_planning_exactly_once() -> None:
    continuation, requirement = _continuation_to(3)

    result = GovernedMultiStepInvestigationPlanningReentryV1(_registry()).consume(
        continuation
    )

    assert result.status is GovernedInvestigationPlanningReentryStatus.PLANNED
    assert result.planning_invocation_count == 1
    assert result.requirement_id == requirement.requirement_id
    assert result.current_step == 3
    assert result.remaining_acquisitions == 2
    assert result.planning_product is not None
    assert (
        result.planning_product.planning_report.requirement_id
        == requirement.requirement_id
    )


def test_red_step_three_plan_is_new_and_only_authorization_eligible() -> None:
    continuation, _ = _continuation_to(3)
    prior_plan_ids = continuation.resulting_state.plan_ids

    result = GovernedMultiStepInvestigationPlanningReentryV1(_registry()).consume(
        continuation
    )

    assert result.status is GovernedInvestigationPlanningReentryStatus.PLANNED
    assert result.planning_status is EvidenceAcquisitionPlanningStatus.PLANNABLE
    assert result.plan_id is not None
    assert result.plan_id not in prior_plan_ids
    assert result.eligible_for_authorization
    assert not result.invokes_authorization
    assert not result.execution_authorized
    assert not result.invokes_capabilities
    assert not result.invokes_reasoning


def test_legacy_step_two_budget_two_remains_exactly_supported() -> None:
    continuation, requirement = _continuation_to(2, budget=2)
    result = GovernedMultiStepInvestigationPlanningReentryV1(_registry()).consume(
        continuation
    )

    assert continuation.current_step == 2
    assert continuation.remaining_acquisitions == 1
    assert continuation.eligible_for_existing_planning
    assert continuation.source_requirement is requirement
    assert result.status is GovernedInvestigationPlanningReentryStatus.PLANNED
    assert result.planning_invocation_count == 1
    assert result.requirement_id == requirement.requirement_id


def test_red_generalization_removes_step_two_guard_without_adding_new_authority(
) -> None:
    continuation_source = inspect.getsource(
        GovernedMultiStepInvestigationProductiveContinuationV1
    )
    planning_source = inspect.getsource(GovernedMultiStepInvestigationPlanningReentryV1)
    planning_tree = ast.parse(planning_source)

    assert "current_step == 2" not in continuation_source
    assert "remaining_acquisitions == 1" not in continuation_source
    assert "bounded_step_two_required" not in planning_source
    assert "current_step != 2" not in planning_source
    assert "remaining_acquisitions != 1" not in planning_source

    forbidden = (
        "GovernedMultiStepInvestigationAuthorizationReentryV1",
        "GovernedIndependenceAuthorizationBoundaryV1",
        "GovernedLevel2ReadOnlyExecutionGatewayV1",
        "GovernedLevel2ReasoningReentryFoundationV1",
        "OfficialMemoryGateway",
        "Curiosity",
        "ResearchLoop",
        "HorizonManager",
    )
    for token in forbidden:
        assert token not in continuation_source
        assert token not in planning_source

    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name in {"authorize", "execute", "reason", "retry", "run_episode"}
        )
        for node in ast.walk(planning_tree)
    )
