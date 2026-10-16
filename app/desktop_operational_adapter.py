from __future__ import annotations

from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)
from app.ui_adapter import UIResponse
from core.desktop_runtime_integration import (
    DesktopRuntimeIntegration,
    DesktopRuntimeRequest,
    DesktopRuntimeStatus,
)
from core.runtime_readiness_gate import RuntimeReadinessResult
from domain.response import ResponseStatus


class DesktopOperationalAdapter:
    """Maps M176 desktop integration results to the stable UI contract."""

    def __init__(
        self,
        *,
        integration: DesktopRuntimeIntegration,
        owner: str,
        readiness_result: RuntimeReadinessResult,
        default_session_id: str = "desktop",
    ) -> None:
        self.integration = integration
        self.owner = owner.strip()
        self.readiness_result = readiness_result
        self.default_session_id = default_session_id.strip()
        if not self.owner or not self.default_session_id:
            raise ValueError("desktop adapter identity must not be blank")

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        resolved_session = (session_id or self.default_session_id).strip()
        result = self.integration.submit(
            DesktopRuntimeRequest(
                owner=self.owner,
                session_id=resolved_session,
                text=text,
                readiness_result=self.readiness_result,
            )
        )
        status = self._ui_status(result.status)
        return UIResponse(
            text=DEFAULT_HOUSEHOLD_CONVERSATION_STYLE.render(result.response_text),
            status=status.value,
            session_id=resolved_session,
            needs_input=result.status is DesktopRuntimeStatus.NEEDS_INPUT,
        )

    @staticmethod
    def _ui_status(status: DesktopRuntimeStatus) -> ResponseStatus:
        if status is DesktopRuntimeStatus.DELIVERED:
            return ResponseStatus.SUCCESS
        if status is DesktopRuntimeStatus.NEEDS_INPUT:
            return ResponseStatus.NEEDS_INFORMATION
        return ResponseStatus.FAILURE
