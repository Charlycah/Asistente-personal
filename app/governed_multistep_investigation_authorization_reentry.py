from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
    GovernedIndependenceAuthorizationReport,
    GovernedInitiationDecision,
)
from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumption,
    GovernedIndependenceAuthorizationProductiveConsumptionV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedInvestigationPlanningReentryResult,
    GovernedInvestigationPlanningReentryStatus,
)
from core.capability_registry import CapabilityRegistryManager
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus


class GovernedInvestigationAuthorizationReentryStatus(StrEnum):
    AUTHORIZED = "authorized"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationAuthorizationReentryResult:
    episode_id: str
    planning_reentry: GovernedInvestigationPlanningReentryResult
    status: GovernedInvestigationAuthorizationReentryStatus
    authorization_product: (
        GovernedIndependenceAuthorizationProductiveConsumption | None
    )
    authorization_id: str | None
    requirement_id: str | None
    plan_id: str | None
    source_reference: str
    world_snapshot_id: str
    current_step: int
    remaining_acquisitions: int
    decision: GovernedInitiationDecision | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = (
        "post-m409.1-multistep-investigation-authorization-reentry-v1"
    )
    canonical_authority: str = (
        "governed_independence_authorization_boundary"
    )
    eligible_for_existing_execution: bool = False
    authorization_invocation_count: int = 0
    execution_authorized: bool = False
    invokes_execution_gateway: bool = False
    invokes_capabilities: bool = False
    invokes_reasoning: bool = False
    modifies_episode_state: bool = False
    creates_questions: bool = False
    emits_conversation: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.episode_id != self.planning_reentry.episode_id:
            raise ValueError("authorization re-entry must preserve episode identity")
        if self.source_reference != self.planning_reentry.source_reference:
            raise ValueError("authorization re-entry must preserve source lineage")
        if self.world_snapshot_id != self.planning_reentry.world_snapshot_id:
            raise ValueError("authorization re-entry must preserve snapshot lineage")
        if self.current_step != self.planning_reentry.current_step:
            raise ValueError("authorization re-entry must preserve current step")
        if self.remaining_acquisitions != (
            self.planning_reentry.remaining_acquisitions
        ):
            raise ValueError("authorization re-entry must preserve episode budget")
        if self.authorization_invocation_count not in {0, 1}:
            raise ValueError("authorization re-entry permits at most one call")
        if self.status is GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED:
            if self.authorization_invocation_count != 1:
                raise ValueError("authorized result requires one authorization call")
            if self.authorization_product is None:
                raise ValueError("authorized result requires authorization product")
            if self.authorization_id != self.authorization_product.authorization_id:
                raise ValueError("authorization identity must be preserved")
            if self.requirement_id != self.authorization_product.requirement_id:
                raise ValueError("authorization requirement must be preserved")
            if self.plan_id != self.authorization_product.plan_id:
                raise ValueError("authorization plan must be preserved")
            if self.decision is not self.authorization_product.decision:
                raise ValueError("authorization decision must be preserved")
        else:
            if self.authorization_product is not None:
                raise ValueError("non-authorized result cannot expose authorization")
            if self.authorization_id is not None or self.decision is not None:
                raise ValueError("non-authorized result cannot expose decision")
        expected_execution_eligibility = (
            self.status is GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
            and self.decision is GovernedInitiationDecision.MAY_INITIATE
        )
        if self.eligible_for_existing_execution != expected_execution_eligibility:
            raise ValueError(
                "execution eligibility must derive only from authorization"
            )
        if self.canonical_authority != (
            "governed_independence_authorization_boundary"
        ):
            raise ValueError("authorization re-entry must preserve authority")
        if any(
            (
                self.execution_authorized,
                self.invokes_execution_gateway,
                self.invokes_capabilities,
                self.invokes_reasoning,
                self.modifies_episode_state,
                self.creates_questions,
                self.emits_conversation,
                self.modifies_memory,
                self.modifies_world_model,
                self.starts_background_process,
            )
        ):
            raise ValueError("authorization re-entry violates governed limits")


