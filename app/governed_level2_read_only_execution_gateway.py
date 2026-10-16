from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from app.governed_evidence_acquisition_productive_consumption import (
    GovernedEvidenceAcquisitionProductiveConsumption,
)
from app.governed_independence_authorization_boundary import (
    GovernedIndependenceLevel,
    GovernedInitiationDecision,
)
from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumption,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.capability_registry import (
    CapabilityEffectClass,
    CapabilityInteractionScope,
    PermissionScope,
)
from core.governed_read_only_evidence import GovernedReadOnlyEvidenceRequest


class GovernedLevel2ExecutionStatus(StrEnum):
    ACQUIRED = "acquired"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedAcquiredEvidenceEnvelope:
    execution_id: str
    status: GovernedLevel2ExecutionStatus
    authorization_id: str
    requirement_id: str
    plan_id: str
    capability_name: str | None
    evidence_description: str | None
    declared_evidence_output: str | None
    observed_value: object | None
    observation_source_reference: str | None
    source_reference: str
    world_snapshot_id: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-level2-read-only-execution-v1"
    canonical_execution_gateway: str = "OfficialCapabilityGateway"
    read_only: bool = True
    establishes_truth: bool = False
    persists_results: bool = False
    creates_questions: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    permits_retry: bool = False
    triggers_reasoning_reentry: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.execution_id.startswith("level2-read-only-execution-"):
            raise ValueError("execution envelope identifier is invalid")
        if not self.authorization_id.startswith("independence-authorization-"):
            raise ValueError("execution envelope requires authorization lineage")
        if not self.requirement_id.startswith("discrimination-requirement-"):
            raise ValueError("execution envelope requires requirement lineage")
        if not self.plan_id.startswith("evidence-acquisition-plan-"):
            raise ValueError("execution envelope requires planning lineage")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("execution envelope requires rationale codes")
        if not self.read_only or any(
            (
                self.establishes_truth,
                self.persists_results,
                self.creates_questions,
                self.modifies_memory,
                self.modifies_world_model,
                self.permits_retry,
                self.triggers_reasoning_reentry,
                self.starts_background_process,
            )
        ):
            raise ValueError("execution envelope violates governed limits")


