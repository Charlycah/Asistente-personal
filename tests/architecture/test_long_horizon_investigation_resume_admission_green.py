from dataclasses import replace

from app.governed_long_horizon_investigation_continuity import (
    GovernedInvestigationResumeStatus,
    GovernedLongHorizonInvestigationContinuityV1,
)
from app.governed_long_horizon_investigation_resume_admission import (
    GovernedInvestigationResumeAdmissionStatus,
    GovernedLongHorizonInvestigationResumeAdmissionV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

SOURCE = "explanatory-model-source-1"
SNAPSHOT = "world-snapshot-1"
REQUIREMENT_ID = "discrimination-requirement-resume-0001"


def _requirement(
    *,
    requirement_id: str = REQUIREMENT_ID,
    source_reference: str = SOURCE,
    world_snapshot_id: str = SNAPSHOT,
) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id=requirement_id,
        hypothesis_ids=("hypothesis-a", "hypothesis-b"),
        source_reference=source_reference,
        world_snapshot_id=world_snapshot_id,
        known_elements=("known:a",),
        missing_evidence_descriptions=("observe distinguishing evidence",),
        evidence_codes=("evidence:distinguish-a-b",),
    )


def _state() -> GovernedInvestigationEpisodeState:
    return (
        GovernedMultiStepInvestigationEpisodeBoundaryV1()
        .start(
            originating_reasoning_id="reasoning-episode-resume-1",
            source_reference=SOURCE,
            world_snapshot_id=SNAPSHOT,
            initial_requirement_id=REQUIREMENT_ID,
        )
        .state
    )


def _checkpoint_and_resume():
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(
        _state(),
        pause_reason="awaiting_explicit_future_resume",
    )
    resume = continuity.resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="conversation-turn-resume-1",
    )
    return checkpoint, resume


def test_exact_requirement_rebinding_produces_admitted_planning_eligibility():
    checkpoint, resume = _checkpoint_and_resume()
    requirement = _requirement()

    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        resume,
        requirement,
    )

    assert result.status is GovernedInvestigationResumeAdmissionStatus.ADMITTED
    assert result.requirement is requirement
    assert result.requirement_id == requirement.requirement_id
    assert result.checkpoint_id == checkpoint.checkpoint_id
    assert result.resume_id == resume.resume_id
    assert result.thread_id == checkpoint.thread_id
    assert result.episode_id == checkpoint.episode_id
    assert result.originating_reasoning_id == checkpoint.originating_reasoning_id
    assert result.eligible_for_existing_planning is True


def test_admission_is_non_executive_and_non_mutating():
    checkpoint, resume = _checkpoint_and_resume()
    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        resume,
        _requirement(),
    )

    assert result.read_only is True
    assert result.planning_execution_authorized is False
    assert result.creates_plans is False
    assert result.invokes_capabilities is False
    assert result.executes_actions is False
    assert result.performs_reasoning is False
    assert result.persists_results is False
    assert result.modifies_memory is False
    assert result.modifies_world_model is False
    assert result.modifies_planning is False
    assert result.starts_background_process is False
    assert result.grants_authority is False
    assert result.creates_episode is False


def test_checkpoint_lineage_mismatch_fails_closed():
    checkpoint, resume = _checkpoint_and_resume()
    mismatched = replace(
        resume,
        checkpoint_id="investigation-checkpoint-other0000000001",
    )

    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        mismatched,
        _requirement(),
    )

    assert result.status is (
        GovernedInvestigationResumeAdmissionStatus.LINEAGE_MISMATCH
    )
    assert result.eligible_for_existing_planning is False


def test_thread_lineage_mismatch_fails_closed():
    checkpoint, resume = _checkpoint_and_resume()
    mismatched = replace(
        resume,
        thread_id="investigation-thread-other0000000000001",
    )

    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        mismatched,
        _requirement(),
    )

    assert result.status is (
        GovernedInvestigationResumeAdmissionStatus.LINEAGE_MISMATCH
    )


