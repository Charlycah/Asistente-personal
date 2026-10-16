from __future__ import annotations

from dataclasses import replace

import pytest

from app.governed_long_horizon_investigation_continuity import (
    GovernedInvestigationResumeStatus,
    GovernedLongHorizonInvestigationContinuityV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)

SOURCE = "explanatory-model-source-1"
SNAPSHOT = "world-snapshot-1"


def _open_state() -> GovernedInvestigationEpisodeState:
    return (
        GovernedMultiStepInvestigationEpisodeBoundaryV1()
        .start(
            originating_reasoning_id="reasoning-episode-1",
            source_reference=SOURCE,
            world_snapshot_id=SNAPSHOT,
            initial_requirement_id="requirement-1",
        )
        .state
    )


def _budget_exhausted_state() -> GovernedInvestigationEpisodeState:
    return GovernedInvestigationEpisodeState(
        episode_id="investigation-episode-budget000000000001",
        originating_reasoning_id="reasoning-episode-1",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        requirement_ids=("requirement-1", "requirement-2"),
        plan_ids=("plan-1", "plan-2"),
        authorization_ids=("authorization-1", "authorization-2"),
        execution_ids=("execution-1", "execution-2"),
        reentry_ids=("reentry-1", "reentry-2"),
        consumed_acquisitions=2,
        current_step=2,
        status=GovernedInvestigationEpisodeStatus.CLOSED,
        stopping_reason=GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED,
    )


def test_episode_state_produces_passive_checkpoint_with_full_lineage():
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    state = _open_state()
    checkpoint = continuity.checkpoint(
        state,
        pause_reason="awaiting_future_evidence",
    )

    assert checkpoint.episode_id == state.episode_id
    assert checkpoint.originating_reasoning_id == state.originating_reasoning_id
    assert checkpoint.source_reference == state.source_reference
    assert checkpoint.world_snapshot_ids == (state.world_snapshot_id,)
    assert checkpoint.requirement_ids == state.requirement_ids
    assert checkpoint.plan_ids == state.plan_ids
    assert checkpoint.authorization_ids == state.authorization_ids
    assert checkpoint.execution_ids == state.execution_ids
    assert checkpoint.reentry_ids == state.reentry_ids
    assert checkpoint.consumed_acquisitions == state.consumed_acquisitions
    assert checkpoint.max_acquisitions == 2
    assert checkpoint.pause_reason == "awaiting_future_evidence"


def test_checkpoint_is_durable_artifact_but_never_self_persists_or_runs():
    checkpoint = GovernedLongHorizonInvestigationContinuityV1().checkpoint(
        _open_state(),
        pause_reason="deferred",
    )

    assert checkpoint.read_only is True
    assert checkpoint.passive is True
    assert checkpoint.durable_artifact is True
    assert checkpoint.persists_self is False
    assert checkpoint.starts_background_process is False
    assert checkpoint.invokes_capabilities is False
    assert checkpoint.executes_actions is False
    assert checkpoint.modifies_memory is False
    assert checkpoint.modifies_world_model is False
    assert checkpoint.modifies_planning is False
    assert checkpoint.performs_reasoning is False
    assert checkpoint.grants_authority is False


def test_checkpoint_requires_explicit_pause_reason():
    with pytest.raises(ValueError, match="explicit pause reason"):
        GovernedLongHorizonInvestigationContinuityV1().checkpoint(
            _open_state(),
            pause_reason="   ",
        )


def test_same_snapshot_explicit_resume_produces_candidate_only():
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(
        _open_state(),
        pause_reason="awaiting_future_evidence",
    )
    candidate = continuity.resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="conversation-turn-22",
    )

    assert candidate.status is GovernedInvestigationResumeStatus.RESUME_CANDIDATE
    assert candidate.previous_world_snapshot_id == SNAPSHOT
    assert candidate.current_world_snapshot_id == SNAPSHOT
    assert candidate.checkpoint_id == checkpoint.checkpoint_id
    assert candidate.thread_id == checkpoint.thread_id
    assert candidate.planning_execution_authorized is False
    assert candidate.modifies_planning is False
    assert candidate.performs_reasoning is False


def test_changed_snapshot_requires_review_and_preserves_both_snapshots():
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(
        _open_state(),
        pause_reason="awaiting_future_evidence",
    )
    candidate = continuity.resume(
        checkpoint,
        current_world_snapshot_id="world-snapshot-2",
        current_source_reference=SOURCE,
        explicit_resume_reference="conversation-turn-23",
    )

    assert candidate.status is (
        GovernedInvestigationResumeStatus.SNAPSHOT_REVIEW_REQUIRED
    )
    assert candidate.previous_world_snapshot_id == SNAPSHOT
    assert candidate.current_world_snapshot_id == "world-snapshot-2"
    assert "investigation_resume:previous_snapshot_preserved" in (
        candidate.rationale_codes
    )


def test_source_lineage_mismatch_fails_closed():
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(
        _open_state(),
        pause_reason="deferred",
    )
    candidate = continuity.resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference="different-source",
        explicit_resume_reference="conversation-turn-24",
    )

    assert candidate.status is (
        GovernedInvestigationResumeStatus.SOURCE_LINEAGE_MISMATCH
    )
    assert "investigation_resume:fail_closed" in candidate.rationale_codes


def test_resolved_inquiry_is_not_silently_reactivated():
    resolved = replace(
        _open_state(),
        status=GovernedInvestigationEpisodeStatus.CLOSED,
        stopping_reason=GovernedInvestigationStoppingReason.RESOLVED,
    )
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(
        resolved,
        pause_reason="historical_checkpoint",
    )
    candidate = continuity.resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="conversation-turn-25",
    )

    assert candidate.status is GovernedInvestigationResumeStatus.RESOLVED_INQUIRY
    assert "investigation_resume:resolved_requirement_not_reactivated" in (
        candidate.rationale_codes
    )


def test_exhausted_short_horizon_budget_requires_separate_review():
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(
        _budget_exhausted_state(),
        pause_reason="budget_exhausted",
    )
    candidate = continuity.resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="conversation-turn-26",
    )

    assert candidate.status is (
        GovernedInvestigationResumeStatus.BUDGET_REVIEW_REQUIRED
    )
    assert checkpoint.max_acquisitions == 2
    assert "investigation_resume:additional_budget_requires_separate_governance" in (
        candidate.rationale_codes
    )


def test_resume_requires_explicit_reference_and_never_becomes_background():
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(
        _open_state(),
        pause_reason="deferred",
    )

    with pytest.raises(ValueError, match="explicit resume reference"):
        continuity.resume(
            checkpoint,
            current_world_snapshot_id=SNAPSHOT,
            current_source_reference=SOURCE,
            explicit_resume_reference=" ",
        )

    candidate = continuity.resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="manual-resume",
    )
    assert candidate.starts_background_process is False
    assert candidate.invokes_capabilities is False
    assert candidate.executes_actions is False
    assert candidate.persists_results is False
    assert candidate.modifies_memory is False
    assert candidate.modifies_world_model is False
    assert candidate.grants_authority is False


def test_checkpoint_and_resume_are_deterministic_for_same_inputs():
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    state = _open_state()

    left = continuity.checkpoint(state, pause_reason="deferred")
    right = continuity.checkpoint(state, pause_reason="deferred")
    assert left == right

    resume_left = continuity.resume(
        left,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="manual-resume",
    )
    resume_right = continuity.resume(
        right,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="manual-resume",
    )
    assert resume_left == resume_right
