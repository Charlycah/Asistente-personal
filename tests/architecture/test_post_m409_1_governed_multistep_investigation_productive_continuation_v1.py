from __future__ import annotations

import ast
import inspect
from dataclasses import fields

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuation,
    GovernedMultiStepInvestigationProductiveContinuationV1,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


def _requirement(
    requirement_id: str,
    *,
    source_reference: str = "scenario-123",
    world_snapshot_id: str = "world-1",
) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id=requirement_id,
        hypothesis_ids=("h1", "h2"),
        source_reference=source_reference,
        world_snapshot_id=world_snapshot_id,
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


def _awaiting_requirement_state():
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, _envelope(1)).state
    return boundary.record_reentry(state, _reentry(1)).state


def test_valid_r2_is_productively_eligible_for_existing_planning() -> None:
    state = _awaiting_requirement_state()
    requirement = _requirement("discrimination-requirement-r2")

    result = GovernedMultiStepInvestigationProductiveContinuationV1().consume(
        state,
        requirement,
    )

    assert (
        result.decision
        is GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
    )
    assert result.eligible_for_existing_planning
    assert result.current_step == 2
    assert result.remaining_acquisitions == 1
    assert (
        result.resulting_state.status
        is GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING
    )


def test_requirement_is_preserved_exactly_without_rewriting() -> None:
    state = _awaiting_requirement_state()
    requirement = _requirement("discrimination-requirement-r2")

    result = GovernedMultiStepInvestigationProductiveContinuationV1().consume(
        state,
        requirement,
    )

    assert result.source_requirement is requirement
    assert result.source_requirement_id == requirement.requirement_id
    assert result.source_reference == requirement.source_reference
    assert result.world_snapshot_id == requirement.world_snapshot_id
    assert not result.creates_requirement
    assert not result.rewrites_requirement


def test_reused_requirement_is_review_and_not_planning_eligible() -> None:
    result = GovernedMultiStepInvestigationProductiveContinuationV1().consume(
        _awaiting_requirement_state(),
        _requirement("discrimination-requirement-r1"),
    )

    assert (
        result.decision
        is GovernedInvestigationContinuationDecision.REVIEW_REQUIRED
    )
    assert not result.eligible_for_existing_planning
    assert (
        result.stopping_reason
        is GovernedInvestigationStoppingReason.LINEAGE_BROKEN
    )


def test_snapshot_mismatch_is_review_and_not_planning_eligible() -> None:
    result = GovernedMultiStepInvestigationProductiveContinuationV1().consume(
        _awaiting_requirement_state(),
        _requirement(
            "discrimination-requirement-r2",
            world_snapshot_id="world-2",
        ),
    )

    assert (
        result.decision
        is GovernedInvestigationContinuationDecision.REVIEW_REQUIRED
    )
    assert not result.eligible_for_existing_planning
    assert (
        result.stopping_reason
        is GovernedInvestigationStoppingReason.SNAPSHOT_CONFLICT
    )


def test_source_mismatch_is_review_and_not_planning_eligible() -> None:
    result = GovernedMultiStepInvestigationProductiveContinuationV1().consume(
        _awaiting_requirement_state(),
        _requirement(
            "discrimination-requirement-r2",
            source_reference="scenario-other",
        ),
    )

    assert (
        result.decision
        is GovernedInvestigationContinuationDecision.REVIEW_REQUIRED
    )
    assert not result.eligible_for_existing_planning


def test_missing_requirement_stops_without_planning_eligibility() -> None:
    result = GovernedMultiStepInvestigationProductiveContinuationV1().consume(
        _awaiting_requirement_state(),
        None,
    )

    assert (
        result.decision
        is GovernedInvestigationContinuationDecision.STOP_REQUIRED
    )
    assert not result.eligible_for_existing_planning
    assert result.source_requirement is None
    assert (
        result.stopping_reason
        is GovernedInvestigationStoppingReason.NO_NEW_REQUIREMENT
    )


def test_closed_episode_cannot_be_productively_continued() -> None:
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.manual_stop(_awaiting_requirement_state()).state

    result = GovernedMultiStepInvestigationProductiveContinuationV1(
        boundary
    ).consume(
        state,
        _requirement("discrimination-requirement-r2"),
    )

    assert not result.eligible_for_existing_planning
    assert (
        result.decision
        is GovernedInvestigationContinuationDecision.REVIEW_REQUIRED
    )


def test_productive_surface_never_executes_planning_or_capabilities() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedMultiStepInvestigationProductiveContinuation)
    }
    for name in (
        "planning_execution_authorized",
        "execution_authorized",
        "invokes_planning",
        "invokes_authorization",
        "invokes_capabilities",
        "invokes_reasoning",
        "creates_requirement",
        "rewrites_requirement",
        "creates_questions",
        "modifies_memory",
        "modifies_world_model",
        "starts_background_process",
    ):
        assert defaults[name] is False


def test_productive_surface_does_not_import_or_call_downstream_authorities() -> None:
    source = inspect.getsource(
        GovernedMultiStepInvestigationProductiveContinuationV1
    )
    tree = ast.parse(source)

    for forbidden in (
        "GovernedEvidenceAcquisitionPlanner",
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
                "plan",
                "authorize",
                "reason",
                "run",
                "run_episode",
                "run_next_step",
            }
        )
        for node in ast.walk(tree)
    )
