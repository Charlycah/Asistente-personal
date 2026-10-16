from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryFoundationV1,
)
from app.governed_long_horizon_investigation_reassessment_requirement_admission import (
    GovernedInvestigationReassessmentRequirementAdmissionResult,
    GovernedInvestigationReassessmentRequirementAdmissionStatus,
)
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedInvestigationAuthorizationReentryResult,
    GovernedInvestigationAuthorizationReentryStatus,
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryResult,
    GovernedInvestigationExecutionReentryStatus,
    GovernedMultiStepInvestigationExecutionReentryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedInvestigationPlanningReentryResult,
    GovernedInvestigationPlanningReentryStatus,
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedInvestigationReasoningClosureResult,
    GovernedInvestigationReasoningClosureStatus,
    GovernedMultiStepInvestigationReasoningClosureV1,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.capability_registry import CapabilityRegistryManager


class GovernedCAP11OneStepContinuationStatus(StrEnum):
    NOT_ELIGIBLE = "not_eligible"
    PLANNING_STOPPED = "planning_stopped"
    AUTHORIZATION_STOPPED = "authorization_stopped"
    EXECUTION_STOPPED = "execution_stopped"
    REASONING_STOPPED = "reasoning_stopped"
    REASONING_COMPLETED = "reasoning_completed"


@dataclass(frozen=True)
class GovernedCAP11OneStepContinuationResult:
    admission: GovernedInvestigationReassessmentRequirementAdmissionResult
    status: GovernedCAP11OneStepContinuationStatus
    planning: GovernedInvestigationPlanningReentryResult | None
    authorization: GovernedInvestigationAuthorizationReentryResult | None
    execution: GovernedInvestigationExecutionReentryResult | None
    reasoning: GovernedInvestigationReasoningClosureResult | None
    rationale_codes: tuple[str, ...]
    planning_invocation_count: int = 0
    authorization_invocation_count: int = 0
    execution_invocation_count: int = 0
    reasoning_invocation_count: int = 0
    derives_next_requirement: bool = False
    recursive_continuation: bool = False
    starts_background_process: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False

    def __post_init__(self) -> None:
        counts = (
            self.planning_invocation_count,
            self.authorization_invocation_count,
            self.execution_invocation_count,
            self.reasoning_invocation_count,
        )
        if any(count not in {0, 1} for count in counts):
            raise ValueError("one-step continuation permits at most one call per stage")
        if not self.rationale_codes:
            raise ValueError("one-step continuation requires rationale codes")
        if any(
            (
                self.derives_next_requirement,
                self.recursive_continuation,
                self.starts_background_process,
                self.modifies_memory,
                self.modifies_world_model,
            )
        ):
            raise ValueError("one-step continuation exceeds its governed boundary")


