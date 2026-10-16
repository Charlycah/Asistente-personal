from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


class GovernedLevel2BProductiveEntryStatus(StrEnum):
    ADMITTED = "admitted"
    NOT_ELIGIBLE = "not_eligible"
    ALREADY_ADMITTED = "already_admitted"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedLevel2BProductiveEntryResult:
    entry_id: str
    status: GovernedLevel2BProductiveEntryStatus
    originating_reasoning_id: str
    source_requirement: DiscriminatingEvidenceRequirement
    requirement_id: str
    episode_id: str | None
    episode_state: GovernedInvestigationEpisodeState | None
    source_reference: str
    world_snapshot_id: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-level2b-productive-entry-v1"
    canonical_episode_authority: str = "multistep_investigation_episode_boundary"
    eligible_for_existing_planning: bool = False
    episode_start_invocation_count: int = 0
    planning_execution_authorized: bool = False
    invokes_planning: bool = False
    invokes_authorization: bool = False
    invokes_execution: bool = False
    invokes_reasoning: bool = False
    invokes_curiosity: bool = False
    creates_questions: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    permits_retry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.entry_id.startswith("level2b-productive-entry-"):
            raise ValueError("productive entry identifier is invalid")
        if (
            self.status is not GovernedLevel2BProductiveEntryStatus.NOT_ELIGIBLE
            and not self.originating_reasoning_id.strip()
        ):
            raise ValueError("productive entry requires reasoning lineage")
        if self.requirement_id != self.source_requirement.requirement_id:
            raise ValueError("productive entry must preserve requirement identity")
        if self.source_reference != self.source_requirement.source_reference:
            raise ValueError("productive entry must preserve source lineage")
        if self.world_snapshot_id != self.source_requirement.world_snapshot_id:
            raise ValueError("productive entry must preserve snapshot lineage")
        if self.episode_start_invocation_count not in {0, 1}:
            raise ValueError("productive entry permits at most one episode start")
        if self.status is GovernedLevel2BProductiveEntryStatus.ADMITTED:
            if self.episode_start_invocation_count != 1:
                raise ValueError("admitted entry requires one episode start")
            if self.episode_state is None or self.episode_id is None:
                raise ValueError("admitted entry requires episode state")
            if self.episode_state.episode_id != self.episode_id:
                raise ValueError("productive entry must preserve episode identity")
            if self.episode_state.requirement_ids != (self.requirement_id,):
                raise ValueError("productive entry must preserve initial requirement")
            if (
                self.episode_state.originating_reasoning_id
                != self.originating_reasoning_id
            ):
                raise ValueError("productive entry must preserve reasoning lineage")
        elif self.status is GovernedLevel2BProductiveEntryStatus.ALREADY_ADMITTED:
            if self.episode_start_invocation_count != 0:
                raise ValueError("duplicate admission cannot restart episode")
            if self.episode_id is None:
                raise ValueError("duplicate admission must expose existing episode id")
        elif self.status is GovernedLevel2BProductiveEntryStatus.NOT_ELIGIBLE:
            if self.episode_start_invocation_count != 0:
                raise ValueError("non-eligible entry cannot start an episode")
            if self.episode_state is not None:
                raise ValueError("non-eligible entry cannot expose episode state")
        else:
            if self.episode_start_invocation_count != 1:
                raise ValueError("review entry must reflect one failed start")
            if self.episode_state is not None:
                raise ValueError("review entry cannot expose accepted episode state")
        expected_planning_eligibility = (
            self.status is GovernedLevel2BProductiveEntryStatus.ADMITTED
            and self.episode_state is not None
            and self.episode_state.status is GovernedInvestigationEpisodeStatus.OPEN
            and self.episode_state.remaining_acquisitions == 2
        )
        if self.eligible_for_existing_planning != expected_planning_eligibility:
            raise ValueError("planning eligibility must derive only from admission")
        if self.canonical_episode_authority != (
            "multistep_investigation_episode_boundary"
        ):
            raise ValueError("productive entry must preserve episode authority")
        if any(
            (
                self.planning_execution_authorized,
                self.invokes_planning,
                self.invokes_authorization,
                self.invokes_execution,
                self.invokes_reasoning,
                self.invokes_curiosity,
                self.creates_questions,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError("productive entry violates governed limits")


class GovernedLevel2BProductiveEntryFoundationV1:
    """Admit one governed R1 into the existing bounded episode lifecycle."""

    def __init__(
        self,
        episode_boundary: GovernedMultiStepInvestigationEpisodeBoundaryV1
        | None = None,
    ) -> None:
        self._episode_boundary = (
            episode_boundary or GovernedMultiStepInvestigationEpisodeBoundaryV1()
        )
        self._admitted: dict[str, str] = {}

    def admit(
        self,
        requirement: DiscriminatingEvidenceRequirement,
        *,
        originating_reasoning_id: str,
    ) -> GovernedLevel2BProductiveEntryResult:
        error = self._eligibility_error(requirement, originating_reasoning_id)
        fingerprint = self._admission_fingerprint(
            requirement,
            originating_reasoning_id,
        )
        if error is not None:
            return self._result(
                requirement,
                originating_reasoning_id,
                fingerprint,
                GovernedLevel2BProductiveEntryStatus.NOT_ELIGIBLE,
                None,
                None,
                (error,),
                episode_start_invocation_count=0,
            )
        existing_episode_id = self._admitted.get(fingerprint)
        if existing_episode_id is not None:
            return self._result(
                requirement,
                originating_reasoning_id,
                fingerprint,
                GovernedLevel2BProductiveEntryStatus.ALREADY_ADMITTED,
                existing_episode_id,
                None,
                ("level2b_entry:admission_lineage_already_consumed",),
                episode_start_invocation_count=0,
            )
        try:
            transition = self._episode_boundary.start(
                originating_reasoning_id=originating_reasoning_id,
                source_reference=requirement.source_reference,
                world_snapshot_id=requirement.world_snapshot_id,
                initial_requirement_id=requirement.requirement_id,
            )
        except Exception:
            return self._result(
                requirement,
                originating_reasoning_id,
                fingerprint,
                GovernedLevel2BProductiveEntryStatus.REVIEW_REQUIRED,
                None,
                None,
                ("level2b_entry:episode_start_failed",),
                episode_start_invocation_count=1,
            )
        state = transition.state
        if (
            transition.decision
            is not GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
            or state.status is not GovernedInvestigationEpisodeStatus.OPEN
            or state.requirement_ids != (requirement.requirement_id,)
            or state.originating_reasoning_id != originating_reasoning_id
            or state.source_reference != requirement.source_reference
            or state.world_snapshot_id != requirement.world_snapshot_id
            or state.max_acquisitions != 2
            or state.consumed_acquisitions != 0
            or state.remaining_acquisitions != 2
            or state.planning_execution_authorized
        ):
            return self._result(
                requirement,
                originating_reasoning_id,
                fingerprint,
                GovernedLevel2BProductiveEntryStatus.REVIEW_REQUIRED,
                state.episode_id,
                None,
                ("level2b_entry:episode_start_contract_mismatch",),
                episode_start_invocation_count=1,
            )
        self._admitted[fingerprint] = state.episode_id
        return self._result(
            requirement,
            originating_reasoning_id,
            fingerprint,
            GovernedLevel2BProductiveEntryStatus.ADMITTED,
            state.episode_id,
            state,
            (
                "level2b_entry:governed_r1_admitted_to_existing_episode_boundary",
                *transition.rationale_codes,
            ),
            episode_start_invocation_count=1,
        )

    @staticmethod
    def _eligibility_error(
        requirement: DiscriminatingEvidenceRequirement,
        originating_reasoning_id: str,
    ) -> str | None:
        if not originating_reasoning_id.strip():
            return "level2b_entry:originating_reasoning_lineage_required"
        if not requirement.read_only:
            return "level2b_entry:read_only_requirement_required"
        if any(
            (
                requirement.creates_acquisition_plan,
                requirement.acquires_evidence,
                requirement.creates_question,
                requirement.modifies_memory,
                requirement.executes_actions,
            )
        ):
            return "level2b_entry:non_executive_requirement_required"
        if not requirement.source_reference.strip():
            return "level2b_entry:source_lineage_required"
        if not requirement.world_snapshot_id.strip():
            return "level2b_entry:snapshot_lineage_required"
        return None

    @staticmethod
    def _admission_fingerprint(
        requirement: DiscriminatingEvidenceRequirement,
        originating_reasoning_id: str,
    ) -> str:
        return sha256(
            repr(
                (
                    originating_reasoning_id,
                    requirement.requirement_id,
                    requirement.source_reference,
                    requirement.world_snapshot_id,
                )
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _result(
        requirement: DiscriminatingEvidenceRequirement,
        originating_reasoning_id: str,
        fingerprint: str,
        status: GovernedLevel2BProductiveEntryStatus,
        episode_id: str | None,
        episode_state: GovernedInvestigationEpisodeState | None,
        rationale_codes: tuple[str, ...],
        *,
        episode_start_invocation_count: int,
    ) -> GovernedLevel2BProductiveEntryResult:
        return GovernedLevel2BProductiveEntryResult(
            entry_id=f"level2b-productive-entry-{fingerprint[:24]}",
            status=status,
            originating_reasoning_id=originating_reasoning_id,
            source_requirement=requirement,
            requirement_id=requirement.requirement_id,
            episode_id=episode_id,
            episode_state=episode_state,
            source_reference=requirement.source_reference,
            world_snapshot_id=requirement.world_snapshot_id,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
            eligible_for_existing_planning=(
                status is GovernedLevel2BProductiveEntryStatus.ADMITTED
            ),
            episode_start_invocation_count=episode_start_invocation_count,
        )
