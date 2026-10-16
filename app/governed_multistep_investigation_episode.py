from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from hashlib import sha256
from typing import TYPE_CHECKING

from app.governed_independence_authorization_boundary import (
    GovernedInitiationDecision,
)
from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumption,
)
from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.planning_foundation import PlanningFoundation
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

if TYPE_CHECKING:
    from app.governed_local_evidence_reasoning_reentry import (
        GovernedLocalEvidenceReasoningReentryResult,
    )


GOVERNED_INVESTIGATION_MAX_ACQUISITIONS = 4


class GovernedInvestigationEpisodeStatus(StrEnum):
    OPEN = "open"
    AWAITING_REENTRY = "awaiting_reentry"
    AWAITING_REQUIREMENT = "awaiting_requirement"
    READY_FOR_PLANNING = "ready_for_planning"
    CLOSED = "closed"
    REVIEW_REQUIRED = "review_required"


class GovernedInvestigationContinuationDecision(StrEnum):
    CONTINUE_ALLOWED = "continue_allowed"
    STOP_REQUIRED = "stop_required"
    REVIEW_REQUIRED = "review_required"


class GovernedInvestigationStoppingReason(StrEnum):
    NONE = "none"
    RESOLVED = "resolved"
    BUDGET_EXHAUSTED = "budget_exhausted"
    NO_NEW_REQUIREMENT = "no_new_requirement"
    NOT_AUTHORIZED = "not_authorized"
    ACQUISITION_UNAVAILABLE = "acquisition_unavailable"
    ACQUISITION_FAILED = "acquisition_failed"
    REVIEW_REQUIRED = "review_required"
    LINEAGE_BROKEN = "lineage_broken"
    SNAPSHOT_CONFLICT = "snapshot_conflict"
    MANUAL_STOP = "manual_stop"


@dataclass(frozen=True)
class GovernedInvestigationEpisodeState:
    episode_id: str
    originating_reasoning_id: str
    source_reference: str
    world_snapshot_id: str
    requirement_ids: tuple[str, ...]
    plan_ids: tuple[str, ...] = ()
    authorization_ids: tuple[str, ...] = ()
    execution_ids: tuple[str, ...] = ()
    local_execution_ids: tuple[str, ...] = ()
    reentry_ids: tuple[str, ...] = ()
    consumed_acquisitions: int = 0
    current_step: int = 1
    status: GovernedInvestigationEpisodeStatus = GovernedInvestigationEpisodeStatus.OPEN
    stopping_reason: GovernedInvestigationStoppingReason = (
        GovernedInvestigationStoppingReason.NONE
    )
    schema_version: str = "post-m409.1-multistep-investigation-episode-v1"
    canonical_planning_authority: str = "planning_foundation"
    max_acquisitions: int = 2
    read_only: bool = True
    planning_execution_authorized: bool = False
    persists_results: bool = False
    invokes_capabilities: bool = False
    performs_reasoning: bool = False
    creates_questions: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.episode_id.startswith("investigation-episode-"):
            raise ValueError("investigation episode identifier is invalid")
        if not self.originating_reasoning_id.strip():
            raise ValueError("investigation episode requires reasoning lineage")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("investigation episode requires source lineage")
        if not self.requirement_ids:
            raise ValueError("investigation episode requires an initial requirement")
        if len(self.requirement_ids) != len(set(self.requirement_ids)):
            raise ValueError("investigation requirement ids must be unique")
        for values, label in (
            (self.plan_ids, "plan"),
            (self.authorization_ids, "authorization"),
            (self.execution_ids, "execution"),
            (self.local_execution_ids, "local execution"),
            (self.reentry_ids, "reentry"),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"investigation {label} ids must be unique")
        if type(self.max_acquisitions) is not int or not (
            1 <= self.max_acquisitions <= GOVERNED_INVESTIGATION_MAX_ACQUISITIONS
        ):
            raise ValueError("investigation budget must be an integer in range 1..4")
        if not 0 <= self.consumed_acquisitions <= self.max_acquisitions:
            raise ValueError("investigation acquisition count is invalid")
        total_executions = len(self.execution_ids) + len(self.local_execution_ids)
        if self.consumed_acquisitions != total_executions:
            raise ValueError("consumed acquisitions must match acquired executions")
        if len(self.reentry_ids) > total_executions:
            raise ValueError("re-entry lineage cannot exceed acquired executions")
        if len(self.plan_ids) != len(self.execution_ids):
            raise ValueError("each acquired execution requires unique plan lineage")
        if len(self.authorization_ids) != len(self.execution_ids):
            raise ValueError(
                "each acquired execution requires unique authorization lineage"
            )
        if type(self.current_step) is not int or not (
            1 <= self.current_step <= self.max_acquisitions
        ):
            raise ValueError("investigation current step is outside governed budget")
        if len(self.requirement_ids) != self.current_step:
            raise ValueError(
                "investigation requirement lineage must match current step"
            )
        if self.canonical_planning_authority != "planning_foundation":
            raise ValueError("episode must remain under planning foundation")
        if not self.read_only or any(
            (
                self.planning_execution_authorized,
                self.persists_results,
                self.invokes_capabilities,
                self.performs_reasoning,
                self.creates_questions,
                self.modifies_memory,
                self.modifies_world_model,
                self.starts_background_process,
            )
        ):
            raise ValueError("investigation episode violates governed limits")
        if self.status is GovernedInvestigationEpisodeStatus.CLOSED:
            if self.stopping_reason is GovernedInvestigationStoppingReason.NONE:
                raise ValueError("closed investigation requires stopping reason")
        elif (
            self.status is GovernedInvestigationEpisodeStatus.REVIEW_REQUIRED
            and self.stopping_reason
            not in {
                GovernedInvestigationStoppingReason.REVIEW_REQUIRED,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                GovernedInvestigationStoppingReason.SNAPSHOT_CONFLICT,
            }
        ):
            raise ValueError("review state requires a review stopping reason")

    @property
    def remaining_acquisitions(self) -> int:
        return self.max_acquisitions - self.consumed_acquisitions

    @property
    def current_requirement_id(self) -> str:
        return self.requirement_ids[-1]