class GovernedCAP11OneStepContinuationCoordinatorV1:
    """Compose one admitted CAP-11 step through existing owners, then stop."""

    def __init__(
        self,
        *,
        capability_registry: CapabilityRegistryManager,
        runtime_registry: OfficialRuntimeCapabilityRegistry,
        reasoning_gateway: object,
    ) -> None:
        self._planning = GovernedMultiStepInvestigationPlanningReentryV1(
            capability_registry
        )
        self._authorization = GovernedMultiStepInvestigationAuthorizationReentryV1(
            capability_registry
        )
        self._execution = GovernedMultiStepInvestigationExecutionReentryV1(
            runtime_registry
        )
        self._reasoning = GovernedMultiStepInvestigationReasoningClosureV1(
            GovernedLevel2ReasoningReentryFoundationV1(reasoning_gateway)
        )

    def consume(
        self,
        admission: GovernedInvestigationReassessmentRequirementAdmissionResult,
        *,
        now: datetime,
    ) -> GovernedCAP11OneStepContinuationResult:
        if now.tzinfo is None:
            raise ValueError("CAP-11 one-step continuation time must be timezone-aware")
        if (
            admission.status
            is not GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
            or not admission.eligible_for_existing_planning
            or admission.continuation is None
        ):
            return self._result(
                admission,
                GovernedCAP11OneStepContinuationStatus.NOT_ELIGIBLE,
                rationale_codes=("cap11_one_step:admitted_planning_eligible_required",),
            )

        planning = self._planning.consume(admission.continuation)
        if planning.status is not GovernedInvestigationPlanningReentryStatus.PLANNED:
            return self._result(
                admission,
                GovernedCAP11OneStepContinuationStatus.PLANNING_STOPPED,
                planning=planning,
                rationale_codes=("cap11_one_step:planning_stopped",),
                planning_invocation_count=1,
            )

        authorization = self._authorization.consume(planning)
        if (
            authorization.status
            is not GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
            or not authorization.eligible_for_existing_execution
        ):
            return self._result(
                admission,
                GovernedCAP11OneStepContinuationStatus.AUTHORIZATION_STOPPED,
                planning=planning,
                authorization=authorization,
                rationale_codes=("cap11_one_step:authorization_stopped",),
                planning_invocation_count=1,
                authorization_invocation_count=1,
            )

        execution = self._execution.consume(authorization, now=now)
        if execution.status is not GovernedInvestigationExecutionReentryStatus.ACQUIRED:
            return self._result(
                admission,
                GovernedCAP11OneStepContinuationStatus.EXECUTION_STOPPED,
                planning=planning,
                authorization=authorization,
                execution=execution,
                rationale_codes=("cap11_one_step:execution_stopped",),
                planning_invocation_count=1,
                authorization_invocation_count=1,
                execution_invocation_count=1,
            )

        reasoning = self._reasoning.consume(execution, now=now)
        if reasoning.status not in {
            GovernedInvestigationReasoningClosureStatus.RECORDED,
            GovernedInvestigationReasoningClosureStatus.CLOSED,
        }:
            return self._result(
                admission,
                GovernedCAP11OneStepContinuationStatus.REASONING_STOPPED,
                planning=planning,
                authorization=authorization,
                execution=execution,
                reasoning=reasoning,
                rationale_codes=("cap11_one_step:reasoning_stopped",),
                planning_invocation_count=1,
                authorization_invocation_count=1,
                execution_invocation_count=1,
                reasoning_invocation_count=1,
            )
        return self._result(
            admission,
            GovernedCAP11OneStepContinuationStatus.REASONING_COMPLETED,
            planning=planning,
            authorization=authorization,
            execution=execution,
            reasoning=reasoning,
            rationale_codes=("cap11_one_step:reasoning_completed_stop",),
            planning_invocation_count=1,
            authorization_invocation_count=1,
            execution_invocation_count=1,
            reasoning_invocation_count=1,
        )

    @staticmethod
    def _result(
        admission: GovernedInvestigationReassessmentRequirementAdmissionResult,
        status: GovernedCAP11OneStepContinuationStatus,
        *,
        planning: GovernedInvestigationPlanningReentryResult | None = None,
        authorization: GovernedInvestigationAuthorizationReentryResult | None = None,
        execution: GovernedInvestigationExecutionReentryResult | None = None,
        reasoning: GovernedInvestigationReasoningClosureResult | None = None,
        rationale_codes: tuple[str, ...],
        planning_invocation_count: int = 0,
        authorization_invocation_count: int = 0,
        execution_invocation_count: int = 0,
        reasoning_invocation_count: int = 0,
    ) -> GovernedCAP11OneStepContinuationResult:
        return GovernedCAP11OneStepContinuationResult(
            admission=admission,
            status=status,
            planning=planning,
            authorization=authorization,
            execution=execution,
            reasoning=reasoning,
            rationale_codes=rationale_codes,
            planning_invocation_count=planning_invocation_count,
            authorization_invocation_count=authorization_invocation_count,
            execution_invocation_count=execution_invocation_count,
            reasoning_invocation_count=reasoning_invocation_count,
        )
