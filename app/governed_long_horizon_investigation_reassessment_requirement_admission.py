from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.governed_long_horizon_investigation_reasoning_reentry_recording import (
    GovernedInvestigationReasoningReentryRecordingResult,
    GovernedInvestigationReasoningReentryRecordingStatus,
)
from app.governed_multi_hypothesis_productive_consumption import (
    GovernedMultiHypothesisProductiveConsumption,
    GovernedMultiHypothesisProductiveConsumptionV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuation,
    GovernedMultiStepInvestigationProductiveContinuationV1,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedInvestigationReasoningClosureResult,
    GovernedInvestigationReasoningClosureStatus,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


class GovernedInvestigationReassessmentRequirementAdmissionStatus(StrEnum):
    ADMITTED = "admitted"
    CLOSED_NO_REQUIREMENT = "closed_no_requirement"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationReassessmentRequirementAdmissionResult:
    thread_id: str | None
    checkpoint_id: str | None
    episode_id: str
    originating_reasoning_id: str
    reentry_id: str | None
    evidence_id: str | None
    source_reference: str
    world_snapshot_id: str
    revised_report_id: str
    status: GovernedInvestigationReassessmentRequirementAdmissionStatus
    discrimination_product: GovernedMultiHypothesisProductiveConsumption | None
    source_requirement: DiscriminatingEvidenceRequirement | None
    continuation: GovernedMultiStepInvestigationProductiveContinuation | None
    resulting_episode_state: GovernedInvestigationEpisodeState | None
    rationale_codes: tuple[str, ...]
    discrimination_invocation_count: int
    continuation_invocation_count: int
    schema_version: str = (
        "post-m409.1-long-horizon-reassessment-requirement-admission-v1"
    )
    canonical_requirement_authority: str = "governed_reasoning"
    canonical_episode_authority: str = (
        "GovernedMultiStepInvestigationProductiveContinuationV1"
    )
    eligible_for_existing_planning: bool = False
    invokes_planning: bool = False
    invokes_authorization: bool = False
    invokes_execution: bool = False
    invokes_reasoning: bool = False
    creates_questions: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    establishes_truth: bool = False
    permits_retry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("requirement admission requires rationale codes")
        if self.discrimination_invocation_count not in {0, 1}:
            raise ValueError("requirement admission permits one discrimination call")
        if self.continuation_invocation_count not in {0, 1}:
            raise ValueError("requirement admission permits one continuation call")
        if self.canonical_requirement_authority != "governed_reasoning":
            raise ValueError("requirement admission must preserve reasoning authority")
        if self.canonical_episode_authority != (
            "GovernedMultiStepInvestigationProductiveContinuationV1"
        ):
            raise ValueError("requirement admission must preserve episode authority")
        if any(
            (
                self.invokes_planning,
                self.invokes_authorization,
                self.invokes_execution,
                self.invokes_reasoning,
                self.creates_questions,
                self.modifies_memory,
                self.modifies_world_model,
                self.establishes_truth,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError("requirement admission operationalizes a later residual")

        if self.status is (
            GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
        ):
            if self.discrimination_product is None or self.source_requirement is None:
                raise ValueError("admitted R2 requires exact canonical products")
            if self.continuation is None or self.resulting_episode_state is None:
                raise ValueError("admitted R2 requires continuation state")
            if self.continuation.source_requirement is not self.source_requirement:
                raise ValueError("admitted R2 must preserve requirement identity")
            if self.resulting_episode_state is not self.continuation.resulting_state:
                raise ValueError("admitted R2 must preserve continuation state")
            if not self.eligible_for_existing_planning:
                raise ValueError("admitted R2 must expose planning eligibility")
            if self.discrimination_invocation_count != 1:
                raise ValueError("admitted R2 requires one discrimination call")
            if self.continuation_invocation_count != 1:
                raise ValueError("admitted R2 requires one continuation call")
        elif self.status is (
            GovernedInvestigationReassessmentRequirementAdmissionStatus
            .CLOSED_NO_REQUIREMENT
        ):
            if (
                self.discrimination_product is None
                or self.source_requirement is not None
            ):
                raise ValueError("no-requirement stop must preserve zero cardinality")
            if self.continuation is None or self.resulting_episode_state is None:
                raise ValueError("no-requirement stop requires canonical continuation")
            if self.eligible_for_existing_planning:
                raise ValueError("closed no-requirement result cannot enter planning")
            if self.discrimination_invocation_count != 1:
                raise ValueError("no-requirement stop requires one discrimination call")
            if self.continuation_invocation_count != 1:
                raise ValueError("no-requirement stop requires one continuation call")
        elif self.continuation is not None or self.resulting_episode_state is not None:
            raise ValueError("fail-closed result cannot expose episode continuation")


class GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1:
    """Derive zero/one governed R2, admit it once, then stop before Planning."""

    def __init__(
        self,
        discrimination: GovernedMultiHypothesisProductiveConsumptionV1 | None = None,
        continuation: (
            GovernedMultiStepInvestigationProductiveContinuationV1 | None
        ) = None,
    ) -> None:
        self._discrimination = (
            discrimination or GovernedMultiHypothesisProductiveConsumptionV1()
        )
        self._continuation = (
            continuation or GovernedMultiStepInvestigationProductiveContinuationV1()
        )

    def consume(
        self,
        reentry_recording: (
            GovernedInvestigationReasoningReentryRecordingResult
            | GovernedInvestigationReasoningClosureResult
        ),
        revised_report: GovernedHypothesisDeepeningReport,
    ) -> GovernedInvestigationReassessmentRequirementAdmissionResult:
        reasoning_reentry = reentry_recording.reasoning_reentry
        state = reentry_recording.resulting_episode_state
        evidence_id = (
            None if reasoning_reentry is None else reasoning_reentry.evidence_id
        )
        is_historical_recording = isinstance(
            reentry_recording,
            GovernedInvestigationReasoningReentryRecordingResult,
        )
        if is_historical_recording:
            input_recorded = (
                reentry_recording.status
                is GovernedInvestigationReasoningReentryRecordingStatus
                .RECORDED_CONTINUATION
            )
            step_budget_eligible = (
                state is not None
                and state.current_step == 1
                and state.remaining_acquisitions == 1
            )
            originating_reasoning_id = reentry_recording.originating_reasoning_id
        else:
            input_recorded = (
                reentry_recording.status
                is GovernedInvestigationReasoningClosureStatus.RECORDED
                and reentry_recording.reasoning_reentry_invocation_count == 1
                and reentry_recording.episode_record_invocation_count == 1
            )
            step_budget_eligible = (
                state is not None
                and 2 <= state.current_step <= state.max_acquisitions - 1
                and state.consumed_acquisitions == state.current_step
                and state.remaining_acquisitions > 0
                and reentry_recording.remaining_acquisitions
                == state.remaining_acquisitions
            )
            originating_reasoning_id = (
                None if state is None else state.originating_reasoning_id
            )

        exact_reentry_lineage = (
            reasoning_reentry is not None
            and reasoning_reentry.reentry_id
            == getattr(
                reentry_recording,
                "reasoning_reentry_id",
                reasoning_reentry.reentry_id,
            )
            and reasoning_reentry.execution_id == reentry_recording.execution_id
            and reasoning_reentry.authorization_id == reentry_recording.authorization_id
            and reasoning_reentry.requirement_id == reentry_recording.requirement_id
            and reasoning_reentry.plan_id == reentry_recording.plan_id
            and reasoning_reentry.source_reference == reentry_recording.source_reference
            and reasoning_reentry.world_snapshot_id
            == reentry_recording.world_snapshot_id
        )
        eligible = all(
            (
                input_recorded,
                reasoning_reentry is not None,
                exact_reentry_lineage,
                evidence_id is not None,
                bool(evidence_id),
                state is not None,
                state is reentry_recording.resulting_episode_state,
                state is not None
                and state.status
                is GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT,
                step_budget_eligible,
                state is not None and state.episode_id == reentry_recording.episode_id,
                state is not None
                and state.originating_reasoning_id == originating_reasoning_id,
                state is not None
                and state.source_reference == reentry_recording.source_reference,
                state is not None
                and state.world_snapshot_id == reentry_recording.world_snapshot_id,
                revised_report.source_reference == reentry_recording.source_reference,
                revised_report.world_snapshot_id == reentry_recording.world_snapshot_id,
                evidence_id is not None
                and any(
                    evidence_id in assessment.evidence_references
                    for assessment in revised_report.assessments
                ),
            )
        )
        if not eligible:
            return self._closed(
                reentry_recording,
                revised_report,
                GovernedInvestigationReassessmentRequirementAdmissionStatus
                .NOT_ELIGIBLE,
                ("investigation_requirement_admission:reassessment_not_eligible",),
                discrimination_calls=0,
            )

        assert state is not None
        try:
            discrimination_product = self._discrimination.consume(revised_report)
        except Exception:
            return self._closed(
                reentry_recording,
                revised_report,
                GovernedInvestigationReassessmentRequirementAdmissionStatus
                .REVIEW_REQUIRED,
                ("investigation_requirement_admission:discrimination_failed",),
                discrimination_calls=1,
            )

        if (
            discrimination_product.source_report_id != revised_report.report_id
            or discrimination_product.source_reference
            != reentry_recording.source_reference
            or discrimination_product.world_snapshot_id
            != reentry_recording.world_snapshot_id
        ):
            return self._closed(
                reentry_recording,
                revised_report,
                GovernedInvestigationReassessmentRequirementAdmissionStatus
                .REVIEW_REQUIRED,
                ("investigation_requirement_admission:discrimination_lineage_invalid",),
                discrimination_calls=1,
                discrimination_product=discrimination_product,
            )

        discrimination_requirements = discrimination_product.discrimination_requirements
        if len(discrimination_requirements) > 1:
            return self._closed(
                reentry_recording,
                revised_report,
                GovernedInvestigationReassessmentRequirementAdmissionStatus
                .REVIEW_REQUIRED,
                ("investigation_requirement_admission:ambiguous_requirements",),
                discrimination_calls=1,
                discrimination_product=discrimination_product,
            )
        requirement = (
            None
            if len(discrimination_requirements) == 0
            else discrimination_requirements[0]
        )

        try:
            continuation = self._continuation.consume(state, requirement)
        except Exception:
            return self._closed(
                reentry_recording,
                revised_report,
                GovernedInvestigationReassessmentRequirementAdmissionStatus
                .REVIEW_REQUIRED,
                ("investigation_requirement_admission:continuation_failed",),
                discrimination_calls=1,
                discrimination_product=discrimination_product,
            )

        if requirement is None:
            valid_stop = all(
                (
                    continuation.source_requirement is None,
                    continuation.decision
                    is GovernedInvestigationContinuationDecision.STOP_REQUIRED,
                    continuation.resulting_state.status
                    is GovernedInvestigationEpisodeStatus.CLOSED,
                    continuation.stopping_reason
                    is GovernedInvestigationStoppingReason.NO_NEW_REQUIREMENT,
                    not continuation.eligible_for_existing_planning,
                )
            )
            if not valid_stop:
                return self._closed(
                    reentry_recording,
                    revised_report,
                    GovernedInvestigationReassessmentRequirementAdmissionStatus
                    .REVIEW_REQUIRED,
                    ("investigation_requirement_admission:unexpected_zero_transition",),
                    discrimination_calls=1,
                    discrimination_product=discrimination_product,
                )
            return self._result(
                reentry_recording,
                revised_report,
                GovernedInvestigationReassessmentRequirementAdmissionStatus
                .CLOSED_NO_REQUIREMENT,
                discrimination_product,
                None,
                continuation,
                ("investigation_requirement_admission:no_new_requirement_closed",),
                eligible_for_existing_planning=False,
            )

        expected_next_step = state.current_step + 1
        valid_admission = all(
            (
                continuation.source_requirement is requirement,
                continuation.source_requirement_id == requirement.requirement_id,
                continuation.decision
                is GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
                continuation.resulting_state.status
                is GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
                continuation.resulting_state.current_step == expected_next_step,
                continuation.resulting_state.consumed_acquisitions
                == state.consumed_acquisitions,
                continuation.resulting_state.remaining_acquisitions
                == state.remaining_acquisitions,
                continuation.resulting_state.episode_id == reentry_recording.episode_id,
                continuation.resulting_state.source_reference
                == reentry_recording.source_reference,
                continuation.resulting_state.world_snapshot_id
                == reentry_recording.world_snapshot_id,
                continuation.eligible_for_existing_planning,
            )
        )
        if not valid_admission:
            return self._closed(
                reentry_recording,
                revised_report,
                GovernedInvestigationReassessmentRequirementAdmissionStatus
                .REVIEW_REQUIRED,
                (
                    "investigation_requirement_admission:"
                    "unexpected_requirement_transition",
                ),
                discrimination_calls=1,
                discrimination_product=discrimination_product,
            )

        rationale = (
            "investigation_requirement_admission:exact_r2_admitted"
            if is_historical_recording
            else "investigation_requirement_admission:exact_next_requirement_admitted"
        )
        return self._result(
            reentry_recording,
            revised_report,
            GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED,
            discrimination_product,
            requirement,
            continuation,
            (rationale,),
            eligible_for_existing_planning=True,
        )

    def consume_local_reentry(
        self,
        episode_transition,
        local_reentry,
        revised_report: GovernedHypothesisDeepeningReport,
    ) -> GovernedInvestigationReassessmentRequirementAdmissionResult:
        """Admit zero/one next requirement from an already-recorded local re-entry."""
        state = episode_transition.state
        eligible = all(
            (
                state.status is GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT,
                local_reentry.episode_id == state.episode_id,
                (
                    local_reentry.originating_reasoning_id
                    == state.originating_reasoning_id
                ),
                local_reentry.requirement_id == state.current_requirement_id,
                bool(local_reentry.evidence_id),
                revised_report.source_reference == state.source_reference,
                revised_report.world_snapshot_id == state.world_snapshot_id,
                any(
                    local_reentry.evidence_id in item.evidence_references
                    for item in revised_report.assessments
                ),
            )
        )
        if not eligible:
            return GovernedInvestigationReassessmentRequirementAdmissionResult(
                thread_id=None, checkpoint_id=None, episode_id=state.episode_id,
                originating_reasoning_id=state.originating_reasoning_id,
                reentry_id=local_reentry.reentry_id,
                evidence_id=local_reentry.evidence_id,
                source_reference=state.source_reference,
                world_snapshot_id=state.world_snapshot_id,
                revised_report_id=revised_report.report_id,
                status=GovernedInvestigationReassessmentRequirementAdmissionStatus.NOT_ELIGIBLE,
                discrimination_product=None, source_requirement=None, continuation=None,
                resulting_episode_state=None,
                rationale_codes=("investigation_requirement_admission:local_reassessment_not_eligible",),
                discrimination_invocation_count=0, continuation_invocation_count=0,
            )
        discrimination_product = self._discrimination.consume(revised_report)
        requirements = discrimination_product.discrimination_requirements
        if len(requirements) > 1:
            return GovernedInvestigationReassessmentRequirementAdmissionResult(
                thread_id=None, checkpoint_id=None, episode_id=state.episode_id,
                originating_reasoning_id=state.originating_reasoning_id,
                reentry_id=local_reentry.reentry_id,
                evidence_id=local_reentry.evidence_id,
                source_reference=state.source_reference,
                world_snapshot_id=state.world_snapshot_id,
                revised_report_id=revised_report.report_id,
                status=GovernedInvestigationReassessmentRequirementAdmissionStatus.REVIEW_REQUIRED,
                discrimination_product=discrimination_product,
                source_requirement=None, continuation=None,
                resulting_episode_state=None,
                rationale_codes=("investigation_requirement_admission:ambiguous_requirements",),
                discrimination_invocation_count=1,
                continuation_invocation_count=0,
            )
        requirement = requirements[0] if requirements else None
        continuation = self._continuation.consume(state, requirement)
        status = (
            GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
            if requirement is not None
            and continuation.eligible_for_existing_planning
            else GovernedInvestigationReassessmentRequirementAdmissionStatus
            .CLOSED_NO_REQUIREMENT
        )
        return GovernedInvestigationReassessmentRequirementAdmissionResult(
            thread_id=None, checkpoint_id=None, episode_id=state.episode_id,
            originating_reasoning_id=state.originating_reasoning_id,
            reentry_id=local_reentry.reentry_id,
            evidence_id=local_reentry.evidence_id,
            source_reference=state.source_reference,
            world_snapshot_id=state.world_snapshot_id,
            revised_report_id=revised_report.report_id, status=status,
            discrimination_product=discrimination_product,
            source_requirement=requirement,
            continuation=continuation,
            resulting_episode_state=continuation.resulting_state,
            rationale_codes=(
                "investigation_requirement_admission:local_reassessment_consumed",
                *continuation.rationale_codes
            ),
            discrimination_invocation_count=1, continuation_invocation_count=1,
            eligible_for_existing_planning=(
                continuation.eligible_for_existing_planning
            ),
        )

    @staticmethod
    def _result(
        reentry_recording: (
            GovernedInvestigationReasoningReentryRecordingResult
            | GovernedInvestigationReasoningClosureResult
        ),
        revised_report: GovernedHypothesisDeepeningReport,
        status: GovernedInvestigationReassessmentRequirementAdmissionStatus,
        discrimination_product: GovernedMultiHypothesisProductiveConsumption,
        requirement: DiscriminatingEvidenceRequirement | None,
        continuation: GovernedMultiStepInvestigationProductiveContinuation,
        rationale_codes: tuple[str, ...],
        *,
        eligible_for_existing_planning: bool,
    ) -> GovernedInvestigationReassessmentRequirementAdmissionResult:
        reasoning_reentry = reentry_recording.reasoning_reentry
        return GovernedInvestigationReassessmentRequirementAdmissionResult(
            thread_id=getattr(reentry_recording, "thread_id", None),
            checkpoint_id=getattr(reentry_recording, "checkpoint_id", None),
            episode_id=reentry_recording.episode_id,
            originating_reasoning_id=(
                reentry_recording.resulting_episode_state.originating_reasoning_id
            ),
            reentry_id=(
                None if reasoning_reentry is None else reasoning_reentry.reentry_id
            ),
            evidence_id=(
                None if reasoning_reentry is None else reasoning_reentry.evidence_id
            ),
            source_reference=reentry_recording.source_reference,
            world_snapshot_id=reentry_recording.world_snapshot_id,
            revised_report_id=revised_report.report_id,
            status=status,
            discrimination_product=discrimination_product,
            source_requirement=requirement,
            continuation=continuation,
            resulting_episode_state=continuation.resulting_state,
            rationale_codes=(*rationale_codes, *continuation.rationale_codes),
            discrimination_invocation_count=1,
            continuation_invocation_count=1,
            eligible_for_existing_planning=eligible_for_existing_planning,
        )

    @staticmethod
    def _closed(
        reentry_recording: (
            GovernedInvestigationReasoningReentryRecordingResult
            | GovernedInvestigationReasoningClosureResult
        ),
        revised_report: GovernedHypothesisDeepeningReport,
        status: GovernedInvestigationReassessmentRequirementAdmissionStatus,
        rationale_codes: tuple[str, ...],
        *,
        discrimination_calls: int,
        discrimination_product: (
            GovernedMultiHypothesisProductiveConsumption | None
        ) = None,
    ) -> GovernedInvestigationReassessmentRequirementAdmissionResult:
        reasoning_reentry = reentry_recording.reasoning_reentry
        return GovernedInvestigationReassessmentRequirementAdmissionResult(
            thread_id=getattr(reentry_recording, "thread_id", None),
            checkpoint_id=getattr(reentry_recording, "checkpoint_id", None),
            episode_id=reentry_recording.episode_id,
            originating_reasoning_id=(
                reentry_recording.resulting_episode_state.originating_reasoning_id
            ),
            reentry_id=(
                None if reasoning_reentry is None else reasoning_reentry.reentry_id
            ),
            evidence_id=(
                None if reasoning_reentry is None else reasoning_reentry.evidence_id
            ),
            source_reference=reentry_recording.source_reference,
            world_snapshot_id=reentry_recording.world_snapshot_id,
            revised_report_id=revised_report.report_id,
            status=status,
            discrimination_product=discrimination_product,
            source_requirement=None,
            continuation=None,
            resulting_episode_state=None,
            rationale_codes=rationale_codes,
            discrimination_invocation_count=discrimination_calls,
            continuation_invocation_count=0,
            eligible_for_existing_planning=False,
        )
