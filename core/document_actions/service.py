from __future__ import annotations

from dataclasses import dataclass

from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus, ToolRequest

from .models import (
    DocumentActionProposal,
    DocumentActionRequest,
    DocumentActionResult,
    DocumentActionType,
)

_CAPABILITIES = {
    DocumentActionType.CREATE_REMINDER: "document.action.create_reminder",
    DocumentActionType.SAVE_SUMMARY: "document.action.save_summary",
    DocumentActionType.OPEN_SOURCE: "document.action.open_source",
}


@dataclass
class GovernedDocumentActionService:
    gateway: ToolGatewayManager

    def prepare(self, request: DocumentActionRequest) -> DocumentActionProposal:
        if not request.explicit_user_consent:
            raise PermissionError("explicit document action consent is required")
        payload = self._payload_for(request)
        return DocumentActionProposal(
            action_type=request.action_type,
            title=self._title_for(request.action_type),
            payload=payload,
        )

    def execute(self, request: DocumentActionRequest) -> DocumentActionResult:
        proposal = self.prepare(request)
        if not request.user_confirmed:
            return DocumentActionResult(
                action_type=request.action_type,
                status="prepared",
                capability_name=_CAPABILITIES[request.action_type],
                output={"title": proposal.title, "payload": proposal.payload},
            )
        capability_name = _CAPABILITIES[request.action_type]
        result = self.gateway.execute(
            ToolRequest(
                capability_name,
                payload=proposal.payload,
                reason="confirmed_document_action",
                source="governed_document_actions",
            )
        )
        if result.normalized_status is not ToolGatewayStatus.ROUTED:
            raise RuntimeError(result.error or "document action was not routed")
        return DocumentActionResult(
            action_type=request.action_type,
            status="executed",
            capability_name=capability_name,
            output=dict(result.output),
        )

    def _payload_for(self, request: DocumentActionRequest) -> dict[str, str]:
        fields = {field.name: field.value for field in request.document.fields}
        if request.action_type is DocumentActionType.CREATE_REMINDER:
            due_date = fields.get("due_date")
            if not due_date:
                raise ValueError("document reminder requires a due date")
            return {
                "title": f"Revisar {request.document.document_type}",
                "due_date": due_date,
                "summary": request.intelligence.summary,
            }
        if request.action_type is DocumentActionType.SAVE_SUMMARY:
            return {
                "document_type": request.document.document_type,
                "summary": request.intelligence.summary,
            }
        if not request.source_url or not request.source_url.strip():
            raise ValueError("opening a source requires an explicit URL")
        return {"url": request.source_url.strip()}

    @staticmethod
    def _title_for(action_type: DocumentActionType) -> str:
        return {
            DocumentActionType.CREATE_REMINDER: "Crear recordatorio documental",
            DocumentActionType.SAVE_SUMMARY: "Guardar resumen documental",
            DocumentActionType.OPEN_SOURCE: "Abrir fuente documental",
        }[action_type]
