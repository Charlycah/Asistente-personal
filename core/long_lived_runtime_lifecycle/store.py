from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from core.platform_runtime_compatibility import apply_private_file_permissions

from .models import LongLivedRuntimeState


@runtime_checkable
class LongLivedRuntimeStateStore(Protocol):
    def load(self) -> LongLivedRuntimeState | None: ...
    def save(self, state: LongLivedRuntimeState) -> None: ...


class JsonLongLivedRuntimeStateStore:
    """Atomically persists lifecycle metadata without conversation content."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def load(self) -> LongLivedRuntimeState | None:
        if not self.path.exists():
            return None
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return LongLivedRuntimeState(
            owner=payload["owner"],
            session_id=payload["session_id"],
            process_id=payload["process_id"],
            status=payload["status"],
            generation=payload["generation"],
            started_at=self._time(payload.get("started_at")),
            heartbeat_at=self._time(payload.get("heartbeat_at")),
            stopped_at=self._time(payload.get("stopped_at")),
            failure=payload.get("failure"),
            updated_at=self._time(payload["updated_at"]),
        )

    def save(self, state: LongLivedRuntimeState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "failure": state.failure,
            "generation": state.generation,
            "heartbeat_at": self._dump(state.heartbeat_at),
            "owner": state.owner,
            "process_id": state.process_id,
            "session_id": state.session_id,
            "started_at": self._dump(state.started_at),
            "status": state.status.value,
            "stopped_at": self._dump(state.stopped_at),
            "updated_at": self._dump(state.updated_at),
        }
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        apply_private_file_permissions(temporary)
        temporary.replace(self.path)
        apply_private_file_permissions(self.path)

    @staticmethod
    def _time(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    @staticmethod
    def _dump(value: datetime | None) -> str | None:
        return value.isoformat() if value else None
