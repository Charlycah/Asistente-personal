from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.governed_independence_authorization_boundary import (
    GovernedInitiationDecision,
)
from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_long_horizon_investigation_a2_authorization_reentry import (
    GovernedInvestigationA2AuthorizationAdmissionResult,
    GovernedInvestigationA2AuthorizationAdmissionStatus,
)
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedInvestigationAuthorizationReentryStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryResult,
    GovernedInvestigationExecutionReentryStatus,
    GovernedMultiStepInvestigationExecutionReentryV1,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


class GovernedInvestigationE2ExecutionAdmissionStatus(StrEnum):
    ACQUIRED = "acquired"
    STOPPED = "stopped"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationE2ExecutionAdmissionResult:
    thread_id: str
    checkpoint_id: str
    episode_id: str
    originating_reasoning_id: str
    execution_id: str | None
    authorization_id: str | None
    requirement_id: str | None
    plan_id: str | None
    source_reference: str
    world_snapshot_id: str
    status: GovernedInvestigationE2ExecutionAdmissionStatus
    execution_reentry: GovernedInvestigationExecutionReentryResult | None
    evidence_envelope: GovernedAcquiredEvidenceEnvelope | None
    resulting_episode_state: GovernedInvestigationEpisodeState | None
    execution_status: GovernedLevel2ExecutionStatus | None
    rationale_codes: tuple[str, ...]
    execution_invocation_count: int
    episode_record_invocation_count: int
    schema_version: str = "post-m409.1-long-horizon-a2-e2-execution-reentry-v1"
    canonical_execution_authority: str = (
        "GovernedMultiStepInvestigationExecutionReentryV1"
    )
    eligible_for_existing_reasoning_reentry: bool = False
    invokes_execution: bool = False
    invokes_reasoning: bool = False
    invokes_planning: bool = False
    invokes_authorization: bool = False
    creates_questions: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    permits_retry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("E2 Execution bridge requires rationale codes")
        if self.execution_invocation_count not in {0, 1}:
            raise ValueError("E2 Execution bridge permits at most one execution")
        if self.episode_record_invocation_count not in {0, 1}:
            raise ValueError("E2 Execution bridge permits at most one episode record")
        if self.invokes_execution != (self.execution_invocation_count == 1):
            raise ValueError("E2 execution flag must match canonical call count")
        if self.canonical_execution_authority != (
            "GovernedMultiStepInvestigationExecutionReentryV1"
        ):
            raise ValueError("E2 Execution bridge must preserve canonical owner")
        if any(
            (
                self.invokes_reasoning,
                self.invokes_planning,
                self.invokes_authorization,
                self.creates_questions,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError("E2 Execution bridge operationalizes a later capability")

        if self.status is GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED:
            if self.execution_reentry is None or self.evidence_envelope is None:
                raise ValueError("acquired E2 requires exact canonical products")
            if self.resulting_episode_state is None:
                raise ValueError("acquired E2 requires resulting episode state")
            if self.execution_reentry.status is not (
                GovernedInvestigationExecutionReentryStatus.ACQUIRED
            ):
                raise ValueError("acquired bridge requires canonical ACQUIRED")
            if self.execution_reentry.evidence_envelope is not self.evidence_envelope:
                raise ValueError("E2 bridge must preserve exact evidence envelope")
            if self.execution_reentry.resulting_episode_state is not (
                self.resulting_episode_state
            ):
                raise ValueError("E2 bridge must preserve exact resulting state")
            if self.execution_invocation_count != 1:
                raise ValueError("acquired E2 requires one execution invocation")
            if self.episode_record_invocation_count != 1:
                raise ValueError("acquired E2 requires one episode record")
        elif self.execution_invocation_count == 0:
            if self.execution_reentry is not None:
                raise ValueError("pre-execution closure cannot expose E2")
            if self.evidence_envelope is not None or self.execution_id is not None:
                raise ValueError("pre-execution closure cannot expose evidence")
            if self.resulting_episode_state is not None:
                raise ValueError("pre-execution closure cannot expose mutated state")
            if self.episode_record_invocation_count != 0:
                raise ValueError("pre-execution closure cannot record acquisition")

        expected_reasoning = (
            self.status is GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED
            and self.execution_reentry is not None
            and self.execution_reentry.eligible_for_reasoning_reentry
            and self.execution_status is GovernedLevel2ExecutionStatus.ACQUIRED
            and self.resulting_episode_state is not None
            and self.resulting_episode_state.status
            is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
        )
        if self.eligible_for_existing_reasoning_reentry != expected_reasoning:
            raise ValueError(
                "second reasoning eligibility must derive only from exact recorded E2"
            )


class GovernedLongHorizonInvestigationE2ExecutionReentryV1:
    """Forward one exact canonical A2 to the existing E2 Execution owner."""

    def __init__(
        self,
        runtime_registry: OfficialRuntimeCapabilityRegistry | None = None,
        execution_reentry: GovernedMultiStepInvestigationExecutionReentryV1
        | None = None,
    ) -> None:
        if execution_reentry is None:
            if runtime_registry is None:
                raise ValueError(
                    "E2 Execution bridge requires runtime registry or existing owner"
                )
            execution_reentry = GovernedMultiStepInvestigationExecutionReentryV1(
                runtime_registry
            )
        self._execution_reentry = execution_reentry

    def consume(
        self,
        authorization_result: GovernedInvestigationA2AuthorizationAdmissionResult,
        *,
        now: datetime,
    ) -> GovernedInvestigationE2ExecutionAdmissionResult:
        authorization_reentry = authorization_result.authorization_reentry
        if not self._eligible(authorization_result):
            return self._closed(
                authorization_result,
                GovernedInvestigationE2ExecutionAdmissionStatus.NOT_ELIGIBLE,
                ("investigation_e2_execution:exact_execution_eligible_a2_required",),
                execution_invocation_count=0,
                episode_record_invocation_count=0,
            )

        assert authorization_reentry is not None
        try:
            execution_reentry = self._execution_reentry.consume(
                authorization_result.authorization_reentry,
                now=now,
            )
        except Exception:
            return self._closed(
                authorization_result,
                GovernedInvestigationE2ExecutionAdmissionStatus.REVIEW_REQUIRED,
                ("investigation_e2_execution:single_existing_e2_invocation_failed",),
                execution_invocation_count=1,
                episode_record_invocation_count=0,
            )

        if execution_reentry.authorization_reentry is not authorization_reentry:
            return self._review_after_execution(
                authorization_result,
                execution_reentry,
                ("investigation_e2_execution:existing_e2_a2_identity_mismatch",),
            )

        status = execution_reentry.status
        if status is GovernedInvestigationExecutionReentryStatus.ACQUIRED:
            if not self._valid_acquired_e2(authorization_result, execution_reentry):
                return self._review_after_execution(
                    authorization_result,
                    execution_reentry,
                    ("investigation_e2_execution:existing_e2_lineage_mismatch",),
                )
            return self._preserved(
                authorization_result,
                execution_reentry,
                GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED,
                (
                    "investigation_e2_execution:exact_canonical_a2_forwarded",
                    "investigation_e2_execution:existing_recorded_e2_preserved",
                    *execution_reentry.rationale_codes,
                ),
            )

        if status is GovernedInvestigationExecutionReentryStatus.STOPPED:
            return self._preserved(
                authorization_result,
                execution_reentry,
                GovernedInvestigationE2ExecutionAdmissionStatus.STOPPED,
                (
                    "investigation_e2_execution:canonical_e2_stopped",
                    *execution_reentry.rationale_codes,
                ),
            )

        return self._review_after_execution(
            authorization_result,
            execution_reentry,
            (
                "investigation_e2_execution:canonical_e2_not_acquired",
                *execution_reentry.rationale_codes,
            ),
        )

    @staticmethod
    def _eligible(
        authorization_result: GovernedInvestigationA2AuthorizationAdmissionResult,
    ) -> bool:
        authorization_reentry = authorization_result.authorization_reentry
        if authorization_reentry is None:
            return False
        authorization_product = authorization_result.authorization_product
        planning_reentry = authorization_reentry.planning_reentry
        continuation = planning_reentry.continuation
        state = continuation.resulting_state
        requirement = continuation.source_requirement
        planning_product = planning_reentry.planning_product
        return all(
            (
                authorization_result.status
                is GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED,
                authorization_result.decision
                is GovernedInitiationDecision.MAY_INITIATE,
                authorization_result.eligible_for_existing_execution,
                authorization_result.authorization_invocation_count == 1,
                authorization_product is not None,
                authorization_reentry.status
                is GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED,
                authorization_reentry.eligible_for_existing_execution,
                authorization_reentry.authorization_invocation_count == 1,
                2 <= authorization_reentry.current_step <= state.max_acquisitions,
                authorization_reentry.current_step == state.current_step,
                state.consumed_acquisitions == authorization_reentry.current_step - 1,
                authorization_reentry.remaining_acquisitions > 0,
                authorization_reentry.remaining_acquisitions
                == state.remaining_acquisitions,
                authorization_reentry.authorization_product is authorization_product,
                planning_product is not None,
                requirement is not None,
                authorization_reentry.episode_id == authorization_result.episode_id,
                planning_reentry.episode_id == authorization_result.episode_id,
                continuation.episode_id == authorization_result.episode_id,
                state.episode_id == authorization_result.episode_id,
                authorization_reentry.authorization_id
                == authorization_result.authorization_id,
                authorization_reentry.requirement_id
                == authorization_result.requirement_id,
                authorization_reentry.plan_id == authorization_result.plan_id,
                requirement.requirement_id == authorization_result.requirement_id,
                requirement.requirement_id == state.current_requirement_id,
                authorization_reentry.source_reference
                == authorization_result.source_reference,
                planning_reentry.source_reference
                == authorization_result.source_reference,
                continuation.source_reference == authorization_result.source_reference,
                state.source_reference == authorization_result.source_reference,
                authorization_product.source_reference
                == authorization_result.source_reference,
                authorization_reentry.world_snapshot_id
                == authorization_result.world_snapshot_id,
                planning_reentry.world_snapshot_id
                == authorization_result.world_snapshot_id,
                continuation.world_snapshot_id
                == authorization_result.world_snapshot_id,
                state.world_snapshot_id == authorization_result.world_snapshot_id,
                authorization_product.world_snapshot_id
                == authorization_result.world_snapshot_id,
                authorization_product.authorization_id
                == authorization_result.authorization_id,
                authorization_product.requirement_id
                == authorization_result.requirement_id,
                authorization_product.plan_id == authorization_result.plan_id,
            )
        )

    @staticmethod
    def _valid_acquired_e2(
        authorization_result: GovernedInvestigationA2AuthorizationAdmissionResult,
        execution_reentry: GovernedInvestigationExecutionReentryResult,
    ) -> bool:
        envelope = execution_reentry.evidence_envelope
        state = execution_reentry.resulting_episode_state
        if envelope is None:
            return False
        authorization_reentry = authorization_result.authorization_reentry
        assert authorization_reentry is not None
        prior_execution_ids = (
            authorization_reentry.planning_reentry.continuation
            .resulting_state.execution_ids
        )
        return all(
            (
                execution_reentry.episode_id == authorization_result.episode_id,
                execution_reentry.authorization_id
                == authorization_result.authorization_id,
                execution_reentry.requirement_id == authorization_result.requirement_id,
                execution_reentry.plan_id == authorization_result.plan_id,
                execution_reentry.source_reference
                == authorization_result.source_reference,
                execution_reentry.world_snapshot_id
                == authorization_result.world_snapshot_id,
                execution_reentry.current_step == authorization_reentry.current_step,
                execution_reentry.remaining_acquisitions
                == authorization_reentry.remaining_acquisitions - 1,
                execution_reentry.execution_status
                is GovernedLevel2ExecutionStatus.ACQUIRED,
                execution_reentry.execution_invocation_count == 1,
                execution_reentry.episode_record_invocation_count == 1,
                execution_reentry.eligible_for_reasoning_reentry,
                state.episode_id == authorization_result.episode_id,
                state.status is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY,
                state.current_step == execution_reentry.current_step,
                state.remaining_acquisitions
                == execution_reentry.remaining_acquisitions,
                envelope.execution_id == execution_reentry.execution_id,
                envelope.authorization_id == authorization_result.authorization_id,
                envelope.requirement_id == authorization_result.requirement_id,
                envelope.plan_id == authorization_result.plan_id,
                envelope.source_reference == authorization_result.source_reference,
                envelope.world_snapshot_id == authorization_result.world_snapshot_id,
                envelope.execution_id not in prior_execution_ids,
            )
        )

    @staticmethod
    def _preserved(
        authorization_result: GovernedInvestigationA2AuthorizationAdmissionResult,
        execution_reentry: GovernedInvestigationExecutionReentryResult,
        status: GovernedInvestigationE2ExecutionAdmissionStatus,
        rationale_codes: tuple[str, ...],
    ) -> GovernedInvestigationE2ExecutionAdmissionResult:
        envelope = execution_reentry.evidence_envelope
        state = execution_reentry.resulting_episode_state
        return GovernedInvestigationE2ExecutionAdmissionResult(
            thread_id=authorization_result.thread_id,
            checkpoint_id=authorization_result.checkpoint_id,
            episode_id=authorization_result.episode_id,
            originating_reasoning_id=authorization_result.originating_reasoning_id,
            execution_id=execution_reentry.execution_id,
            authorization_id=authorization_result.authorization_id,
            requirement_id=authorization_result.requirement_id,
            plan_id=authorization_result.plan_id,
            source_reference=authorization_result.source_reference,
            world_snapshot_id=authorization_result.world_snapshot_id,
            status=status,
            execution_reentry=execution_reentry,
            evidence_envelope=envelope,
            resulting_episode_state=state,
            execution_status=execution_reentry.execution_status,
            rationale_codes=rationale_codes,
            execution_invocation_count=execution_reentry.execution_invocation_count,
            episode_record_invocation_count=(
                execution_reentry.episode_record_invocation_count
            ),
            eligible_for_existing_reasoning_reentry=(
                status is GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED
                and execution_reentry.eligible_for_reasoning_reentry
            ),
            invokes_execution=execution_reentry.execution_invocation_count == 1,
        )

    @staticmethod
    def _review_after_execution(
        authorization_result: GovernedInvestigationA2AuthorizationAdmissionResult,
        execution_reentry: GovernedInvestigationExecutionReentryResult,
        rationale_codes: tuple[str, ...],
    ) -> GovernedInvestigationE2ExecutionAdmissionResult:
        return GovernedInvestigationE2ExecutionAdmissionResult(
            thread_id=authorization_result.thread_id,
            checkpoint_id=authorization_result.checkpoint_id,
            episode_id=authorization_result.episode_id,
            originating_reasoning_id=authorization_result.originating_reasoning_id,
            execution_id=None,
            authorization_id=authorization_result.authorization_id,
            requirement_id=authorization_result.requirement_id,
            plan_id=authorization_result.plan_id,
            source_reference=authorization_result.source_reference,
            world_snapshot_id=authorization_result.world_snapshot_id,
            status=GovernedInvestigationE2ExecutionAdmissionStatus.REVIEW_REQUIRED,
            execution_reentry=execution_reentry,
            evidence_envelope=None,
            resulting_episode_state=execution_reentry.resulting_episode_state,
            execution_status=execution_reentry.execution_status,
            rationale_codes=rationale_codes,
            execution_invocation_count=execution_reentry.execution_invocation_count,
            episode_record_invocation_count=(
                execution_reentry.episode_record_invocation_count
            ),
            eligible_for_existing_reasoning_reentry=False,
            invokes_execution=execution_reentry.execution_invocation_count == 1,
        )

    @staticmethod
    def _closed(
        authorization_result: GovernedInvestigationA2AuthorizationAdmissionResult,
        status: GovernedInvestigationE2ExecutionAdmissionStatus,
        rationale_codes: tuple[str, ...],
        *,
        execution_invocation_count: int,
        episode_record_invocation_count: int,
    ) -> GovernedInvestigationE2ExecutionAdmissionResult:
        return GovernedInvestigationE2ExecutionAdmissionResult(
            thread_id=authorization_result.thread_id,
            checkpoint_id=authorization_result.checkpoint_id,
            episode_id=authorization_result.episode_id,
            originating_reasoning_id=authorization_result.originating_reasoning_id,
            execution_id=None,
            authorization_id=authorization_result.authorization_id,
            requirement_id=authorization_result.requirement_id,
            plan_id=authorization_result.plan_id,
            source_reference=authorization_result.source_reference,
            world_snapshot_id=authorization_result.world_snapshot_id,
            status=status,
            execution_reentry=None,
            evidence_envelope=None,
            resulting_episode_state=None,
            execution_status=None,
            rationale_codes=rationale_codes,
            execution_invocation_count=execution_invocation_count,
            episode_record_invocation_count=episode_record_invocation_count,
            eligible_for_existing_reasoning_reentry=False,
            invokes_execution=execution_invocation_count == 1,
        )
