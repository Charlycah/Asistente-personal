from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from core.tool_gateway import ToolCapability, ToolGatewayManager
from core.web_enrichment import WebEnrichmentProvider


@dataclass
class WebEnrichmentAdapter:
    provider: WebEnrichmentProvider

    CAPABILITY = "web.enrichment.lookup"

    def register_with_gateway(self, gateway: ToolGatewayManager) -> None:
        gateway.register_capability(
            ToolCapability(
                name=self.CAPABILITY,
                description="Passive web enrichment for user-approved document fields",
                risk_level="medium",
                requires_confirmation=True,
                metadata={"permission_scope": "network"},
            ),
            handler=self.lookup,
        )

    def lookup(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        raw_fields = payload.get("fields", {})
        if not isinstance(raw_fields, Mapping):
            raise ValueError("web enrichment fields must be a mapping")
        fields = {str(key): str(value) for key, value in raw_fields.items()}
        result = self.provider.enrich(fields)
        return {
            "provider_name": result.provider_name,
            "findings": [
                {
                    "key": item.key,
                    "value": item.value,
                    "confidence": item.confidence,
                    "source_indexes": list(item.source_indexes),
                }
                for item in result.findings
            ],
            "sources": [
                {
                    "title": item.title,
                    "provider": item.provider,
                    "url": item.url,
                }
                for item in result.sources
            ],
            "warnings": list(result.warnings),
        }
