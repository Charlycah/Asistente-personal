from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.governed_independence_authorization_boundary import (
    GovernedInitiationDecision,
)
from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumption,
)
from app.governed_long_horizon_investigation_p2_planning_reentry import (
    GovernedInvestigationP2PlanningAdmissionResult,
    GovernedInvestigationP2PlanningAdmissionStatus,
)
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedInvestigationAuthorizationReentryResult,
    GovernedInvestigationAuthorizationReentryStatus,
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedInvestigationPlanningReentryStatus,
)
from core.capability_registry import CapabilityRegistryManager
from core.evidence_acquisition_planning import EvidenceAcquisitionPlanningStatus


class GovernedInvestigationA2AuthorizationAdmissionStatus(StrEnum):
    AUTHORIZED = "authorized"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationA2AuthorizationAdmissionResult:
    thread_id: str
    checkpoint_id: str
    episode_id: str
    originating_reasoning_id: str
    requirement_id: str | None
    plan_id: str | None
    source_reference: str
    world_snapshot_id: str
    status: GovernedInvestigationA2AuthorizationAdmissionStatus
    authorization_reentry: GovernedInvestigationAuthorizationReentryResult | None
    authorization_product: (
        GovernedIndependenceAuthorizationProductiveConsumption | None
    )
    authorization_id: str | None
    decision: GovernedInitiationDecision | None
    rationale_codes: tuple[str, ...]
    authorization_invocation_count: int
    schema_version: str = "post-m409.1-long-horizon-p2-a2-authorization-reentry-v1"
    canonical_authorization_authority: str = (
        "GovernedMultiStepInvestigationAuthorizationReentryV1"
    )
    eligible_for_existing_execution: bool = False
    invokes_authorization: bool = False
    invokes_execution: bool = False
    invokes_reasoning: bool = False
    invokes_planning: bool = False
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
            raise ValueError("A2 Authorization bridge requires rationale codes")
        if self.authorization_invocation_count not in {0, 1}:
            raise ValueError("A2 Authorization bridge permits at most one call")
        if self.invokes_authorization != (self.authorization_invocation_count == 1):
            raise ValueError("A2 Authorization invocation flag must match call count")
        if self.canonical_authorization_authority != (
            "GovernedMultiStepInvestigationAuthorizationReentryV1"
        ):
            raise ValueError("A2 Authorization bridge must preserve canonical owner")
        if any(
            (
                self.invokes_execution,
                self.invokes_reasoning,
                self.invokes_planning,
                self.rewrites_requirement,
                self.modifies_episode_state,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError(
                "A2 Authorization bridge operationalizes a later capability"
            )

        if self.status is (
            GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED
        ):
            if self.authorization_invocation_count != 1:
                raise ValueError("authorized A2 requires one authorization call")
            if self.authorization_reentry is None or self.authorization_product is None:
                raise ValueError("authorized A2 requires exact canonical products")
            if self.authorization_reentry.status is not (
                GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
            ):
                raise ValueError("authorized bridge requires canonical AUTHORIZED")
            if self.authorization_reentry.authorization_product is not (
                self.authorization_product
            ):
                raise ValueError("A2 bridge must preserve exact authorization product")
            if self.authorization_id != self.authorization_reentry.authorization_id:
                raise ValueError("A2 bridge must preserve authorization identity")
            if self.requirement_id != self.authorization_reentry.requirement_id:
                raise ValueError("A2 bridge must preserve R2 identity")
            if self.plan_id != self.authorization_reentry.plan_id:
                raise ValueError("A2 bridge must preserve P2 identity")
            if self.decision is not self.authorization_reentry.decision:
                raise ValueError("A2 bridge must preserve authorization decision")
        else:
            if self.authorization_invocation_count == 0:
                if self.authorization_reentry is not None:
                    raise ValueError("pre-authorization closure cannot expose A2")
                if self.authorization_product is not None:
                    raise ValueError("pre-authorization closure cannot expose product")
                if self.authorization_id is not None or self.decision is not None:
                    raise ValueError("pre-authorization closure cannot expose decision")
            elif self.status is (
                GovernedInvestigationA2AuthorizationAdmissionStatus.REVIEW_REQUIRED
            ):
                if self.authorization_product is not None:
                    raise ValueError("review-required A2 cannot expose trusted product")
                if self.authorization_id is not None or self.decision is not None:
                    raise ValueError(
                        "review-required A2 cannot expose trusted decision"
                    )

        expected_execution = (
            self.status
            is GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED
            and self.decision is GovernedInitiationDecision.MAY_INITIATE
            and self.authorization_reentry is not None
            and self.authorization_reentry.eligible_for_existing_execution
        )
        if self.eligible_for_existing_execution != expected_execution:
            raise ValueError(
                "E2 eligibility must derive only from exact MAY_INITIATE A2"
            )


class GovernedLongHorizonInvestigationA2AuthorizationReentryV1:
    """Forward one exact canonical P2 to the existing A2 Authorization owner."""

    def __init__(
        self,
        registry: CapabilityRegistryManager | None = None,
        authorization_reentry: (
            GovernedMultiStepInvestigationAuthorizationReentryV1 | None
        ) = None,
    ) -> None:
        if authorization_reentry is None:
            if registry is None:
                raise ValueError(
                    "A2 Authorization bridge requires registry or existing owner"
                )
            authorization_reentry = (
                GovernedMultiStepInvestigationAuthorizationReentryV1(registry)
            )
        self._authorization_reentry = authorization_reentry

    def consume(
        self,
        planning_result: GovernedInvestigationP2PlanningAdmissionResult,
    ) -> GovernedInvestigationA2AuthorizationAdmissionResult:
        planning_reentry = planning_result.planning_reentry
        if not self._eligible(planning_result):
            return self._closed(
                planning_result,
                GovernedInvestigationA2AuthorizationAdmissionStatus.NOT_ELIGIBLE,
                ("investigation_a2_authorization:exact_p2_not_eligible",),
                authorization_invocation_count=0,
            )

        assert planning_reentry is not None
        try:
            authorization_reentry = self._authorization_reentry.consume(
                planning_result.planning_reentry
            )
        except Exception:
            return self._closed(
                planning_result,
                GovernedInvestigationA2AuthorizationAdmissionStatus.REVIEW_REQUIRED,
                ("investigation_a2_authorization:existing_owner_failed",),
                authorization_invocation_count=1,
            )

        if authorization_reentry.status is not (
            GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
        ):
            return self._review_after_authorization(
                planning_result,
                authorization_reentry,
                ("investigation_a2_authorization:unexpected_existing_owner_status",),
            )

        authorization_product = authorization_reentry.authorization_product
        if authorization_product is None:
            return self._review_after_authorization(
                planning_result,
                authorization_reentry,
                (
                    "investigation_a2_authorization:missing_existing_"
                    "authorization_product",
                ),
            )

        prior_authorization_ids = (
            planning_reentry.continuation.resulting_state.authorization_ids
        )
        valid_authorization = all(
            (
                authorization_reentry.planning_reentry is planning_reentry,
                authorization_reentry.episode_id == planning_result.episode_id,
                authorization_reentry.requirement_id == planning_result.requirement_id,
                authorization_reentry.plan_id == planning_result.plan_id,
                authorization_reentry.source_reference
                == planning_result.source_reference,
                authorization_reentry.world_snapshot_id
                == planning_result.world_snapshot_id,
                authorization_reentry.current_step == planning_reentry.current_step,
                authorization_reentry.remaining_acquisitions
                == planning_reentry.remaining_acquisitions,
                authorization_reentry.authorization_invocation_count == 1,
                authorization_reentry.authorization_id
                == authorization_product.authorization_id,
                authorization_reentry.requirement_id
                == authorization_product.requirement_id,
                authorization_reentry.plan_id == authorization_product.plan_id,
                authorization_reentry.source_reference
                == authorization_product.source_reference,
                authorization_reentry.world_snapshot_id
                == authorization_product.world_snapshot_id,
                authorization_reentry.decision is authorization_product.decision,
                authorization_reentry.authorization_id not in prior_authorization_ids,
                authorization_product.authorization_report
                is not None,
                authorization_product.authorization_report.authorization_id
                == authorization_reentry.authorization_id,
                authorization_product.authorization_report.requirement_id
                == planning_result.requirement_id,
                authorization_product.authorization_report.plan_id
                == planning_result.plan_id,
                authorization_product.authorization_report.source_reference
                == planning_result.source_reference,
                authorization_product.authorization_report.world_snapshot_id
                == planning_result.world_snapshot_id,
            )
        )
        if not valid_authorization:
            return self._review_after_authorization(
                planning_result,
                authorization_reentry,
                ("investigation_a2_authorization:existing_a2_lineage_mismatch",),
            )

        eligible_for_existing_execution = (
            authorization_reentry.decision is GovernedInitiationDecision.MAY_INITIATE
            and authorization_reentry.eligible_for_existing_execution
        )
        return GovernedInvestigationA2AuthorizationAdmissionResult(
            thread_id=planning_result.thread_id,
            checkpoint_id=planning_result.checkpoint_id,
            episode_id=planning_result.episode_id,
            originating_reasoning_id=planning_result.originating_reasoning_id,
            requirement_id=planning_result.requirement_id,
            plan_id=planning_result.plan_id,
            source_reference=planning_result.source_reference,
            world_snapshot_id=planning_result.world_snapshot_id,
            status=GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED,
            authorization_reentry=authorization_reentry,
            authorization_product=authorization_product,
            authorization_id=authorization_reentry.authorization_id,
            decision=authorization_reentry.decision,
            rationale_codes=(
                "investigation_a2_authorization:exact_canonical_p2_forwarded",
                "investigation_a2_authorization:existing_a2_preserved",
                *authorization_reentry.rationale_codes,
            ),
            authorization_invocation_count=1,
            eligible_for_existing_execution=eligible_for_existing_execution,
            invokes_authorization=True,
        )

    @staticmethod
    def _eligible(
        planning_result: GovernedInvestigationP2PlanningAdmissionResult,
    ) -> bool:
        planning_reentry = planning_result.planning_reentry
        if planning_reentry is None:
            return False
        planning_product = planning_reentry.planning_product
        continuation = planning_reentry.continuation
        requirement = continuation.source_requirement
        state = continuation.resulting_state
        return all(
            (
                planning_result.status
                is GovernedInvestigationP2PlanningAdmissionStatus.PLANNED,
                planning_result.eligible_for_existing_authorization,
                planning_result.planning_status
                is EvidenceAcquisitionPlanningStatus.PLANNABLE,
                planning_result.planning_invocation_count == 1,
                planning_reentry.status
                is GovernedInvestigationPlanningReentryStatus.PLANNED,
                planning_reentry.eligible_for_authorization,
                planning_reentry.planning_status
                is EvidenceAcquisitionPlanningStatus.PLANNABLE,
                2 <= planning_reentry.current_step <= state.max_acquisitions,
                planning_reentry.current_step == state.current_step,
                state.consumed_acquisitions == planning_reentry.current_step - 1,
                planning_reentry.remaining_acquisitions > 0,
                planning_reentry.remaining_acquisitions
                == state.remaining_acquisitions,
                planning_reentry.planning_invocation_count == 1,
                planning_product is not None,
                requirement is not None,
                planning_reentry.episode_id == planning_result.episode_id,
                continuation.episode_id == planning_result.episode_id,
                state.episode_id == planning_result.episode_id,
                planning_reentry.requirement_id == planning_result.requirement_id,
                planning_reentry.plan_id == planning_result.plan_id,
                planning_reentry.source_reference == planning_result.source_reference,
                planning_reentry.world_snapshot_id
                == planning_result.world_snapshot_id,
                continuation.source_reference == planning_result.source_reference,
                continuation.world_snapshot_id == planning_result.world_snapshot_id,
                state.source_reference == planning_result.source_reference,
                state.world_snapshot_id == planning_result.world_snapshot_id,
                requirement.requirement_id == planning_result.requirement_id,
                requirement.requirement_id == state.current_requirement_id,
                requirement.source_reference == planning_result.source_reference,
                requirement.world_snapshot_id == planning_result.world_snapshot_id,
                planning_product.requirement_id == planning_result.requirement_id,
                planning_product.planning_report.plan_id == planning_result.plan_id,
                planning_product.source_reference == planning_result.source_reference,
                planning_product.world_snapshot_id == planning_result.world_snapshot_id,
            )
        )

    @staticmethod
    def _review_after_authorization(
        planning_result: GovernedInvestigationP2PlanningAdmissionResult,
        authorization_reentry: GovernedInvestigationAuthorizationReentryResult,
        rationale_codes: tuple[str, ...],
    ) -> GovernedInvestigationA2AuthorizationAdmissionResult:
        return GovernedInvestigationA2AuthorizationAdmissionResult(
            thread_id=planning_result.thread_id,
            checkpoint_id=planning_result.checkpoint_id,
            episode_id=planning_result.episode_id,
            originating_reasoning_id=planning_result.originating_reasoning_id,
            requirement_id=planning_result.requirement_id,
            plan_id=planning_result.plan_id,
            source_reference=planning_result.source_reference,
            world_snapshot_id=planning_result.world_snapshot_id,
            status=GovernedInvestigationA2AuthorizationAdmissionStatus.REVIEW_REQUIRED,
            authorization_reentry=authorization_reentry,
            authorization_product=None,
            authorization_id=None,
            decision=None,
            rationale_codes=(*rationale_codes, *authorization_reentry.rationale_codes),
            authorization_invocation_count=1,
            eligible_for_existing_execution=False,
            invokes_authorization=True,
        )

    @staticmethod
    def _closed(
        planning_result: GovernedInvestigationP2PlanningAdmissionResult,
        status: GovernedInvestigationA2AuthorizationAdmissionStatus,
        rationale_codes: tuple[str, ...],
        *,
        authorization_invocation_count: int,
    ) -> GovernedInvestigationA2AuthorizationAdmissionResult:
        return GovernedInvestigationA2AuthorizationAdmissionResult(
            thread_id=planning_result.thread_id,
            checkpoint_id=planning_result.checkpoint_id,
            episode_id=planning_result.episode_id,
            originating_reasoning_id=planning_result.originating_reasoning_id,
            requirement_id=planning_result.requirement_id,
            plan_id=planning_result.plan_id,
            source_reference=planning_result.source_reference,
            world_snapshot_id=planning_result.world_snapshot_id,
            status=status,
            authorization_reentry=None,
            authorization_product=None,
            authorization_id=None,
            decision=None,
            rationale_codes=rationale_codes,
            authorization_invocation_count=authorization_invocation_count,
            eligible_for_existing_execution=False,
            invokes_authorization=authorization_invocation_count == 1,
        )
