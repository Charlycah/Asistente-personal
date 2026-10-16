from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.governed_level2_read_only_execution_gateway import (
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import GovernedLevel2ReasoningReentryResult
from app.governed_long_horizon_investigation_e2_execution_reentry import (
    GovernedInvestigationE2ExecutionAdmissionResult,
    GovernedInvestigationE2ExecutionAdmissionStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryStatus,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedInvestigationReasoningClosureResult,
    GovernedInvestigationReasoningClosureStatus,
    GovernedMultiStepInvestigationReasoningClosureV1,
)


class GovernedInvestigationRR2TerminalClosureStatus(StrEnum):
    RECORDED = "recorded"
    CLOSED = "closed"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationRR2TerminalClosureResult:
    thread_id: str
    checkpoint_id: str
    episode_id: str
    originating_reasoning_id: str
    execution_id: str | None
    authorization_id: str | None
    requirement_id: str | None
    plan_id: str | None
    source_reference: str
    world_snapshot_id: str
    status: GovernedInvestigationRR2TerminalClosureStatus
    closure: GovernedInvestigationReasoningClosureResult | None
    reasoning_reentry: GovernedLevel2ReasoningReentryResult | None
    resulting_episode_state: GovernedInvestigationEpisodeState | None
    reasoning_reentry_id: str | None
    stopping_reason: GovernedInvestigationStoppingReason | None
    rationale_codes: tuple[str, ...]
    reasoning_closure_invocation_count: int
    reasoning_reentry_invocation_count: int
    episode_record_invocation_count: int
    schema_version: str = "post-m409.1-long-horizon-e2-rr2-terminal-closure-v1"
    canonical_reasoning_closure_authority: str = (
        "GovernedMultiStepInvestigationReasoningClosureV1"
    )
    episode_closed: bool = False
    eligible_for_existing_planning: bool = False
    eligible_for_authorization: bool = False
    eligible_for_existing_execution: bool = False
    eligible_for_reasoning_reentry: bool = False
    creates_requirement: bool = False
    invokes_curiosity: bool = False
    permits_retry: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    emits_conversation: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("RR2 terminal closure requires rationale codes")
        if self.reasoning_closure_invocation_count not in {0, 1}:
            raise ValueError("RR2 bridge permits at most one closure invocation")
        if self.reasoning_reentry_invocation_count not in {0, 1}:
            raise ValueError("RR2 bridge permits at most one reasoning re-entry")
        if self.episode_record_invocation_count not in {0, 1}:
            raise ValueError("RR2 bridge permits at most one episode record")
        if self.canonical_reasoning_closure_authority != (
            "GovernedMultiStepInvestigationReasoningClosureV1"
        ):
            raise ValueError("RR2 bridge must preserve canonical closure owner")
        if any(
            (
                self.eligible_for_existing_planning,
                self.eligible_for_authorization,
                self.eligible_for_existing_execution,
                self.eligible_for_reasoning_reentry,
                self.creates_requirement,
                self.invokes_curiosity,
                self.permits_retry,
                self.modifies_memory,
                self.modifies_world_model,
                self.emits_conversation,
                self.starts_background_process,
            )
        ):
            raise ValueError("RR(N) bridge exposes a forbidden later capability")
        if self.status is GovernedInvestigationRR2TerminalClosureStatus.RECORDED:
            if self.closure is None or self.reasoning_reentry is None:
                raise ValueError(
                    "recorded RR(N) requires exact canonical closure products"
                )
            if self.resulting_episode_state is None:
                raise ValueError("recorded RR(N) requires exact episode state")
            if self.closure.status is not (
                GovernedInvestigationReasoningClosureStatus.RECORDED
            ):
                raise ValueError("recorded RR(N) requires canonical RECORDED")
            if self.closure.reasoning_reentry is not self.reasoning_reentry:
                raise ValueError("RR(N) bridge must preserve exact reasoning re-entry")
            if self.closure.resulting_episode_state is not self.resulting_episode_state:
                raise ValueError("RR(N) bridge must preserve exact episode state")
            if self.episode_closed:
                raise ValueError("recorded RR(N) cannot mark episode closed")
            if self.reasoning_closure_invocation_count != 1:
                raise ValueError("recorded RR(N) requires one closure invocation")
            if self.reasoning_reentry_invocation_count != 1:
                raise ValueError("recorded RR(N) requires one reasoning re-entry")
            if self.episode_record_invocation_count != 1:
                raise ValueError("recorded RR(N) requires one episode record")
        elif self.status is GovernedInvestigationRR2TerminalClosureStatus.CLOSED:
            if self.closure is None or self.reasoning_reentry is None:
                raise ValueError("closed RR2 requires exact canonical closure products")
            if self.resulting_episode_state is None:
                raise ValueError("closed RR2 requires exact terminal episode state")
            if self.closure.status is not (
                GovernedInvestigationReasoningClosureStatus.CLOSED
            ):
                raise ValueError("closed RR2 requires canonical CLOSED")
            if self.closure.reasoning_reentry is not self.reasoning_reentry:
                raise ValueError("RR2 bridge must preserve exact reasoning re-entry")
            if self.closure.resulting_episode_state is not self.resulting_episode_state:
                raise ValueError("RR2 bridge must preserve exact terminal state")
            if not self.episode_closed:
                raise ValueError("closed RR2 must mark episode closed")
            if self.reasoning_closure_invocation_count != 1:
                raise ValueError("closed RR2 requires one closure invocation")
            if self.reasoning_reentry_invocation_count != 1:
                raise ValueError("closed RR2 requires one reasoning re-entry")
            if self.episode_record_invocation_count != 1:
                raise ValueError("closed RR2 requires one episode record")
        elif self.episode_closed:
            raise ValueError("non-closed RR2 cannot mark episode closed")


class GovernedLongHorizonInvestigationRR2TerminalClosureV1:
    """Forward exact acquired E(N) to the existing reasoning closure owner."""

    def __init__(
        self,
        reasoning_closure: GovernedMultiStepInvestigationReasoningClosureV1,
    ) -> None:
        self._reasoning_closure = reasoning_closure

    def consume(
        self,
        e2_result: GovernedInvestigationE2ExecutionAdmissionResult,
        *,
        now: datetime,
    ) -> GovernedInvestigationRR2TerminalClosureResult:
        execution_reentry = e2_result.execution_reentry
        if not self._eligible(e2_result):
            return self._closed(
                e2_result,
                GovernedInvestigationRR2TerminalClosureStatus.NOT_ELIGIBLE,
                ("investigation_rr2_closure:exact_recorded_e2_required",),
            )

        assert execution_reentry is not None
        try:
            closure = self._reasoning_closure.consume(
                e2_result.execution_reentry,
                now=now,
            )
        except Exception:
            return self._closed(
                e2_result,
                GovernedInvestigationRR2TerminalClosureStatus.REVIEW_REQUIRED,
                ("investigation_rr2_closure:single_existing_closure_failed",),
                reasoning_closure_invocation_count=1,
            )

        if closure.execution_reentry is not execution_reentry:
            return self._review_after_closure(
                e2_result,
                closure,
                ("investigation_rr2_closure:existing_closure_e2_identity_mismatch",),
            )
        if closure.status not in {
            GovernedInvestigationReasoningClosureStatus.RECORDED,
            GovernedInvestigationReasoningClosureStatus.CLOSED,
        }:
            return self._review_after_closure(
                e2_result,
                closure,
                (
                    "investigation_rr2_closure:canonical_reasoning_closure_required",
                    *closure.rationale_codes,
                ),
            )
        if not self._valid_closure(e2_result, closure):
            return self._review_after_closure(
                e2_result,
                closure,
                ("investigation_rr2_closure:reasoning_lineage_mismatch",),
            )

        is_terminal = (
            closure.status is GovernedInvestigationReasoningClosureStatus.CLOSED
        )
        return GovernedInvestigationRR2TerminalClosureResult(
            thread_id=e2_result.thread_id,
            checkpoint_id=e2_result.checkpoint_id,
            episode_id=e2_result.episode_id,
            originating_reasoning_id=e2_result.originating_reasoning_id,
            execution_id=e2_result.execution_id,
            authorization_id=e2_result.authorization_id,
            requirement_id=e2_result.requirement_id,
            plan_id=e2_result.plan_id,
            source_reference=e2_result.source_reference,
            world_snapshot_id=e2_result.world_snapshot_id,
            status=(
                GovernedInvestigationRR2TerminalClosureStatus.CLOSED
                if is_terminal
                else GovernedInvestigationRR2TerminalClosureStatus.RECORDED
            ),
            closure=closure,
            reasoning_reentry=closure.reasoning_reentry,
            resulting_episode_state=closure.resulting_episode_state,
            reasoning_reentry_id=closure.reasoning_reentry_id,
            stopping_reason=closure.stopping_reason,
            rationale_codes=(
                "investigation_rr2_closure:exact_acquired_en_forwarded",
                (
                    "investigation_rr2_closure:canonical_terminal_closed_preserved"
                    if is_terminal
                    else (
                        "investigation_rr2_closure:"
                        "canonical_intermediate_recorded_preserved"
                    )
                ),
                *closure.rationale_codes,
            ),
            reasoning_closure_invocation_count=1,
            reasoning_reentry_invocation_count=(
                closure.reasoning_reentry_invocation_count
            ),
            episode_record_invocation_count=closure.episode_record_invocation_count,
            episode_closed=is_terminal,
        )

    @staticmethod
    def _eligible(e2_result: GovernedInvestigationE2ExecutionAdmissionResult) -> bool:
        execution_reentry = e2_result.execution_reentry
        envelope = e2_result.evidence_envelope
        state = e2_result.resulting_episode_state
        if execution_reentry is None or envelope is None or state is None:
            return False
        authorization_reentry = execution_reentry.authorization_reentry
        return all(
            (
                e2_result.status
                is GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED,
                e2_result.eligible_for_existing_reasoning_reentry,
                e2_result.execution_status is GovernedLevel2ExecutionStatus.ACQUIRED,
                e2_result.execution_invocation_count == 1,
                e2_result.episode_record_invocation_count == 1,
                execution_reentry.status
                is GovernedInvestigationExecutionReentryStatus.ACQUIRED,
                execution_reentry.eligible_for_reasoning_reentry,
                execution_reentry.execution_invocation_count == 1,
                execution_reentry.episode_record_invocation_count == 1,
                execution_reentry.current_step == state.current_step,
                execution_reentry.remaining_acquisitions
                == state.remaining_acquisitions,
                execution_reentry.evidence_envelope is envelope,
                execution_reentry.resulting_episode_state is state,
                execution_reentry.episode_id == e2_result.episode_id,
                execution_reentry.execution_id == e2_result.execution_id,
                execution_reentry.authorization_id == e2_result.authorization_id,
                execution_reentry.requirement_id == e2_result.requirement_id,
                execution_reentry.plan_id == e2_result.plan_id,
                execution_reentry.source_reference == e2_result.source_reference,
                execution_reentry.world_snapshot_id == e2_result.world_snapshot_id,
                envelope.execution_id == e2_result.execution_id,
                envelope.authorization_id == e2_result.authorization_id,
                envelope.requirement_id == e2_result.requirement_id,
                envelope.plan_id == e2_result.plan_id,
                envelope.source_reference == e2_result.source_reference,
                envelope.world_snapshot_id == e2_result.world_snapshot_id,
                state.episode_id == e2_result.episode_id,
                state.status is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY,
                2 <= state.current_step <= state.max_acquisitions,
                state.consumed_acquisitions == state.current_step,
                state.remaining_acquisitions
                == state.max_acquisitions - state.current_step,
                authorization_reentry.episode_id == e2_result.episode_id,
                authorization_reentry.source_reference == e2_result.source_reference,
                authorization_reentry.world_snapshot_id == e2_result.world_snapshot_id,
            )
        )

    @staticmethod
    def _valid_closure(
        e2_result: GovernedInvestigationE2ExecutionAdmissionResult,
        closure: GovernedInvestigationReasoningClosureResult,
    ) -> bool:
        reentry = closure.reasoning_reentry
        state = closure.resulting_episode_state
        prior_state = e2_result.resulting_episode_state
        if reentry is None or prior_state is None:
            return False
        return all(
            (
                closure.episode_id == e2_result.episode_id,
                closure.execution_id == e2_result.execution_id,
                closure.authorization_id == e2_result.authorization_id,
                closure.requirement_id == e2_result.requirement_id,
                closure.plan_id == e2_result.plan_id,
                closure.source_reference == e2_result.source_reference,
                closure.world_snapshot_id == e2_result.world_snapshot_id,
                closure.reasoning_reentry_invocation_count == 1,
                closure.episode_record_invocation_count == 1,
                closure.remaining_acquisitions
                == closure.resulting_episode_state.remaining_acquisitions,
                reentry.execution_id == e2_result.execution_id,
                reentry.authorization_id == e2_result.authorization_id,
                reentry.requirement_id == e2_result.requirement_id,
                reentry.plan_id == e2_result.plan_id,
                reentry.source_reference == e2_result.source_reference,
                reentry.world_snapshot_id == e2_result.world_snapshot_id,
                reentry.reentry_id not in prior_state.reentry_ids,
                state.episode_id == e2_result.episode_id,
                state.current_step == prior_state.current_step,
                state.remaining_acquisitions == prior_state.remaining_acquisitions,
                state.reentry_ids == (*prior_state.reentry_ids, reentry.reentry_id),
                (
                    closure.status is GovernedInvestigationReasoningClosureStatus.CLOSED
                    and closure.episode_closed
                    and closure.stopping_reason
                    is GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
                    and state.status is GovernedInvestigationEpisodeStatus.CLOSED
                    and state.stopping_reason
                    is GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
                    and state.remaining_acquisitions == 0
                    or closure.status
                    is GovernedInvestigationReasoningClosureStatus.RECORDED
                    and not closure.episode_closed
                    and closure.stopping_reason
                    is GovernedInvestigationStoppingReason.NONE
                    and state.status
                    is GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
                    and state.stopping_reason
                    is GovernedInvestigationStoppingReason.NONE
                    and state.remaining_acquisitions > 0
                ),
            )
        )

    @staticmethod
    def _review_after_closure(
        e2_result: GovernedInvestigationE2ExecutionAdmissionResult,
        closure: GovernedInvestigationReasoningClosureResult,
        rationale_codes: tuple[str, ...],
    ) -> GovernedInvestigationRR2TerminalClosureResult:
        return GovernedInvestigationRR2TerminalClosureResult(
            thread_id=e2_result.thread_id,
            checkpoint_id=e2_result.checkpoint_id,
            episode_id=e2_result.episode_id,
            originating_reasoning_id=e2_result.originating_reasoning_id,
            execution_id=e2_result.execution_id,
            authorization_id=e2_result.authorization_id,
            requirement_id=e2_result.requirement_id,
            plan_id=e2_result.plan_id,
            source_reference=e2_result.source_reference,
            world_snapshot_id=e2_result.world_snapshot_id,
            status=GovernedInvestigationRR2TerminalClosureStatus.REVIEW_REQUIRED,
            closure=closure,
            reasoning_reentry=None,
            resulting_episode_state=None,
            reasoning_reentry_id=None,
            stopping_reason=None,
            rationale_codes=rationale_codes,
            reasoning_closure_invocation_count=1,
            reasoning_reentry_invocation_count=(
                closure.reasoning_reentry_invocation_count
            ),
            episode_record_invocation_count=closure.episode_record_invocation_count,
            episode_closed=False,
        )

    @staticmethod
    def _closed(
        e2_result: GovernedInvestigationE2ExecutionAdmissionResult,
        status: GovernedInvestigationRR2TerminalClosureStatus,
        rationale_codes: tuple[str, ...],
        *,
        reasoning_closure_invocation_count: int = 0,
    ) -> GovernedInvestigationRR2TerminalClosureResult:
        return GovernedInvestigationRR2TerminalClosureResult(
            thread_id=e2_result.thread_id,
            checkpoint_id=e2_result.checkpoint_id,
            episode_id=e2_result.episode_id,
            originating_reasoning_id=e2_result.originating_reasoning_id,
            execution_id=e2_result.execution_id,
            authorization_id=e2_result.authorization_id,
            requirement_id=e2_result.requirement_id,
            plan_id=e2_result.plan_id,
            source_reference=e2_result.source_reference,
            world_snapshot_id=e2_result.world_snapshot_id,
            status=status,
            closure=None,
            reasoning_reentry=None,
            resulting_episode_state=None,
            reasoning_reentry_id=None,
            stopping_reason=None,
            rationale_codes=rationale_codes,
            reasoning_closure_invocation_count=reasoning_closure_invocation_count,
            reasoning_reentry_invocation_count=0,
            episode_record_invocation_count=0,
            episode_closed=False,
        )
