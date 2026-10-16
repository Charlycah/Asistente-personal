from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumption,
    GovernedEvidenceAcquisitionProductiveConsumptionV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeStatus,
)
from app.governed_multistep_investigation_productive_continuation import (
    GovernedMultiStepInvestigationProductiveContinuation,
)
from core.capability_registry import CapabilityRegistryManager
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus


class GovernedInvestigationPlanningReentryStatus(StrEnum):
    PLANNED = "planned"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationPlanningReentryResult:
    episode_id: str
    continuation: GovernedMultiStepInvestigationProductiveContinuation
    status: GovernedInvestigationPlanningReentryStatus
    planning_product: GovernedEvidenceAcquisitionProductiveConsumption | None
    requirement_id: str | None
    plan_id: str | None
    source_reference: str
    world_snapshot_id: str
    current_step: int
    remaining_acquisitions: int
    planning_status: EvidenceAcquisitionPlanningStatus | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = (
        "post-m409.1-multistep-investigation-planning-reentry-v1"
    )
    canonical_planning_authority: str = "planning_foundation"
    eligible_for_authorization: bool = False
    planning_invocation_count: int = 0
    planning_execution_authorized: bool = False
    execution_authorized: bool = False
    invokes_authorization: bool = False
    invokes_capabilities: bool = False
    invokes_reasoning: bool = False
    rewrites_requirement: bool = False
    modifies_episode_state: bool = False
    creates_questions: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.episode_id != self.continuation.episode_id:
            raise ValueError("planning re-entry must preserve episode identity")
        if self.source_reference != self.continuation.source_reference:
            raise ValueError("planning re-entry must preserve source lineage")
        if self.world_snapshot_id != self.continuation.world_snapshot_id:
            raise ValueError("planning re-entry must preserve snapshot lineage")
        if self.current_step != self.continuation.current_step:
            raise ValueError("planning re-entry must preserve current step")
        if self.remaining_acquisitions != (
            self.continuation.remaining_acquisitions
        ):
            raise ValueError("planning re-entry must preserve episode budget")
        if self.planning_invocation_count not in {0, 1}:
            raise ValueError("planning re-entry permits at most one planning call")
        if self.status is GovernedInvestigationPlanningReentryStatus.PLANNED:
            if self.planning_invocation_count != 1:
                raise ValueError("planned result requires exactly one planning call")
            if self.planning_product is None:
                raise ValueError("planned result requires planning product")
            if self.requirement_id != self.planning_product.requirement_id:
                raise ValueError("planning re-entry must preserve requirement lineage")
            if self.plan_id != self.planning_product.planning_report.plan_id:
                raise ValueError("planning re-entry must preserve plan identity")
            if self.planning_status is not self.planning_product.status:
                raise ValueError("planning re-entry must preserve planning status")
        else:
            if self.planning_product is not None or self.plan_id is not None:
                raise ValueError("non-planned result cannot expose a plan")
            if self.planning_invocation_count != (
                1
                if self.status
                is GovernedInvestigationPlanningReentryStatus.REVIEW_REQUIRED
                else 0
            ):
                raise ValueError("planning invocation count is inconsistent")
        expected_authorization_eligibility = (
            self.status is GovernedInvestigationPlanningReentryStatus.PLANNED
            and self.planning_status is EvidenceAcquisitionPlanningStatus.PLANNABLE
        )
        if self.eligible_for_authorization != expected_authorization_eligibility:
            raise ValueError(
                "authorization eligibility must derive only from valid planning"
            )
        if self.canonical_planning_authority != "planning_foundation":
            raise ValueError("planning re-entry must preserve planning authority")
        if any(
            (
                self.planning_execution_authorized,
                self.execution_authorized,
                self.invokes_authorization,
                self.invokes_capabilities,
                self.invokes_reasoning,
                self.rewrites_requirement,
                self.modifies_episode_state,
                self.creates_questions,
                self.modifies_memory,
                self.modifies_world_model,
                self.starts_background_process,
            )
        ):
            raise ValueError("planning re-entry violates governed limits")


