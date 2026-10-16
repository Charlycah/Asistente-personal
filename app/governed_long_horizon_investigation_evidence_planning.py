from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumption,
    GovernedEvidenceAcquisitionProductiveConsumptionV1,
)
from app.governed_long_horizon_investigation_resume_admission import (
    GovernedInvestigationResumeAdmission,
    GovernedInvestigationResumeAdmissionStatus,
)
from core.capability_registry import CapabilityRegistryManager
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus


class GovernedInvestigationEvidencePlanningStatus(StrEnum):
    PLANNED = "planned"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationEvidencePlanningResult:
    admission_id: str
    thread_id: str
    checkpoint_id: str
    resume_id: str
    episode_id: str
    originating_reasoning_id: str
    requirement_id: str
    source_reference: str
    world_snapshot_id: str
    status: GovernedInvestigationEvidencePlanningStatus
    rationale_codes: tuple[str, ...]
    planning_product: GovernedEvidenceAcquisitionProductiveConsumption | None
    plan_id: str | None
    planning_status: EvidenceAcquisitionPlanningStatus | None
    eligible_for_authorization: bool
    schema_version: str = "post-m409.1-long-horizon-resume-existing-planning-v1"
    canonical_planning_authority: str = "planning_foundation"
    read_only: bool = True
    planning_execution_authorized: bool = False
    execution_authorized: bool = False
    invokes_authorization: bool = False
    invokes_capabilities: bool = False
    acquires_evidence: bool = False
    invokes_reasoning: bool = False
    modifies_episode_state: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.canonical_planning_authority != "planning_foundation":
            raise ValueError(
                "evidence planning bridge must preserve planning authority"
            )
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("evidence planning bridge requires rationale codes")
        if not self.read_only or any(
            (
                self.planning_execution_authorized,
                self.execution_authorized,
                self.invokes_authorization,
                self.invokes_capabilities,
                self.acquires_evidence,
                self.invokes_reasoning,
                self.modifies_episode_state,
                self.modifies_memory,
                self.modifies_world_model,
                self.starts_background_process,
            )
        ):
            raise ValueError("evidence planning bridge violates governed limits")
        if self.status is GovernedInvestigationEvidencePlanningStatus.PLANNED:
            if self.planning_product is None or self.plan_id is None:
                raise ValueError(
                    "planned bridge result requires the existing planning product"
                )
            if self.planning_status is None:
                raise ValueError("planned bridge result requires planning status")
            if self.requirement_id != self.planning_product.requirement_id:
                raise ValueError(
                    "planned bridge result must preserve requirement identity"
                )
            if self.source_reference != self.planning_product.source_reference:
                raise ValueError("planned bridge result must preserve source lineage")
            if self.world_snapshot_id != self.planning_product.world_snapshot_id:
                raise ValueError("planned bridge result must preserve snapshot lineage")
            if self.plan_id != self.planning_product.planning_report.plan_id:
                raise ValueError("planned bridge result must preserve plan identity")
            if self.planning_status is not self.planning_product.status:
                raise ValueError("planned bridge result must preserve planning status")
        elif any(
            value is not None
            for value in (self.planning_product, self.plan_id, self.planning_status)
        ):
            raise ValueError(
                "non-planned bridge result cannot expose a planning product"
            )
        expected_eligibility = (
            self.status is GovernedInvestigationEvidencePlanningStatus.PLANNED
            and self.planning_status is EvidenceAcquisitionPlanningStatus.PLANNABLE
        )
        if self.eligible_for_authorization != expected_eligibility:
            raise ValueError(
                "authorization eligibility must derive from plannable status"
            )


