from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from core.governed_reasoning import (
    EvidenceKind,
    EvidenceReference,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
    GovernedReasoningResult,
    ReasoningQuery,
)
from core.scope_guard import ScopeDomain


class GovernedReasoningReentryStatus(StrEnum):
    REEVALUATED = "reevaluated"
    NOT_ELIGIBLE = "not_eligible"
    ALREADY_CONSUMED = "already_consumed"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedLevel2ReasoningReentryResult:
    reentry_id: str
    status: GovernedReasoningReentryStatus
    execution_id: str
    authorization_id: str
    requirement_id: str
    plan_id: str
    capability_name: str | None
    evidence_id: str | None
    source_reference: str
    world_snapshot_id: str
    reasoning_result: GovernedReasoningResult | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-level2-reasoning-reentry-v1"
    canonical_reasoning_authority: str = "governed_reasoning"
    automatic_reevaluation_count: int = 0
    establishes_truth: bool = False
    persists_memory: bool = False
    modifies_world_model: bool = False
    invokes_capabilities: bool = False
    permits_follow_up_execution: bool = False
    creates_questions: bool = False
    emits_conversation: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.reentry_id.startswith("level2-reasoning-reentry-"):
            raise ValueError("reasoning re-entry identifier is invalid")
        if self.automatic_reevaluation_count not in {0, 1}:
            raise ValueError("reasoning re-entry permits at most one reevaluation")
        if (
            self.status is GovernedReasoningReentryStatus.REEVALUATED
            and self.automatic_reevaluation_count != 1
        ):
            raise ValueError("successful re-entry requires exactly one reevaluation")
        if (
            self.status is not GovernedReasoningReentryStatus.REEVALUATED
            and self.automatic_reevaluation_count != 0
        ):
            raise ValueError("non-reevaluated result cannot count a reevaluation")
        if self.canonical_reasoning_authority != "governed_reasoning":
            raise ValueError("reasoning re-entry must preserve canonical authority")
        if any(
            (
                self.establishes_truth,
                self.persists_memory,
                self.modifies_world_model,
                self.invokes_capabilities,
                self.permits_follow_up_execution,
                self.creates_questions,
                self.emits_conversation,
                self.starts_background_process,
            )
        ):
            raise ValueError("reasoning re-entry violates governed limits")