class GovernedMultiStepInvestigationPlanningReentryV1:
    """Invoke existing Evidence Acquisition Planning once for an admitted step."""

    def __init__(
        self,
        registry: CapabilityRegistryManager,
        planning_surface: GovernedEvidenceAcquisitionProductiveConsumptionV1
        | None = None,
    ) -> None:
        self._planning_surface = (
            planning_surface
            or GovernedEvidenceAcquisitionProductiveConsumptionV1(registry)
        )

    def consume(
        self,
        continuation: GovernedMultiStepInvestigationProductiveContinuation,
    ) -> GovernedInvestigationPlanningReentryResult:
        eligibility_error = self._eligibility_error(continuation)
        if eligibility_error is not None:
            return self._result(
                continuation,
                GovernedInvestigationPlanningReentryStatus.NOT_ELIGIBLE,
                None,
                (eligibility_error,),
                planning_invocation_count=0,
            )

        requirement = continuation.source_requirement
        if requirement is None:
            return self._result(
                continuation,
                GovernedInvestigationPlanningReentryStatus.NOT_ELIGIBLE,
                None,
                ("planning_reentry:governed_requirement_required",),
                planning_invocation_count=0,
            )

        try:
            planning_product = self._planning_surface.consume(requirement)
        except Exception:
            return self._result(
                continuation,
                GovernedInvestigationPlanningReentryStatus.REVIEW_REQUIRED,
                None,
                ("planning_reentry:single_planning_invocation_failed",),
                planning_invocation_count=1,
            )

        planning = planning_product.planning_report
        if (
            planning.requirement_id != requirement.requirement_id
            or planning.source_reference != continuation.source_reference
            or planning.world_snapshot_id != continuation.world_snapshot_id
        ):
            return self._result(
                continuation,
                GovernedInvestigationPlanningReentryStatus.REVIEW_REQUIRED,
                None,
                ("planning_reentry:planning_lineage_mismatch",),
                planning_invocation_count=1,
            )
        if planning.plan_id in continuation.resulting_state.plan_ids:
            return self._result(
                continuation,
                GovernedInvestigationPlanningReentryStatus.REVIEW_REQUIRED,
                None,
                ("planning_reentry:prior_plan_reuse_forbidden",),
                planning_invocation_count=1,
            )
        return self._result(
            continuation,
            GovernedInvestigationPlanningReentryStatus.PLANNED,
            planning_product,
            ("planning_reentry:new_plan_produced_by_existing_planning",),
            planning_invocation_count=1,
        )

    @staticmethod
    def _eligibility_error(
        continuation: GovernedMultiStepInvestigationProductiveContinuation,
    ) -> str | None:
        state = continuation.resulting_state
        requirement = continuation.source_requirement
        if not continuation.eligible_for_existing_planning:
            return "planning_reentry:continuation_not_planning_eligible"
        if (
            continuation.decision
            is not GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
        ):
            return "planning_reentry:continue_allowed_required"
        if state.status is not GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING:
            return "planning_reentry:episode_not_ready_for_planning"
        if not (
            2 <= continuation.current_step <= state.max_acquisitions
            and state.consumed_acquisitions == continuation.current_step - 1
            and continuation.remaining_acquisitions > 0
        ):
            return "planning_reentry:governed_step_budget_alignment_required"
        if requirement is None:
            return "planning_reentry:governed_requirement_required"
        if requirement is not continuation.source_requirement:
            return "planning_reentry:requirement_identity_mismatch"
        if requirement.requirement_id != state.current_requirement_id:
            return "planning_reentry:requirement_lineage_mismatch"
        if requirement.source_reference != continuation.source_reference:
            return "planning_reentry:source_lineage_mismatch"
        if requirement.world_snapshot_id != continuation.world_snapshot_id:
            return "planning_reentry:snapshot_lineage_mismatch"
        if continuation.planning_execution_authorized:
            return "planning_reentry:non_executive_continuation_required"
        return None

    @staticmethod
    def _result(
        continuation: GovernedMultiStepInvestigationProductiveContinuation,
        status: GovernedInvestigationPlanningReentryStatus,
        planning_product: GovernedEvidenceAcquisitionProductiveConsumption | None,
        rationale_codes: tuple[str, ...],
        *,
        planning_invocation_count: int,
    ) -> GovernedInvestigationPlanningReentryResult:
        planning = (
            None if planning_product is None else planning_product.planning_report
        )
        fingerprint = sha256(
            repr(
                (
                    continuation.episode_id,
                    status.value,
                    continuation.source_requirement_id,
                    None if planning is None else planning.plan_id,
                    None if planning is None else planning.status.value,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedInvestigationPlanningReentryResult(
            episode_id=continuation.episode_id,
            continuation=continuation,
            status=status,
            planning_product=planning_product,
            requirement_id=continuation.source_requirement_id,
            plan_id=None if planning is None else planning.plan_id,
            source_reference=continuation.source_reference,
            world_snapshot_id=continuation.world_snapshot_id,
            current_step=continuation.current_step,
            remaining_acquisitions=continuation.remaining_acquisitions,
            planning_status=None if planning is None else planning.status,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
            eligible_for_authorization=(
                status is GovernedInvestigationPlanningReentryStatus.PLANNED
                and planning is not None
                and planning.status is EvidenceAcquisitionPlanningStatus.PLANNABLE
            ),
            planning_invocation_count=planning_invocation_count,
        )
