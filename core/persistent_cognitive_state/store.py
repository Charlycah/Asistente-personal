from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from .models import PersistentCognitiveState


class JsonPersistentCognitiveStateStore:
    """Owns one small, atomic and backward-compatible cognitive state file."""

    SCHEMA_VERSION = 1

    def __init__(self, path: Path | str = ".roby/cognitive_state.json") -> None:
        self.path = Path(path)
        self._lock = RLock()
        self._state = self._load_or_initialize()

    def load(self) -> PersistentCognitiveState:
        with self._lock:
            self._state = self._read()
            return self._state

    def save(self, state: PersistentCognitiveState) -> PersistentCognitiveState:
        with self._lock:
            self._persist(state)
            self._state = state
            return state

    def update(
        self,
        *,
        active_objective: str | None = None,
        current_focus: str | None = None,
        confidence: float | None = None,
        last_decision: str | None = None,
        updated_at: datetime | None = None,
    ) -> PersistentCognitiveState:
        with self._lock:
            state = self._state.with_updates(
                active_objective=active_objective,
                current_focus=current_focus,
                confidence=confidence,
                last_decision=last_decision,
                updated_at=updated_at,
            )
            self._persist(state)
            self._state = state
            return state

    def snapshot(self) -> PersistentCognitiveState:
        with self._lock:
            return self._state

    def reset(
        self, *, updated_at: datetime | None = None
    ) -> PersistentCognitiveState:
        timestamp = updated_at or datetime.now(timezone.utc)
        return self.save(PersistentCognitiveState(updated_at=timestamp))

    def _load_or_initialize(self) -> PersistentCognitiveState:
        if self.path.exists():
            return self._read()
        state = PersistentCognitiveState.empty()
        self._persist(state)
        return state

    def _read(self) -> PersistentCognitiveState:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != self.SCHEMA_VERSION:
                raise ValueError("unsupported schema")
            state = payload["state"]
            return PersistentCognitiveState(
                active_objective=state.get("active_objective"),
                current_focus=state.get("current_focus"),
                confidence=float(state.get("confidence", 0.0)),
                last_decision=state.get("last_decision"),
                updated_at=self._parse_time(state.get("updated_at")),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError(
                f"invalid persistent cognitive state file: {self.path}"
            ) from error

    def _persist(self, state: PersistentCognitiveState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "state": {
                "active_objective": state.active_objective,
                "current_focus": state.current_focus,
                "confidence": state.confidence,
                "last_decision": state.last_decision,
                "updated_at": (
                    state.updated_at.isoformat()
                    if state.updated_at is not None
                    else None
                ),
            },
        }
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)

    @staticmethod
    def _parse_time(value: object) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(str(value))
