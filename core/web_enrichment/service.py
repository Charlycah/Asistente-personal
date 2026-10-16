from __future__ import annotations

from dataclasses import dataclass

from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus, ToolRequest

from .models import (
    EnrichmentFinding,
    EnrichmentSource,
    WebEnrichmentRequest,
    WebEnrichmentResult,
)


@dataclass
class GovernedWebEnrichmentService:
    gateway: ToolGatewayManager
    capability_name: str = "web.enrichment.lookup"

    def enrich(self, request: WebEnrichmentRequest) -> WebEnrichmentResult:
        if not request.explicit_user_consent:
            raise PermissionError("explicit web enrichment consent is required")
        if not request.user_requested:
            raise PermissionError("web enrichment must be explicitly requested")
        available = {field.name: field.value for field in request.document.fields}
        selected = request.allowed_fields or tuple(sorted(available))
        payload_fields = {
            name: available[name] for name in selected if name in available
        }
        if not payload_fields:
            raise ValueError(
                "web enrichment requires at least one allowed document field"
            )
        result = self.gateway.execute(
            ToolRequest(
                self.capability_name,
                payload={
                    "document_type": request.document.document_type,
                    "fields": payload_fields,
                },
                reason="document_web_enrichment_requested",
                source="governed_web_enrichment",
            )
        )
        if result.normalized_status is not ToolGatewayStatus.ROUTED:
            raise RuntimeError(result.error or "web enrichment was not routed")
        output = result.output
        sources = tuple(
            EnrichmentSource(
                title=str(item["title"]),
                provider=str(item["provider"]),
                url=str(item["url"]) if item.get("url") else None,
            )
            for item in output.get("sources", ())
        )
        findings = tuple(
            EnrichmentFinding(
                key=str(item["key"]),
                value=str(item["value"]),
                confidence=float(item["confidence"]),
                source_indexes=tuple(int(i) for i in item.get("source_indexes", ())),
            )
            for item in output.get("findings", ())
        )
        return WebEnrichmentResult(
            query_fields=payload_fields,
            findings=findings,
            sources=sources,
            provider_name=str(output.get("provider_name", "gateway-provider")),
            warnings=tuple(str(item) for item in output.get("warnings", ())),
        )