def test_only_current_checkpoint_requirement_can_be_rebound():
    checkpoint, resume = _checkpoint_and_resume()
    other = _requirement(
        requirement_id="discrimination-requirement-other-0002",
    )

    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        resume,
        other,
    )

    assert result.status is (
        GovernedInvestigationResumeAdmissionStatus.REQUIREMENT_MISMATCH
    )
    assert result.eligible_for_existing_planning is False


def test_requirement_source_lineage_mismatch_fails_closed():
    checkpoint, resume = _checkpoint_and_resume()
    other_source = _requirement(source_reference="different-source")

    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        resume,
        other_source,
    )

    assert result.status is (
        GovernedInvestigationResumeAdmissionStatus.LINEAGE_MISMATCH
    )


def test_changed_snapshot_resume_is_review_required_not_admitted():
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(
        _state(),
        pause_reason="awaiting_explicit_future_resume",
    )
    resume = continuity.resume(
        checkpoint,
        current_world_snapshot_id="world-snapshot-2",
        current_source_reference=SOURCE,
        explicit_resume_reference="conversation-turn-resume-2",
    )
    assert resume.status is GovernedInvestigationResumeStatus.SNAPSHOT_REVIEW_REQUIRED

    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        resume,
        _requirement(),
    )

    assert result.status is (GovernedInvestigationResumeAdmissionStatus.REVIEW_REQUIRED)
    assert result.eligible_for_existing_planning is False


def test_same_status_with_tampered_snapshot_still_fails_closed():
    checkpoint, resume = _checkpoint_and_resume()
    tampered = replace(
        resume,
        current_world_snapshot_id="world-snapshot-2",
    )

    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        tampered,
        _requirement(),
    )

    assert result.status is (
        GovernedInvestigationResumeAdmissionStatus.SNAPSHOT_MISMATCH
    )


def test_resolved_inquiry_cannot_be_reactivated_by_requirement_rebinding():
    resolved = replace(
        _state(),
        status=GovernedInvestigationEpisodeStatus.CLOSED,
        stopping_reason=GovernedInvestigationStoppingReason.RESOLVED,
    )
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(
        resolved,
        pause_reason="historical_resolved_checkpoint",
    )
    resume = continuity.resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="conversation-turn-resume-3",
    )

    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        resume,
        _requirement(),
    )

    assert result.status is GovernedInvestigationResumeAdmissionStatus.NOT_ELIGIBLE
    assert result.eligible_for_existing_planning is False


def test_exhausted_budget_cannot_be_reopened_by_admission():
    state = GovernedInvestigationEpisodeState(
        episode_id="investigation-episode-budgetresume000001",
        originating_reasoning_id="reasoning-episode-resume-1",
        source_reference=SOURCE,
        world_snapshot_id=SNAPSHOT,
        requirement_ids=(
            "discrimination-requirement-first-0001",
            REQUIREMENT_ID,
        ),
        plan_ids=("plan-1", "plan-2"),
        authorization_ids=("authorization-1", "authorization-2"),
        execution_ids=("execution-1", "execution-2"),
        reentry_ids=("reentry-1", "reentry-2"),
        consumed_acquisitions=2,
        current_step=2,
        status=GovernedInvestigationEpisodeStatus.CLOSED,
        stopping_reason=GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED,
    )
    continuity = GovernedLongHorizonInvestigationContinuityV1()
    checkpoint = continuity.checkpoint(state, pause_reason="budget_exhausted")
    resume = continuity.resume(
        checkpoint,
        current_world_snapshot_id=SNAPSHOT,
        current_source_reference=SOURCE,
        explicit_resume_reference="conversation-turn-resume-4",
    )

    result = GovernedLongHorizonInvestigationResumeAdmissionV1().admit(
        checkpoint,
        resume,
        _requirement(),
    )

    assert result.status is (
        GovernedInvestigationResumeAdmissionStatus.BUDGET_EXHAUSTED
    )
    assert result.eligible_for_existing_planning is False


def test_admission_is_deterministic_for_identical_explicit_inputs():
    checkpoint, resume = _checkpoint_and_resume()
    requirement = _requirement()
    foundation = GovernedLongHorizonInvestigationResumeAdmissionV1()

    left = foundation.admit(checkpoint, resume, requirement)
    right = foundation.admit(checkpoint, resume, requirement)

    assert left == right
