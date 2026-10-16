from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from .models import LocalRuntimeState


@runtime_checkable
class LocalRuntimeStateStore(Protocol):
    def load(self) -> LocalRuntimeState | None: ...
    def save(self, state: LocalRuntimeState) -> None: ...


class JsonLocalRuntimeStateStore:
    """Persists only operational lifecycle metadata, never conversation content."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def load(self) -> LocalRuntimeState | None:
        if not self.path.exists():
            return None
        with self.path.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
        return LocalRuntimeState(
            owner=payload["owner"],
            session_id=payload["session_id"],
            status=payload["status"],
            started_at=self._time(payload.get("started_at")),
            stopped_at=self._time(payload.get("stopped_at")),
            failure=payload.get("failure"),
            updated_at=self._time(payload["updated_at"]),
        )

    def save(self, state: LocalRuntimeState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "owner": state.owner,
            "session_id": state.session_id,
            "status": state.status.value,
            "started_at": self._dump_time(state.started_at),
            "stopped_at": self._dump_time(state.stopped_at),
            "failure": state.failure,
            "updated_at": self._dump_time(state.updated_at),
        }
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(self.path)

    @staticmethod
    def _time(value: str | None):
        return datetime.fromisoformat(value) if value else None

    @staticmethod
    def _dump_time(value):
        return value.isoformat() if value else None
