from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumption,
)
from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
    GovernedIndependenceAuthorizationReport,
    GovernedInitiationDecision,
)
from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumption,
    GovernedIndependenceAuthorizationProductiveConsumptionV1,
)
from app.governed_long_horizon_investigation_evidence_planning import (
    GovernedInvestigationEvidencePlanningResult,
    GovernedInvestigationEvidencePlanningStatus,
)
from core.capability_registry import CapabilityRegistryManager
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus


class GovernedInvestigationEvidenceAuthorizationStatus(StrEnum):
    AUTHORIZED = "authorized"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationEvidenceAuthorizationResult:
    admission_id: str
    thread_id: str
    checkpoint_id: str
    resume_id: str
    episode_id: str
    originating_reasoning_id: str
    requirement_id: str
    source_reference: str
    world_snapshot_id: str
    plan_id: str | None
    planning_product: GovernedEvidenceAcquisitionProductiveConsumption | None
    status: GovernedInvestigationEvidenceAuthorizationStatus
    rationale_codes: tuple[str, ...]
    authorization_report: GovernedIndependenceAuthorizationReport | None
    authorization_product: GovernedIndependenceAuthorizationProductiveConsumption | None
    authorization_id: str | None
    decision: GovernedInitiationDecision | None
    eligible_for_existing_execution: bool
    schema_version: str = "post-m409.1-long-horizon-existing-authorization-v1"
    canonical_authorization_authority: str = (
        "governed_independence_authorization_boundary"
    )
    read_only: bool = True
    execution_authorized: bool = False
    invokes_execution_gateway: bool = False
    invokes_capabilities: bool = False
    acquires_evidence: bool = False
    invokes_reasoning: bool = False
    modifies_episode_state: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authorization_authority != (
            "governed_independence_authorization_boundary"
        ):
            raise ValueError("authorization bridge must preserve canonical authority")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("authorization bridge requires rationale codes")
        if not self.read_only or any(
            (
                self.execution_authorized,
                self.invokes_execution_gateway,
                self.invokes_capabilities,
                self.acquires_evidence,
                self.invokes_reasoning,
                self.modifies_episode_state,
                self.modifies_memory,
                self.modifies_world_model,
                self.starts_background_process,
            )
        ):
            raise ValueError("authorization bridge violates governed limits")

        if self.status is GovernedInvestigationEvidenceAuthorizationStatus.AUTHORIZED:
            required = (
                self.plan_id,
                self.planning_product,
                self.authorization_report,
                self.authorization_product,
                self.authorization_id,
                self.decision,
            )
            if any(value is None for value in required):
                raise ValueError("authorized bridge result requires canonical products")
            assert self.planning_product is not None
            assert self.authorization_report is not None
            assert self.authorization_product is not None
            if self.plan_id != self.planning_product.planning_report.plan_id:
                raise ValueError("authorization bridge must preserve plan identity")
            if self.requirement_id != self.planning_product.requirement_id:
                raise ValueError(
                    "authorization bridge must preserve requirement lineage"
                )
            if self.source_reference != self.planning_product.source_reference:
                raise ValueError("authorization bridge must preserve source lineage")
            if self.world_snapshot_id != self.planning_product.world_snapshot_id:
                raise ValueError("authorization bridge must preserve snapshot lineage")
            if self.authorization_report.requirement_id != self.requirement_id:
                raise ValueError("authorization report requirement lineage mismatch")
            if self.authorization_report.plan_id != self.plan_id:
                raise ValueError("authorization report plan lineage mismatch")
            if self.authorization_report.source_reference != self.source_reference:
                raise ValueError("authorization report source lineage mismatch")
            if self.authorization_report.world_snapshot_id != self.world_snapshot_id:
                raise ValueError("authorization report snapshot lineage mismatch")
            if self.authorization_product.authorization_report is not (
                self.authorization_report
            ):
                raise ValueError("authorization product must preserve exact report")
            if self.authorization_id != self.authorization_report.authorization_id:
                raise ValueError("authorization bridge must preserve authorization id")
            if self.decision is not self.authorization_report.decision:
                raise ValueError("authorization bridge must preserve decision")
        else:
            exposed = (
                self.plan_id,
                self.planning_product,
                self.authorization_report,
                self.authorization_product,
                self.authorization_id,
                self.decision,
            )
            if any(value is not None for value in exposed):
                raise ValueError("closed authorization result cannot expose products")

        expected_eligibility = (
            self.status is GovernedInvestigationEvidenceAuthorizationStatus.AUTHORIZED
            and self.decision is GovernedInitiationDecision.MAY_INITIATE
        )
        if self.eligible_for_existing_execution != expected_eligibility:
            raise ValueError(
                "execution-gate eligibility must derive from authorization"
            )


