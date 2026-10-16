from __future__ import annotations

from app.governed_external_information_source_integration import (
    GovernedExternalInformationSourceIntegration,
)
from app.governed_place_business_source_query_composition import (
    GovernedPlaceBusinessSourceQueryCompositionResult as PreparedResult,
)
from app.governed_place_business_source_query_composition import (
    GovernedPlaceBusinessSourceQueryCompositionStatus as PreparationStatus,
)
from app.official_conversation_gateway import OfficialConversationGateway
from core.governed_external_intelligence.models import (
    ExternalIntelligenceCapability,
    ExternalIntelligenceEnvelope,
    ExternalIntelligenceRequest,
)


class GovernedPlaceBusinessExternalExecutionComposition:
    """Execute one explicitly authorized prepared place/business query to M400."""

    def __init__(
        self,
        *,
        gateway: OfficialConversationGateway,
        integration: GovernedExternalInformationSourceIntegration | None = None,
    ) -> None:
        self._gateway = gateway
        self._integration = (
            integration or GovernedExternalInformationSourceIntegration()
        )

    def execute(
        self,
        prepared: PreparedResult,
        *,
        external_access_authorized: bool,
        request_id: str,
        owner: str,
        purpose: str,
        network_used: bool,
    ) -> ExternalIntelligenceEnvelope:
        if not external_access_authorized:
            raise ValueError("explicit external access authorization is required")
        if (
            prepared.status is not PreparationStatus.PREPARED
            or prepared.prepared_query is None
        ):
            raise ValueError("S2B-A requires an already PREPARED S1 result")

        prepared_query = prepared.prepared_query
        source_id = prepared_query.source.source_id
        if prepared_query.query.source_id != source_id:
            raise ValueError("prepared query source identity must be preserved")

        executed = self._gateway.execute_governed_source_query(prepared_query.query)
        request = ExternalIntelligenceRequest(
            request_id=request_id,
            owner=owner,
            capability=ExternalIntelligenceCapability.INFORMATION_SOURCE,
            purpose=purpose,
            target_id=source_id,
            external_access_requested=external_access_authorized,
        )
        return self._integration.admit_traced_query_result(
            request,
            executed,
            network_used=network_used,
        )
