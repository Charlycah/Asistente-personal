from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from app.governed_multistep_investigation_episode import (
    GOVERNED_INVESTIGATION_MAX_ACQUISITIONS,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
)


class GovernedInvestigationResumeStatus(StrEnum):
    RESUME_CANDIDATE = "resume_candidate"
    SNAPSHOT_REVIEW_REQUIRED = "snapshot_review_required"
    SOURCE_LINEAGE_MISMATCH = "source_lineage_mismatch"
    RESOLVED_INQUIRY = "resolved_inquiry"
    BUDGET_REVIEW_REQUIRED = "budget_review_required"


@dataclass(frozen=True)
class GovernedPassiveInvestigationCheckpoint:
    checkpoint_id: str
    thread_id: str
    episode_id: str
    originating_reasoning_id: str
    source_reference: str
    world_snapshot_ids: tuple[str, ...]
    requirement_ids: tuple[str, ...]
    plan_ids: tuple[str, ...]
    authorization_ids: tuple[str, ...]
    execution_ids: tuple[str, ...]
    reentry_ids: tuple[str, ...]
    consumed_acquisitions: int
    current_step: int
    max_acquisitions: int
    episode_status: GovernedInvestigationEpisodeStatus
    stopping_reason: GovernedInvestigationStoppingReason
    pause_reason: str
    source_fingerprint: str
    schema_version: str = "post-m409.1-long-horizon-checkpoint-v1"
    canonical_planning_authority: str = "planning_foundation"
    read_only: bool = True
    passive: bool = True
    durable_artifact: bool = True
    persists_self: bool = False
    starts_background_process: bool = False
    invokes_capabilities: bool = False
    executes_actions: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    modifies_planning: bool = False
    performs_reasoning: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.checkpoint_id.startswith("investigation-checkpoint-"):
            raise ValueError("investigation checkpoint identifier is invalid")
        if not self.thread_id.startswith("investigation-thread-"):
            raise ValueError("investigation thread identifier is invalid")
        if not self.episode_id.startswith("investigation-episode-"):
            raise ValueError("investigation checkpoint requires episode lineage")
        if not self.originating_reasoning_id.strip():
            raise ValueError("investigation checkpoint requires reasoning lineage")
        if not self.source_reference.strip():
            raise ValueError("investigation checkpoint requires source lineage")
        if not self.world_snapshot_ids or any(
            not item.strip() for item in self.world_snapshot_ids
        ):
            raise ValueError("investigation checkpoint requires snapshot lineage")
        if not self.requirement_ids:
            raise ValueError("investigation checkpoint requires requirement lineage")
        if len(self.requirement_ids) != len(set(self.requirement_ids)):
            raise ValueError("investigation checkpoint requirement ids must be unique")
        for values, label in (
            (self.plan_ids, "plan"),
            (self.authorization_ids, "authorization"),
            (self.execution_ids, "execution"),
            (self.reentry_ids, "reentry"),
        ):
            if len(values) != len(set(values)):
                raise ValueError(
                    f"investigation checkpoint {label} ids must be unique"
                )
        if self.consumed_acquisitions != len(self.execution_ids):
            raise ValueError(
                "investigation checkpoint acquisition lineage is inconsistent"
            )
        if not 0 <= self.consumed_acquisitions <= self.max_acquisitions:
            raise ValueError("investigation checkpoint budget is invalid")
        if type(self.max_acquisitions) is not int or not (
            1
            <= self.max_acquisitions
            <= GOVERNED_INVESTIGATION_MAX_ACQUISITIONS
        ):
            raise ValueError("investigation checkpoint budget is outside 1..4")
        if type(self.current_step) is not int or not (
            1 <= self.current_step <= self.max_acquisitions
        ):
            raise ValueError("investigation checkpoint current step is invalid")
        if len(self.requirement_ids) != self.current_step:
            raise ValueError(
                "investigation checkpoint requirement lineage must match current step"
            )
        if not self.pause_reason.strip():
            raise ValueError("investigation checkpoint requires explicit pause reason")
        if not self.source_fingerprint.strip():
            raise ValueError("investigation checkpoint requires source fingerprint")
        if self.canonical_planning_authority != "planning_foundation":
            raise ValueError("checkpoint must preserve planning authority")
        if not self.read_only or not self.passive or not self.durable_artifact:
            raise ValueError("investigation checkpoint must remain passive/read-only")
        if any(
            (
                self.persists_self,
                self.starts_background_process,
                self.invokes_capabilities,
                self.executes_actions,
                self.modifies_memory,
                self.modifies_world_model,
                self.modifies_planning,
                self.performs_reasoning,
                self.grants_authority,
            )
        ):
            raise ValueError("investigation checkpoint violates governed limits")