class GovernedLongHorizonInvestigationEvidencePlanningV1:
    """Bridge admitted resume lineage into the existing planning_foundation owner."""

    def __init__(self, registry: CapabilityRegistryManager) -> None:
        self._planning = GovernedEvidenceAcquisitionProductiveConsumptionV1(registry)

    def consume(
        self,
        admission: GovernedInvestigationResumeAdmission,
    ) -> GovernedInvestigationEvidencePlanningResult:
        if not self._eligible(admission):
            return self._closed_result(
                admission,
                status=GovernedInvestigationEvidencePlanningStatus.NOT_ELIGIBLE,
                rationale_codes=(
                    "investigation_resume_existing_planning:not_eligible",
                    "investigation_resume_existing_planning:planning_not_invoked",
                ),
            )

        try:
            planning_product = self._planning.consume(admission.requirement)
        except Exception:
            return self._closed_result(
                admission,
                status=GovernedInvestigationEvidencePlanningStatus.REVIEW_REQUIRED,
                rationale_codes=(
                    "investigation_resume_existing_planning:planning_failed",
                    "investigation_resume_existing_planning:review_required",
                ),
            )

        if not self._lineage_matches(admission, planning_product):
            return self._closed_result(
                admission,
                status=GovernedInvestigationEvidencePlanningStatus.REVIEW_REQUIRED,
                rationale_codes=(
                    "investigation_resume_existing_planning:planning_lineage_mismatch",
                    "investigation_resume_existing_planning:review_required",
                ),
            )

        planning_status = planning_product.status
        return GovernedInvestigationEvidencePlanningResult(
            admission_id=admission.admission_id,
            thread_id=admission.thread_id,
            checkpoint_id=admission.checkpoint_id,
            resume_id=admission.resume_id,
            episode_id=admission.episode_id,
            originating_reasoning_id=admission.originating_reasoning_id,
            requirement_id=admission.requirement_id,
            source_reference=admission.source_reference,
            world_snapshot_id=admission.world_snapshot_id,
            status=GovernedInvestigationEvidencePlanningStatus.PLANNED,
            rationale_codes=(
                "investigation_resume_existing_planning:existing_planning_consumed",
                f"investigation_resume_existing_planning:{planning_status.value}",
            ),
            planning_product=planning_product,
            plan_id=planning_product.planning_report.plan_id,
            planning_status=planning_status,
            eligible_for_authorization=(
                planning_status is EvidenceAcquisitionPlanningStatus.PLANNABLE
            ),
        )

    @staticmethod
    def _eligible(admission: GovernedInvestigationResumeAdmission) -> bool:
        return all(
            (
                admission.status is GovernedInvestigationResumeAdmissionStatus.ADMITTED,
                admission.eligible_for_existing_planning,
                admission.requirement_id == admission.requirement.requirement_id,
                admission.source_reference == admission.requirement.source_reference,
                admission.world_snapshot_id == admission.requirement.world_snapshot_id,
                admission.canonical_planning_authority == "planning_foundation",
                admission.read_only,
                not admission.planning_execution_authorized,
                not admission.invokes_capabilities,
                not admission.executes_actions,
                not admission.modifies_memory,
                not admission.modifies_world_model,
                not admission.modifies_planning,
                not admission.starts_background_process,
                not admission.grants_authority,
            )
        )

    @staticmethod
    def _lineage_matches(
        admission: GovernedInvestigationResumeAdmission,
        planning_product: GovernedEvidenceAcquisitionProductiveConsumption,
    ) -> bool:
        return all(
            (
                planning_product.requirement_id == admission.requirement_id,
                planning_product.source_reference == admission.source_reference,
                planning_product.world_snapshot_id == admission.world_snapshot_id,
                planning_product.canonical_authority == "planning_foundation",
                planning_product.read_only,
                planning_product.consultative,
                not planning_product.planning_execution_authorized,
                not planning_product.invokes_capabilities,
                not planning_product.acquires_evidence,
                not planning_product.executes_actions,
                not planning_product.grants_authority,
            )
        )

    @staticmethod
    def _closed_result(
        admission: GovernedInvestigationResumeAdmission,
        *,
        status: GovernedInvestigationEvidencePlanningStatus,
        rationale_codes: tuple[str, ...],
    ) -> GovernedInvestigationEvidencePlanningResult:
        return GovernedInvestigationEvidencePlanningResult(
            admission_id=admission.admission_id,
            thread_id=admission.thread_id,
            checkpoint_id=admission.checkpoint_id,
            resume_id=admission.resume_id,
            episode_id=admission.episode_id,
            originating_reasoning_id=admission.originating_reasoning_id,
            requirement_id=admission.requirement_id,
            source_reference=admission.source_reference,
            world_snapshot_id=admission.world_snapshot_id,
            status=status,
            rationale_codes=rationale_codes,
            planning_product=None,
            plan_id=None,
            planning_status=None,
            eligible_for_authorization=False,
        )
