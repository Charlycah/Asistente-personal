from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread
from typing import Any

from .models import (
    ApplicationSession,
    LifecycleEvent,
    LifecycleEventKind,
    LifecycleExitReason,
    LifecycleSnapshot,
)

ShutdownStep = tuple[str, Callable[[], object]]


class ApplicationLifecycleManager:
    """Owns ROBY's application session, shutdown and restart boundary."""

    def __init__(
        self,
        *,
        state_path: Path = Path(".roby/runtime/application_lifecycle.json"),
        shutdown_timeout_seconds: float = 5.0,
        version: str = "ROBY XI.2",
    ) -> None:
        if shutdown_timeout_seconds <= 0:
            raise ValueError("shutdown_timeout_seconds debe ser mayor que cero")
        self.state_path = state_path
        self.shutdown_timeout_seconds = shutdown_timeout_seconds
        self.version = version
        self._current_session: ApplicationSession | None = None
        self._previous_session: ApplicationSession | None = None
        self._unexpected_previous_shutdown = False
        self._restart_requested = False
        self._events: list[LifecycleEvent] = []
        self._closed = False

    @property
    def restart_requested(self) -> bool:
        return self._restart_requested

    @property
    def unexpected_previous_shutdown(self) -> bool:
        return self._unexpected_previous_shutdown

    def start(self, *, now: datetime | None = None) -> LifecycleSnapshot:
        if self._current_session is not None and not self._closed:
            return self.snapshot()
        moment = _utc(now)
        persisted = self._read_state()
        self._previous_session = _session_from_dict(persisted.get("current_session"))
        self._unexpected_previous_shutdown = bool(
            self._previous_session is not None
            and not self._previous_session.clean_shutdown
        )
        if self._unexpected_previous_shutdown:
            self._record(
                LifecycleEventKind.UNEXPECTED_TERMINATION,
                moment,
                detail="La sesión anterior no registró un cierre limpio.",
            )
            self._record(
                LifecycleEventKind.RECOVERY_COMPLETED,
                moment,
                detail="El estado de ciclo de vida fue recuperado.",
            )
        session_id = hashlib.sha256(
            f"{moment.isoformat()}|{self.version}".encode("utf-8")
        ).hexdigest()
        self._current_session = ApplicationSession(
            session_id=session_id,
            started_at=moment,
            version=self.version,
        )
        self._closed = False
        self._restart_requested = False
        self._record(LifecycleEventKind.APPLICATION_STARTED, moment)
        self._persist()
        return self.snapshot()

    def shutdown(
        self,
        *,
        reason: LifecycleExitReason,
        steps: Iterable[ShutdownStep] = (),
        now: datetime | None = None,
    ) -> LifecycleSnapshot:
        if self._closed:
            return self.snapshot()
        moment = _utc(now)
        for name, callback in steps:
            self._run_step(name, callback, moment)
        if self._current_session is None:
            self.start(now=moment)
        assert self._current_session is not None
        self._current_session = replace(
            self._current_session,
            stopped_at=moment,
            clean_shutdown=True,
            exit_reason=reason,
        )
        self._restart_requested = reason is LifecycleExitReason.RESTART
        event_kind = (
            LifecycleEventKind.APPLICATION_RESTART_REQUESTED
            if self._restart_requested
            else LifecycleEventKind.APPLICATION_STOPPED
        )
        self._record(event_kind, moment, reason=reason)
        self._closed = True
        self._persist()
        return self.snapshot()

    def snapshot(self) -> LifecycleSnapshot:
        return LifecycleSnapshot(
            current_session=self._current_session,
            previous_session=self._previous_session,
            unexpected_previous_shutdown=self._unexpected_previous_shutdown,
            restart_requested=self._restart_requested,
            events=tuple(self._events),
        )

    def recovery_message(self) -> str:
        if not self._unexpected_previous_shutdown:
            return ""
        return (
            "La última sesión no terminó correctamente. "
            "Revisé el estado y recuperé la información disponible."
        )

    def _run_step(
        self,
        name: str,
        callback: Callable[[], object],
        moment: datetime,
    ) -> None:
        errors: list[BaseException] = []

        def invoke() -> None:
            try:
                callback()
            except BaseException as exc:  # pragma: no cover - surfaced as audit
                errors.append(exc)

        worker = Thread(target=invoke, daemon=True, name=f"roby-shutdown-{name}")
        worker.start()
        worker.join(self.shutdown_timeout_seconds)
        if worker.is_alive():
            self._record(
                LifecycleEventKind.SHUTDOWN_STEP_TIMED_OUT,
                moment,
                detail=name,
            )
        elif errors:
            self._record(
                LifecycleEventKind.SHUTDOWN_STEP_FAILED,
                moment,
                detail=f"{name}: {type(errors[0]).__name__}",
            )

    def _record(
        self,
        kind: LifecycleEventKind,
        occurred_at: datetime,
        *,
        reason: LifecycleExitReason | None = None,
        detail: str = "",
    ) -> None:
        self._events.append(
            LifecycleEvent(
                kind=kind,
                occurred_at=occurred_at,
                reason=reason,
                detail=detail,
            )
        )

    def _read_state(self) -> dict[str, Any]:
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {}
        return raw if isinstance(raw, dict) else {}

    def _persist(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "rp25.1-v1",
            "current_session": (
                self._current_session.as_dict()
                if self._current_session is not None
                else None
            ),
            "previous_session": (
                self._previous_session.as_dict()
                if self._previous_session is not None
                else None
            ),
            "restart_requested": self._restart_requested,
            "events": [event.as_dict() for event in self._events[-100:]],
        }
        temporary = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.state_path)


def _utc(value: datetime | None) -> datetime:
    moment = value or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)


def _session_from_dict(value: object) -> ApplicationSession | None:
    if not isinstance(value, dict):
        return None
    try:
        reason_raw = value.get("exit_reason")
        reason = LifecycleExitReason(reason_raw) if reason_raw else None
        stopped_raw = value.get("stopped_at")
        return ApplicationSession(
            session_id=str(value["session_id"]),
            started_at=datetime.fromisoformat(str(value["started_at"])),
            stopped_at=(
                datetime.fromisoformat(str(stopped_raw)) if stopped_raw else None
            ),
            clean_shutdown=bool(value.get("clean_shutdown", False)),
            exit_reason=reason,
            version=str(value.get("version", "ROBY XI.2")),
        )
    except (KeyError, TypeError, ValueError):
        return None
