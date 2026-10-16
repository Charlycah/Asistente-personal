from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
    GovernedLevel2ReadOnlyExecutionGatewayV1,
)
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedInvestigationAuthorizationReentryResult,
    GovernedInvestigationAuthorizationReentryStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeState,
    GovernedInvestigationEpisodeStatus,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


class GovernedInvestigationExecutionReentryStatus(StrEnum):
    ACQUIRED = "acquired"
    NOT_ELIGIBLE = "not_eligible"
    STOPPED = "stopped"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedInvestigationExecutionReentryResult:
    episode_id: str
    authorization_reentry: GovernedInvestigationAuthorizationReentryResult
    status: GovernedInvestigationExecutionReentryStatus
    evidence_envelope: GovernedAcquiredEvidenceEnvelope | None
    resulting_episode_state: GovernedInvestigationEpisodeState
    execution_id: str | None
    authorization_id: str | None
    requirement_id: str | None
    plan_id: str | None
    source_reference: str
    world_snapshot_id: str
    current_step: int
    remaining_acquisitions: int
    execution_status: GovernedLevel2ExecutionStatus | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = (
        "post-m409.1-multistep-investigation-execution-reentry-v1"
    )
    canonical_execution_gateway: str = "OfficialCapabilityGateway"
    eligible_for_reasoning_reentry: bool = False
    execution_invocation_count: int = 0
    episode_record_invocation_count: int = 0
    invokes_reasoning: bool = False
    creates_questions: bool = False
    emits_conversation: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    permits_retry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.episode_id != self.authorization_reentry.episode_id:
            raise ValueError("execution re-entry must preserve episode identity")
        if self.source_reference != self.authorization_reentry.source_reference:
            raise ValueError("execution re-entry must preserve source lineage")
        if self.world_snapshot_id != self.authorization_reentry.world_snapshot_id:
            raise ValueError("execution re-entry must preserve snapshot lineage")
        if self.execution_invocation_count not in {0, 1}:
            raise ValueError("execution re-entry permits at most one execution")
        if self.episode_record_invocation_count not in {0, 1}:
            raise ValueError("execution re-entry permits at most one episode record")
        if self.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED:
            if self.evidence_envelope is None:
                raise ValueError("acquired result requires evidence envelope")
            if self.execution_invocation_count != 1:
                raise ValueError("acquired result requires one execution")
            if self.episode_record_invocation_count != 1:
                raise ValueError("acquired result requires one episode record")
            if self.execution_status is not GovernedLevel2ExecutionStatus.ACQUIRED:
                raise ValueError("acquired result requires acquired execution status")
            if (
                self.resulting_episode_state.status
                is not GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
            ):
                raise ValueError("acquired step must await reasoning re-entry")
        expected_reasoning_eligibility = (
            self.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
            and self.execution_status is GovernedLevel2ExecutionStatus.ACQUIRED
            and self.resulting_episode_state.status
            is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
        )
        if self.eligible_for_reasoning_reentry != expected_reasoning_eligibility:
            raise ValueError(
                "reasoning eligibility must derive only from recorded acquired E2"
            )
        if self.canonical_execution_gateway != "OfficialCapabilityGateway":
            raise ValueError("execution re-entry must preserve execution authority")
        if any(
            (
                self.invokes_reasoning,
                self.creates_questions,
                self.emits_conversation,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.starts_background_process,
            )
        ):
            raise ValueError("execution re-entry violates governed limits")


