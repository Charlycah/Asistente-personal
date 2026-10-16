from __future__ import annotations

import ast
import inspect
from dataclasses import fields

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumptionV1,
)
from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
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
    CapabilityRegistryManager,
)
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


def _registry(*outputs: str) -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name="local.sensor",
            description="Local read-only evidence provider.",
            evidence_outputs=outputs,
        )
    )
    return registry


def _requirement(
    requirement_id: str,
    *,
    description: str = "new discriminating observation",
) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id=requirement_id,
        hypothesis_ids=("h1", "h2"),
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        known_elements=("shared-fact",),
        missing_evidence_descriptions=(description,),
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


def _continuation(
    requirement: DiscriminatingEvidenceRequirement | None = None,
):
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, _envelope(1)).state
    state = boundary.record_reentry(state, _reentry(1)).state
    return GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(
        state,
        requirement
        if requirement is not None
        else _requirement("discrimination-requirement-r2"),
    )


def test_valid_continuation_invokes_existing_planning_once_and_produces_p2() -> None:
    registry = _registry("new discriminating observation")
    continuation = _continuation()

    result = GovernedMultiStepInvestigationPlanningReentryV1(
        registry
    ).consume(continuation)

    assert result.status is GovernedInvestigationPlanningReentryStatus.PLANNED
    assert result.planning_invocation_count == 1
    assert result.planning_product is not None
    assert result.plan_id == result.planning_product.planning_report.plan_id
    assert result.plan_id not in continuation.resulting_state.plan_ids


def test_exact_r2_is_preserved_into_existing_planning() -> None:
    registry = _registry("new discriminating observation")
    requirement = _requirement("discrimination-requirement-r2")
    continuation = _continuation(requirement)

    result = GovernedMultiStepInvestigationPlanningReentryV1(
        registry
    ).consume(continuation)

    assert result.requirement_id == requirement.requirement_id
    assert result.planning_product is not None
    assert (
        result.planning_product.planning_report.requirement_id
        == requirement.requirement_id
    )
    assert continuation.source_requirement is requirement
    assert not result.rewrites_requirement


def test_plannable_p2_is_only_eligible_for_authorization_not_execution() -> None:
    registry = _registry("new discriminating observation")

    result = GovernedMultiStepInvestigationPlanningReentryV1(
        registry
    ).consume(_continuation())

    assert result.planning_status is EvidenceAcquisitionPlanningStatus.PLANNABLE
    assert result.eligible_for_authorization
    assert not result.planning_execution_authorized
    assert not result.execution_authorized
    assert not result.invokes_authorization
    assert not result.invokes_capabilities


def test_no_capability_plan_is_preserved_but_not_authorization_eligible() -> None:
    registry = _registry("different evidence")

    result = GovernedMultiStepInvestigationPlanningReentryV1(
        registry
    ).consume(_continuation())

    assert result.status is GovernedInvestigationPlanningReentryStatus.PLANNED
    assert (
        result.planning_status
        is EvidenceAcquisitionPlanningStatus.NO_CAPABILITY_AVAILABLE
    )
    assert not result.eligible_for_authorization


def test_ambiguous_plan_is_not_authorization_eligible() -> None:
    registry = CapabilityRegistryManager()
    for name in ("sensor.a", "sensor.b"):
        registry.register(
            CapabilityDescriptor(
                name=name,
                description=f"Evidence provider {name}.",
                evidence_outputs=("new discriminating observation",),
            )
        )

    result = GovernedMultiStepInvestigationPlanningReentryV1(
        registry
    ).consume(_continuation())

    assert result.planning_status is EvidenceAcquisitionPlanningStatus.AMBIGUOUS
    assert not result.eligible_for_authorization


def test_noneligible_continuation_never_invokes_planning() -> None:
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    continuation = GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(state, _requirement("discrimination-requirement-r2"))

    result = GovernedMultiStepInvestigationPlanningReentryV1(
        _registry("new discriminating observation")
    ).consume(continuation)

    assert result.status is GovernedInvestigationPlanningReentryStatus.NOT_ELIGIBLE
    assert result.planning_invocation_count == 0
    assert result.planning_product is None
    assert not result.eligible_for_authorization


def test_planning_failure_fails_closed_after_one_call() -> None:
    class FailingPlanningSurface:
        calls = 0

        def consume(self, requirement):
            self.calls += 1
            raise RuntimeError("synthetic planning failure")

    surface = FailingPlanningSurface()
    result = GovernedMultiStepInvestigationPlanningReentryV1(
        _registry("new discriminating observation"),
        planning_surface=surface,
    ).consume(_continuation())

    assert surface.calls == 1
    assert (
        result.status
        is GovernedInvestigationPlanningReentryStatus.REVIEW_REQUIRED
    )
    assert result.planning_invocation_count == 1
    assert result.planning_product is None
    assert not result.eligible_for_authorization


def test_prior_plan_reuse_is_rejected() -> None:
    class ReusedPlanningSurface:
        def __init__(self, product):
            self.product = product

        def consume(self, requirement):
            return self.product

    continuation = _continuation()
    registry = _registry("new discriminating observation")
    normal_product = GovernedEvidenceAcquisitionProductiveConsumptionV1(
        registry
    ).consume(continuation.source_requirement)
    reused_report = normal_product.planning_report.__class__(
        **{
            **normal_product.planning_report.__dict__,
            "plan_id": continuation.resulting_state.plan_ids[0],
        }
    )
    reused_product = normal_product.__class__(
        **{
            **normal_product.__dict__,
            "planning_report": reused_report,
        }
    )

    result = GovernedMultiStepInvestigationPlanningReentryV1(
        registry,
        planning_surface=ReusedPlanningSurface(reused_product),
    ).consume(continuation)

    assert (
        result.status
        is GovernedInvestigationPlanningReentryStatus.REVIEW_REQUIRED
    )
    assert not result.eligible_for_authorization


def test_result_preserves_episode_lineage_without_mutating_episode_state() -> None:
    continuation = _continuation()
    before = continuation.resulting_state
    result = GovernedMultiStepInvestigationPlanningReentryV1(
        _registry("new discriminating observation")
    ).consume(continuation)

    assert result.episode_id == continuation.episode_id
    assert result.source_reference == continuation.source_reference
    assert result.world_snapshot_id == continuation.world_snapshot_id
    assert result.current_step == 2
    assert result.remaining_acquisitions == 1
    assert continuation.resulting_state == before
    assert not result.modifies_episode_state


def test_contract_has_no_downstream_execution_or_side_effect_authority() -> None:
    defaults = {
        field.name: field.default
        for field in fields(
            __import__(
                "app.governed_multistep_investigation_planning_reentry",
                fromlist=["GovernedInvestigationPlanningReentryResult"],
            ).GovernedInvestigationPlanningReentryResult
        )
    }
    for name in (
        "planning_execution_authorized",
        "execution_authorized",
        "invokes_authorization",
        "invokes_capabilities",
        "invokes_reasoning",
        "rewrites_requirement",
        "modifies_episode_state",
        "creates_questions",
        "modifies_memory",
        "modifies_world_model",
        "starts_background_process",
    ):
        assert defaults[name] is False


def test_adapter_contains_no_authorization_execution_reasoning_or_loop_calls() -> None:
    source = inspect.getsource(GovernedMultiStepInvestigationPlanningReentryV1)
    tree = ast.parse(source)

    for forbidden in (
        "GovernedIndependenceAuthorization",
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
                "authorize",
                "reason",
                "run",
                "run_episode",
                "run_next_step",
            }
        )
        for node in ast.walk(tree)
    )
