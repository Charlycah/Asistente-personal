from __future__ import annotations

from dataclasses import fields
from types import SimpleNamespace

import pytest

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
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.planning_foundation import PlanningFoundation
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


def _boundary() -> GovernedMultiStepInvestigationEpisodeBoundaryV1:
    return GovernedMultiStepInvestigationEpisodeBoundaryV1(PlanningFoundation())


def _start():
    return _boundary().start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        initial_requirement_id="discrimination-requirement-r1",
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


def _envelope(
    step: int,
    *,
    status: GovernedLevel2ExecutionStatus = GovernedLevel2ExecutionStatus.ACQUIRED,
    requirement_id: str | None = None,
    world_snapshot_id: str = "world-1",
) -> GovernedAcquiredEvidenceEnvelope:
    acquired = status is GovernedLevel2ExecutionStatus.ACQUIRED
    rid = requirement_id or f"discrimination-requirement-r{step}"
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=f"level2-read-only-execution-step-{step:02d}-abcdef123456",
        status=status,
        authorization_id=(
            f"independence-authorization-step-{step:02d}-abcdef123456"
        ),
        requirement_id=rid,
        plan_id=f"evidence-acquisition-plan-step-{step:02d}-abcdef123456",
        capability_name="local.sensor" if acquired else None,
        evidence_description="room temperature" if acquired else None,
        declared_evidence_output="room_temperature" if acquired else None,
        observed_value=22.0 + step if acquired else None,
        observation_source_reference="local:test-reader" if acquired else None,
        source_reference="scenario-123",
        world_snapshot_id=world_snapshot_id,
        rationale_codes=("execution:test",),
        source_fingerprint="f" * 64,
    )


def _reentry(
    step: int,
    *,
    requirement_id: str | None = None,
    world_snapshot_id: str = "world-1",
) -> GovernedLevel2ReasoningReentryResult:
    envelope = _envelope(
        step,
        requirement_id=requirement_id,
        world_snapshot_id=world_snapshot_id,
    )
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


def _after_first_reentry():
    boundary = _boundary()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, _envelope(1)).state
    state = boundary.record_reentry(state, _reentry(1)).state
    return boundary, state


def test_episode_starts_under_existing_planning_authority_with_fixed_budget() -> None:
    transition = _start()
    state = transition.state

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
    )
    assert state.canonical_planning_authority == "planning_foundation"
    assert state.max_acquisitions == 2
    assert state.consumed_acquisitions == 0
    assert state.remaining_acquisitions == 2
    assert not state.planning_execution_authorized


def test_first_acquisition_consumes_exactly_one_budget_slot() -> None:
    boundary = _boundary()
    state = _start().state

    transition = boundary.record_acquisition(state, _envelope(1))

    assert transition.state.consumed_acquisitions == 1
    assert transition.state.remaining_acquisitions == 1
    assert (
        transition.state.status
        is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
    )
    assert transition.state.execution_ids == (_envelope(1).execution_id,)


def test_first_reentry_does_not_consume_second_acquisition_slot() -> None:
    boundary = _boundary()
    state = _start().state
    state = boundary.record_acquisition(state, _envelope(1)).state

    transition = boundary.record_reentry(state, _reentry(1))

    assert transition.state.consumed_acquisitions == 1
    assert transition.state.remaining_acquisitions == 1
    assert (
        transition.state.status
        is GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
    )


def test_new_requirement_allows_only_reentry_to_existing_planning() -> None:
    boundary, state = _after_first_reentry()

    transition = boundary.evaluate_continuation(
        state,
        _requirement("discrimination-requirement-r2"),
    )

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
    )
    assert transition.state.current_step == 2
    assert (
        transition.state.status
        is GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING
    )
    assert transition.state.requirement_ids == (
        "discrimination-requirement-r1",
        "discrimination-requirement-r2",
    )
    assert not transition.state.planning_execution_authorized


def test_second_acquisition_and_reentry_close_episode_at_budget_two() -> None:
    boundary, state = _after_first_reentry()
    state = boundary.evaluate_continuation(
        state,
        _requirement("discrimination-requirement-r2"),
    ).state
    state = boundary.record_acquisition(state, _envelope(2)).state

    transition = boundary.record_reentry(state, _reentry(2))

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.STOP_REQUIRED
    )
    assert transition.state.consumed_acquisitions == 2
    assert transition.state.remaining_acquisitions == 0
    assert transition.state.status is GovernedInvestigationEpisodeStatus.CLOSED
    assert (
        transition.state.stopping_reason
        is GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
    )


def test_requirement_reuse_for_second_step_is_rejected() -> None:
    boundary, state = _after_first_reentry()

    transition = boundary.evaluate_continuation(
        state,
        _requirement("discrimination-requirement-r1"),
    )

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.REVIEW_REQUIRED
    )
    assert transition.state.status is GovernedInvestigationEpisodeStatus.REVIEW_REQUIRED


def test_snapshot_change_for_second_requirement_is_rejected() -> None:
    boundary, state = _after_first_reentry()

    transition = boundary.evaluate_continuation(
        state,
        _requirement(
            "discrimination-requirement-r2",
            world_snapshot_id="world-2",
        ),
    )

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.REVIEW_REQUIRED
    )
    assert (
        transition.state.stopping_reason
        is GovernedInvestigationStoppingReason.SNAPSHOT_CONFLICT
    )


