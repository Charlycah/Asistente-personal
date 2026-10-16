from __future__ import annotations

from core.llm_provider import LLMResponse

from .models import (
    ExternalInferenceEvidence,
    ExternalInformationEvidence,
    ExternalIntelligenceCapability,
    ExternalIntelligenceEnvelope,
    ExternalIntelligenceProvenance,
    ExternalIntelligenceRequest,
    ExternalIntelligenceStatus,
)


class GovernedExternalIntelligenceBoundary:
    """Admission boundary for external evidence; never selects or executes it."""

    BOUNDARY_ID = "external_intelligence_boundary"

    @property
    def boundary_id(self) -> str:
        return self.BOUNDARY_ID

    def admit_inference(
        self,
        request: ExternalIntelligenceRequest,
        response: LLMResponse,
        provenance: ExternalIntelligenceProvenance,
    ) -> ExternalIntelligenceEnvelope:
        if request.capability is not ExternalIntelligenceCapability.INFERENCE_PROVIDER:
            raise ValueError("external inference admission requires inference request")
        if not request.external_access_requested:
            raise ValueError("external inference admission requires explicit request")
        if (
            request.target_id
            and request.target_id != response.provider.strip().casefold()
        ):
            raise ValueError("external inference result must match requested target")
        evidence = ExternalInferenceEvidence(
            text=response.text,
            provider=response.provider,
            model=response.model,
            accepted_by_provider=response.accepted,
            provider_error=response.error,
        )
        status = (
            ExternalIntelligenceStatus.ACCEPTED
            if response.accepted and not response.error
            else ExternalIntelligenceStatus.REJECTED
        )
        return ExternalIntelligenceEnvelope(
            request=request,
            provenance=provenance,
            status=status,
            inference=evidence,
            rationale=(
                "external_inference_is_subordinate_evidence",
                "provider_does_not_gain_cognitive_authority",
                "routing_and_execution_remain_external_to_boundary",
                "roby_retains_interpretation_and_decision",
            ),
        )

    def admit_information(
        self,
        request: ExternalIntelligenceRequest,
        *,
        source_id: str,
        items: tuple[dict[str, object], ...],
        provenance: ExternalIntelligenceProvenance,
        source_status: str = "succeeded",
        source_error: str | None = None,
    ) -> ExternalIntelligenceEnvelope:
        if request.capability is not ExternalIntelligenceCapability.INFORMATION_SOURCE:
            raise ValueError("external information admission requires source request")
        if not request.external_access_requested:
            raise ValueError("external information admission requires explicit request")
        normalized_source = source_id.strip().casefold()
        if request.target_id and request.target_id != normalized_source:
            raise ValueError("external information result must match requested target")
        evidence = ExternalInformationEvidence(
            source_id=source_id,
            items=items,
            source_status=source_status,
            source_error=source_error,
        )
        status = (
            ExternalIntelligenceStatus.REJECTED
            if source_error
            else ExternalIntelligenceStatus.ACCEPTED
        )
        return ExternalIntelligenceEnvelope(
            request=request,
            provenance=provenance,
            status=status,
            information=evidence,
            rationale=(
                "external_information_is_subordinate_evidence",
                "source_does_not_gain_cognitive_authority",
                "source_query_execution_remains_external_to_boundary",
                "roby_retains_interpretation_and_decision",
            ),
        )
