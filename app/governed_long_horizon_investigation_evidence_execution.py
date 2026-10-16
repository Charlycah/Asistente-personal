from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.governed_independence_authorization_boundary import (
    GovernedIndependenceLevel,
    GovernedInitiationDecision,
)
from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
    GovernedLevel2ReadOnlyExecutionGatewayV1,
)
from app.governed_long_horizon_investigation_evidence_authorization import (
    GovernedInvestigationEvidenceAuthorizationResult,
    GovernedInvestigationEvidenceAuthorizationStatus,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


class GovernedInvestigationEvidenceExecutionStatus(StrEnum):
    ACQUIRED = "acquired"
    NOT_ELIGIBLE = "not_eligible"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationEvidenceExecutionResult:
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
    authorization_id: str | None
    status: GovernedInvestigationEvidenceExecutionStatus
    evidence_envelope: GovernedAcquiredEvidenceEnvelope | None
    execution_id: str | None
    execution_status: GovernedLevel2ExecutionStatus | None
    rationale_codes: tuple[str, ...]
    execution_invocation_count: int
    schema_version: str = "post-m409.1-long-horizon-existing-execution-v1"
    canonical_execution_gateway: str = "OfficialCapabilityGateway"
    read_only: bool = True
    establishes_truth: bool = False
    persists_results: bool = False
    creates_questions: bool = False
    records_episode_evidence: bool = False
    invokes_reasoning: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    permits_retry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("execution bridge requires rationale codes")
        if self.execution_invocation_count not in {0, 1}:
            raise ValueError("execution bridge permits at most one gateway call")
        if self.canonical_execution_gateway != "OfficialCapabilityGateway":
            raise ValueError("execution bridge must preserve canonical gateway")
        if not self.read_only or any(
            (
                self.establishes_truth,
                self.persists_results,
                self.creates_questions,
                self.records_episode_evidence,
                self.invokes_reasoning,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError("execution bridge operationalizes a later residual")

        if self.status is GovernedInvestigationEvidenceExecutionStatus.NOT_ELIGIBLE:
            if any(
                value is not None
                for value in (
                    self.evidence_envelope,
                    self.execution_id,
                    self.execution_status,
                )
            ):
                raise ValueError("ineligible execution cannot expose an envelope")
            if self.execution_invocation_count != 0:
                raise ValueError("ineligible execution cannot invoke the gateway")
            return

        if self.evidence_envelope is None or self.execution_status is None:
            if (
                self.status
                is GovernedInvestigationEvidenceExecutionStatus.REVIEW_REQUIRED
            ):
                if self.execution_id is not None:
                    raise ValueError("envelope-less review cannot expose execution id")
                return
            raise ValueError("executed result requires canonical evidence envelope")

        envelope = self.evidence_envelope
        if self.execution_invocation_count != 1:
            raise ValueError("canonical envelope requires exactly one gateway call")
        if self.execution_id != envelope.execution_id:
            raise ValueError("execution bridge must preserve execution identity")
        if self.execution_status is not envelope.status:
            raise ValueError("execution bridge must preserve execution status")
        if self.authorization_id != envelope.authorization_id:
            raise ValueError("execution bridge must preserve authorization lineage")
        if self.requirement_id != envelope.requirement_id:
            raise ValueError("execution bridge must preserve requirement lineage")
        if self.plan_id != envelope.plan_id:
            raise ValueError("execution bridge must preserve planning lineage")
        if self.source_reference != envelope.source_reference:
            raise ValueError("execution bridge must preserve source lineage")
        if self.world_snapshot_id != envelope.world_snapshot_id:
            raise ValueError("execution bridge must preserve snapshot lineage")
        expected = _bridge_status(envelope.status)
        if self.status is not expected:
            raise ValueError("bridge status must derive from canonical gateway status")


class GovernedLongHorizonInvestigationEvidenceExecutionV1:
    """Consume one eligible Level 2 authorization through the canonical gateway."""

    def __init__(
        self,
        runtime_registry: OfficialRuntimeCapabilityRegistry,
        execution_gateway: GovernedLevel2ReadOnlyExecutionGatewayV1 | None = None,
    ) -> None:
        self._execution_gateway = execution_gateway or (
            GovernedLevel2ReadOnlyExecutionGatewayV1(runtime_registry)
        )

    def consume(
        self,
        authorization_result: GovernedInvestigationEvidenceAuthorizationResult,
        *,
        now: datetime,
    ) -> GovernedInvestigationEvidenceExecutionResult:
        if not self._eligible(authorization_result):
            return self._closed_result(
                authorization_result,
                status=GovernedInvestigationEvidenceExecutionStatus.NOT_ELIGIBLE,
                rationale_codes=(
                    "investigation_existing_execution:not_eligible",
                    "investigation_existing_execution:gateway_not_invoked",
                ),
                execution_invocation_count=0,
            )

        authorization = authorization_result.authorization_product
        planning = authorization_result.planning_product
        assert authorization is not None
        assert planning is not None
        try:
            envelope = self._execution_gateway.execute(
                authorization,
                planning,
                now=now,
            )
        except Exception as exc:
            return self._closed_result(
                authorization_result,
                status=GovernedInvestigationEvidenceExecutionStatus.REVIEW_REQUIRED,
                rationale_codes=(
                    "investigation_existing_execution:single_gateway_call_failed",
                    f"investigation_existing_execution:{type(exc).__name__}",
                ),
                execution_invocation_count=1,
            )

        if not self._lineage_matches(authorization_result, envelope):
            return self._closed_result(
                authorization_result,
                status=GovernedInvestigationEvidenceExecutionStatus.REVIEW_REQUIRED,
                rationale_codes=(
                    "investigation_existing_execution:gateway_lineage_mismatch",
                    "investigation_existing_execution:review_required",
                ),
                execution_invocation_count=1,
            )

        return GovernedInvestigationEvidenceExecutionResult(
            admission_id=authorization_result.admission_id,
            thread_id=authorization_result.thread_id,
            checkpoint_id=authorization_result.checkpoint_id,
            resume_id=authorization_result.resume_id,
            episode_id=authorization_result.episode_id,
            originating_reasoning_id=authorization_result.originating_reasoning_id,
            requirement_id=authorization_result.requirement_id,
            source_reference=authorization_result.source_reference,
            world_snapshot_id=authorization_result.world_snapshot_id,
            plan_id=authorization_result.plan_id,
            authorization_id=authorization_result.authorization_id,
            status=_bridge_status(envelope.status),
            evidence_envelope=envelope,
            execution_id=envelope.execution_id,
            execution_status=envelope.status,
            rationale_codes=(
                "investigation_existing_execution:existing_gateway_consumed",
                f"investigation_existing_execution:{envelope.status.value}",
            ),
            execution_invocation_count=1,
        )

    @staticmethod
    def _eligible(
        authorization_result: GovernedInvestigationEvidenceAuthorizationResult,
    ) -> bool:
        authorization = authorization_result.authorization_product
        planning = authorization_result.planning_product
        return all(
            (
                authorization_result.status
                is GovernedInvestigationEvidenceAuthorizationStatus.AUTHORIZED,
                authorization_result.decision
                is GovernedInitiationDecision.MAY_INITIATE,
                authorization_result.eligible_for_existing_execution,
                authorization is not None,
                planning is not None,
                authorization is not None
                and authorization.decision is GovernedInitiationDecision.MAY_INITIATE,
                authorization is not None
                and authorization.independence_level
                is GovernedIndependenceLevel.LEVEL_2_READ_ONLY,
                authorization is not None
                and authorization.eligible_for_next_governed_gate,
                authorization is not None and authorization.read_only,
                authorization is not None and authorization.consultative,
                authorization is not None and not authorization.execution_authorized,
                authorization is not None and not authorization.invokes_capabilities,
                authorization is not None and not authorization.executes_actions,
                authorization is not None
                and authorization.authorization_id
                == authorization_result.authorization_id,
                authorization is not None
                and authorization.requirement_id == authorization_result.requirement_id,
                authorization is not None
                and authorization.plan_id == authorization_result.plan_id,
                authorization is not None
                and authorization.source_reference
                == authorization_result.source_reference,
                authorization is not None
                and authorization.world_snapshot_id
                == authorization_result.world_snapshot_id,
                planning is not None
                and planning.requirement_id == authorization_result.requirement_id,
                planning is not None
                and planning.planning_report.plan_id == authorization_result.plan_id,
                planning is not None
                and planning.source_reference == authorization_result.source_reference,
                planning is not None
                and planning.world_snapshot_id
                == authorization_result.world_snapshot_id,
                authorization_result.read_only,
                not authorization_result.execution_authorized,
                not authorization_result.invokes_execution_gateway,
                not authorization_result.invokes_capabilities,
                not authorization_result.acquires_evidence,
                not authorization_result.invokes_reasoning,
                not authorization_result.modifies_episode_state,
                not authorization_result.modifies_memory,
                not authorization_result.modifies_world_model,
                not authorization_result.starts_background_process,
            )
        )

    @staticmethod
    def _lineage_matches(
        authorization_result: GovernedInvestigationEvidenceAuthorizationResult,
        envelope: GovernedAcquiredEvidenceEnvelope,
    ) -> bool:
        return all(
            (
                envelope.authorization_id == authorization_result.authorization_id,
                envelope.requirement_id == authorization_result.requirement_id,
                envelope.plan_id == authorization_result.plan_id,
                envelope.source_reference == authorization_result.source_reference,
                envelope.world_snapshot_id == authorization_result.world_snapshot_id,
                envelope.canonical_execution_gateway == "OfficialCapabilityGateway",
                envelope.read_only,
                not envelope.establishes_truth,
                not envelope.persists_results,
                not envelope.creates_questions,
                not envelope.modifies_memory,
                not envelope.modifies_world_model,
                not envelope.permits_retry,
                not envelope.starts_background_process,
            )
        )

    @staticmethod
    def _closed_result(
        authorization_result: GovernedInvestigationEvidenceAuthorizationResult,
        *,
        status: GovernedInvestigationEvidenceExecutionStatus,
        rationale_codes: tuple[str, ...],
        execution_invocation_count: int,
    ) -> GovernedInvestigationEvidenceExecutionResult:
        return GovernedInvestigationEvidenceExecutionResult(
            admission_id=authorization_result.admission_id,
            thread_id=authorization_result.thread_id,
            checkpoint_id=authorization_result.checkpoint_id,
            resume_id=authorization_result.resume_id,
            episode_id=authorization_result.episode_id,
            originating_reasoning_id=authorization_result.originating_reasoning_id,
            requirement_id=authorization_result.requirement_id,
            source_reference=authorization_result.source_reference,
            world_snapshot_id=authorization_result.world_snapshot_id,
            plan_id=authorization_result.plan_id,
            authorization_id=authorization_result.authorization_id,
            status=status,
            evidence_envelope=None,
            execution_id=None,
            execution_status=None,
            rationale_codes=rationale_codes,
            execution_invocation_count=execution_invocation_count,
        )


def _bridge_status(
    status: GovernedLevel2ExecutionStatus,
) -> GovernedInvestigationEvidenceExecutionStatus:
    return GovernedInvestigationEvidenceExecutionStatus(status.value)
