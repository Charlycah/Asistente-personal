from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.governed_long_horizon_investigation_reassessment_requirement_admission import (
    GovernedInvestigationReassessmentRequirementAdmissionResult,
    GovernedInvestigationReassessmentRequirementAdmissionStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeStatus,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedInvestigationPlanningReentryResult,
    GovernedInvestigationPlanningReentryStatus,
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from core.capability_registry import CapabilityRegistryManager
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus


class GovernedInvestigationP2PlanningAdmissionStatus(StrEnum):
    PLANNED = "planned"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationP2PlanningAdmissionResult:
    thread_id: str
    checkpoint_id: str
    episode_id: str
    originating_reasoning_id: str
    requirement_id: str | None
    source_reference: str
    world_snapshot_id: str
    status: GovernedInvestigationP2PlanningAdmissionStatus
    planning_reentry: GovernedInvestigationPlanningReentryResult | None
    plan_id: str | None
    planning_status: EvidenceAcquisitionPlanningStatus | None
    rationale_codes: tuple[str, ...]
    planning_invocation_count: int
    schema_version: str = "post-m409.1-long-horizon-r2-p2-planning-reentry-v1"
    canonical_planning_authority: str = (
        "GovernedMultiStepInvestigationPlanningReentryV1"
    )
    eligible_for_existing_authorization: bool = False
    invokes_planning: bool = False
    invokes_authorization: bool = False
    invokes_execution: bool = False
    invokes_reasoning: bool = False
    rewrites_requirement: bool = False
    modifies_episode_state: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    permits_retry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("P2 Planning bridge requires rationale codes")
        if self.planning_invocation_count not in {0, 1}:
            raise ValueError("P2 Planning bridge permits at most one planning call")
        if self.invokes_planning != (self.planning_invocation_count == 1):
            raise ValueError("P2 Planning invocation flag must match call count")
        if self.canonical_planning_authority != (
            "GovernedMultiStepInvestigationPlanningReentryV1"
        ):
            raise ValueError("P2 Planning bridge must preserve canonical owner")
        if any(
            (
                self.invokes_authorization,
                self.invokes_execution,
                self.invokes_reasoning,
                self.rewrites_requirement,
                self.modifies_episode_state,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError("P2 Planning bridge operationalizes a later capability")

        if self.status is GovernedInvestigationP2PlanningAdmissionStatus.PLANNED:
            if self.planning_invocation_count != 1 or self.planning_reentry is None:
                raise ValueError("planned P2 requires one exact planning re-entry")
            if self.planning_reentry.status is not (
                GovernedInvestigationPlanningReentryStatus.PLANNED
            ):
                raise ValueError("planned bridge result requires canonical PLANNED")
            if self.requirement_id != self.planning_reentry.requirement_id:
                raise ValueError("planned bridge must preserve R2 identity")
            if self.plan_id != self.planning_reentry.plan_id:
                raise ValueError("planned bridge must preserve P2 identity")
            if self.planning_status is not self.planning_reentry.planning_status:
                raise ValueError("planned bridge must preserve planning status")
        elif self.status is GovernedInvestigationP2PlanningAdmissionStatus.NOT_ELIGIBLE:
            if self.planning_invocation_count != 0 or self.planning_reentry is not None:
                raise ValueError("ineligible P2 must stop before Planning")
            if self.plan_id is not None or self.planning_status is not None:
                raise ValueError("ineligible P2 cannot expose planning products")
        elif self.planning_invocation_count == 0:
            if self.planning_reentry is not None:
                raise ValueError("pre-planning review cannot expose planning re-entry")
            if self.plan_id is not None or self.planning_status is not None:
                raise ValueError("pre-planning review cannot expose P2")

        expected_authorization = (
            self.status is GovernedInvestigationP2PlanningAdmissionStatus.PLANNED
            and self.planning_status is EvidenceAcquisitionPlanningStatus.PLANNABLE
            and self.planning_reentry is not None
            and self.planning_reentry.eligible_for_authorization
        )
        if self.eligible_for_existing_authorization != expected_authorization:
            raise ValueError(
                "A2 eligibility must derive only from exact PLANNABLE P2"
            )


class GovernedLongHorizonInvestigationP2PlanningReentryV1:
    """Forward one exact admitted R2 continuation to the existing P2 owner."""

    def __init__(
        self,
        registry: CapabilityRegistryManager | None = None,
        planning_reentry: GovernedMultiStepInvestigationPlanningReentryV1 | None = None,
    ) -> None:
        if planning_reentry is None:
            if registry is None:
                raise ValueError(
                    "P2 Planning bridge requires registry or existing owner"
                )
            planning_reentry = GovernedMultiStepInvestigationPlanningReentryV1(registry)
        self._planning_reentry = planning_reentry

    def consume(
        self,
        admission: GovernedInvestigationReassessmentRequirementAdmissionResult,
    ) -> GovernedInvestigationP2PlanningAdmissionResult:
        continuation = admission.continuation
        source_requirement = admission.source_requirement
        resulting_episode_state = admission.resulting_episode_state

        eligible = all(
            (
                admission.status
                is GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED,
                admission.eligible_for_existing_planning,
                continuation is not None,
                source_requirement is not None,
                resulting_episode_state is not None,
                continuation is admission.continuation,
                source_requirement is continuation.source_requirement
                if continuation is not None
                else False,
                resulting_episode_state is continuation.resulting_state
                if continuation is not None
                else False,
                continuation is not None
                and continuation.decision
                is GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
                continuation is not None
                and continuation.eligible_for_existing_planning,
                resulting_episode_state is not None
                and resulting_episode_state.status
                is GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING,
                continuation is not None and continuation.current_step >= 2,
                continuation is not None
                and resulting_episode_state is not None
                and continuation.current_step == resulting_episode_state.current_step,
                continuation is not None
                and resulting_episode_state is not None
                and continuation.remaining_acquisitions
                == resulting_episode_state.remaining_acquisitions,
                continuation is not None
                and continuation.episode_id == admission.episode_id,
                resulting_episode_state is not None
                and resulting_episode_state.episode_id == admission.episode_id,
                source_requirement is not None
                and source_requirement.requirement_id
                == resulting_episode_state.current_requirement_id
                if resulting_episode_state is not None
                else False,
                continuation is not None
                and continuation.source_reference == admission.source_reference,
                continuation is not None
                and continuation.world_snapshot_id == admission.world_snapshot_id,
                source_requirement is not None
                and source_requirement.source_reference == admission.source_reference,
                source_requirement is not None
                and source_requirement.world_snapshot_id == admission.world_snapshot_id,
                resulting_episode_state is not None
                and resulting_episode_state.source_reference
                == admission.source_reference,
                resulting_episode_state is not None
                and resulting_episode_state.world_snapshot_id
                == admission.world_snapshot_id,
            )
        )
        if not eligible:
            return self._closed(
                admission,
                GovernedInvestigationP2PlanningAdmissionStatus.NOT_ELIGIBLE,
                ("investigation_p2_planning:exact_r2_admission_not_eligible",),
                planning_invocation_count=0,
            )

        assert continuation is not None
        assert source_requirement is not None
        assert resulting_episode_state is not None
        try:
            planning_reentry = self._planning_reentry.consume(admission.continuation)
        except Exception:
            return self._closed(
                admission,
                GovernedInvestigationP2PlanningAdmissionStatus.REVIEW_REQUIRED,
                ("investigation_p2_planning:existing_owner_failed",),
                planning_invocation_count=1,
            )

        if planning_reentry.status is not (
            GovernedInvestigationPlanningReentryStatus.PLANNED
        ):
            return self._review_after_planning(
                admission,
                planning_reentry,
                ("investigation_p2_planning:unexpected_existing_owner_status",),
            )

        planning_product = planning_reentry.planning_product
        if planning_product is None:
            return self._review_after_planning(
                admission,
                planning_reentry,
                ("investigation_p2_planning:missing_existing_planning_product",),
            )
        planning_report = planning_product.planning_report
        valid_planning = all(
            (
                planning_reentry.continuation is admission.continuation,
                planning_reentry.episode_id == admission.episode_id,
                planning_reentry.requirement_id == source_requirement.requirement_id,
                planning_reentry.source_reference == admission.source_reference,
                planning_reentry.world_snapshot_id == admission.world_snapshot_id,
                planning_reentry.current_step == continuation.current_step,
                planning_reentry.remaining_acquisitions
                == continuation.remaining_acquisitions,
                planning_reentry.planning_invocation_count == 1,
                planning_product.requirement_id == source_requirement.requirement_id,
                planning_report.requirement_id == source_requirement.requirement_id,
                planning_report.source_reference == admission.source_reference,
                planning_report.world_snapshot_id == admission.world_snapshot_id,
                planning_reentry.plan_id == planning_report.plan_id,
                planning_report.plan_id not in resulting_episode_state.plan_ids,
                planning_reentry.planning_status is planning_product.status,
                planning_reentry.planning_status is planning_report.status,
            )
        )
        if not valid_planning:
            return self._review_after_planning(
                admission,
                planning_reentry,
                ("investigation_p2_planning:existing_p2_lineage_mismatch",),
            )

        eligible_for_existing_authorization = (
            planning_reentry.planning_status
            is EvidenceAcquisitionPlanningStatus.PLANNABLE
            and planning_reentry.eligible_for_authorization
        )
        return GovernedInvestigationP2PlanningAdmissionResult(
            thread_id=admission.thread_id,
            checkpoint_id=admission.checkpoint_id,
            episode_id=admission.episode_id,
            originating_reasoning_id=admission.originating_reasoning_id,
            requirement_id=source_requirement.requirement_id,
            source_reference=admission.source_reference,
            world_snapshot_id=admission.world_snapshot_id,
            status=GovernedInvestigationP2PlanningAdmissionStatus.PLANNED,
            planning_reentry=planning_reentry,
            plan_id=planning_reentry.plan_id,
            planning_status=planning_reentry.planning_status,
            rationale_codes=(
                "investigation_p2_planning:exact_admitted_continuation_forwarded",
                "investigation_p2_planning:existing_p2_preserved",
                *planning_reentry.rationale_codes,
            ),
            planning_invocation_count=1,
            eligible_for_existing_authorization=eligible_for_existing_authorization,
            invokes_planning=True,
        )

    @staticmethod
    def _review_after_planning(
        admission: GovernedInvestigationReassessmentRequirementAdmissionResult,
        planning_reentry: GovernedInvestigationPlanningReentryResult,
        rationale_codes: tuple[str, ...],
    ) -> GovernedInvestigationP2PlanningAdmissionResult:
        return GovernedInvestigationP2PlanningAdmissionResult(
            thread_id=admission.thread_id,
            checkpoint_id=admission.checkpoint_id,
            episode_id=admission.episode_id,
            originating_reasoning_id=admission.originating_reasoning_id,
            requirement_id=(
                None
                if admission.source_requirement is None
                else admission.source_requirement.requirement_id
            ),
            source_reference=admission.source_reference,
            world_snapshot_id=admission.world_snapshot_id,
            status=GovernedInvestigationP2PlanningAdmissionStatus.REVIEW_REQUIRED,
            planning_reentry=planning_reentry,
            plan_id=planning_reentry.plan_id,
            planning_status=planning_reentry.planning_status,
            rationale_codes=(*rationale_codes, *planning_reentry.rationale_codes),
            planning_invocation_count=1,
            eligible_for_existing_authorization=False,
            invokes_planning=True,
        )

    @staticmethod
    def _closed(
        admission: GovernedInvestigationReassessmentRequirementAdmissionResult,
        status: GovernedInvestigationP2PlanningAdmissionStatus,
        rationale_codes: tuple[str, ...],
        *,
        planning_invocation_count: int,
    ) -> GovernedInvestigationP2PlanningAdmissionResult:
        return GovernedInvestigationP2PlanningAdmissionResult(
            thread_id=admission.thread_id,
            checkpoint_id=admission.checkpoint_id,
            episode_id=admission.episode_id,
            originating_reasoning_id=admission.originating_reasoning_id,
            requirement_id=(
                None
                if admission.source_requirement is None
                else admission.source_requirement.requirement_id
            ),
            source_reference=admission.source_reference,
            world_snapshot_id=admission.world_snapshot_id,
            status=status,
            planning_reentry=None,
            plan_id=None,
            planning_status=None,
            rationale_codes=rationale_codes,
            planning_invocation_count=planning_invocation_count,
            eligible_for_existing_authorization=False,
            invokes_planning=planning_invocation_count == 1,
        )