@dataclass(frozen=True)
class GovernedInvestigationResumeCandidate:
    resume_id: str
    checkpoint_id: str
    thread_id: str
    previous_world_snapshot_id: str
    current_world_snapshot_id: str
    explicit_resume_reference: str
    status: GovernedInvestigationResumeStatus
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-long-horizon-resume-v1"
    canonical_planning_authority: str = "planning_foundation"
    read_only: bool = True
    consultative: bool = True
    planning_execution_authorized: bool = False
    invokes_capabilities: bool = False
    executes_actions: bool = False
    starts_background_process: bool = False
    performs_reasoning: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    modifies_planning: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.resume_id.startswith("investigation-resume-"):
            raise ValueError("investigation resume identifier is invalid")
        if not self.checkpoint_id.startswith("investigation-checkpoint-"):
            raise ValueError("investigation resume requires checkpoint lineage")
        if not self.thread_id.startswith("investigation-thread-"):
            raise ValueError("investigation resume requires thread lineage")
        if not self.previous_world_snapshot_id.strip():
            raise ValueError("investigation resume requires previous snapshot")
        if not self.current_world_snapshot_id.strip():
            raise ValueError("investigation resume requires current snapshot")
        if not self.explicit_resume_reference.strip():
            raise ValueError("investigation resume requires explicit resume reference")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("investigation resume requires rationale codes")
        if not self.source_fingerprint.strip():
            raise ValueError("investigation resume requires source fingerprint")
        if self.canonical_planning_authority != "planning_foundation":
            raise ValueError("resume candidate must preserve planning authority")
        if not self.read_only or not self.consultative:
            raise ValueError("resume candidate must remain consultative/read-only")
        if any(
            (
                self.planning_execution_authorized,
                self.invokes_capabilities,
                self.executes_actions,
                self.starts_background_process,
                self.performs_reasoning,
                self.persists_results,
                self.modifies_memory,
                self.modifies_world_model,
                self.modifies_planning,
                self.grants_authority,
            )
        ):
            raise ValueError("investigation resume candidate violates governed limits")


