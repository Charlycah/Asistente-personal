from __future__ import annotations

import inspect
from hashlib import sha256

import pytest

from app.governed_long_horizon_investigation_continuity import (
    GovernedInvestigationResumeStatus,
    GovernedLongHorizonInvestigationContinuityV1,
)
from app.governed_multistep_investigation_episode import (
    GOVERNED_INVESTIGATION_MAX_ACQUISITIONS,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)

REASONING = "reasoning-cap11-green"
SOURCE = "source-cap11-green"
SNAPSHOT = "snapshot-cap11-green"
R1 = "requirement-cap11-green-r1"


def test_green_governed_budget_accepts_only_integer_range_one_through_four():
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    assert GOVERNED_INVESTIGATION_MAX_ACQUISITIONS == 4

    for budget in range(1, GOVERNED_INVESTIGATION_MAX_ACQUISITIONS + 1):
        state = boundary.start(
            originating_reasoning_id=REASONING,
            source_reference=SOURCE,
            world_snapshot_id=SNAPSHOT,
            initial_requirement_id=R1,
            max_acquisitions=budget,
        ).state
        assert state.max_acquisitions == budget

    for invalid in (0, 5, -1, True):
        with pytest.raises(ValueError, match="range 1..4"):
            boundary.start(
                originating_reasoning_id=REASONING,
                source_reference=SOURCE,
                world_snapshot_id=SNAPSHOT,
                initial_requirement_id=R1,
                max_acquisitions=invalid,
            )


def test_green_default_and_explicit_two_preserve_historical_episode_identity():
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    legacy_fingerprint = sha256(
        repr((REASONING, SOURCE, SNAPSHOT, R1)).encode("utf-8")
    ).hexdigest()
    expected = f"investigation-episode-{legacy_fingerprint[:24]}"

    default_state = boundary.start(
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
        max_acquisitions=4,
    ).state

    assert default_state.episode_id == expected
    assert explicit_two.episode_id == expected
    assert explicit_four.episode_id != expected


def test_green_step_three_checkpoint_preserves_exact_constitution():
    state = GovernedInvestigationEpisodeState(
        episode_id="investigation-episode-cap11-green-step3",
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        requirement_ids=(
            R1,
            "requirement-cap11-green-r2",
            "requirement-cap11-green-r3",
        ),
        plan_ids=("plan-cap11-green-1", "plan-cap11-green-2"),
        authorization_ids=("auth-cap11-green-1", "auth-cap11-green-2"),
        execution_ids=("exec-cap11-green-1", "exec-cap11-green-2"),
        reentry_ids=("rr-cap11-green-1", "rr-cap11-green-2"),
        consumed_acquisitions=2,
        current_step=3,
        max_acquisitions=4,
        status=GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
    )
    checkpoint = GovernedLongHorizonInvestigationContinuityV1().checkpoint(
        state,
        pause_reason="cap11 green bounded pause",
    )

    assert checkpoint.current_step == 3
    assert checkpoint.max_acquisitions == 4
    assert checkpoint.consumed_acquisitions == 2
    assert checkpoint.requirement_ids is state.requirement_ids
    assert checkpoint.execution_ids is state.execution_ids


def test_green_step_three_resume_is_passive_and_never_grows_budget():
    state = GovernedInvestigationEpisodeState(
        episode_id="investigation-episode-cap11-green-resume",
        originating_reasoning_id=REASONING,
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        requirement_ids=(
            R1,
            "requirement-cap11-green-r2",
            "requirement-cap11-green-r3",
        ),
        plan_ids=("plan-cap11-green-1", "plan-cap11-green-2"),
        authorization_ids=("auth-cap11-green-1", "auth-cap11-green-2"),
        execution_ids=("exec-cap11-green-1", "exec-cap11-green-2"),
        reentry_ids=("rr-cap11-green-1", "rr-cap11-green-2"),
        consumed_acquisitions=2,
        current_step=3,
        max_acquisitions=4,
        status=GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
    )
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(state, pause_reason="resume later")
    candidate = continuity.resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="cap11-green-resume",
    )

    assert candidate.status is GovernedInvestigationResumeStatus.RESUME_CANDIDATE
    assert checkpoint.max_acquisitions == 4
    assert checkpoint.current_step == 3
    assert not candidate.planning_execution_authorized
    assert not candidate.grants_authority


def test_green_generalization_adds_no_step_three_productive_authority():
    episode_source = inspect.getsource(GovernedMultiStepInvestigationEpisodeBoundaryV1)
    continuity_source = inspect.getsource(GovernedLongHorizonInvestigationContinuityV1)

    assert ".plan(" not in episode_source
    assert ".execute(" not in episode_source
    assert ".reenter(" not in episode_source
    assert ".plan(" not in continuity_source
    assert ".execute(" not in continuity_source
    assert ".reenter(" not in continuity_source
