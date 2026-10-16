from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryFoundationV1,
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
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryResult,
    GovernedInvestigationExecutionReentryStatus,
)


class GovernedInvestigationReasoningClosureStatus(StrEnum):
    RECORDED = "recorded"
    CLOSED = "closed"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationReasoningClosureResult:
    episode_id: str
    execution_reentry: GovernedInvestigationExecutionReentryResult
    status: GovernedInvestigationReasoningClosureStatus
    reasoning_reentry: GovernedLevel2ReasoningReentryResult | None
    resulting_episode_state: GovernedInvestigationEpisodeState
    execution_id: str | None
    authorization_id: str | None
    requirement_id: str | None
    plan_id: str | None
    reasoning_reentry_id: str | None
    source_reference: str
    world_snapshot_id: str
    remaining_acquisitions: int
    stopping_reason: GovernedInvestigationStoppingReason
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = (
        "post-m409.1-multistep-investigation-reasoning-closure-v1"
    )
    canonical_reasoning_authority: str = "governed_reasoning"
    canonical_episode_authority: str = "planning_foundation"
    episode_closed: bool = False
    reasoning_reentry_invocation_count: int = 0
    episode_record_invocation_count: int = 0
    eligible_for_existing_planning: bool = False
    eligible_for_authorization: bool = False
    eligible_for_existing_execution: bool = False
    eligible_for_reasoning_reentry: bool = False
    creates_requirement: bool = False
    invokes_planning: bool = False
    invokes_authorization: bool = False
    invokes_execution: bool = False
    invokes_curiosity: bool = False
    creates_questions: bool = False
    emits_conversation: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    permits_retry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.episode_id != self.execution_reentry.episode_id:
            raise ValueError("reasoning closure must preserve episode identity")
        if self.source_reference != self.execution_reentry.source_reference:
            raise ValueError("reasoning closure must preserve source lineage")
        if self.world_snapshot_id != self.execution_reentry.world_snapshot_id:
            raise ValueError("reasoning closure must preserve snapshot lineage")
        if self.reasoning_reentry_invocation_count not in {0, 1}:
            raise ValueError("reasoning closure permits at most one re-entry")
        if self.episode_record_invocation_count not in {0, 1}:
            raise ValueError("reasoning closure permits at most one episode record")
        if self.status is GovernedInvestigationReasoningClosureStatus.RECORDED:
            if self.reasoning_reentry is None:
                raise ValueError("recorded episode requires reasoning re-entry")
            if self.reasoning_reentry_invocation_count != 1:
                raise ValueError("recorded episode requires one reasoning re-entry")
            if self.episode_record_invocation_count != 1:
                raise ValueError("recorded episode requires one episode record")
            if self.episode_closed:
                raise ValueError("recorded result cannot mark episode closed")
            if (
                self.resulting_episode_state.status
                is not GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
            ):
                raise ValueError("recorded result must await next requirement")
            if self.remaining_acquisitions <= 0:
                raise ValueError("recorded result requires remaining budget")
            if self.stopping_reason is not GovernedInvestigationStoppingReason.NONE:
                raise ValueError("recorded result cannot carry stopping reason")
        elif self.status is GovernedInvestigationReasoningClosureStatus.CLOSED:
            if self.reasoning_reentry is None:
                raise ValueError("closed episode requires reasoning re-entry")
            if self.reasoning_reentry_invocation_count != 1:
                raise ValueError("closed episode requires one reasoning re-entry")
            if self.episode_record_invocation_count != 1:
                raise ValueError("closed episode requires one episode record")
            if not self.episode_closed:
                raise ValueError("closed result must mark episode closed")
            if (
                self.resulting_episode_state.status
                is not GovernedInvestigationEpisodeStatus.CLOSED
            ):
                raise ValueError("closed result requires terminal episode state")
            if self.remaining_acquisitions != 0:
                raise ValueError("closed Level 2B episode must have zero budget")
        elif self.episode_closed:
            raise ValueError("non-closed result cannot mark episode closed")
        if self.canonical_reasoning_authority != "governed_reasoning":
            raise ValueError("reasoning closure must preserve reasoning authority")
        if self.canonical_episode_authority != "planning_foundation":
            raise ValueError("reasoning closure must preserve episode authority")
        if any(
            (
                self.eligible_for_existing_planning,
                self.eligible_for_authorization,
                self.eligible_for_existing_execution,
                self.eligible_for_reasoning_reentry,
                self.creates_requirement,
                self.invokes_planning,
                self.invokes_authorization,
                self.invokes_execution,
                self.invokes_curiosity,
                self.creates_questions,
                self.emits_conversation,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError("reasoning closure violates governed limits")


class GovernedMultiStepInvestigationReasoningClosureV1:
    """Re-enter reasoning once for an acquired governed investigation step."""

    def __init__(
        self,
        reasoning_reentry: GovernedLevel2ReasoningReentryFoundationV1,
        episode_boundary: GovernedMultiStepInvestigationEpisodeBoundaryV1
        | None = None,
    ) -> None:
        self._reasoning_reentry = reasoning_reentry
        self._episode_boundary = (
            episode_boundary or GovernedMultiStepInvestigationEpisodeBoundaryV1()
        )

    def consume(
        self,
        execution_reentry: GovernedInvestigationExecutionReentryResult,
        *,
        now: datetime,
    ) -> GovernedInvestigationReasoningClosureResult:
        error = self._eligibility_error(execution_reentry)
        if error is not None:
            return self._result(
                execution_reentry,
                GovernedInvestigationReasoningClosureStatus.NOT_ELIGIBLE,
                None,
                execution_reentry.resulting_episode_state,
                (error,),
                reasoning_reentry_invocation_count=0,
                episode_record_invocation_count=0,
            )
        envelope = execution_reentry.evidence_envelope
        if envelope is None:
            return self._result(
                execution_reentry,
                GovernedInvestigationReasoningClosureStatus.NOT_ELIGIBLE,
                None,
                execution_reentry.resulting_episode_state,
                ("reasoning_closure:acquired_envelope_required",),
                reasoning_reentry_invocation_count=0,
                episode_record_invocation_count=0,
            )
        try:
            reentry = self._reasoning_reentry.reenter(envelope, now=now)
        except Exception:
            return self._result(
                execution_reentry,
                GovernedInvestigationReasoningClosureStatus.REVIEW_REQUIRED,
                None,
                execution_reentry.resulting_episode_state,
                ("reasoning_closure:single_reasoning_reentry_failed",),
                reasoning_reentry_invocation_count=1,
                episode_record_invocation_count=0,
            )
        lineage_error = self._reentry_lineage_error(execution_reentry, reentry)
        if lineage_error is not None:
            return self._result(
                execution_reentry,
                GovernedInvestigationReasoningClosureStatus.REVIEW_REQUIRED,
                reentry,
                execution_reentry.resulting_episode_state,
                (lineage_error,),
                reasoning_reentry_invocation_count=1,
                episode_record_invocation_count=0,
            )
        if reentry.status is not GovernedReasoningReentryStatus.REEVALUATED:
            return self._result(
                execution_reentry,
                GovernedInvestigationReasoningClosureStatus.REVIEW_REQUIRED,
                reentry,
                execution_reentry.resulting_episode_state,
                ("reasoning_closure:successful_reasoning_reentry_required",),
                reasoning_reentry_invocation_count=1,
                episode_record_invocation_count=0,
            )
        state = execution_reentry.resulting_episode_state
        transition = self._episode_boundary.record_reentry(state, reentry)

        if state.remaining_acquisitions > 0:
            if (
                transition.decision
                is not GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
                or transition.state.status
                is not GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
                or transition.state.stopping_reason
                is not GovernedInvestigationStoppingReason.NONE
                or transition.state.remaining_acquisitions
                != state.remaining_acquisitions
            ):
                return self._result(
                    execution_reentry,
                    GovernedInvestigationReasoningClosureStatus.REVIEW_REQUIRED,
                    reentry,
                    transition.state,
                    ("reasoning_closure:intermediate_boundary_not_satisfied",),
                    reasoning_reentry_invocation_count=1,
                    episode_record_invocation_count=1,
                )
            return self._result(
                execution_reentry,
                GovernedInvestigationReasoningClosureStatus.RECORDED,
                reentry,
                transition.state,
                (
                    "reasoning_closure:reentry_recorded_awaiting_requirement",
                    *transition.rationale_codes,
                ),
                reasoning_reentry_invocation_count=1,
                episode_record_invocation_count=1,
            )

        if (
            transition.decision
            is not GovernedInvestigationContinuationDecision.STOP_REQUIRED
            or transition.state.status
            is not GovernedInvestigationEpisodeStatus.CLOSED
            or transition.state.stopping_reason
            is not GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
            or bool(transition.state.remaining_acquisitions)
        ):
            return self._result(
                execution_reentry,
                GovernedInvestigationReasoningClosureStatus.REVIEW_REQUIRED,
                reentry,
                transition.state,
                ("reasoning_closure:terminal_boundary_not_satisfied",),
                reasoning_reentry_invocation_count=1,
                episode_record_invocation_count=1,
            )
        return self._result(
            execution_reentry,
            GovernedInvestigationReasoningClosureStatus.CLOSED,
            reentry,
            transition.state,
            (
                "reasoning_closure:reentry_closed_budget_exhausted_episode",
                *transition.rationale_codes,
            ),
            reasoning_reentry_invocation_count=1,
            episode_record_invocation_count=1,
        )

    @staticmethod
    def _eligibility_error(
        execution_reentry: GovernedInvestigationExecutionReentryResult,
    ) -> str | None:
        state = execution_reentry.resulting_episode_state
        if (
            execution_reentry.status
            is not GovernedInvestigationExecutionReentryStatus.ACQUIRED
        ):
            return "reasoning_closure:acquired_execution_required"
        if not execution_reentry.eligible_for_reasoning_reentry:
            return "reasoning_closure:execution_not_reasoning_eligible"
        if execution_reentry.execution_invocation_count != 1:
            return "reasoning_closure:single_execution_required"
        if execution_reentry.episode_record_invocation_count != 1:
            return "reasoning_closure:single_episode_record_required"
        if state.status is not GovernedInvestigationEpisodeStatus.AWAITING_REENTRY:
            return "reasoning_closure:episode_must_await_reentry"
        if not (
            2 <= execution_reentry.current_step <= state.max_acquisitions
            and state.current_step == execution_reentry.current_step
            and state.consumed_acquisitions == execution_reentry.current_step
            and execution_reentry.remaining_acquisitions
            == state.remaining_acquisitions
        ):
            return "reasoning_closure:governed_step_budget_alignment_required"
        return None

    @staticmethod
    def _reentry_lineage_error(
        execution_reentry: GovernedInvestigationExecutionReentryResult,
        reentry: GovernedLevel2ReasoningReentryResult,
    ) -> str | None:
        if reentry.execution_id != execution_reentry.execution_id:
            return "reasoning_closure:execution_lineage_mismatch"
        if reentry.authorization_id != execution_reentry.authorization_id:
            return "reasoning_closure:authorization_lineage_mismatch"
        if reentry.requirement_id != execution_reentry.requirement_id:
            return "reasoning_closure:requirement_lineage_mismatch"
        if reentry.plan_id != execution_reentry.plan_id:
            return "reasoning_closure:plan_lineage_mismatch"
        if reentry.source_reference != execution_reentry.source_reference:
            return "reasoning_closure:source_lineage_mismatch"
        if reentry.world_snapshot_id != execution_reentry.world_snapshot_id:
            return "reasoning_closure:snapshot_lineage_mismatch"
        if reentry.reentry_id in execution_reentry.resulting_episode_state.reentry_ids:
            return "reasoning_closure:prior_reentry_reuse_forbidden"
        return None

    @staticmethod
    def _result(
        execution_reentry: GovernedInvestigationExecutionReentryResult,
        status: GovernedInvestigationReasoningClosureStatus,
        reentry: GovernedLevel2ReasoningReentryResult | None,
        state: GovernedInvestigationEpisodeState,
        rationale_codes: tuple[str, ...],
        *,
        reasoning_reentry_invocation_count: int,
        episode_record_invocation_count: int,
    ) -> GovernedInvestigationReasoningClosureResult:
        fingerprint = sha256(
            repr(
                (
                    execution_reentry.episode_id,
                    status.value,
                    execution_reentry.execution_id,
                    None if reentry is None else reentry.reentry_id,
                    state.status.value,
                    state.stopping_reason.value,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedInvestigationReasoningClosureResult(
            episode_id=execution_reentry.episode_id,
            execution_reentry=execution_reentry,
            status=status,
            reasoning_reentry=reentry,
            resulting_episode_state=state,
            execution_id=execution_reentry.execution_id,
            authorization_id=execution_reentry.authorization_id,
            requirement_id=execution_reentry.requirement_id,
            plan_id=execution_reentry.plan_id,
            reasoning_reentry_id=None if reentry is None else reentry.reentry_id,
            source_reference=execution_reentry.source_reference,
            world_snapshot_id=execution_reentry.world_snapshot_id,
            remaining_acquisitions=state.remaining_acquisitions,
            stopping_reason=state.stopping_reason,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
            episode_closed=(
                status is GovernedInvestigationReasoningClosureStatus.CLOSED
            ),
            reasoning_reentry_invocation_count=reasoning_reentry_invocation_count,
            episode_record_invocation_count=episode_record_invocation_count,
        )
