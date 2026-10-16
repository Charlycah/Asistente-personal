from __future__ import annotations

from pathlib import Path

import pytest

from app.vision_gateway import GovernedVisionGateway
from app.windows_workspace_gateway import OfficialWindowsWorkspaceGateway
from core.governed_image_repository import ImageCategory, ImageStoreRequest
from core.windows_workspace import (
    WorkspaceActionRequest,
    WorkspaceCapability,
    WorkspaceProcess,
    WorkspaceRisk,
    WorkspaceScreenshot,
    WorkspaceWindow,
)
from infrastructure.vision.file_image_repository import FileImageRepository


class FakeWorkspaceProvider:
    def active_window(self) -> WorkspaceWindow:
        return WorkspaceWindow("window-1", "ROBY", 42, "python")

    def list_windows(self) -> tuple[WorkspaceWindow, ...]:
        return (self.active_window(),)

    def list_processes(self) -> tuple[WorkspaceProcess, ...]:
        return (WorkspaceProcess(42, "python", "python.exe"),)

    def screenshot(self) -> WorkspaceScreenshot:
        return WorkspaceScreenshot(b"desktop-pixels")


class UnusedVisionCore:
    pass


def _gateway() -> OfficialWindowsWorkspaceGateway:
    return OfficialWindowsWorkspaceGateway(provider=FakeWorkspaceProvider())


def test_gateway_exposes_read_only_workspace_observations() -> None:
    gateway = _gateway()
    assert gateway.active_window() == WorkspaceWindow("window-1", "ROBY", 42, "python")
    assert gateway.list_windows()[0].title == "ROBY"
    assert gateway.list_processes()[0].name == "python"


def test_capability_registry_is_descriptive_and_complete() -> None:
    capabilities = _gateway().capabilities()
    assert set(capabilities) == set(WorkspaceCapability)
    assert WorkspaceCapability.INPUT_AUTOMATION in capabilities


def test_reversible_action_is_only_prepared() -> None:
    plan = _gateway().prepare_action(
        WorkspaceActionRequest(
            capability=WorkspaceCapability.OPEN_APPLICATION,
            target="notepad.exe",
            user_requested=True,
        )
    )
    assert plan.risk is WorkspaceRisk.REVERSIBLE
    assert plan.authorized is True
    assert plan.executable is False


def test_sensitive_action_requires_consent_and_confirmation() -> None:
    request = WorkspaceActionRequest(
        capability=WorkspaceCapability.TERMINATE_PROCESS,
        target="42",
        user_requested=True,
        explicit_user_consent=True,
        confirmation=False,
    )
    assert _gateway().prepare_action(request).authorized is False
    confirmed = WorkspaceActionRequest(
        capability=request.capability,
        target=request.target,
        user_requested=True,
        explicit_user_consent=True,
        confirmation=True,
    )
    assert _gateway().prepare_action(confirmed).authorized is True


def test_workspace_screenshot_can_enter_governed_vision_retention(
    tmp_path: Path,
) -> None:
    repository = FileImageRepository(tmp_path / "images")
    vision = GovernedVisionGateway(
        vision_core=UnusedVisionCore(),  # type: ignore[arg-type]
        image_repository=repository,
    )
    stored = _gateway().store_screenshot(
        vision_gateway=vision,
        request=ImageStoreRequest(
            owner="Carlos",
            label="escritorio",
            category=ImageCategory.GENERAL,
            tags=("windows", "screenshot"),
            explicit_user_consent=True,
            user_requested=True,
        ),
    )
    assert stored.mime_type == "image/png"
    asset = next(repository.assets.glob(f"{stored.image_id}.*"))
    assert asset.read_bytes() == b"desktop-pixels"


def test_workspace_screenshot_retention_preserves_vision_consent(
    tmp_path: Path,
) -> None:
    vision = GovernedVisionGateway(
        vision_core=UnusedVisionCore(),  # type: ignore[arg-type]
        image_repository=FileImageRepository(tmp_path / "images"),
    )
    with pytest.raises(PermissionError, match="explicit user consent"):
        _gateway().store_screenshot(
            vision_gateway=vision,
            request=ImageStoreRequest(
                owner="Carlos",
                label="escritorio",
                category=ImageCategory.GENERAL,
                explicit_user_consent=False,
                user_requested=True,
            ),
        )


def test_m363_documentation_declares_gateway_and_non_execution() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M363_WINDOWS_WORKSPACE_FOUNDATION.md").read_text(
        encoding="utf-8"
    )
    assert "OfficialWindowsWorkspaceGateway" in document
    assert "executable=False" in document
    assert "ToolGateway" in document


def test_root_documents_preserve_m363_milestone() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "Base canónica actual:** M" in readme
    assert "## M363 — Windows Workspace Foundation" in changelog