@dataclass(frozen=True)
class GovernedInvestigationEpisodeTransition:
    decision: GovernedInvestigationContinuationDecision
    state: GovernedInvestigationEpisodeState
    rationale_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("investigation transition requires rationale codes")


class GovernedMultiStepInvestigationEpisodeBoundaryV1:
    """Bounded state transitions; never planning, authorization, or execution."""

    def __init__(self, planning_foundation: PlanningFoundation | None = None) -> None:
        self._planning_foundation = planning_foundation or PlanningFoundation()
        snapshot = self._planning_foundation.snapshot
        if snapshot.canonical_authority != "planning_foundation":
            raise ValueError("canonical planning authority is required")
        if not snapshot.read_only or snapshot.planning_execution_authorized:
            raise ValueError("planning foundation must remain read-only")

    def start(
        self,
        *,
        originating_reasoning_id: str,
        source_reference: str,
        world_snapshot_id: str,
        initial_requirement_id: str,
        max_acquisitions: int = 2,
    ) -> GovernedInvestigationEpisodeTransition:
        if type(max_acquisitions) is not int or not (
            1 <= max_acquisitions <= GOVERNED_INVESTIGATION_MAX_ACQUISITIONS
        ):
            raise ValueError("investigation budget must be an integer in range 1..4")
        identity_parts: tuple[object, ...] = (
            originating_reasoning_id,
            source_reference,
            world_snapshot_id,
            initial_requirement_id,
        )
        if max_acquisitions != 2:
            identity_parts = (*identity_parts, max_acquisitions)
        fingerprint = sha256(repr(identity_parts).encode("utf-8")).hexdigest()
        state = GovernedInvestigationEpisodeState(
            episode_id=f"investigation-episode-{fingerprint[:24]}",
            originating_reasoning_id=originating_reasoning_id,
            source_reference=source_reference,
            world_snapshot_id=world_snapshot_id,
            requirement_ids=(initial_requirement_id,),
            max_acquisitions=max_acquisitions,
        )
        return self._transition(
            GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
            state,
            ("investigation:episode_opened_under_planning_foundation",),
        )

    def record_acquisition(
        self,
        state: GovernedInvestigationEpisodeState,
        envelope: GovernedAcquiredEvidenceEnvelope,
    ) -> GovernedInvestigationEpisodeTransition:
        if state.status not in {
            GovernedInvestigationEpisodeStatus.OPEN,
            GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
        }:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:acquisition_not_expected_in_current_state",
            )
        lineage_error = self._execution_lineage_error(state, envelope)
        if lineage_error is not None:
            return self._review(
                state,
                lineage_error[0],
                lineage_error[1],
            )
        if envelope.status is GovernedLevel2ExecutionStatus.UNAVAILABLE:
            return self._close(
                state,
                GovernedInvestigationStoppingReason.ACQUISITION_UNAVAILABLE,
                "investigation:authorized_acquisition_unavailable",
            )
        if envelope.status is GovernedLevel2ExecutionStatus.FAILED:
            return self._close(
                state,
                GovernedInvestigationStoppingReason.ACQUISITION_FAILED,
                "investigation:acquisition_failed_without_retry",
            )
        if envelope.status in {
            GovernedLevel2ExecutionStatus.DENIED,
            GovernedLevel2ExecutionStatus.REVIEW_REQUIRED,
        }:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.REVIEW_REQUIRED,
                "investigation:execution_not_admissible",
            )
        if state.remaining_acquisitions <= 0:
            return self._close(
                state,
                GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED,
                "investigation:budget_already_exhausted",
            )
        next_state = replace(
            state,
            plan_ids=(*state.plan_ids, envelope.plan_id),
            authorization_ids=(
                *state.authorization_ids,
                envelope.authorization_id,
            ),
            execution_ids=(*state.execution_ids, envelope.execution_id),
            consumed_acquisitions=state.consumed_acquisitions + 1,
            status=GovernedInvestigationEpisodeStatus.AWAITING_REENTRY,
        )
        return self._transition(
            GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
            next_state,
            ("investigation:one_acquisition_recorded",),
        )

    def record_local_evidence_reentry(
        self,
        state: GovernedInvestigationEpisodeState,
        reentry: "GovernedLocalEvidenceReasoningReentryResult",
    ) -> GovernedInvestigationEpisodeTransition:
        from app.governed_local_evidence_reasoning_reentry import (
            GovernedLocalEvidenceReasoningReentryStatus,
        )

        if (
            reentry.knowledge_execution_id in state.local_execution_ids
            or reentry.reentry_id in state.reentry_ids
        ):
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:local_execution_or_reentry_lineage_reused",
            )
        if state.status not in {
            GovernedInvestigationEpisodeStatus.OPEN,
            GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
        }:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:local_reentry_not_expected_in_current_state",
            )
        if (
            reentry.episode_id != state.episode_id
            or reentry.originating_reasoning_id != state.originating_reasoning_id
            or reentry.requirement_id != state.current_requirement_id
        ):
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:local_reentry_lineage_mismatch",
            )
        # Source and snapshot lineage remain owned by the episode state. The local
        # re-entry already validated them against the original requirement before
        # reasoning, so this boundary never substitutes selected source lineage.
        if not state.source_reference.strip() or not state.world_snapshot_id.strip():
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:local_reentry_source_lineage_missing",
            )
        if (
            reentry.status
            is not GovernedLocalEvidenceReasoningReentryStatus.REEVALUATED
        ):
            return self._review(
                state,
                GovernedInvestigationStoppingReason.REVIEW_REQUIRED,
                "investigation:successful_local_reentry_required",
            )
        if not reentry.knowledge_execution_id or not reentry.selected_source_reference:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:local_execution_lineage_missing",
            )
        if state.remaining_acquisitions <= 0:
            return self._close(
                state,
                GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED,
                "investigation:budget_already_exhausted",
            )

        next_local_executions = (
            *state.local_execution_ids,
            reentry.knowledge_execution_id,
        )
        next_reentries = (*state.reentry_ids, reentry.reentry_id)
        next_consumed = state.consumed_acquisitions + 1
        if next_consumed == state.max_acquisitions:
            next_state = replace(
                state,
                local_execution_ids=next_local_executions,
                reentry_ids=next_reentries,
                consumed_acquisitions=next_consumed,
                status=GovernedInvestigationEpisodeStatus.CLOSED,
                stopping_reason=GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED,
            )
            return self._transition(
                GovernedInvestigationContinuationDecision.STOP_REQUIRED,
                next_state,
                ("investigation:local_reentry_closes_exhausted_budget_episode",),
            )

        next_state = replace(
            state,
            local_execution_ids=next_local_executions,
            reentry_ids=next_reentries,
            consumed_acquisitions=next_consumed,
            status=GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT,
        )
        return self._transition(
            GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
            next_state,
            ("investigation:local_reentry_may_present_new_requirement",),
        )

    def record_reentry(
        self,
        state: GovernedInvestigationEpisodeState,
        reentry: GovernedLevel2ReasoningReentryResult,
    ) -> GovernedInvestigationEpisodeTransition:
        if state.status is not GovernedInvestigationEpisodeStatus.AWAITING_REENTRY:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:reentry_not_expected_in_current_state",
            )
        if not state.execution_ids or reentry.execution_id != state.execution_ids[-1]:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:reentry_execution_lineage_mismatch",
            )
        if (
            reentry.authorization_id != state.authorization_ids[-1]
            or reentry.requirement_id != state.current_requirement_id
            or reentry.plan_id != state.plan_ids[-1]
            or reentry.source_reference != state.source_reference
        ):
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:reentry_lineage_mismatch",
            )
        if reentry.world_snapshot_id != state.world_snapshot_id:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.SNAPSHOT_CONFLICT,
                "investigation:reentry_snapshot_conflict",
            )
        if reentry.status is not GovernedReasoningReentryStatus.REEVALUATED:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.REVIEW_REQUIRED,
                "investigation:successful_reentry_required",
            )
        if reentry.reentry_id in state.reentry_ids:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:reentry_lineage_reused",
            )
        next_reentries = (*state.reentry_ids, reentry.reentry_id)
        if state.consumed_acquisitions == state.max_acquisitions:
            next_state = replace(
                state,
                reentry_ids=next_reentries,
                status=GovernedInvestigationEpisodeStatus.CLOSED,
                stopping_reason=(GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED),
            )
            rationale = (
                "investigation:second_reentry_closes_fixed_budget_episode"
                if state.max_acquisitions == 2
                else "investigation:reentry_closes_exhausted_budget_episode"
            )
            return self._transition(
                GovernedInvestigationContinuationDecision.STOP_REQUIRED,
                next_state,
                (rationale,),
            )
        next_state = replace(
            state,
            reentry_ids=next_reentries,
            status=GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT,
        )
        rationale = (
            "investigation:first_reentry_may_present_new_requirement"
            if state.max_acquisitions == 2
            else "investigation:reentry_may_present_new_requirement"
        )
        return self._transition(
            GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
            next_state,
            (rationale,),
        )

    def evaluate_continuation(
        self,
        state: GovernedInvestigationEpisodeState,
        requirement: DiscriminatingEvidenceRequirement | None,
    ) -> GovernedInvestigationEpisodeTransition:
        if state.status is not GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:continuation_not_expected_in_current_state",
            )
        if state.remaining_acquisitions <= 0:
            return self._close(
                state,
                GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED,
                "investigation:no_continuation_budget_available",
            )
        if requirement is None:
            return self._close(
                state,
                GovernedInvestigationStoppingReason.NO_NEW_REQUIREMENT,
                "investigation:no_new_discriminating_requirement",
            )
        if requirement.requirement_id in state.requirement_ids:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:requirement_reuse_forbidden_in_v1",
            )
        if requirement.source_reference != state.source_reference:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:requirement_source_lineage_mismatch",
            )
        if requirement.world_snapshot_id != state.world_snapshot_id:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.SNAPSHOT_CONFLICT,
                "investigation:requirement_snapshot_conflict",
            )
        next_state = replace(
            state,
            requirement_ids=(*state.requirement_ids, requirement.requirement_id),
            current_step=state.current_step + 1,
            status=GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
        )
        return self._transition(
            GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
            next_state,
            ("investigation:new_requirement_may_reenter_existing_planning",),
        )

    def record_authorization_stop(
        self,
        state: GovernedInvestigationEpisodeState,
        authorization: GovernedIndependenceAuthorizationProductiveConsumption,
    ) -> GovernedInvestigationEpisodeTransition:
        if authorization.requirement_id != state.current_requirement_id:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:authorization_requirement_mismatch",
            )
        if (
            authorization.source_reference != state.source_reference
            or authorization.world_snapshot_id != state.world_snapshot_id
        ):
            return self._review(
                state,
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:authorization_source_lineage_mismatch",
            )
        if authorization.decision is GovernedInitiationDecision.MAY_INITIATE:
            return self._transition(
                GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
                state,
                ("investigation:authorization_may_continue_to_existing_gateway",),
            )
        if authorization.decision is GovernedInitiationDecision.REVIEW_REQUIRED:
            return self._review(
                state,
                GovernedInvestigationStoppingReason.REVIEW_REQUIRED,
                "investigation:authorization_review_required",
            )
        return self._close(
            state,
            GovernedInvestigationStoppingReason.NOT_AUTHORIZED,
            "investigation:authorization_does_not_permit_level2_continuation",
        )

    def manual_stop(
        self,
        state: GovernedInvestigationEpisodeState,
    ) -> GovernedInvestigationEpisodeTransition:
        return self._close(
            state,
            GovernedInvestigationStoppingReason.MANUAL_STOP,
            "investigation:manual_stop",
        )

    @staticmethod
    def _execution_lineage_error(
        state: GovernedInvestigationEpisodeState,
        envelope: GovernedAcquiredEvidenceEnvelope,
    ) -> tuple[GovernedInvestigationStoppingReason, str] | None:
        if envelope.requirement_id != state.current_requirement_id:
            return (
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:execution_requirement_mismatch",
            )
        if envelope.source_reference != state.source_reference:
            return (
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:execution_source_lineage_mismatch",
            )
        if envelope.world_snapshot_id != state.world_snapshot_id:
            return (
                GovernedInvestigationStoppingReason.SNAPSHOT_CONFLICT,
                "investigation:execution_snapshot_conflict",
            )
        if envelope.execution_id in state.execution_ids:
            return (
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:execution_lineage_reused",
            )
        if envelope.plan_id in state.plan_ids:
            return (
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:plan_lineage_reused",
            )
        if envelope.authorization_id in state.authorization_ids:
            return (
                GovernedInvestigationStoppingReason.LINEAGE_BROKEN,
                "investigation:authorization_lineage_reused",
            )
        return None

    @staticmethod
    def _transition(
        decision: GovernedInvestigationContinuationDecision,
        state: GovernedInvestigationEpisodeState,
        rationale_codes: tuple[str, ...],
    ) -> GovernedInvestigationEpisodeTransition:
        return GovernedInvestigationEpisodeTransition(
            decision=decision,
            state=state,
            rationale_codes=rationale_codes,
        )

    @classmethod
    def _close(
        cls,
        state: GovernedInvestigationEpisodeState,
        reason: GovernedInvestigationStoppingReason,
        rationale: str,
    ) -> GovernedInvestigationEpisodeTransition:
        closed = replace(
            state,
            status=GovernedInvestigationEpisodeStatus.CLOSED,
            stopping_reason=reason,
        )
        return cls._transition(
            GovernedInvestigationContinuationDecision.STOP_REQUIRED,
            closed,
            (rationale,),
        )

    @classmethod
    def _review(
        cls,
        state: GovernedInvestigationEpisodeState,
        reason: GovernedInvestigationStoppingReason,
        rationale: str,
    ) -> GovernedInvestigationEpisodeTransition:
        reviewed = replace(
            state,
            status=GovernedInvestigationEpisodeStatus.REVIEW_REQUIRED,
            stopping_reason=reason,
        )
        return cls._transition(
            GovernedInvestigationContinuationDecision.REVIEW_REQUIRED,
            reviewed,
            (rationale,),
        )
