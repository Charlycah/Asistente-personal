from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256

from core.governed_reasoning.context import ReasoningQuery
from core.governed_reasoning.evidence import (
    EvidenceKind,
    EvidenceReference,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)
from core.governed_reasoning.orchestrator import GovernedReasoningResult
from core.knowledge_source_policy import KnowledgeSourceKind

from .cognitive_evidence_local_library_bridge import (
    GovernedCognitiveEvidenceLibraryBridgeStatus,
    GovernedCognitiveEvidenceLibraryResult,
)
from .governed_local_library_conversation import (
    GovernedLocalLibraryConversationStatus,
)
from .governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from .governed_roby_initiated_library_access import (
    GovernedRobyInitiatedLibraryAccessStatus,
)

_MAX_SUMMARY_CHARS = 2_000


class GovernedLocalEvidenceReasoningReentryStatus(str, Enum):
    REEVALUATED = "reevaluated"
    NOT_ELIGIBLE = "not_eligible"
    ALREADY_CONSUMED = "already_consumed"
    REVIEW_REQUIRED = "review_required"
    LINEAGE_MISMATCH = "lineage_mismatch"


@dataclass(frozen=True)
class GovernedLocalEvidenceReasoningReentryRequest:
    owner: str
    turn_id: str
    originating_reasoning_id: str
    requirement: DiscriminatingEvidenceRequirement
    episode_id: str
    bridge_result: GovernedCognitiveEvidenceLibraryResult


@dataclass(frozen=True)
class GovernedLocalEvidenceReasoningReentryResult:
    reentry_id: str
    status: GovernedLocalEvidenceReasoningReentryStatus
    owner: str
    turn_id: str
    originating_reasoning_id: str
    requirement_id: str
    episode_id: str
    source_decision_id: str | None = None
    knowledge_execution_id: str | None = None
    selected_source_reference: str | None = None
    evidence_id: str | None = None
    reasoning_result: GovernedReasoningResult | None = None
    rationale_codes: tuple[str, ...] = ()
    source_fingerprint: str = ""


