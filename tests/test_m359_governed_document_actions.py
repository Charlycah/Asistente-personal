from core.document_actions import (
    DocumentActionRequest,
    DocumentActionType,
    GovernedDocumentActionService,
)
from core.document_extraction import ExtractedField, StructuredDocument
from core.document_intelligence import DocumentIntelligence
from core.tool_gateway import ToolCapability, ToolGatewayManager


def _document() -> StructuredDocument:
    return StructuredDocument(
        document_type="invoice",
        fields=(
            ExtractedField("due_date", "15/08/2026", 0.9, "Vence 15/08/2026"),
        ),
        extractor_name="test",
    )


def _intelligence() -> DocumentIntelligence:
    return DocumentIntelligence(
        document_type="invoice",
        summary="Factura con vencimiento identificado.",
        completeness=0.8,
        consistency=1.0,
        missing_fields=(),
        issues=(),
        intelligence_name="test",
    )


def test_m359_requires_explicit_consent() -> None:
    service = GovernedDocumentActionService(ToolGatewayManager())
    request = DocumentActionRequest(
        _document(), _intelligence(), DocumentActionType.SAVE_SUMMARY
    )
    try:
        service.prepare(request)
    except PermissionError:
        pass
    else:
        raise AssertionError("consent must be required")


def test_m359_prepares_without_executing_before_confirmation() -> None:
    gateway = ToolGatewayManager()
    service = GovernedDocumentActionService(gateway)
    request = DocumentActionRequest(
        _document(),
        _intelligence(),
        DocumentActionType.CREATE_REMINDER,
        explicit_user_consent=True,
    )
    result = service.execute(request)
    assert result.status == "prepared"
    assert not gateway.audit_log


def test_m359_routes_confirmed_action_through_gateway() -> None:
    gateway = ToolGatewayManager()
    gateway.register_capability(
        ToolCapability(
            "document.action.save_summary",
            "Save an explicitly confirmed document summary",
            risk_level="medium",
            requires_confirmation=True,
            metadata={"permission_scope": "storage"},
        ),
        handler=lambda payload: {"saved": True, "summary": payload["summary"]},
    )
    service = GovernedDocumentActionService(gateway)
    request = DocumentActionRequest(
        _document(),
        _intelligence(),
        DocumentActionType.SAVE_SUMMARY,
        explicit_user_consent=True,
        user_confirmed=True,
    )
    result = service.execute(request)
    assert result.status == "executed"
    assert result.output["saved"] is True
    assert gateway.last_result is not None


def test_m359_open_source_requires_explicit_url() -> None:
    service = GovernedDocumentActionService(ToolGatewayManager())
    request = DocumentActionRequest(
        _document(),
        _intelligence(),
        DocumentActionType.OPEN_SOURCE,
        explicit_user_consent=True,
    )
    try:
        service.prepare(request)
    except ValueError as exc:
        assert "URL" in str(exc)
    else:
        raise AssertionError("source URL must be required")