@pytest.mark.parametrize(
    ("status", "reason"),
    (
        (
            GovernedLevel2ExecutionStatus.UNAVAILABLE,
            GovernedInvestigationStoppingReason.ACQUISITION_UNAVAILABLE,
        ),
        (
            GovernedLevel2ExecutionStatus.FAILED,
            GovernedInvestigationStoppingReason.ACQUISITION_FAILED,
        ),
    ),
)
def test_non_acquired_second_execution_stops_without_consuming_remaining_budget(
    status: GovernedLevel2ExecutionStatus,
    reason: GovernedInvestigationStoppingReason,
) -> None:
    boundary, state = _after_first_reentry()
    state = boundary.evaluate_continuation(
        state,
        _requirement("discrimination-requirement-r2"),
    ).state

    transition = boundary.record_acquisition(
        state,
        _envelope(2, status=status),
    )

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.STOP_REQUIRED
    )
    assert transition.state.consumed_acquisitions == 1
    assert transition.state.remaining_acquisitions == 1
    assert transition.state.stopping_reason is reason


def test_reusing_first_plan_or_authorization_lineage_is_rejected() -> None:
    boundary, state = _after_first_reentry()
    state = boundary.evaluate_continuation(
        state,
        _requirement("discrimination-requirement-r2"),
    ).state
    first = _envelope(1)
    second = _envelope(2)
    forged = GovernedAcquiredEvidenceEnvelope(
        execution_id=second.execution_id,
        status=second.status,
        authorization_id=first.authorization_id,
        requirement_id=second.requirement_id,
        plan_id=first.plan_id,
        capability_name=second.capability_name,
        evidence_description=second.evidence_description,
        declared_evidence_output=second.declared_evidence_output,
        observed_value=second.observed_value,
        observation_source_reference=second.observation_source_reference,
        source_reference=second.source_reference,
        world_snapshot_id=second.world_snapshot_id,
        rationale_codes=second.rationale_codes,
        source_fingerprint=second.source_fingerprint,
    )

    transition = boundary.record_acquisition(state, forged)

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.REVIEW_REQUIRED
    )
    assert (
        transition.state.stopping_reason
        is GovernedInvestigationStoppingReason.LINEAGE_BROKEN
    )


@pytest.mark.parametrize(
    "decision",
    (
        GovernedInitiationDecision.MUST_ASK,
        GovernedInitiationDecision.MUST_ABSTAIN,
    ),
)
def test_non_authorized_continuation_closes_level2_episode(
    decision: GovernedInitiationDecision,
) -> None:
    boundary, state = _after_first_reentry()
    state = boundary.evaluate_continuation(
        state,
        _requirement("discrimination-requirement-r2"),
    ).state
    authorization = SimpleNamespace(
        requirement_id=state.current_requirement_id,
        source_reference=state.source_reference,
        world_snapshot_id=state.world_snapshot_id,
        decision=decision,
    )

    transition = boundary.record_authorization_stop(state, authorization)

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.STOP_REQUIRED
    )
    assert (
        transition.state.stopping_reason
        is GovernedInvestigationStoppingReason.NOT_AUTHORIZED
    )


def test_no_new_requirement_closes_without_second_acquisition() -> None:
    boundary, state = _after_first_reentry()

    transition = boundary.evaluate_continuation(state, None)

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.STOP_REQUIRED
    )
    assert transition.state.consumed_acquisitions == 1
    assert (
        transition.state.stopping_reason
        is GovernedInvestigationStoppingReason.NO_NEW_REQUIREMENT
    )


def test_manual_stop_is_terminal_without_execution() -> None:
    boundary, state = _after_first_reentry()

    transition = boundary.manual_stop(state)

    assert (
        transition.decision
        is GovernedInvestigationContinuationDecision.STOP_REQUIRED
    )
    assert transition.state.status is GovernedInvestigationEpisodeStatus.CLOSED
    assert (
        transition.state.stopping_reason
        is GovernedInvestigationStoppingReason.MANUAL_STOP
    )


def test_budget_cannot_exceed_governed_hard_cap_in_foundation_v1() -> None:
    with pytest.raises(ValueError, match="range 1..4"):
        GovernedInvestigationEpisodeState(
            episode_id="investigation-episode-1234567890abcdef12345678",
            originating_reasoning_id="reasoning-1",
            source_reference="scenario-123",
            world_snapshot_id="world-1",
            requirement_ids=("discrimination-requirement-r1",),
            max_acquisitions=5,
        )


def test_episode_contract_has_no_execution_reasoning_or_persistence_authority() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedInvestigationEpisodeState)
    }
    for name in (
        "planning_execution_authorized",
        "persists_results",
        "invokes_capabilities",
        "performs_reasoning",
        "creates_questions",
        "modifies_memory",
        "modifies_world_model",
        "starts_background_process",
    ):
        assert defaults[name] is False


def test_boundary_has_no_loop_runner_or_execution_method() -> None:
    names = set(dir(GovernedMultiStepInvestigationEpisodeBoundaryV1))

    assert "run" not in names
    assert "execute" not in names
    assert "plan" not in names
    assert "authorize" not in names
    assert "run_episode" not in names
    assert "run_next_step" not in names
