from __future__ import annotations

from app.vision_gateway import GovernedVisionGateway
from core.governed_image_repository import ImageStoreRequest, StoredImage
from core.windows_workspace import (
    CAPABILITY_RISKS,
    WindowsWorkspaceProvider,
    WorkspaceActionPlan,
    WorkspaceActionRequest,
    WorkspaceCapability,
    WorkspaceProcess,
    WorkspaceRisk,
    WorkspaceWindow,
)


class OfficialWindowsWorkspaceGateway:
    """Single governed application boundary for the Windows workspace."""

    def __init__(self, *, provider: WindowsWorkspaceProvider) -> None:
        self.provider = provider

    @staticmethod
    def capabilities() -> tuple[WorkspaceCapability, ...]:
        return tuple(WorkspaceCapability)

    def active_window(self) -> WorkspaceWindow | None:
        return self.provider.active_window()

    def list_windows(self) -> tuple[WorkspaceWindow, ...]:
        return self.provider.list_windows()

    def list_processes(self) -> tuple[WorkspaceProcess, ...]:
        return self.provider.list_processes()

    def prepare_action(self, request: WorkspaceActionRequest) -> WorkspaceActionPlan:
        risk = CAPABILITY_RISKS[request.capability]
        authorized = request.user_requested
        rationale = ["explicit_user_request_required"]
        if risk is WorkspaceRisk.SENSITIVE:
            authorized = (
                authorized
                and request.explicit_user_consent
                and request.confirmation
            )
            rationale.extend(("explicit_consent_required", "confirmation_required"))
        executable = False
        rationale.append("m363_foundation_does_not_execute_platform_mutations")
        return WorkspaceActionPlan(
            request=request,
            risk=risk,
            authorized=authorized,
            executable=executable,
            rationale=tuple(rationale),
        )

    def store_screenshot(
        self,
        *,
        vision_gateway: GovernedVisionGateway,
        request: ImageStoreRequest,
    ) -> StoredImage:
        screenshot = self.provider.screenshot()
        return vision_gateway.store_image(
            request,
            image_bytes=screenshot.image_bytes,
            mime_type=screenshot.mime_type,
        )
