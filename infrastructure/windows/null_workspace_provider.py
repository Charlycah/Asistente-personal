from __future__ import annotations

from core.windows_workspace import (
    WorkspaceProcess,
    WorkspaceScreenshot,
    WorkspaceWindow,
)


class NullWindowsWorkspaceProvider:
    """Safe provider used when Windows inspection is not configured."""

    def active_window(self) -> WorkspaceWindow | None:
        return None

    def list_windows(self) -> tuple[WorkspaceWindow, ...]:
        return ()

    def list_processes(self) -> tuple[WorkspaceProcess, ...]:
        return ()

    def screenshot(self) -> WorkspaceScreenshot:
        raise RuntimeError("Windows screenshot provider is not configured")
