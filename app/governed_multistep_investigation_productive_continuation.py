from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationEpisodeTransition,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)


@dataclass(frozen=True)
class GovernedMultiStepInvestigationProductiveContinuation:
    episode_id: str
    source_requirement: DiscriminatingEvidenceRequirement | None
    transition: GovernedInvestigationEpisodeTransition
    decision: GovernedInvestigationContinuationDecision
    resulting_state: GovernedInvestigationEpisodeState
    source_requirement_id: str | None
    source_reference: str
    world_snapshot_id: str
    current_step: int
    remaining_acquisitions: int
    stopping_reason: GovernedInvestigationStoppingReason
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = (
        "post-m409.1-multistep-investigation-productive-continuation-v1"
    )
    canonical_planning_authority: str = "planning_foundation"
    eligible_for_existing_planning: bool = False
    planning_execution_authorized: bool = False
    execution_authorized: bool = False
    invokes_planning: bool = False
    invokes_authorization: bool = False
    invokes_capabilities: bool = False
    invokes_reasoning: bool = False
    creates_requirement: bool = False
    rewrites_requirement: bool = False
    creates_questions: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.episode_id.startswith("investigation-episode-"):
            raise ValueError("productive continuation requires episode identity")
        if self.transition.state != self.resulting_state:
            raise ValueError("productive continuation must preserve transition state")
        if self.transition.decision is not self.decision:
            raise ValueError(
                "productive continuation must preserve transition decision"
            )
        if self.rationale_codes != self.transition.rationale_codes:
            raise ValueError("productive continuation must preserve rationale")
        if self.resulting_state.episode_id != self.episode_id:
            raise ValueError("productive continuation must preserve episode lineage")
        if self.source_reference != self.resulting_state.source_reference:
            raise ValueError("productive continuation must preserve source lineage")
        if self.world_snapshot_id != self.resulting_state.world_snapshot_id:
            raise ValueError("productive continuation must preserve snapshot lineage")
        if self.current_step != self.resulting_state.current_step:
            raise ValueError("productive continuation must preserve current step")
        if self.remaining_acquisitions != (
            self.resulting_state.remaining_acquisitions
        ):
            raise ValueError("productive continuation must preserve budget state")
        if self.stopping_reason is not self.resulting_state.stopping_reason:
            raise ValueError("productive continuation must preserve stopping reason")
        if self.source_requirement is None:
            if self.source_requirement_id is not None:
                raise ValueError("missing requirement cannot expose an id")
        else:
            if (
                self.source_requirement_id
                != self.source_requirement.requirement_id
            ):
                raise ValueError("productive continuation must preserve requirement")
        expected_eligibility = (
            self.decision
            is GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
            and self.resulting_state.status
            is GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING
            and 2 <= self.resulting_state.current_step
            <= self.resulting_state.max_acquisitions
            and self.resulting_state.consumed_acquisitions
            == self.resulting_state.current_step - 1
            and self.resulting_state.remaining_acquisitions > 0
            and self.source_requirement is not None
            and self.source_requirement.requirement_id
            == self.resulting_state.current_requirement_id
        )
        if self.eligible_for_existing_planning != expected_eligibility:
            raise ValueError("planning eligibility must derive only from transition")
        if expected_eligibility and self.source_requirement is not None:
            if self.source_requirement.source_reference != self.source_reference:
                raise ValueError("admitted continuation source mismatch")
            if (
                self.source_requirement.world_snapshot_id
                != self.world_snapshot_id
            ):
                raise ValueError("admitted continuation snapshot mismatch")
        if self.canonical_planning_authority != "planning_foundation":
            raise ValueError("productive continuation must preserve planning authority")
        if any(
            (
                self.planning_execution_authorized,
                self.execution_authorized,
                self.invokes_planning,
                self.invokes_authorization,
                self.invokes_capabilities,
                self.invokes_reasoning,
                self.creates_requirement,
                self.rewrites_requirement,
                self.creates_questions,
                self.modifies_memory,
                self.modifies_world_model,
                self.starts_background_process,
            )
        ):
            raise ValueError("productive continuation violates governed limits")


class GovernedMultiStepInvestigationProductiveContinuationV1:
    """Expose one continuation decision without performing the next step."""

    def __init__(
        self,
        boundary: GovernedMultiStepInvestigationEpisodeBoundaryV1 | None = None,
    ) -> None:
        self._boundary = boundary or GovernedMultiStepInvestigationEpisodeBoundaryV1()

    def consume(
        self,
        state: GovernedInvestigationEpisodeState,
        requirement: DiscriminatingEvidenceRequirement | None,
    ) -> GovernedMultiStepInvestigationProductiveContinuation:
        transition = self._boundary.evaluate_continuation(state, requirement)
        fingerprint = sha256(
            repr(
                (
                    state.episode_id,
                    None if requirement is None else requirement.requirement_id,
                    transition.decision.value,
                    transition.state.current_step,
                    transition.state.remaining_acquisitions,
                    transition.state.stopping_reason.value,
                    transition.rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        eligible = (
            transition.decision
            is GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
            and transition.state.status
            is GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING
            and 2 <= transition.state.current_step
            <= transition.state.max_acquisitions
            and transition.state.consumed_acquisitions
            == transition.state.current_step - 1
            and transition.state.remaining_acquisitions > 0
            and requirement is not None
            and requirement.requirement_id == transition.state.current_requirement_id
        )
        return GovernedMultiStepInvestigationProductiveContinuation(
            episode_id=state.episode_id,
            source_requirement=requirement,
            transition=transition,
            decision=transition.decision,
            resulting_state=transition.state,
            source_requirement_id=(
                None if requirement is None else requirement.requirement_id
            ),
            source_reference=transition.state.source_reference,
            world_snapshot_id=transition.state.world_snapshot_id,
            current_step=transition.state.current_step,
            remaining_acquisitions=transition.state.remaining_acquisitions,
            stopping_reason=transition.state.stopping_reason,
            rationale_codes=transition.rationale_codes,
            source_fingerprint=fingerprint,
            eligible_for_existing_planning=eligible,
        )