class GovernedLevel2ReasoningReentryFoundationV1:
    """One-shot adapter from acquired evidence into governed reasoning."""

    def __init__(
        self,
        reasoning_gateway: object,
    ) -> None:
        if not hasattr(reasoning_gateway, "orchestrator") or not callable(
            getattr(reasoning_gateway, "reason", None)
        ):
            raise TypeError("reasoning re-entry requires governed reasoning gateway")
        self._reasoning_gateway = reasoning_gateway
        self._consumed_execution_ids: set[str] = set()

    def reenter(
        self,
        envelope: GovernedAcquiredEvidenceEnvelope,
        *,
        now: datetime,
    ) -> GovernedLevel2ReasoningReentryResult:
        if now.tzinfo is None:
            raise ValueError("reasoning re-entry timestamp must be timezone-aware")
        if envelope.execution_id in self._consumed_execution_ids:
            return self._result(
                envelope,
                GovernedReasoningReentryStatus.ALREADY_CONSUMED,
                None,
                None,
                ("reentry:execution_lineage_already_consumed",),
            )
        eligibility = self._eligibility_error(envelope)
        if eligibility is not None:
            return self._result(
                envelope,
                GovernedReasoningReentryStatus.NOT_ELIGIBLE,
                None,
                None,
                (eligibility,),
            )

        reference = self._evidence_reference(envelope, now)
        context_assembler = self._reasoning_gateway.orchestrator.context_assembler
        registry = context_assembler.evidence_registry
        registry.register_reference(reference, source=envelope)
        query = ReasoningQuery(
            text=(
                "Reevaluate the governed hypothesis context using the acquired "
                f"observation for requirement {envelope.requirement_id}."
            ),
            owner="shared",
            domains=(ScopeDomain.PERSONAL_OPERATIONS,),
            topics=(
                envelope.evidence_description or "acquired evidence",
                envelope.declared_evidence_output or "observation",
            ),
            evidence_ids=(reference.evidence_id,),
            as_of=now,
        )
        self._consumed_execution_ids.add(envelope.execution_id)
        try:
            reasoning_result = self._reasoning_gateway.reason(query, now=now)
        except Exception:
            return self._result(
                envelope,
                GovernedReasoningReentryStatus.REVIEW_REQUIRED,
                reference.evidence_id,
                None,
                ("reentry:single_reasoning_evaluation_failed",),
            )
        return self._result(
            envelope,
            GovernedReasoningReentryStatus.REEVALUATED,
            reference.evidence_id,
            reasoning_result,
            ("reentry:one_governed_reasoning_reevaluation_completed",),
        )

    @staticmethod
    def _eligibility_error(
        envelope: GovernedAcquiredEvidenceEnvelope,
    ) -> str | None:
        if envelope.status is not GovernedLevel2ExecutionStatus.ACQUIRED:
            return "reentry:acquired_execution_required"
        if envelope.establishes_truth:
            return "reentry:truth_establishing_input_forbidden"
        if (
            envelope.observed_value is None
            or envelope.capability_name is None
            or envelope.evidence_description is None
            or envelope.declared_evidence_output is None
            or envelope.observation_source_reference is None
        ):
            return "reentry:complete_acquired_evidence_required"
        if (
            not envelope.authorization_id.startswith("independence-authorization-")
            or not envelope.requirement_id.startswith("discrimination-requirement-")
            or not envelope.plan_id.startswith("evidence-acquisition-plan-")
            or not envelope.source_reference.strip()
            or not envelope.world_snapshot_id.strip()
        ):
            return "reentry:complete_lineage_required"
        return None

    @staticmethod
    def _evidence_reference(
        envelope: GovernedAcquiredEvidenceEnvelope,
        now: datetime,
    ) -> EvidenceReference:
        fingerprint = sha256(
            repr(
                (
                    envelope.execution_id,
                    envelope.authorization_id,
                    envelope.requirement_id,
                    envelope.plan_id,
                    envelope.capability_name,
                    envelope.evidence_description,
                    envelope.declared_evidence_output,
                    envelope.observation_source_reference,
                    repr(envelope.observed_value),
                    envelope.source_reference,
                    envelope.world_snapshot_id,
                )
            ).encode("utf-8")
        ).hexdigest()
        return EvidenceReference(
            source_type=EvidenceSourceType.LEVEL2_ACQUIRED,
            source_id=envelope.execution_id,
            kind=EvidenceKind.OBSERVATION,
            owner="shared",
            status=EvidenceStatus.ACTIVE,
            sensitivity=EvidenceSensitivity.PERSONAL,
            observed_at=now,
            fingerprint=fingerprint,
            summary=(
                f"{envelope.evidence_description}: "
                f"{envelope.observed_value!r}"
            ),
            metadata=(
                ("authorization_id", envelope.authorization_id),
                ("requirement_id", envelope.requirement_id),
                ("plan_id", envelope.plan_id),
                ("capability_name", envelope.capability_name),
                (
                    "declared_evidence_output",
                    envelope.declared_evidence_output,
                ),
                (
                    "observation_source_reference",
                    envelope.observation_source_reference,
                ),
                ("source_reference", envelope.source_reference),
                ("world_snapshot_id", envelope.world_snapshot_id),
                ("epistemic_role", "observation_not_truth"),
            ),
        )

    @staticmethod
    def _result(
        envelope: GovernedAcquiredEvidenceEnvelope,
        status: GovernedReasoningReentryStatus,
        evidence_id: str | None,
        reasoning_result: GovernedReasoningResult | None,
        rationale_codes: tuple[str, ...],
    ) -> GovernedLevel2ReasoningReentryResult:
        fingerprint = sha256(
            repr(
                (
                    envelope.execution_id,
                    status.value,
                    evidence_id,
                    None
                    if reasoning_result is None
                    else reasoning_result.decision.decision_id,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedLevel2ReasoningReentryResult(
            reentry_id=f"level2-reasoning-reentry-{fingerprint[:24]}",
            status=status,
            execution_id=envelope.execution_id,
            authorization_id=envelope.authorization_id,
            requirement_id=envelope.requirement_id,
            plan_id=envelope.plan_id,
            capability_name=envelope.capability_name,
            evidence_id=evidence_id,
            source_reference=envelope.source_reference,
            world_snapshot_id=envelope.world_snapshot_id,
            reasoning_result=reasoning_result,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
            automatic_reevaluation_count=(
                1
                if status is GovernedReasoningReentryStatus.REEVALUATED
                else 0
            ),
        )