class GovernedLevel2ReadOnlyExecutionGatewayV1:
    """One-shot Level 2 read through the existing official capability gateway."""

    def __init__(self, runtime_registry: OfficialRuntimeCapabilityRegistry) -> None:
        self._runtime_registry = runtime_registry

    def execute(
        self,
        authorization: GovernedIndependenceAuthorizationProductiveConsumption,
        planning: GovernedEvidenceAcquisitionProductiveConsumption,
        *,
        now: datetime,
    ) -> GovernedAcquiredEvidenceEnvelope:
        gate = self._preflight(authorization, planning)
        if gate is not None:
            return gate
        capability_name = authorization.capability_name
        if capability_name is None:
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.DENIED,
                None,
                None,
                None,
                None,
                ("execution:authorized_capability_missing",),
            )
        registration = self._runtime_registry.registration_for(capability_name)
        if registration is None or not registration.descriptor.enabled:
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.UNAVAILABLE,
                capability_name,
                None,
                None,
                None,
                ("execution:authorized_capability_unavailable",),
            )
        if registration.evidence_reader is None:
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.UNAVAILABLE,
                capability_name,
                None,
                None,
                None,
                ("execution:evidence_reader_unavailable",),
            )
        descriptor = registration.descriptor
        if (
            descriptor.normalized_effect_class is not CapabilityEffectClass.READ_ONLY
            or descriptor.normalized_interaction_scope
            is not CapabilityInteractionScope.INTERNAL
            or descriptor.normalized_permission_scope is PermissionScope.NETWORK
        ):
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.DENIED,
                capability_name,
                None,
                None,
                None,
                ("execution:v1_local_read_only_contract_not_satisfied",),
            )
        candidate = planning.candidates[0]
        if candidate.capability_name != capability_name:
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.REVIEW_REQUIRED,
                capability_name,
                None,
                None,
                None,
                ("execution:planning_authorization_capability_mismatch",),
            )
        if candidate.declared_evidence_output not in descriptor.evidence_outputs:
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.REVIEW_REQUIRED,
                capability_name,
                candidate.evidence_description,
                candidate.declared_evidence_output,
                None,
                ("execution:evidence_output_declaration_mismatch",),
            )
        request = GovernedReadOnlyEvidenceRequest(
            authorization_id=authorization.authorization_id,
            requirement_id=authorization.requirement_id,
            plan_id=authorization.plan_id,
            capability_name=capability_name,
            evidence_description=candidate.evidence_description,
            declared_evidence_output=candidate.declared_evidence_output,
            source_reference=authorization.source_reference,
            world_snapshot_id=authorization.world_snapshot_id,
        )
        try:
            observation = (
                self._runtime_registry.execute_read_only_evidence_registration(
                    registration,
                request,
                    now=now,
                )
            )
        except Exception as exc:
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.FAILED,
                capability_name,
                candidate.evidence_description,
                candidate.declared_evidence_output,
                None,
                (f"execution:single_attempt_failed:{type(exc).__name__}",),
            )
        if observation.evidence_output != candidate.declared_evidence_output:
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.REVIEW_REQUIRED,
                capability_name,
                candidate.evidence_description,
                candidate.declared_evidence_output,
                None,
                ("execution:observation_output_mismatch",),
            )
        return self._result(
            authorization,
            planning,
            GovernedLevel2ExecutionStatus.ACQUIRED,
            capability_name,
            candidate.evidence_description,
            candidate.declared_evidence_output,
            (observation.value, observation.source_reference),
            (
                "execution:one_read_only_observation_acquired",
                *observation.rationale_codes,
            ),
        )

    def _preflight(self, authorization, planning):
        if (
            authorization.decision is not GovernedInitiationDecision.MAY_INITIATE
            or authorization.independence_level
            is not GovernedIndependenceLevel.LEVEL_2_READ_ONLY
            or not authorization.eligible_for_next_governed_gate
        ):
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.DENIED,
                authorization.capability_name,
                None,
                None,
                None,
                ("execution:level2_may_initiate_required",),
            )
        if authorization.execution_authorized:
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.REVIEW_REQUIRED,
                authorization.capability_name,
                None,
                None,
                None,
                ("execution:unexpected_pre_authorized_state",),
            )
        if (
            authorization.requirement_id != planning.requirement_id
            or authorization.plan_id != planning.planning_report.plan_id
            or authorization.source_reference != planning.source_reference
            or authorization.world_snapshot_id != planning.world_snapshot_id
        ):
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.REVIEW_REQUIRED,
                authorization.capability_name,
                None,
                None,
                None,
                ("execution:authorization_planning_lineage_mismatch",),
            )
        if len(planning.candidates) != 1:
            return self._result(
                authorization,
                planning,
                GovernedLevel2ExecutionStatus.REVIEW_REQUIRED,
                authorization.capability_name,
                None,
                None,
                None,
                ("execution:exactly_one_planning_candidate_required",),
            )
        return None

    @staticmethod
    def _result(
        authorization,
        planning,
        status,
        capability_name,
        evidence_description,
        declared_evidence_output,
        observation,
        rationale_codes,
    ):
        observed_value = None if observation is None else observation[0]
        observation_source = None if observation is None else observation[1]
        fingerprint = sha256(
            repr(
                (
                    authorization.authorization_id,
                    authorization.requirement_id,
                    authorization.plan_id,
                    status.value,
                    capability_name,
                    evidence_description,
                    declared_evidence_output,
                    observation_source,
                    repr(observed_value),
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedAcquiredEvidenceEnvelope(
            execution_id=f"level2-read-only-execution-{fingerprint[:24]}",
            status=status,
            authorization_id=authorization.authorization_id,
            requirement_id=authorization.requirement_id,
            plan_id=authorization.plan_id,
            capability_name=capability_name,
            evidence_description=evidence_description,
            declared_evidence_output=declared_evidence_output,
            observed_value=observed_value,
            observation_source_reference=observation_source,
            source_reference=authorization.source_reference,
            world_snapshot_id=authorization.world_snapshot_id,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