class GovernedLongHorizonInvestigationContinuityV1:
    """Passive temporal continuity around the existing investigation lifecycle."""

    CANONICAL_PLANNING_AUTHORITY = "planning_foundation"

    def checkpoint(
        self,
        state: GovernedInvestigationEpisodeState,
        *,
        pause_reason: str,
    ) -> GovernedPassiveInvestigationCheckpoint:
        self._validate_state(state)
        if not pause_reason.strip():
            raise ValueError("checkpoint requires explicit pause reason")

        thread_fingerprint = sha256(
            repr(
                (
                    state.originating_reasoning_id,
                    state.source_reference,
                    state.requirement_ids[0],
                )
            ).encode("utf-8")
        ).hexdigest()
        thread_id = f"investigation-thread-{thread_fingerprint[:24]}"
        fingerprint = sha256(
            repr(
                (
                    thread_id,
                    state.episode_id,
                    state.originating_reasoning_id,
                    state.source_reference,
                    state.world_snapshot_id,
                    state.requirement_ids,
                    state.plan_ids,
                    state.authorization_ids,
                    state.execution_ids,
                    state.reentry_ids,
                    state.consumed_acquisitions,
                    state.current_step,
                    state.max_acquisitions,
                    state.status.value,
                    state.stopping_reason.value,
                    pause_reason.strip(),
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedPassiveInvestigationCheckpoint(
            checkpoint_id=f"investigation-checkpoint-{fingerprint[:24]}",
            thread_id=thread_id,
            episode_id=state.episode_id,
            originating_reasoning_id=state.originating_reasoning_id,
            source_reference=state.source_reference,
            world_snapshot_ids=(state.world_snapshot_id,),
            requirement_ids=state.requirement_ids,
            plan_ids=state.plan_ids,
            authorization_ids=state.authorization_ids,
            execution_ids=state.execution_ids,
            reentry_ids=state.reentry_ids,
            consumed_acquisitions=state.consumed_acquisitions,
            current_step=state.current_step,
            max_acquisitions=state.max_acquisitions,
            episode_status=state.status,
            stopping_reason=state.stopping_reason,
            pause_reason=pause_reason.strip(),
            source_fingerprint=fingerprint,
        )

    def resume(
        self,
        checkpoint: GovernedPassiveInvestigationCheckpoint,
        *,
        current_world_snapshot_id: str,
        current_source_reference: str,
        explicit_resume_reference: str,
    ) -> GovernedInvestigationResumeCandidate:
        if not current_world_snapshot_id.strip():
            raise ValueError("resume requires current world snapshot")
        if not current_source_reference.strip():
            raise ValueError("resume requires current source reference")
        if not explicit_resume_reference.strip():
            raise ValueError("resume requires explicit resume reference")

        previous_snapshot = checkpoint.world_snapshot_ids[-1]
        if current_source_reference != checkpoint.source_reference:
            status = GovernedInvestigationResumeStatus.SOURCE_LINEAGE_MISMATCH
            rationale = (
                "investigation_resume:source_lineage_mismatch",
                "investigation_resume:fail_closed",
            )
        elif (
            checkpoint.episode_status is GovernedInvestigationEpisodeStatus.CLOSED
            and checkpoint.stopping_reason
            is GovernedInvestigationStoppingReason.RESOLVED
        ):
            status = GovernedInvestigationResumeStatus.RESOLVED_INQUIRY
            rationale = (
                "investigation_resume:resolved_requirement_not_reactivated",
                "investigation_resume:explicit_new_gap_required",
            )
        elif checkpoint.consumed_acquisitions >= checkpoint.max_acquisitions:
            status = GovernedInvestigationResumeStatus.BUDGET_REVIEW_REQUIRED
            rationale = (
                "investigation_resume:historical_budget_exhausted",
                "investigation_resume:additional_budget_requires_separate_governance",
            )
        elif current_world_snapshot_id != previous_snapshot:
            status = GovernedInvestigationResumeStatus.SNAPSHOT_REVIEW_REQUIRED
            rationale = (
                "investigation_resume:world_snapshot_changed",
                "investigation_resume:previous_snapshot_preserved",
                "investigation_resume:compatibility_review_required",
            )
        else:
            status = GovernedInvestigationResumeStatus.RESUME_CANDIDATE
            rationale = (
                "investigation_resume:explicit_resume_requested",
                "investigation_resume:same_snapshot_continuity",
                "investigation_resume:existing_planning_gates_still_required",
            )

        fingerprint = sha256(
            repr(
                (
                    checkpoint.checkpoint_id,
                    checkpoint.thread_id,
                    checkpoint.source_fingerprint,
                    previous_snapshot,
                    current_world_snapshot_id,
                    current_source_reference,
                    explicit_resume_reference.strip(),
                    status.value,
                    rationale,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedInvestigationResumeCandidate(
            resume_id=f"investigation-resume-{fingerprint[:24]}",
            checkpoint_id=checkpoint.checkpoint_id,
            thread_id=checkpoint.thread_id,
            previous_world_snapshot_id=previous_snapshot,
            current_world_snapshot_id=current_world_snapshot_id,
            explicit_resume_reference=explicit_resume_reference.strip(),
            status=status,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _validate_state(state: GovernedInvestigationEpisodeState) -> None:
        if state.canonical_planning_authority != "planning_foundation":
            raise ValueError("checkpoint requires canonical planning lineage")
        if not state.read_only:
            raise ValueError("checkpoint requires read-only episode state")
        if any(
            (
                state.planning_execution_authorized,
                state.persists_results,
                state.invokes_capabilities,
                state.performs_reasoning,
                state.creates_questions,
                state.modifies_memory,
                state.modifies_world_model,
                state.starts_background_process,
            )
        ):
            raise ValueError("checkpoint requires governed episode state")
