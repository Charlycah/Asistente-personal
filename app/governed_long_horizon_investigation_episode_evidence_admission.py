from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
)
from app.governed_long_horizon_investigation_continuity import (
    GovernedPassiveInvestigationCheckpoint,
)
from app.governed_long_horizon_investigation_evidence_execution import (
    GovernedInvestigationEvidenceExecutionResult,
    GovernedInvestigationEvidenceExecutionStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationEpisodeTransition,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)


class GovernedInvestigationEpisodeEvidenceAdmissionStatus(StrEnum):
    ADMITTED = "admitted"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationEpisodeEvidenceAdmissionResult:
    thread_id: str
    checkpoint_id: str
    episode_id: str
    originating_reasoning_id: str
    requirement_id: str
    source_reference: str
    world_snapshot_id: str
    status: GovernedInvestigationEpisodeEvidenceAdmissionStatus
    evidence_envelope: GovernedAcquiredEvidenceEnvelope | None
    transition: GovernedInvestigationEpisodeTransition | None
    resulting_episode_state: GovernedInvestigationEpisodeState | None
    rationale_codes: tuple[str, ...]
    eligible_for_existing_reasoning_reentry: bool
    episode_admission_invocation_count: int
    schema_version: str = (
        "post-m409.1-long-horizon-episode-evidence-admission-v1"
    )
    canonical_episode_authority: str = (
        "GovernedMultiStepInvestigationEpisodeBoundaryV1"
    )
    read_only_evidence: bool = True
    establishes_truth: bool = False
    persists_results: bool = False
    invokes_reasoning: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    permits_retry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("episode admission requires rationale codes")
        if self.episode_admission_invocation_count not in {0, 1}:
            raise ValueError("episode admission permits at most one boundary call")
        if self.canonical_episode_authority != (
            "GovernedMultiStepInvestigationEpisodeBoundaryV1"
        ):
            raise ValueError("episode admission must preserve canonical authority")
        if not self.read_only_evidence or any(
            (
                self.establishes_truth,
                self.persists_results,
                self.invokes_reasoning,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError("episode admission operationalizes a later residual")

        admitted = (
            self.status
            is GovernedInvestigationEpisodeEvidenceAdmissionStatus.ADMITTED
        )
        if admitted:
            if self.evidence_envelope is None:
                raise ValueError("admitted evidence must preserve canonical envelope")
            if self.transition is None or self.resulting_episode_state is None:
                raise ValueError("admitted evidence requires canonical transition")
            if self.transition.state is not self.resulting_episode_state:
                raise ValueError("episode admission must preserve transition state")
            if (
                self.transition.decision
                is not GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
            ):
                raise ValueError("admitted evidence requires continue transition")
            if (
                self.resulting_episode_state.status
                is not GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
            ):
                raise ValueError("admitted evidence must await governed reentry")
            if not self.eligible_for_existing_reasoning_reentry:
                raise ValueError("admitted evidence must expose later reentry gate")
            if self.episode_admission_invocation_count != 1:
                raise ValueError("admitted evidence requires one boundary call")
            return

        if self.eligible_for_existing_reasoning_reentry:
            raise ValueError("closed admission cannot enable reasoning reentry")
        if self.transition is not None or self.resulting_episode_state is not None:
            raise ValueError("closed admission cannot expose an episode transition")
        if self.episode_admission_invocation_count != 0:
            raise ValueError("closed admission cannot invoke episode boundary")


class GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1:
    """Admit one acquired envelope through the existing episode boundary."""

    def __init__(
        self,
        episode_boundary: GovernedMultiStepInvestigationEpisodeBoundaryV1 | None = None,
    ) -> None:
        self._episode_boundary = episode_boundary or (
            GovernedMultiStepInvestigationEpisodeBoundaryV1()
        )

    def consume(
        self,
        execution_result: GovernedInvestigationEvidenceExecutionResult,
        checkpoint: GovernedPassiveInvestigationCheckpoint,
    ) -> GovernedInvestigationEpisodeEvidenceAdmissionResult:
        envelope = execution_result.evidence_envelope
        common_lineage = all(
            (
                execution_result.status
                is GovernedInvestigationEvidenceExecutionStatus.ACQUIRED,
                envelope is not None,
                execution_result.checkpoint_id == checkpoint.checkpoint_id,
                execution_result.thread_id == checkpoint.thread_id,
                execution_result.episode_id == checkpoint.episode_id,
                execution_result.originating_reasoning_id
                == checkpoint.originating_reasoning_id,
                execution_result.source_reference == checkpoint.source_reference,
                execution_result.world_snapshot_id == checkpoint.world_snapshot_ids[-1],
                execution_result.requirement_id == checkpoint.requirement_ids[-1],
                envelope is not None
                and envelope.requirement_id == checkpoint.requirement_ids[-1],
                envelope is not None
                and envelope.source_reference == checkpoint.source_reference,
                envelope is not None
                and envelope.world_snapshot_id == checkpoint.world_snapshot_ids[-1],
            )
        )
        if not common_lineage:
            return _closed_result(
                execution_result,
                GovernedInvestigationEpisodeEvidenceAdmissionStatus.NOT_ELIGIBLE,
                (
                    "investigation_episode_admission:lineage_not_eligible",
                    "investigation_episode_admission:boundary_not_invoked",
                ),
            )

        if checkpoint.episode_status is GovernedInvestigationEpisodeStatus.OPEN:
            valid_shape = all(
                (
                    checkpoint.consumed_acquisitions == 0,
                    len(checkpoint.requirement_ids) == 1,
                    not checkpoint.plan_ids,
                    not checkpoint.authorization_ids,
                    not checkpoint.execution_ids,
                    not checkpoint.reentry_ids,
                    checkpoint.stopping_reason
                    is GovernedInvestigationStoppingReason.NONE,
                )
            )
            current_step = 1
        elif (
            checkpoint.episode_status
            is GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING
        ):
            valid_shape = all(
                (
                    checkpoint.consumed_acquisitions == 1,
                    len(checkpoint.requirement_ids) == 2,
                    len(checkpoint.plan_ids) == 1,
                    len(checkpoint.authorization_ids) == 1,
                    len(checkpoint.execution_ids) == 1,
                    len(checkpoint.reentry_ids) == 1,
                    checkpoint.stopping_reason
                    is GovernedInvestigationStoppingReason.NONE,
                )
            )
            current_step = 2
        else:
            valid_shape = False
            current_step = 1

        if not valid_shape:
            return _closed_result(
                execution_result,
                GovernedInvestigationEpisodeEvidenceAdmissionStatus.REVIEW_REQUIRED,
                (
                    "investigation_episode_admission:checkpoint_state_ambiguous",
                    "investigation_episode_admission:fail_closed",
                ),
            )

        try:
            state = GovernedInvestigationEpisodeState(
                episode_id=checkpoint.episode_id,
                originating_reasoning_id=checkpoint.originating_reasoning_id,
                source_reference=checkpoint.source_reference,
                world_snapshot_id=checkpoint.world_snapshot_ids[-1],
                requirement_ids=checkpoint.requirement_ids,
                plan_ids=checkpoint.plan_ids,
                authorization_ids=checkpoint.authorization_ids,
                execution_ids=checkpoint.execution_ids,
                reentry_ids=checkpoint.reentry_ids,
                consumed_acquisitions=checkpoint.consumed_acquisitions,
                current_step=current_step,
                status=checkpoint.episode_status,
                stopping_reason=checkpoint.stopping_reason,
                max_acquisitions=checkpoint.max_acquisitions,
            )
        except (TypeError, ValueError):
            return _closed_result(
                execution_result,
                GovernedInvestigationEpisodeEvidenceAdmissionStatus.REVIEW_REQUIRED,
                (
                    "investigation_episode_admission:checkpoint_projection_invalid",
                    "investigation_episode_admission:fail_closed",
                ),
            )

        assert envelope is not None
        try:
            transition = self._episode_boundary.record_acquisition(
                state,
                execution_result.evidence_envelope,
            )
        except Exception:
            return _closed_result(
                execution_result,
                GovernedInvestigationEpisodeEvidenceAdmissionStatus.REVIEW_REQUIRED,
                (
                    "investigation_episode_admission:boundary_call_failed",
                    "investigation_episode_admission:fail_closed",
                ),
            )

        if not (
            transition.decision
            is GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
            and transition.state.status
            is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
        ):
            return _closed_result(
                execution_result,
                GovernedInvestigationEpisodeEvidenceAdmissionStatus.REVIEW_REQUIRED,
                (
                    "investigation_episode_admission:unexpected_transition",
                    "investigation_episode_admission:fail_closed",
                ),
            )

        return GovernedInvestigationEpisodeEvidenceAdmissionResult(
            thread_id=execution_result.thread_id,
            checkpoint_id=execution_result.checkpoint_id,
            episode_id=execution_result.episode_id,
            originating_reasoning_id=execution_result.originating_reasoning_id,
            requirement_id=execution_result.requirement_id,
            source_reference=execution_result.source_reference,
            world_snapshot_id=execution_result.world_snapshot_id,
            status=GovernedInvestigationEpisodeEvidenceAdmissionStatus.ADMITTED,
            evidence_envelope=execution_result.evidence_envelope,
            transition=transition,
            resulting_episode_state=transition.state,
            rationale_codes=(
                "investigation_episode_admission:existing_boundary_consumed",
                "investigation_episode_admission:awaiting_governed_reentry",
            ),
            eligible_for_existing_reasoning_reentry=True,
            episode_admission_invocation_count=1,
        )


def _closed_result(
    execution_result: GovernedInvestigationEvidenceExecutionResult,
    status: GovernedInvestigationEpisodeEvidenceAdmissionStatus,
    rationale_codes: tuple[str, ...],
) -> GovernedInvestigationEpisodeEvidenceAdmissionResult:
    return GovernedInvestigationEpisodeEvidenceAdmissionResult(
        thread_id=execution_result.thread_id,
        checkpoint_id=execution_result.checkpoint_id,
        episode_id=execution_result.episode_id,
        originating_reasoning_id=execution_result.originating_reasoning_id,
        requirement_id=execution_result.requirement_id,
        source_reference=execution_result.source_reference,
        world_snapshot_id=execution_result.world_snapshot_id,
        status=status,
        evidence_envelope=execution_result.evidence_envelope,
        transition=None,
        resulting_episode_state=None,
        rationale_codes=rationale_codes,
        eligible_for_existing_reasoning_reentry=False,
        episode_admission_invocation_count=0,
    )
