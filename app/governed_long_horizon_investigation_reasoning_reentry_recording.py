from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryFoundationV1,
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_episode_evidence_admission import (
    GovernedInvestigationEpisodeEvidenceAdmissionResult,
    GovernedInvestigationEpisodeEvidenceAdmissionStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationEpisodeTransition,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)


class GovernedInvestigationReasoningReentryRecordingStatus(StrEnum):
    RECORDED_CONTINUATION = "recorded_continuation"
    RECORDED_CLOSED = "recorded_closed"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationReasoningReentryRecordingResult:
    thread_id: str
    checkpoint_id: str
    episode_id: str
    originating_reasoning_id: str
    execution_id: str | None
    authorization_id: str | None
    requirement_id: str
    plan_id: str | None
    source_reference: str
    world_snapshot_id: str
    status: GovernedInvestigationReasoningReentryRecordingStatus
    reasoning_reentry: GovernedLevel2ReasoningReentryResult | None
    transition: GovernedInvestigationEpisodeTransition | None
    resulting_episode_state: GovernedInvestigationEpisodeState | None
    rationale_codes: tuple[str, ...]
    reasoning_reentry_invocation_count: int
    episode_record_invocation_count: int
    schema_version: str = "post-m409.1-long-horizon-reentry-recording-v1"
    canonical_reasoning_authority: str = "governed_reasoning"
    canonical_episode_authority: str = (
        "GovernedMultiStepInvestigationEpisodeBoundaryV1"
    )
    establishes_truth: bool = False
    persists_results: bool = False
    creates_requirements: bool = False
    invokes_planning: bool = False
    invokes_execution: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    permits_retry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("reentry recording requires rationale codes")
        if self.reasoning_reentry_invocation_count not in {0, 1}:
            raise ValueError("reentry recording permits at most one reasoning call")
        if self.episode_record_invocation_count not in {0, 1}:
            raise ValueError("reentry recording permits at most one episode call")
        if self.canonical_reasoning_authority != "governed_reasoning":
            raise ValueError("reentry recording must preserve reasoning authority")
        if self.canonical_episode_authority != (
            "GovernedMultiStepInvestigationEpisodeBoundaryV1"
        ):
            raise ValueError("reentry recording must preserve episode authority")
        if any(
            (
                self.establishes_truth,
                self.persists_results,
                self.creates_requirements,
                self.invokes_planning,
                self.invokes_execution,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError("reentry recording operationalizes a later residual")

        recorded = self.status in {
            GovernedInvestigationReasoningReentryRecordingStatus.RECORDED_CONTINUATION,
            GovernedInvestigationReasoningReentryRecordingStatus.RECORDED_CLOSED,
        }
        if recorded:
            if self.reasoning_reentry is None or self.transition is None:
                raise ValueError("recorded reentry requires canonical products")
            if self.resulting_episode_state is not self.transition.state:
                raise ValueError("recorded reentry must preserve transition state")
            if self.reasoning_reentry_invocation_count != 1:
                raise ValueError("recorded reentry requires one reasoning call")
            if self.episode_record_invocation_count != 1:
                raise ValueError("recorded reentry requires one episode call")
        elif self.transition is not None or self.resulting_episode_state is not None:
            raise ValueError("closed bridge result cannot expose episode transition")


class GovernedLongHorizonInvestigationReasoningReentryRecordingV1:
    """Reenter canonical reasoning once, then record that exact reentry once."""

    def __init__(
        self,
        reasoning_reentry: GovernedLevel2ReasoningReentryFoundationV1,
        episode_boundary: GovernedMultiStepInvestigationEpisodeBoundaryV1 | None = None,
    ) -> None:
        self._reasoning_reentry = reasoning_reentry
        self._episode_boundary = episode_boundary or (
            GovernedMultiStepInvestigationEpisodeBoundaryV1()
        )

    def consume(
        self,
        admission: GovernedInvestigationEpisodeEvidenceAdmissionResult,
        *,
        now: datetime,
    ) -> GovernedInvestigationReasoningReentryRecordingResult:
        envelope = admission.evidence_envelope
        state = admission.resulting_episode_state
        eligible = all(
            (
                admission.status
                is GovernedInvestigationEpisodeEvidenceAdmissionStatus.ADMITTED,
                admission.eligible_for_existing_reasoning_reentry,
                envelope is not None,
                state is not None,
                state is admission.resulting_episode_state,
                state is not None
                and state.status
                is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY,
                state is not None and state.episode_id == admission.episode_id,
                state is not None
                and state.originating_reasoning_id
                == admission.originating_reasoning_id,
                state is not None
                and state.current_requirement_id == admission.requirement_id,
                state is not None
                and state.source_reference == admission.source_reference,
                state is not None
                and state.world_snapshot_id == admission.world_snapshot_id,
                envelope is not None
                and envelope.requirement_id == admission.requirement_id,
                envelope is not None
                and envelope.source_reference == admission.source_reference,
                envelope is not None
                and envelope.world_snapshot_id == admission.world_snapshot_id,
                state is not None
                and envelope is not None
                and bool(state.execution_ids)
                and state.execution_ids[-1] == envelope.execution_id,
                state is not None
                and envelope is not None
                and bool(state.authorization_ids)
                and state.authorization_ids[-1] == envelope.authorization_id,
                state is not None
                and envelope is not None
                and bool(state.plan_ids)
                and state.plan_ids[-1] == envelope.plan_id,
            )
        )
        if not eligible:
            return self._closed(
                admission,
                GovernedInvestigationReasoningReentryRecordingStatus.NOT_ELIGIBLE,
                ("investigation_reentry_recording:admission_not_eligible",),
                reasoning_calls=0,
            )

        assert envelope is not None
        assert state is not None
        try:
            reasoning_reentry = self._reasoning_reentry.reenter(
                admission.evidence_envelope,
                now=now,
            )
        except Exception:
            return self._closed(
                admission,
                GovernedInvestigationReasoningReentryRecordingStatus.REVIEW_REQUIRED,
                ("investigation_reentry_recording:reasoning_reentry_failed",),
                reasoning_calls=1,
            )

        exact_lineage = all(
            (
                reasoning_reentry.status is GovernedReasoningReentryStatus.REEVALUATED,
                reasoning_reentry.execution_id == envelope.execution_id,
                reasoning_reentry.authorization_id == envelope.authorization_id,
                reasoning_reentry.requirement_id == admission.requirement_id,
                reasoning_reentry.plan_id == envelope.plan_id,
                reasoning_reentry.source_reference == admission.source_reference,
                reasoning_reentry.world_snapshot_id == admission.world_snapshot_id,
            )
        )
        if not exact_lineage:
            return self._closed(
                admission,
                GovernedInvestigationReasoningReentryRecordingStatus.REVIEW_REQUIRED,
                ("investigation_reentry_recording:reentry_lineage_invalid",),
                reasoning_calls=1,
            )

        try:
            transition = self._episode_boundary.record_reentry(
                admission.resulting_episode_state,
                reasoning_reentry,
            )
        except Exception:
            return self._closed(
                admission,
                GovernedInvestigationReasoningReentryRecordingStatus.REVIEW_REQUIRED,
                ("investigation_reentry_recording:episode_record_failed",),
                reasoning_calls=1,
            )

        if (
            transition.decision
            is GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
            and transition.state.status
            is GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
            and transition.state.stopping_reason
            is GovernedInvestigationStoppingReason.NONE
        ):
            status = (
                GovernedInvestigationReasoningReentryRecordingStatus
                .RECORDED_CONTINUATION
            )
        elif (
            transition.decision
            is GovernedInvestigationContinuationDecision.STOP_REQUIRED
            and transition.state.status is GovernedInvestigationEpisodeStatus.CLOSED
            and transition.state.stopping_reason
            is GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
        ):
            status = (
                GovernedInvestigationReasoningReentryRecordingStatus.RECORDED_CLOSED
            )
        else:
            return self._closed(
                admission,
                GovernedInvestigationReasoningReentryRecordingStatus.REVIEW_REQUIRED,
                ("investigation_reentry_recording:unexpected_episode_transition",),
                reasoning_calls=1,
            )

        return GovernedInvestigationReasoningReentryRecordingResult(
            thread_id=admission.thread_id,
            checkpoint_id=admission.checkpoint_id,
            episode_id=admission.episode_id,
            originating_reasoning_id=admission.originating_reasoning_id,
            execution_id=envelope.execution_id,
            authorization_id=envelope.authorization_id,
            requirement_id=admission.requirement_id,
            plan_id=envelope.plan_id,
            source_reference=admission.source_reference,
            world_snapshot_id=admission.world_snapshot_id,
            status=status,
            reasoning_reentry=reasoning_reentry,
            transition=transition,
            resulting_episode_state=transition.state,
            rationale_codes=(
                "investigation_reentry_recording:canonical_reentry_recorded",
                *transition.rationale_codes,
            ),
            reasoning_reentry_invocation_count=1,
            episode_record_invocation_count=1,
        )

    @staticmethod
    def _closed(
        admission: GovernedInvestigationEpisodeEvidenceAdmissionResult,
        status: GovernedInvestigationReasoningReentryRecordingStatus,
        rationale_codes: tuple[str, ...],
        *,
        reasoning_calls: int,
    ) -> GovernedInvestigationReasoningReentryRecordingResult:
        envelope = admission.evidence_envelope
        return GovernedInvestigationReasoningReentryRecordingResult(
            thread_id=admission.thread_id,
            checkpoint_id=admission.checkpoint_id,
            episode_id=admission.episode_id,
            originating_reasoning_id=admission.originating_reasoning_id,
            execution_id=None if envelope is None else envelope.execution_id,
            authorization_id=None if envelope is None else envelope.authorization_id,
            requirement_id=admission.requirement_id,
            plan_id=None if envelope is None else envelope.plan_id,
            source_reference=admission.source_reference,
            world_snapshot_id=admission.world_snapshot_id,
            status=status,
            reasoning_reentry=None,
            transition=None,
            resulting_episode_state=None,
            rationale_codes=rationale_codes,
            reasoning_reentry_invocation_count=reasoning_calls,
            episode_record_invocation_count=0,
        )
