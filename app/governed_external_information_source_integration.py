from __future__ import annotations

from app.governed_source_query import (
    GovernedSourceQueryResult,
    GovernedSourceQueryStatus,
)
from core.governed_external_intelligence.boundary import (
    GovernedExternalIntelligenceBoundary,
)
from core.governed_external_intelligence.models import (
    ExternalExecutionScope,
    ExternalIntelligenceCapability,
    ExternalIntelligenceEnvelope,
    ExternalIntelligenceProvenance,
    ExternalIntelligenceRequest,
)


class GovernedExternalInformationSourceIntegration:
    """Admits results from the existing governed information-source path."""

    INTEGRATION_ID = "external_intelligence_information_source_integration"

    def __init__(
        self,
        boundary: GovernedExternalIntelligenceBoundary | None = None,
    ) -> None:
        self._boundary = boundary or GovernedExternalIntelligenceBoundary()

    @property
    def integration_id(self) -> str:
        return self.INTEGRATION_ID

    def admit_query_result(
        self,
        request: ExternalIntelligenceRequest,
        result: GovernedSourceQueryResult,
        *,
        execution_scope: ExternalExecutionScope = ExternalExecutionScope.REMOTE,
        network_used: bool,
    ) -> ExternalIntelligenceEnvelope:
        return self._admit(
            request,
            result,
            execution_scope=execution_scope,
            network_used=network_used,
            trace_ids=(),
        )

    def admit_traced_query_result(
        self,
        request: ExternalIntelligenceRequest,
        result: GovernedSourceQueryResult,
        *,
        execution_scope: ExternalExecutionScope = ExternalExecutionScope.REMOTE,
        network_used: bool,
    ) -> ExternalIntelligenceEnvelope:
        if not result.execution_id:
            raise ValueError("source integration requires source execution trace")
        return self._admit(
            request,
            result,
            execution_scope=execution_scope,
            network_used=network_used,
            trace_ids=(result.execution_id,),
        )

    def _admit(
        self,
        request: ExternalIntelligenceRequest,
        result: GovernedSourceQueryResult,
        *,
        execution_scope: ExternalExecutionScope,
        network_used: bool,
        trace_ids: tuple[str, ...],
    ) -> ExternalIntelligenceEnvelope:
        if request.capability is not ExternalIntelligenceCapability.INFORMATION_SOURCE:
            raise ValueError(
                "source integration requires information source capability"
            )
        if not request.external_access_requested:
            raise ValueError("source integration requires explicit external request")
        source_id = result.source.source_id.strip().casefold()
        if result.query.source_id != source_id:
            raise ValueError("source integration query must match governed source")
        if request.target_id and request.target_id != source_id:
            raise ValueError("source integration target must match governed source")
        if result.response is None:
            raise ValueError("source integration requires executed query result")
        if result.response.source_id != source_id:
            raise ValueError("source integration response must match governed source")
        if result.status not in {
            GovernedSourceQueryStatus.SUCCEEDED,
            GovernedSourceQueryStatus.EMPTY,
            GovernedSourceQueryStatus.FAILED,
        }:
            raise ValueError("source integration requires terminal query result")

        response = result.response
        source_error = str(response.error.kind) if response.error is not None else None
        observed_at = response.received_at
        if observed_at is None:
            raise ValueError("source integration requires response timestamp")
        provenance = ExternalIntelligenceProvenance(
            actor_id=source_id,
            capability=ExternalIntelligenceCapability.INFORMATION_SOURCE,
            execution_scope=execution_scope,
            network_used=network_used,
            observed_at=observed_at,
            trace_ids=trace_ids,
        )
        items = tuple(dict(item) for item in response.raw_items)
        return self._boundary.admit_information(
            request,
            source_id=source_id,
            items=items,
            provenance=provenance,
            source_status=result.status.value,
            source_error=source_error,
        )