class GovernedLocalEvidenceReasoningReentryV1:
    """Re-enter one already-acquired local artifact through reasoning authority."""

    def __init__(
        self,
        *,
        reasoning_gateway: OfficialGovernedReasoningRuntimeGateway,
    ) -> None:
        self.reasoning_gateway = reasoning_gateway
        self._consumed_execution_ids: set[str] = set()

    def reenter(
        self,
        request: GovernedLocalEvidenceReasoningReentryRequest,
        *,
        now: datetime,
    ) -> GovernedLocalEvidenceReasoningReentryResult:
        if now.tzinfo is None:
            raise ValueError("local evidence re-entry time must be timezone-aware")
        bridge = request.bridge_result
        source_decision = bridge.source_decision
        base = dict(
            owner=request.owner,
            turn_id=request.turn_id,
            originating_reasoning_id=request.originating_reasoning_id,
            requirement_id=request.requirement.requirement_id,
            episode_id=request.episode_id,
            source_decision_id=source_decision.decision_id,
        )
        if (
            bridge.status
            is not GovernedCognitiveEvidenceLibraryBridgeStatus.LOCAL_LIBRARY_PROPOSED
            or bridge.dispatch_result is None
            or bridge.dispatch_result.status
            is not GovernedRobyInitiatedLibraryAccessStatus.COMPLETED
            or bridge.dispatch_result.library_result is None
            or bridge.dispatch_result.library_result.status
            is not GovernedLocalLibraryConversationStatus.COMPLETED
        ):
            return self._result(
                GovernedLocalEvidenceReasoningReentryStatus.NOT_ELIGIBLE,
                rationale_codes=("completed_local_artifact_required",),
                **base,
            )

        library_result = bridge.dispatch_result.library_result
        artifact = library_result.artifact
        execution = library_result.execution
        selected_source_reference = library_result.source_reference
        if (
            artifact is None
            or execution is None
            or artifact.source is not KnowledgeSourceKind.LOCAL_DOCUMENTS
            or not selected_source_reference
        ):
            return self._result(
                GovernedLocalEvidenceReasoningReentryStatus.NOT_ELIGIBLE,
                selected_source_reference=selected_source_reference,
                rationale_codes=("local_documents_artifact_required",),
                **base,
            )

        if (
            bridge.request.requirement.requirement_id
            != request.requirement.requirement_id
            or bridge.proposal is None
            or bridge.proposal.requirement_id != request.requirement.requirement_id
            or bridge.proposal.source_reference != request.requirement.source_reference
            or bridge.proposal.world_snapshot_id
            != request.requirement.world_snapshot_id
        ):
            return self._result(
                GovernedLocalEvidenceReasoningReentryStatus.LINEAGE_MISMATCH,
                knowledge_execution_id=execution.execution_id,
                selected_source_reference=selected_source_reference,
                rationale_codes=("cognitive_requirement_lineage_mismatch",),
                **base,
            )

        if execution.execution_id in self._consumed_execution_ids:
            return self._result(
                GovernedLocalEvidenceReasoningReentryStatus.ALREADY_CONSUMED,
                knowledge_execution_id=execution.execution_id,
                selected_source_reference=selected_source_reference,
                rationale_codes=("knowledge_execution_already_consumed",),
                **base,
            )

        fingerprint = sha256(
            "|".join(
                (
                    execution.execution_id,
                    artifact.content,
                    selected_source_reference,
                    request.requirement.requirement_id,
                )
            ).encode("utf-8")
        ).hexdigest()
        summary = artifact.content[:_MAX_SUMMARY_CHARS].strip()
        reference = EvidenceReference(
            source_type=EvidenceSourceType.KNOWLEDGE,
            source_id=execution.execution_id,
            kind=EvidenceKind.OBSERVATION,
            owner=request.owner,
            status=EvidenceStatus.ACTIVE,
            sensitivity=EvidenceSensitivity.PERSONAL,
            observed_at=execution.created_at,
            fingerprint=fingerprint,
            summary=summary,
            metadata=(
                ("epistemic_role", "local_document_evidence_not_truth"),
                ("originating_reasoning_id", request.originating_reasoning_id),
                ("requirement_id", request.requirement.requirement_id),
                ("episode_id", request.episode_id),
                ("source_decision_id", source_decision.decision_id),
                ("knowledge_execution_id", execution.execution_id),
                ("selected_source_reference", selected_source_reference),
                ("world_snapshot_id", request.requirement.world_snapshot_id),
                ("knowledge_source", artifact.source.value),
            ),
        )
        registry = (
            self.reasoning_gateway.orchestrator.context_assembler.evidence_registry
        )
        registry.register_reference(reference, source=artifact)
        query = ReasoningQuery(
            text=" ".join(request.requirement.missing_evidence_descriptions),
            owner=request.owner,
            evidence_ids=(reference.evidence_id,),
            as_of=now,
        )
        reasoning_result = self.reasoning_gateway.reason(query, now=now)
        self._consumed_execution_ids.add(execution.execution_id)
        status = (
            GovernedLocalEvidenceReasoningReentryStatus.REVIEW_REQUIRED
            if reasoning_result.requires_human_review
            else GovernedLocalEvidenceReasoningReentryStatus.REEVALUATED
        )
        return self._result(
            status,
            knowledge_execution_id=execution.execution_id,
            selected_source_reference=selected_source_reference,
            evidence_id=reference.evidence_id,
            reasoning_result=reasoning_result,
            rationale_codes=("local_document_evidence_reentered_once",),
            source_fingerprint=fingerprint,
            **base,
        )

    @staticmethod
    def _result(
        status: GovernedLocalEvidenceReasoningReentryStatus,
        *,
        owner: str,
        turn_id: str,
        originating_reasoning_id: str,
        requirement_id: str,
        episode_id: str,
        source_decision_id: str | None = None,
        knowledge_execution_id: str | None = None,
        selected_source_reference: str | None = None,
        evidence_id: str | None = None,
        reasoning_result: GovernedReasoningResult | None = None,
        rationale_codes: tuple[str, ...] = (),
        source_fingerprint: str = "",
    ) -> GovernedLocalEvidenceReasoningReentryResult:
        identity = "|".join(
            (
                owner.casefold(),
                turn_id,
                originating_reasoning_id,
                requirement_id,
                episode_id,
                status.value,
                knowledge_execution_id or "none",
                evidence_id or "none",
            )
        )
        return GovernedLocalEvidenceReasoningReentryResult(
            reentry_id=(
                "local-evidence-reentry-" + sha256(identity.encode()).hexdigest()
            ),
            status=status,
            owner=owner,
            turn_id=turn_id,
            originating_reasoning_id=originating_reasoning_id,
            requirement_id=requirement_id,
            episode_id=episode_id,
            source_decision_id=source_decision_id,
            knowledge_execution_id=knowledge_execution_id,
            selected_source_reference=selected_source_reference,
            evidence_id=evidence_id,
            reasoning_result=reasoning_result,
            rationale_codes=rationale_codes,
            source_fingerprint=source_fingerprint,
        )
