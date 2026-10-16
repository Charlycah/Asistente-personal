import pytest

from core.document_extraction import ExtractedField, StructuredDocument
from core.tool_gateway import ToolGatewayManager
from core.web_enrichment import (
    EnrichmentFinding,
    EnrichmentSource,
    GovernedWebEnrichmentService,
    WebEnrichmentRequest,
    WebEnrichmentResult,
)
from infrastructure.web_enrichment import WebEnrichmentAdapter


class FakeProvider:
    def __init__(self) -> None:
        self.received = None

    def enrich(self, fields):
        self.received = dict(fields)
        return WebEnrichmentResult(
            query_fields=fields,
            findings=(
                EnrichmentFinding("issuer_status", "public record found", 0.91, (0,)),
            ),
            sources=(
                EnrichmentSource(
                    "Official issuer record",
                    "fake-public-registry",
                    "https://example.test/issuer",
                ),
            ),
            provider_name="fake-provider",
            warnings=("informational_only",),
        )


def document():
    return StructuredDocument(
        "invoice",
        (
            ExtractedField("issuer", "Empresa Electrica SA", 0.9, "Empresa"),
            ExtractedField("tax_id", "30-12345678-9", 0.9, "CUIT"),
            ExtractedField("total_amount", "$ 42.850", 0.9, "Total"),
        ),
        "extractor",
    )


def build():
    provider = FakeProvider()
    gateway = ToolGatewayManager()
    WebEnrichmentAdapter(provider).register_with_gateway(gateway)
    return GovernedWebEnrichmentService(gateway), provider, gateway


def test_web_enrichment_routes_only_allowed_fields():
    service, provider, gateway = build()
    result = service.enrich(
        WebEnrichmentRequest(
            document(),
            explicit_user_consent=True,
            allowed_fields=("issuer", "tax_id"),
        )
    )
    assert provider.received == {
        "issuer": "Empresa Electrica SA",
        "tax_id": "30-12345678-9",
    }
    assert "total_amount" not in result.query_fields
    assert result.findings[0].source_indexes == (0,)
    assert gateway.last_result.succeeded


@pytest.mark.parametrize("field", ["explicit_user_consent", "user_requested"])
def test_web_enrichment_requires_explicit_authorization(field):
    service, provider, _ = build()
    values = {"explicit_user_consent": True, "user_requested": True}
    values[field] = False
    with pytest.raises(PermissionError):
        service.enrich(WebEnrichmentRequest(document(), **values))
    assert provider.received is None


def test_web_enrichment_rejects_empty_allowed_payload():
    service, _, _ = build()
    with pytest.raises(ValueError, match="allowed document field"):
        service.enrich(
            WebEnrichmentRequest(
                document(),
                explicit_user_consent=True,
                allowed_fields=("missing",),
            )
        )


def test_web_enrichment_is_passive_and_auditable():
    service, _, gateway = build()
    result = service.enrich(
        WebEnrichmentRequest(document(), explicit_user_consent=True)
    )
    assert result.provider_name == "fake-provider"
    assert result.warnings == ("informational_only",)
    assert gateway.audit_log
    assert "execute" not in str(result).lower()
    assert "payment" not in str(result).lower()


def test_result_rejects_unknown_source_reference():
    with pytest.raises(ValueError, match="unknown source"):
        WebEnrichmentResult(
            {},
            (EnrichmentFinding("key", "value", 0.8, (1,)),),
            (EnrichmentSource("title", "provider"),),
            "provider",
        )
