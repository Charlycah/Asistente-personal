from __future__ import annotations

from core.governed_provider_execution_adapter import (
    LocalProviderExecutionResult,
    LocalProviderExecutionStatus,
)
from core.provider_health_evaluation import ProviderKind

from .boundary import GovernedExternalIntelligenceBoundary
from .models import (
    ExternalExecutionScope,
    ExternalIntelligenceCapability,
    ExternalIntelligenceEnvelope,
    ExternalIntelligenceProvenance,
    ExternalIntelligenceRequest,
)


class GovernedExternalProviderIntegration:
    """Admits results from the existing governed provider execution path."""

    INTEGRATION_ID = "external_intelligence_provider_integration"

    def __init__(
        self,
        boundary: GovernedExternalIntelligenceBoundary | None = None,
    ) -> None:
        self._boundary = boundary or GovernedExternalIntelligenceBoundary()

    @property
    def integration_id(self) -> str:
        return self.INTEGRATION_ID

    def admit_execution_result(
        self,
        request: ExternalIntelligenceRequest,
        execution: LocalProviderExecutionResult,
        *,
        network_used: bool,
    ) -> ExternalIntelligenceEnvelope:
        if request.capability is not ExternalIntelligenceCapability.INFERENCE_PROVIDER:
            raise ValueError("provider integration requires inference capability")
        if not request.external_access_requested:
            raise ValueError("provider integration requires explicit external request")
        if request.owner.casefold() != execution.request.owner.casefold():
            raise ValueError("provider integration owner must match governed execution")
        if execution.status not in {
            LocalProviderExecutionStatus.COMPLETED,
            LocalProviderExecutionStatus.REJECTED,
            LocalProviderExecutionStatus.FAILED,
        }:
            raise ValueError("provider integration requires attempted execution")
        if not execution.provider_call_performed or execution.response is None:
            raise ValueError("provider integration requires provider response evidence")

        route = execution.request.route
        selected = route.selected_provider
        if selected is None or route.route_kind is None:
            raise ValueError("provider integration requires governed selected provider")
        provider_id = selected.provider_name.strip().casefold()
        if execution.selected_provider_name.casefold() != provider_id:
            raise ValueError("provider integration execution must match governed route")
        if request.target_id and request.target_id != provider_id:
            raise ValueError("provider integration target must match governed route")

        scope = (
            ExternalExecutionScope.LOCAL
            if route.route_kind is ProviderKind.LOCAL
            else ExternalExecutionScope.REMOTE
        )
        provenance = ExternalIntelligenceProvenance(
            actor_id=provider_id,
            capability=ExternalIntelligenceCapability.INFERENCE_PROVIDER,
            execution_scope=scope,
            network_used=network_used,
            observed_at=execution.created_at,
            trace_ids=(route.route_id, execution.execution_id),
        )
        return self._boundary.admit_inference(
            request,
            execution.response,
            provenance,
        )
