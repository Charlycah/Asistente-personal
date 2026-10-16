from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class LifecycleExitReason(StrEnum):
    WINDOW_CLOSE = "window_close"
    MENU_EXIT = "menu_exit"
    VOICE_SHUTDOWN = "voice_shutdown"
    CONSOLE_EXIT = "console_exit"
    RESTART = "restart"
    SIGNAL = "signal"
    FATAL_ERROR = "fatal_error"


class LifecycleEventKind(StrEnum):
    APPLICATION_STARTED = "application_started"
    APPLICATION_STOPPED = "application_stopped"
    APPLICATION_RESTART_REQUESTED = "application_restart_requested"
    UNEXPECTED_TERMINATION = "unexpected_termination"
    RECOVERY_COMPLETED = "recovery_completed"
    SHUTDOWN_STEP_FAILED = "shutdown_step_failed"
    SHUTDOWN_STEP_TIMED_OUT = "shutdown_step_timed_out"


@dataclass(frozen=True)
class LifecycleEvent:
    kind: LifecycleEventKind
    occurred_at: datetime
    reason: LifecycleExitReason | None = None
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "occurred_at": self.occurred_at.isoformat(),
            "reason": self.reason.value if self.reason is not None else None,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class ApplicationSession:
    session_id: str
    started_at: datetime
    stopped_at: datetime | None = None
    clean_shutdown: bool = False
    exit_reason: LifecycleExitReason | None = None
    version: str = "ROBY XI.2"

    @property
    def duration_seconds(self) -> float | None:
        if self.stopped_at is None:
            return None
        return max(0.0, (self.stopped_at - self.started_at).total_seconds())

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "stopped_at": (
                self.stopped_at.isoformat() if self.stopped_at is not None else None
            ),
            "clean_shutdown": self.clean_shutdown,
            "exit_reason": (
                self.exit_reason.value if self.exit_reason is not None else None
            ),
            "version": self.version,
            "duration_seconds": self.duration_seconds,
        }


@dataclass(frozen=True)
class LifecycleSnapshot:
    current_session: ApplicationSession | None
    previous_session: ApplicationSession | None
    unexpected_previous_shutdown: bool
    restart_requested: bool
    events: tuple[LifecycleEvent, ...] = field(default_factory=tuple)