class GovernedLongHorizonInvestigationEvidenceAuthorizationV1:
    """Bridge an eligible existing plan into the canonical authorization owner."""

    def __init__(self, registry: CapabilityRegistryManager) -> None:
        self._authorization = GovernedIndependenceAuthorizationBoundaryV1(registry)

    def consume(
        self,
        planning_result: GovernedInvestigationEvidencePlanningResult,
    ) -> GovernedInvestigationEvidenceAuthorizationResult:
        if not self._eligible(planning_result):
            return self._closed_result(
                planning_result,
                status=GovernedInvestigationEvidenceAuthorizationStatus.NOT_ELIGIBLE,
                rationale_codes=(
                    "investigation_existing_authorization:not_eligible",
                    "investigation_existing_authorization:authorization_not_invoked",
                ),
            )

        planning_product = planning_result.planning_product
        assert planning_product is not None
        try:
            report = self._authorization.evaluate(planning_product)
            product = GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(
                report
            )
        except Exception:
            return self._closed_result(
                planning_result,
                status=GovernedInvestigationEvidenceAuthorizationStatus.REVIEW_REQUIRED,
                rationale_codes=(
                    "investigation_existing_authorization:authorization_failed",
                    "investigation_existing_authorization:review_required",
                ),
            )

        if not self._lineage_matches(planning_result, report, product):
            return self._closed_result(
                planning_result,
                status=GovernedInvestigationEvidenceAuthorizationStatus.REVIEW_REQUIRED,
                rationale_codes=(
                    (
                        "investigation_existing_authorization:"
                        "authorization_lineage_mismatch"
                    ),
                    "investigation_existing_authorization:review_required",
                ),
            )

        return GovernedInvestigationEvidenceAuthorizationResult(
            admission_id=planning_result.admission_id,
            thread_id=planning_result.thread_id,
            checkpoint_id=planning_result.checkpoint_id,
            resume_id=planning_result.resume_id,
            episode_id=planning_result.episode_id,
            originating_reasoning_id=planning_result.originating_reasoning_id,
            requirement_id=planning_result.requirement_id,
            source_reference=planning_result.source_reference,
            world_snapshot_id=planning_result.world_snapshot_id,
            plan_id=planning_result.plan_id,
            planning_product=planning_product,
            status=GovernedInvestigationEvidenceAuthorizationStatus.AUTHORIZED,
            rationale_codes=(
                "investigation_existing_authorization:existing_authorization_consumed",
                f"investigation_existing_authorization:{report.decision.value}",
            ),
            authorization_report=report,
            authorization_product=product,
            authorization_id=report.authorization_id,
            decision=report.decision,
            eligible_for_existing_execution=(
                report.decision is GovernedInitiationDecision.MAY_INITIATE
            ),
        )

    @staticmethod
    def _eligible(planning_result: GovernedInvestigationEvidencePlanningResult) -> bool:
        product = planning_result.planning_product
        return all(
            (
                planning_result.status
                is GovernedInvestigationEvidencePlanningStatus.PLANNED,
                planning_result.planning_status
                is EvidenceAcquisitionPlanningStatus.PLANNABLE,
                planning_result.eligible_for_authorization,
                product is not None,
                planning_result.plan_id is not None,
                product is not None
                and planning_result.plan_id == product.planning_report.plan_id,
                product is not None
                and planning_result.requirement_id == product.requirement_id,
                product is not None
                and planning_result.source_reference == product.source_reference,
                product is not None
                and planning_result.world_snapshot_id == product.world_snapshot_id,
                product is not None and product.read_only,
                product is not None and product.consultative,
                product is not None and not product.planning_execution_authorized,
                product is not None and not product.invokes_capabilities,
                product is not None and not product.acquires_evidence,
                product is not None and not product.executes_actions,
                product is not None and not product.grants_authority,
                planning_result.read_only,
                not planning_result.execution_authorized,
                not planning_result.invokes_capabilities,
                not planning_result.acquires_evidence,
                not planning_result.invokes_reasoning,
                not planning_result.modifies_episode_state,
                not planning_result.modifies_memory,
                not planning_result.modifies_world_model,
                not planning_result.starts_background_process,
            )
        )

    @staticmethod
    def _lineage_matches(
        planning_result: GovernedInvestigationEvidencePlanningResult,
        report: GovernedIndependenceAuthorizationReport,
        product: GovernedIndependenceAuthorizationProductiveConsumption,
    ) -> bool:
        return all(
            (
                report.requirement_id == planning_result.requirement_id,
                report.plan_id == planning_result.plan_id,
                report.source_reference == planning_result.source_reference,
                report.world_snapshot_id == planning_result.world_snapshot_id,
                product.authorization_report is report,
                product.authorization_id == report.authorization_id,
                product.decision is report.decision,
                product.requirement_id == planning_result.requirement_id,
                product.plan_id == planning_result.plan_id,
                product.source_reference == planning_result.source_reference,
                product.world_snapshot_id == planning_result.world_snapshot_id,
                product.canonical_authority
                == "governed_independence_authorization_boundary",
                product.read_only,
                product.consultative,
                not product.execution_authorized,
                not product.invokes_capabilities,
                not product.executes_actions,
                not product.grants_authority,
            )
        )

    @staticmethod
    def _closed_result(
        planning_result: GovernedInvestigationEvidencePlanningResult,
        *,
        status: GovernedInvestigationEvidenceAuthorizationStatus,
        rationale_codes: tuple[str, ...],
    ) -> GovernedInvestigationEvidenceAuthorizationResult:
        return GovernedInvestigationEvidenceAuthorizationResult(
            admission_id=planning_result.admission_id,
            thread_id=planning_result.thread_id,
            checkpoint_id=planning_result.checkpoint_id,
            resume_id=planning_result.resume_id,
            episode_id=planning_result.episode_id,
            originating_reasoning_id=planning_result.originating_reasoning_id,
            requirement_id=planning_result.requirement_id,
            source_reference=planning_result.source_reference,
            world_snapshot_id=planning_result.world_snapshot_id,
            plan_id=None,
            planning_product=None,
            status=status,
            rationale_codes=rationale_codes,
            authorization_report=None,
            authorization_product=None,
            authorization_id=None,
            decision=None,
            eligible_for_existing_execution=False,
        )