class GovernedMultiStepInvestigationExecutionReentryV1:
    """Execute one authorized step-2 read and record it in the episode."""

    def __init__(
        self,
        runtime_registry: OfficialRuntimeCapabilityRegistry,
        execution_gateway: GovernedLevel2ReadOnlyExecutionGatewayV1 | None = None,
        episode_boundary: GovernedMultiStepInvestigationEpisodeBoundaryV1
        | None = None,
    ) -> None:
        self._execution_gateway = (
            execution_gateway
            or GovernedLevel2ReadOnlyExecutionGatewayV1(runtime_registry)
        )
        self._episode_boundary = (
            episode_boundary or GovernedMultiStepInvestigationEpisodeBoundaryV1()
        )

    def consume(
        self,
        authorization_reentry: GovernedInvestigationAuthorizationReentryResult,
        *,
        now: datetime,
    ) -> GovernedInvestigationExecutionReentryResult:
        error = self._eligibility_error(authorization_reentry)
        if error is not None:
            return self._result(
                authorization_reentry,
                GovernedInvestigationExecutionReentryStatus.NOT_ELIGIBLE,
                None,
                authorization_reentry.planning_reentry.continuation.resulting_state,
                (error,),
                execution_invocation_count=0,
                episode_record_invocation_count=0,
            )

        authorization = authorization_reentry.authorization_product
        planning = authorization_reentry.planning_reentry.planning_product
        if authorization is None or planning is None:
            return self._result(
                authorization_reentry,
                GovernedInvestigationExecutionReentryStatus.NOT_ELIGIBLE,
                None,
                authorization_reentry.planning_reentry.continuation.resulting_state,
                ("execution_reentry:authorization_and_planning_required",),
                execution_invocation_count=0,
                episode_record_invocation_count=0,
            )

        try:
            envelope = self._execution_gateway.execute(
                authorization,
                planning,
                now=now,
            )
        except Exception:
            return self._result(
                authorization_reentry,
                GovernedInvestigationExecutionReentryStatus.REVIEW_REQUIRED,
                None,
                authorization_reentry.planning_reentry.continuation.resulting_state,
                ("execution_reentry:single_execution_invocation_failed",),
                execution_invocation_count=1,
                episode_record_invocation_count=0,
            )

        lineage_error = self._execution_lineage_error(
            authorization_reentry,
            envelope,
        )
        if lineage_error is not None:
            return self._result(
                authorization_reentry,
                GovernedInvestigationExecutionReentryStatus.REVIEW_REQUIRED,
                envelope,
                authorization_reentry.planning_reentry.continuation.resulting_state,
                (lineage_error,),
                execution_invocation_count=1,
                episode_record_invocation_count=0,
            )

        state = authorization_reentry.planning_reentry.continuation.resulting_state
        transition = self._episode_boundary.record_acquisition(state, envelope)
        if envelope.status is GovernedLevel2ExecutionStatus.ACQUIRED:
            if (
                transition.decision
                is not GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED
                or transition.state.status
                is not GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
                or transition.state.current_step != authorization_reentry.current_step
                or transition.state.consumed_acquisitions
                != authorization_reentry.current_step
            ):
                return self._result(
                    authorization_reentry,
                    GovernedInvestigationExecutionReentryStatus.REVIEW_REQUIRED,
                    envelope,
                    transition.state,
                    ("execution_reentry:episode_rejected_acquired_e2",),
                    execution_invocation_count=1,
                    episode_record_invocation_count=1,
                )
            return self._result(
                authorization_reentry,
                GovernedInvestigationExecutionReentryStatus.ACQUIRED,
                envelope,
                transition.state,
                (
                    "execution_reentry:e2_recorded_awaiting_reasoning_reentry",
                    *transition.rationale_codes,
                ),
                execution_invocation_count=1,
                episode_record_invocation_count=1,
            )

        status = (
            GovernedInvestigationExecutionReentryStatus.REVIEW_REQUIRED
            if transition.state.status
            is GovernedInvestigationEpisodeStatus.REVIEW_REQUIRED
            else GovernedInvestigationExecutionReentryStatus.STOPPED
        )
        return self._result(
            authorization_reentry,
            status,
            envelope,
            transition.state,
            (
                "execution_reentry:non_acquired_e2_stops_without_retry",
                *transition.rationale_codes,
            ),
            execution_invocation_count=1,
            episode_record_invocation_count=1,
        )

    @staticmethod
    def _eligibility_error(
        authorization_reentry: GovernedInvestigationAuthorizationReentryResult,
    ) -> str | None:
        planning_reentry = authorization_reentry.planning_reentry
        continuation = planning_reentry.continuation
        state = continuation.resulting_state
        if (
            authorization_reentry.status
            is not GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
        ):
            return "execution_reentry:authorized_a2_required"
        if not authorization_reentry.eligible_for_existing_execution:
            return "execution_reentry:a2_not_execution_eligible"
        if authorization_reentry.authorization_invocation_count != 1:
            return "execution_reentry:single_authorization_lineage_required"
        if not (
            2 <= authorization_reentry.current_step <= state.max_acquisitions
            and state.consumed_acquisitions
            == authorization_reentry.current_step - 1
            and authorization_reentry.remaining_acquisitions
            == state.remaining_acquisitions
            and authorization_reentry.remaining_acquisitions > 0
        ):
            return "execution_reentry:governed_step_budget_alignment_required"
        if authorization_reentry.execution_authorized:
            return "execution_reentry:unexpected_pre_authorized_state"
        if state.status is not GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING:
            return "execution_reentry:episode_not_ready_for_step_two_acquisition"
        if authorization_reentry.authorization_product is None:
            return "execution_reentry:authorization_product_required"
        if planning_reentry.planning_product is None:
            return "execution_reentry:planning_product_required"
        return None

    @staticmethod
    def _execution_lineage_error(
        authorization_reentry: GovernedInvestigationAuthorizationReentryResult,
        envelope: GovernedAcquiredEvidenceEnvelope,
    ) -> str | None:
        if envelope.authorization_id != authorization_reentry.authorization_id:
            return "execution_reentry:authorization_lineage_mismatch"
        if envelope.requirement_id != authorization_reentry.requirement_id:
            return "execution_reentry:requirement_lineage_mismatch"
        if envelope.plan_id != authorization_reentry.plan_id:
            return "execution_reentry:plan_lineage_mismatch"
        if envelope.source_reference != authorization_reentry.source_reference:
            return "execution_reentry:source_lineage_mismatch"
        if envelope.world_snapshot_id != authorization_reentry.world_snapshot_id:
            return "execution_reentry:snapshot_lineage_mismatch"
        state = authorization_reentry.planning_reentry.continuation.resulting_state
        if envelope.execution_id in state.execution_ids:
            return "execution_reentry:prior_execution_reuse_forbidden"
        return None

    @staticmethod
    def _result(
        authorization_reentry: GovernedInvestigationAuthorizationReentryResult,
        status: GovernedInvestigationExecutionReentryStatus,
        envelope: GovernedAcquiredEvidenceEnvelope | None,
        state: GovernedInvestigationEpisodeState,
        rationale_codes: tuple[str, ...],
        *,
        execution_invocation_count: int,
        episode_record_invocation_count: int,
    ) -> GovernedInvestigationExecutionReentryResult:
        fingerprint = sha256(
            repr(
                (
                    authorization_reentry.episode_id,
                    status.value,
                    authorization_reentry.authorization_id,
                    authorization_reentry.plan_id,
                    None if envelope is None else envelope.execution_id,
                    None if envelope is None else envelope.status.value,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedInvestigationExecutionReentryResult(
            episode_id=authorization_reentry.episode_id,
            authorization_reentry=authorization_reentry,
            status=status,
            evidence_envelope=envelope,
            resulting_episode_state=state,
            execution_id=None if envelope is None else envelope.execution_id,
            authorization_id=authorization_reentry.authorization_id,
            requirement_id=authorization_reentry.requirement_id,
            plan_id=authorization_reentry.plan_id,
            source_reference=authorization_reentry.source_reference,
            world_snapshot_id=authorization_reentry.world_snapshot_id,
            current_step=state.current_step,
            remaining_acquisitions=state.remaining_acquisitions,
            execution_status=None if envelope is None else envelope.status,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
            eligible_for_reasoning_reentry=(
                status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
                and envelope is not None
                and envelope.status is GovernedLevel2ExecutionStatus.ACQUIRED
                and state.status
                is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
            ),
            execution_invocation_count=execution_invocation_count,
            episode_record_invocation_count=episode_record_invocation_count,
        )
