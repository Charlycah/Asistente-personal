from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from .models import CognitiveState

_SCHEMA_VERSION = 1
_STATE_FIELDS = {
    "active_objective",
    "current_focus",
    "confidence",
    "last_decision",
    "updated_at",
}


@runtime_checkable
class CognitiveStateStore(Protocol):
    """Persistence boundary for the cognitive-state contract."""

    def load(self) -> CognitiveState | None: ...

    def save(self, state: CognitiveState) -> Path: ...

    def delete(self) -> bool: ...


class JsonCognitiveStateStore:
    """Atomic JSON persistence for one cognitive-state snapshot."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else self.default_path()

    @staticmethod
    def default_path() -> Path:
        return Path.cwd() / ".roby" / "cognitive_state.json"

    def load(self) -> CognitiveState | None:
        if not self.path.exists():
            return None
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return _decode_document(payload)
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError(f"invalid cognitive state file: {self.path}") from error

    def save(self, state: CognitiveState) -> Path:
        if not isinstance(state, CognitiveState):
            raise TypeError("state must be a CognitiveState")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "schema_version": _SCHEMA_VERSION,
            "state": _encode_state(state),
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f"{self.path.name}.",
            suffix=".tmp",
            dir=self.path.parent,
            text=True,
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(
                    document,
                    stream,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, self.path)
        finally:
            temporary_path.unlink(missing_ok=True)
        return self.path

    def delete(self) -> bool:
        if not self.path.exists():
            return False
        self.path.unlink()
        return True


def _encode_state(state: CognitiveState) -> dict[str, object]:
    return {
        "active_objective": state.active_objective,
        "current_focus": state.current_focus,
        "confidence": state.confidence,
        "last_decision": state.last_decision,
        "updated_at": state.updated_at.isoformat(),
    }


def _decode_document(payload: object) -> CognitiveState:
    if not isinstance(payload, dict):
        raise ValueError("cognitive state document must be an object")
    if set(payload) != {"schema_version", "state"}:
        raise ValueError("cognitive state document has invalid fields")
    if payload["schema_version"] != _SCHEMA_VERSION:
        raise ValueError("unsupported cognitive state schema")
    state_payload = payload["state"]
    if not isinstance(state_payload, dict) or set(state_payload) != _STATE_FIELDS:
        raise ValueError("cognitive state payload has invalid fields")
    active_objective = _optional_text(state_payload["active_objective"])
    current_focus = _optional_text(state_payload["current_focus"])
    last_decision = _optional_text(state_payload["last_decision"])
    confidence = state_payload["confidence"]
    updated_at = state_payload["updated_at"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("cognitive state confidence must be numeric")
    if not isinstance(updated_at, str):
        raise ValueError("cognitive state timestamp must be text")
    return CognitiveState(
        active_objective=active_objective,
        current_focus=current_focus,
        confidence=float(confidence),
        last_decision=last_decision,
        updated_at=datetime.fromisoformat(updated_at),
    )


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("cognitive state optional text must be text or null")
    return value