class GovernedMultiStepInvestigationAuthorizationReentryV1:
    """Invoke existing independence authorization once for valid P2."""

    def __init__(
        self,
        registry: CapabilityRegistryManager,
        authorization_boundary: GovernedIndependenceAuthorizationBoundaryV1
        | None = None,
    ) -> None:
        self._authorization_boundary = (
            authorization_boundary
            or GovernedIndependenceAuthorizationBoundaryV1(registry)
        )

    def consume(
        self,
        planning_reentry: GovernedInvestigationPlanningReentryResult,
    ) -> GovernedInvestigationAuthorizationReentryResult:
        eligibility_error = self._eligibility_error(planning_reentry)
        if eligibility_error is not None:
            return self._result(
                planning_reentry,
                GovernedInvestigationAuthorizationReentryStatus.NOT_ELIGIBLE,
                None,
                (eligibility_error,),
                authorization_invocation_count=0,
            )
        planning_product = planning_reentry.planning_product
        if planning_product is None:
            return self._result(
                planning_reentry,
                GovernedInvestigationAuthorizationReentryStatus.NOT_ELIGIBLE,
                None,
                ("authorization_reentry:planning_product_required",),
                authorization_invocation_count=0,
            )
        try:
            report = self._authorization_boundary.evaluate(planning_product)
            product = (
                GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(
                    report
                )
            )
        except Exception:
            return self._result(
                planning_reentry,
                GovernedInvestigationAuthorizationReentryStatus.REVIEW_REQUIRED,
                None,
                ("authorization_reentry:single_authorization_call_failed",),
                authorization_invocation_count=1,
            )
        lineage_error = self._authorization_lineage_error(
            planning_reentry,
            report,
        )
        if lineage_error is not None:
            return self._result(
                planning_reentry,
                GovernedInvestigationAuthorizationReentryStatus.REVIEW_REQUIRED,
                None,
                (lineage_error,),
                authorization_invocation_count=1,
            )
        if report.authorization_id in (
            planning_reentry.continuation.resulting_state.authorization_ids
        ):
            return self._result(
                planning_reentry,
                GovernedInvestigationAuthorizationReentryStatus.REVIEW_REQUIRED,
                None,
                ("authorization_reentry:prior_authorization_reuse_forbidden",),
                authorization_invocation_count=1,
            )
        return self._result(
            planning_reentry,
            GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED,
            product,
            ("authorization_reentry:new_a2_from_existing_authority",),
            authorization_invocation_count=1,
        )

    @staticmethod
    def _eligibility_error(
        planning_reentry: GovernedInvestigationPlanningReentryResult,
    ) -> str | None:
        if (
            planning_reentry.status
            is not GovernedInvestigationPlanningReentryStatus.PLANNED
        ):
            return "authorization_reentry:planned_p2_required"
        if not planning_reentry.eligible_for_authorization:
            return "authorization_reentry:p2_not_authorization_eligible"
        if (
            planning_reentry.planning_status
            is not EvidenceAcquisitionPlanningStatus.PLANNABLE
        ):
            return "authorization_reentry:plannable_p2_required"
        state = planning_reentry.continuation.resulting_state
        if not (
            2 <= planning_reentry.current_step <= state.max_acquisitions
            and state.consumed_acquisitions == planning_reentry.current_step - 1
            and planning_reentry.remaining_acquisitions > 0
        ):
            return "authorization_reentry:governed_step_budget_alignment_required"
        if planning_reentry.execution_authorized:
            return "authorization_reentry:non_executive_p2_required"
        if planning_reentry.planning_product is None:
            return "authorization_reentry:planning_product_required"
        return None

    @staticmethod
    def _authorization_lineage_error(
        planning_reentry: GovernedInvestigationPlanningReentryResult,
        report: GovernedIndependenceAuthorizationReport,
    ) -> str | None:
        if report.requirement_id != planning_reentry.requirement_id:
            return "authorization_reentry:requirement_lineage_mismatch"
        if report.plan_id != planning_reentry.plan_id:
            return "authorization_reentry:plan_lineage_mismatch"
        if report.source_reference != planning_reentry.source_reference:
            return "authorization_reentry:source_lineage_mismatch"
        if report.world_snapshot_id != planning_reentry.world_snapshot_id:
            return "authorization_reentry:snapshot_lineage_mismatch"
        return None

    @staticmethod
    def _result(
        planning_reentry: GovernedInvestigationPlanningReentryResult,
        status: GovernedInvestigationAuthorizationReentryStatus,
        authorization_product: (
            GovernedIndependenceAuthorizationProductiveConsumption | None
        ),
        rationale_codes: tuple[str, ...],
        *,
        authorization_invocation_count: int,
    ) -> GovernedInvestigationAuthorizationReentryResult:
        fingerprint = sha256(
            repr(
                (
                    planning_reentry.episode_id,
                    status.value,
                    planning_reentry.requirement_id,
                    planning_reentry.plan_id,
                    None
                    if authorization_product is None
                    else authorization_product.authorization_id,
                    None
                    if authorization_product is None
                    else authorization_product.decision.value,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedInvestigationAuthorizationReentryResult(
            episode_id=planning_reentry.episode_id,
            planning_reentry=planning_reentry,
            status=status,
            authorization_product=authorization_product,
            authorization_id=(
                None
                if authorization_product is None
                else authorization_product.authorization_id
            ),
            requirement_id=planning_reentry.requirement_id,
            plan_id=planning_reentry.plan_id,
            source_reference=planning_reentry.source_reference,
            world_snapshot_id=planning_reentry.world_snapshot_id,
            current_step=planning_reentry.current_step,
            remaining_acquisitions=planning_reentry.remaining_acquisitions,
            decision=(
                None
                if authorization_product is None
                else authorization_product.decision
            ),
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
            eligible_for_existing_execution=(
                authorization_product is not None
                and authorization_product.decision
                is GovernedInitiationDecision.MAY_INITIATE
            ),
            authorization_invocation_count=authorization_invocation_count,
        )
