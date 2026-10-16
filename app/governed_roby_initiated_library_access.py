from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.governed_local_library.initiative import LOCAL_LIBRARY_READ_CAPABILITY

from .governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
    GovernedIndependenceAuthorizationReport,
    GovernedInitiationDecision,
    GovernedReadOnlyCapabilityInitiationRequest,
)
from .governed_local_library_conversation import (
    GovernedLocalLibraryConversationResult,
    GovernedLocalLibraryConversationStatus,
    GovernedLocalLibraryConversationV1,
)


class GovernedRobyInitiatedLibraryAccessStatus(str, Enum):
    COMPLETED = "completed"
    NO_MATCH = "no_match"
    NEEDS_DISAMBIGUATION = "needs_disambiguation"
    MUST_ASK = "must_ask"
    ABSTAINED = "abstained"
    REVIEW_REQUIRED = "review_required"
    FAILED = "failed"


@dataclass(frozen=True)
class GovernedRobyInitiatedLibraryAccessResult:
    status: GovernedRobyInitiatedLibraryAccessStatus
    authorization: GovernedIndependenceAuthorizationReport
    transparency_message: str | None = None
    library_result: GovernedLocalLibraryConversationResult | None = None


class GovernedRobyInitiatedLibraryAccessV1:
    """Authorize ROBY initiative, then reuse the certified library conversation path."""

    def __init__(
        self,
        *,
        authorization_boundary: GovernedIndependenceAuthorizationBoundaryV1,
        library_conversation: GovernedLocalLibraryConversationV1,
    ) -> None:
        self.authorization_boundary = authorization_boundary
        self.library_conversation = library_conversation

    def handle_proposal(
        self,
        *,
        owner: str,
        search_query: str,
        reason: str,
        source_reference: str,
        world_snapshot_id: str,
        now: datetime,
    ) -> GovernedRobyInitiatedLibraryAccessResult:
        if now.tzinfo is None:
            raise ValueError("ROBY-initiated library time must be timezone-aware")
        request = GovernedReadOnlyCapabilityInitiationRequest(
            owner=owner,
            capability_name=LOCAL_LIBRARY_READ_CAPABILITY,
            reason=reason,
            source_reference=source_reference,
            world_snapshot_id=world_snapshot_id,
        )
        authorization = self.authorization_boundary.evaluate_capability_initiation(
            request
        )
        if authorization.decision is GovernedInitiationDecision.MUST_ASK:
            return self._result(
                GovernedRobyInitiatedLibraryAccessStatus.MUST_ASK,
                authorization,
            )
        if authorization.decision is GovernedInitiationDecision.MUST_ABSTAIN:
            return self._result(
                GovernedRobyInitiatedLibraryAccessStatus.ABSTAINED,
                authorization,
            )
        if authorization.decision is GovernedInitiationDecision.REVIEW_REQUIRED:
            return self._result(
                GovernedRobyInitiatedLibraryAccessStatus.REVIEW_REQUIRED,
                authorization,
            )

        transparency = (
            "Voy a consultar la Biblioteca para buscar evidencia local relevante."
        )
        library_result = self.library_conversation.handle_admitted_request(
            owner=owner,
            search_query=search_query,
            now=now,
        )
        status_map = {
            GovernedLocalLibraryConversationStatus.COMPLETED:
                GovernedRobyInitiatedLibraryAccessStatus.COMPLETED,
            GovernedLocalLibraryConversationStatus.NO_MATCH:
                GovernedRobyInitiatedLibraryAccessStatus.NO_MATCH,
            GovernedLocalLibraryConversationStatus.NEEDS_DISAMBIGUATION:
                GovernedRobyInitiatedLibraryAccessStatus.NEEDS_DISAMBIGUATION,
            GovernedLocalLibraryConversationStatus.FAILED:
                GovernedRobyInitiatedLibraryAccessStatus.FAILED,
        }
        return GovernedRobyInitiatedLibraryAccessResult(
            status=status_map[library_result.status],
            authorization=authorization,
            transparency_message=transparency,
            library_result=library_result,
        )

    @staticmethod
    def _result(
        status: GovernedRobyInitiatedLibraryAccessStatus,
        authorization: GovernedIndependenceAuthorizationReport,
    ) -> GovernedRobyInitiatedLibraryAccessResult:
        return GovernedRobyInitiatedLibraryAccessResult(
            status=status,
            authorization=authorization,
        )
