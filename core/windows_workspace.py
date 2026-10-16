from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable


class WorkspaceCapability(str, Enum):
    ACTIVE_WINDOW = "active_window"
    LIST_WINDOWS = "list_windows"
    LIST_PROCESSES = "list_processes"
    SCREENSHOT = "screenshot"
    OPEN_APPLICATION = "open_application"
    OPEN_PATH = "open_path"
    CLOSE_APPLICATION = "close_application"
    TERMINATE_PROCESS = "terminate_process"
    MOVE_PATH = "move_path"
    DELETE_PATH = "delete_path"
    INPUT_AUTOMATION = "input_automation"


class WorkspaceRisk(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE = "reversible"
    SENSITIVE = "sensitive"


CAPABILITY_RISKS: dict[WorkspaceCapability, WorkspaceRisk] = {
    WorkspaceCapability.ACTIVE_WINDOW: WorkspaceRisk.READ_ONLY,
    WorkspaceCapability.LIST_WINDOWS: WorkspaceRisk.READ_ONLY,
    WorkspaceCapability.LIST_PROCESSES: WorkspaceRisk.READ_ONLY,
    WorkspaceCapability.SCREENSHOT: WorkspaceRisk.READ_ONLY,
    WorkspaceCapability.OPEN_APPLICATION: WorkspaceRisk.REVERSIBLE,
    WorkspaceCapability.OPEN_PATH: WorkspaceRisk.REVERSIBLE,
    WorkspaceCapability.CLOSE_APPLICATION: WorkspaceRisk.SENSITIVE,
    WorkspaceCapability.TERMINATE_PROCESS: WorkspaceRisk.SENSITIVE,
    WorkspaceCapability.MOVE_PATH: WorkspaceRisk.SENSITIVE,
    WorkspaceCapability.DELETE_PATH: WorkspaceRisk.SENSITIVE,
    WorkspaceCapability.INPUT_AUTOMATION: WorkspaceRisk.SENSITIVE,
}


@dataclass(frozen=True)
class WorkspaceWindow:
    window_id: str
    title: str
    process_id: int | None = None
    application: str = ""

    def __post_init__(self) -> None:
        if not self.window_id.strip():
            raise ValueError("window id must not be blank")
        object.__setattr__(self, "window_id", self.window_id.strip())
        object.__setattr__(self, "title", self.title.strip())
        object.__setattr__(self, "application", self.application.strip())


@dataclass(frozen=True)
class WorkspaceProcess:
    process_id: int
    name: str
    executable: str = ""

    def __post_init__(self) -> None:
        if self.process_id < 0:
            raise ValueError("process id must not be negative")
        if not self.name.strip():
            raise ValueError("process name must not be blank")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "executable", self.executable.strip())


@dataclass(frozen=True)
class WorkspaceScreenshot:
    image_bytes: bytes
    mime_type: str = "image/png"

    def __post_init__(self) -> None:
        if not self.image_bytes:
            raise ValueError("screenshot must not be empty")
        if self.mime_type not in {"image/png", "image/jpeg"}:
            raise ValueError("unsupported screenshot media type")


@dataclass(frozen=True)
class WorkspaceActionRequest:
    capability: WorkspaceCapability
    target: str
    user_requested: bool
    explicit_user_consent: bool = False
    confirmation: bool = False

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise ValueError("workspace action target must not be blank")
        object.__setattr__(self, "target", self.target.strip())


@dataclass(frozen=True)
class WorkspaceActionPlan:
    request: WorkspaceActionRequest
    risk: WorkspaceRisk
    authorized: bool
    executable: bool
    rationale: tuple[str, ...]


@runtime_checkable
class WindowsWorkspaceProvider(Protocol):
    def active_window(self) -> WorkspaceWindow | None: ...
    def list_windows(self) -> tuple[WorkspaceWindow, ...]: ...
    def list_processes(self) -> tuple[WorkspaceProcess, ...]: ...
    def screenshot(self) -> WorkspaceScreenshot: ...
