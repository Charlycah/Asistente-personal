from __future__ import annotations

import inspect
from hashlib import sha256

import pytest

from app import governed_multistep_investigation_episode as episode_module
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_continuity import (
    GovernedInvestigationResumeStatus,
    GovernedLongHorizonInvestigationContinuityV1,
    GovernedPassiveInvestigationCheckpoint,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

SOURCE = "scenario-cap11-nstep"
SNAPSHOT = "world-cap11-nstep"
REASONING = "reasoning-cap11-nstep"
R1 = "discrimination-requirement-r1-cap11-nstep"
R2 = "discrimination-requirement-r2-cap11-nstep"
R3 = "discrimination-requirement-r3-cap11-nstep"
HARD_CAP = 4


def _requirement(requirement_id: str) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id=requirement_id,
        hypothesis_ids=("h1", "h2"),
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("next discriminating evidence",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _state_after_rr2_with_budget_remaining() -> GovernedInvestigationEpisodeState:
    return GovernedInvestigationEpisodeState(
        episode_id="investigation-episode-cap11-nstep-0001",
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        requirement_ids=(R1, R2),
        plan_ids=("plan-r1-cap11", "plan-r2-cap11"),
        authorization_ids=("auth-r1-cap11", "auth-r2-cap11"),
        execution_ids=("execution-r1-cap11", "execution-r2-cap11"),
        reentry_ids=("reentry-r1-cap11", "reentry-r2-cap11"),
        consumed_acquisitions=2,
        current_step=2,
        status=GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT,
        max_acquisitions=HARD_CAP,
    )


def _state_awaiting_second_reentry_with_budget_remaining():
    return GovernedInvestigationEpisodeState(
        episode_id="investigation-episode-cap11-nstep-0002",
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        requirement_ids=(R1, R2),
        plan_ids=("plan-r1-cap11", "plan-r2-cap11"),
        authorization_ids=("auth-r1-cap11", "auth-r2-cap11"),
        execution_ids=("execution-r1-cap11", "execution-r2-cap11"),
        reentry_ids=("reentry-r1-cap11",),
        consumed_acquisitions=2,
        current_step=2,
        status=GovernedInvestigationEpisodeStatus.AWAITING_REENTRY,
        max_acquisitions=HARD_CAP,
    )


def _rr2() -> GovernedLevel2ReasoningReentryResult:
    return GovernedLevel2ReasoningReentryResult(
        reentry_id="level2-reasoning-reentry-r2-cap11-nstep",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id="execution-r2-cap11",
        authorization_id="auth-r2-cap11",
        requirement_id=R2,
        plan_id="plan-r2-cap11",
        capability_name="local.sensor",
        evidence_id="evidence-r2-cap11",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        reasoning_result=None,
        rationale_codes=("reentry:cap11-nstep",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )


def test_red_constitution_declares_finite_hard_cap_four():
    assert episode_module.GOVERNED_INVESTIGATION_MAX_ACQUISITIONS == HARD_CAP


def test_red_start_accepts_explicit_budget_and_preserves_legacy_identity():
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    signature = inspect.signature(boundary.start)
    parameter = signature.parameters["max_acquisitions"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default == 2

    historical = boundary.start(
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id=R1,
    ).state
    explicit_two = boundary.start(
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id=R1,
        max_acquisitions=2,
    ).state
    explicit_four = boundary.start(
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        initial_requirement_id=R1,
        max_acquisitions=HARD_CAP,
    ).state

    assert explicit_two.episode_id == historical.episode_id
    assert explicit_four.episode_id != historical.episode_id
    assert explicit_four.max_acquisitions == HARD_CAP
    assert explicit_four.current_step == 1


def test_red_state_accepts_step_three_within_budget_and_rejects_out_of_range():
    state = GovernedInvestigationEpisodeState(
        episode_id="investigation-episode-cap11-nstep-0003",
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        requirement_ids=(R1, R2, R3),
        plan_ids=("plan-r1-cap11", "plan-r2-cap11"),
        authorization_ids=("auth-r1-cap11", "auth-r2-cap11"),
        execution_ids=("execution-r1-cap11", "execution-r2-cap11"),
        reentry_ids=("reentry-r1-cap11", "reentry-r2-cap11"),
        consumed_acquisitions=2,
        current_step=3,
        status=GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
        max_acquisitions=HARD_CAP,
    )
    assert state.current_step == 3
    assert state.remaining_acquisitions == 2

    with pytest.raises(ValueError):
        GovernedInvestigationEpisodeState(
            episode_id="investigation-episode-cap11-nstep-over-cap",
            originating_reasoning_id=REASONING,
            source_reference=SOURCE,
            world_snapshot_id=SNAPSHOT,
            requirement_ids=(R1,),
            current_step=1,
            max_acquisitions=HARD_CAP + 1,
        )


def test_red_second_reentry_does_not_close_when_generalized_budget_remains():
    transition = GovernedMultiStepInvestigationEpisodeBoundaryV1().record_reentry(
        _state_awaiting_second_reentry_with_budget_remaining(),
        _rr2(),
    )
    assert transition.decision is (
        GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
    )
    assert transition.state.status is (
        GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
    )
    assert transition.state.stopping_reason is GovernedInvestigationStoppingReason.NONE
    assert transition.state.current_step == 2
    assert transition.state.remaining_acquisitions == 2


def test_red_continuation_advances_exactly_one_step_without_invoking_planning():
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    transition = boundary.evaluate_continuation(
        _state_after_rr2_with_budget_remaining(),
        _requirement(R3),
    )
    assert transition.decision is (
        GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
    )
    assert transition.state.status is (
        GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING
    )
    assert transition.state.current_step == 3
    assert transition.state.requirement_ids == (R1, R2, R3)
    assert transition.state.max_acquisitions == HARD_CAP
    assert not transition.state.planning_execution_authorized
    source = inspect.getsource(boundary.evaluate_continuation)
    assert ".plan(" not in source


def test_red_checkpoint_carries_exact_current_step_and_budget_in_fingerprint():
    annotations = inspect.get_annotations(GovernedPassiveInvestigationCheckpoint)
    assert annotations["current_step"] is int
    source = inspect.getsource(GovernedLongHorizonInvestigationContinuityV1.checkpoint)
    assert "state.current_step" in source
    assert "current_step=state.current_step" in source

    state = _state_after_rr2_with_budget_remaining()
    checkpoint = GovernedLongHorizonInvestigationContinuityV1().checkpoint(
        state,
        pause_reason="explicit bounded pause",
    )
    assert checkpoint.current_step == state.current_step
    assert checkpoint.max_acquisitions == state.max_acquisitions
    assert checkpoint.consumed_acquisitions == state.consumed_acquisitions


def test_red_resume_accepts_nonexhausted_step_three_checkpoint_without_budget_growth():
    checkpoint = GovernedPassiveInvestigationCheckpoint(
        checkpoint_id="investigation-checkpoint-cap11-nstep-0001",
        thread_id="investigation-thread-cap11-nstep-0001",
        episode_id="investigation-episode-cap11-nstep-0004",
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_ids=(SNAPSHOT,),
        requirement_ids=(R1, R2, R3),
        plan_ids=("plan-r1-cap11", "plan-r2-cap11"),
        authorization_ids=("auth-r1-cap11", "auth-r2-cap11"),
        execution_ids=("execution-r1-cap11", "execution-r2-cap11"),
        reentry_ids=("reentry-r1-cap11", "reentry-r2-cap11"),
        consumed_acquisitions=2,
        current_step=3,
        max_acquisitions=HARD_CAP,
        episode_status=GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
        stopping_reason=GovernedInvestigationStoppingReason.NONE,
        pause_reason="pause before step three planning",
        source_fingerprint="f" * 64,
    )
    candidate = GovernedLongHorizonInvestigationContinuityV1().resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="resume-cap11-step-three",
    )
    assert candidate.status is GovernedInvestigationResumeStatus.RESUME_CANDIDATE
    assert checkpoint.max_acquisitions == HARD_CAP
    assert checkpoint.current_step == 3


def test_red_exhausted_generalized_checkpoint_still_requires_budget_review():
    checkpoint = GovernedPassiveInvestigationCheckpoint(
        checkpoint_id="investigation-checkpoint-cap11-nstep-0002",
        thread_id="investigation-thread-cap11-nstep-0002",
        episode_id="investigation-episode-cap11-nstep-0005",
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_ids=(SNAPSHOT,),
        requirement_ids=(R1, R2, R3, "discrimination-requirement-r4-cap11-nstep"),
        plan_ids=("p1", "p2", "p3", "p4"),
        authorization_ids=("a1", "a2", "a3", "a4"),
        execution_ids=("e1", "e2", "e3", "e4"),
        reentry_ids=("rr1", "rr2", "rr3", "rr4"),
        consumed_acquisitions=HARD_CAP,
        current_step=HARD_CAP,
        max_acquisitions=HARD_CAP,
        episode_status=GovernedInvestigationEpisodeStatus.CLOSED,
        stopping_reason=GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED,
        pause_reason="terminal checkpoint",
        source_fingerprint="a" * 64,
    )
    candidate = GovernedLongHorizonInvestigationContinuityV1().resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="resume-exhausted-cap11",
    )
    assert candidate.status is GovernedInvestigationResumeStatus.BUDGET_REVIEW_REQUIRED
    assert checkpoint.max_acquisitions == HARD_CAP


def test_legacy_two_acquisition_start_identity_and_default_remain_unchanged():
    fingerprint = sha256(
        repr((REASONING, SOURCE, SNAPSHOT, R1)).encode("utf-8")
    ).hexdigest()
    expected_episode_id = f"investigation-episode-{fingerprint[:24]}"
    state = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1()
        .start(
            originating_reasoning_id=REASONING,
            source_reference=SOURCE,
            world_snapshot_id=SNAPSHOT,
            initial_requirement_id=R1,
        )
        .state
    )
    assert state.episode_id == expected_episode_id
    assert state.max_acquisitions == 2
    assert state.current_step == 1
    assert state.remaining_acquisitions == 2
