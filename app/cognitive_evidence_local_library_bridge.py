from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from types import SimpleNamespace

from core.governed_provider_routing import ProviderRouteStatus
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)
from core.knowledge_source_policy import (
    KnowledgeSourceDecision,
    KnowledgeSourcePolicy,
    KnowledgeSourcePolicyRequest,
    KnowledgeSourceStatus,
)

from .governed_roby_initiated_library_access import (
    GovernedRobyInitiatedLibraryAccessResult,
    GovernedRobyInitiatedLibraryAccessV1,
)
from .knowledge_runtime import (
    KnowledgeRuntimeAssessment,
    OfficialKnowledgeRuntimeGateway,
)


class GovernedCognitiveEvidenceLibraryBridgeStatus(str, Enum):
    LOCAL_LIBRARY_PROPOSED = "local_library_proposed"
    INTERNAL_SUFFICIENT = "internal_sufficient"
    EXTERNAL_REQUIRED = "external_required"
    VERIFICATION_REQUIRED = "verification_required"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"
    LIBRARY_UNAVAILABLE = "library_unavailable"


@dataclass(frozen=True)
class GovernedCognitiveEvidenceLibraryRequest:
    owner: str
    requirement: DiscriminatingEvidenceRequirement
    internal_confidence: float
    library_available: bool

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("cognitive evidence owner must not be blank")
        if not 0 <= self.internal_confidence <= 1:
            raise ValueError("internal confidence must be between zero and one")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class GovernedCognitiveEvidenceLibraryProposal:
    owner: str
    search_query: str
    reason: str
    source_reference: str
    world_snapshot_id: str
    requirement_id: str
    source_decision_id: str

    def __post_init__(self) -> None:
        for name in (
            "owner",
            "search_query",
            "reason",
            "source_reference",
            "world_snapshot_id",
            "requirement_id",
            "source_decision_id",
        ):
            value = getattr(self, name).strip()
            if not value:
                raise ValueError(f"cognitive library proposal {name} must not be blank")
            object.__setattr__(self, name, value)


@dataclass(frozen=True)
class GovernedCognitiveEvidenceLibraryResult:
    status: GovernedCognitiveEvidenceLibraryBridgeStatus
    request: GovernedCognitiveEvidenceLibraryRequest
    assessment: KnowledgeRuntimeAssessment
    source_decision: KnowledgeSourceDecision
    proposal: GovernedCognitiveEvidenceLibraryProposal | None = None
    dispatch_result: GovernedRobyInitiatedLibraryAccessResult | None = None


class GovernedCognitiveEvidenceToLocalLibraryBridgeV1:
    """Bridge one reasoning evidence gap into the existing governed library path."""

    def __init__(
        self,
        *,
        knowledge_runtime: OfficialKnowledgeRuntimeGateway,
        roby_initiated: GovernedRobyInitiatedLibraryAccessV1,
        source_policy: KnowledgeSourcePolicy | None = None,
    ) -> None:
        self.knowledge_runtime = knowledge_runtime
        self.roby_initiated = roby_initiated
        self.source_policy = source_policy or KnowledgeSourcePolicy()

    def handle(
        self,
        request: GovernedCognitiveEvidenceLibraryRequest,
        *,
        now: datetime,
    ) -> GovernedCognitiveEvidenceLibraryResult:
        if now.tzinfo is None:
            raise ValueError("cognitive evidence bridge time must be timezone-aware")
        assessment = self.knowledge_runtime.assess_evidence_requirement(
            request.requirement,
            request.internal_confidence,
            request.library_available,
        )
        route = self._no_provider_route(
            request.owner, request.requirement.requirement_id
        )
        source_decision = self.source_policy.decide(
            KnowledgeSourcePolicyRequest(
                owner=request.owner,
                provider_route=route,
                need=assessment.need,
            ),
            now=now,
        )
        if not request.library_available:
            return self._result(
                GovernedCognitiveEvidenceLibraryBridgeStatus.LIBRARY_UNAVAILABLE,
                request,
                assessment,
                source_decision,
            )
        if source_decision.status is KnowledgeSourceStatus.LOCAL_SOURCE_PREFERRED:
            proposal = GovernedCognitiveEvidenceLibraryProposal(
                owner=request.owner,
                search_query=assessment.query,
                reason=(
                    "Evidencia discriminante local requerida por "
                    "razonamiento gobernado: "
                    f"{request.requirement.requirement_id}"
                ),
                source_reference=request.requirement.source_reference,
                world_snapshot_id=request.requirement.world_snapshot_id,
                requirement_id=request.requirement.requirement_id,
                source_decision_id=source_decision.decision_id,
            )
            dispatch_result = self.roby_initiated.handle_proposal(
                owner=proposal.owner,
                search_query=proposal.search_query,
                reason=proposal.reason,
                source_reference=proposal.source_reference,
                world_snapshot_id=proposal.world_snapshot_id,
                now=now,
            )
            return GovernedCognitiveEvidenceLibraryResult(
                status=GovernedCognitiveEvidenceLibraryBridgeStatus.LOCAL_LIBRARY_PROPOSED,
                request=request,
                assessment=assessment,
                source_decision=source_decision,
                proposal=proposal,
                dispatch_result=dispatch_result,
            )
        status_map = {
            KnowledgeSourceStatus.INTERNAL_SUFFICIENT: (
                GovernedCognitiveEvidenceLibraryBridgeStatus.INTERNAL_SUFFICIENT
            ),
            KnowledgeSourceStatus.EXTERNAL_SOURCE_REQUIRED: (
                GovernedCognitiveEvidenceLibraryBridgeStatus.EXTERNAL_REQUIRED
            ),
            KnowledgeSourceStatus.VERIFICATION_REQUIRED: (
                GovernedCognitiveEvidenceLibraryBridgeStatus.VERIFICATION_REQUIRED
            ),
            KnowledgeSourceStatus.WITHHELD: (
                GovernedCognitiveEvidenceLibraryBridgeStatus.WITHHELD
            ),
            KnowledgeSourceStatus.NOT_APPLICABLE: (
                GovernedCognitiveEvidenceLibraryBridgeStatus.NOT_APPLICABLE
            ),
        }
        return self._result(
            status_map[source_decision.status],
            request,
            assessment,
            source_decision,
        )

    @staticmethod
    def _no_provider_route(owner: str, requirement_id: str):
        request = SimpleNamespace(owner=owner)
        return SimpleNamespace(
            request=request,
            status=ProviderRouteStatus.NO_PROVIDER_REQUIRED,
            route_id=sha256(
                f"cognitive-library|{owner.casefold()}|{requirement_id}".encode()
            ).hexdigest(),
        )

    @staticmethod
    def _result(
        status: GovernedCognitiveEvidenceLibraryBridgeStatus,
        request: GovernedCognitiveEvidenceLibraryRequest,
        assessment: KnowledgeRuntimeAssessment,
        source_decision: KnowledgeSourceDecision,
    ) -> GovernedCognitiveEvidenceLibraryResult:
        return GovernedCognitiveEvidenceLibraryResult(
            status=status,
            request=request,
            assessment=assessment,
            source_decision=source_decision,
        )
