from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from .models import CognitiveState
from .persistence import _decode_document, _encode_state

_SCHEMA_VERSION = 1
_TRANSITION_FIELDS = {"before", "after", "recorded_at", "reason"}


@dataclass(frozen=True, slots=True)
class CognitiveStateTransition:
    """One explicit transition between two cognitive-state snapshots."""

    before: CognitiveState
    after: CognitiveState
    recorded_at: datetime
    reason: str

    def __post_init__(self) -> None:
        if self.recorded_at.tzinfo is None:
            raise ValueError("transition timestamp must be timezone-aware")
        normalized_reason = self.reason.strip()
        if not normalized_reason:
            raise ValueError("transition reason must not be blank")
        object.__setattr__(self, "reason", normalized_reason)


@runtime_checkable
class CognitiveStateTransitionStore(Protocol):
    """Bounded persistence boundary for cognitive-state transitions."""

    def append(self, transition: CognitiveStateTransition) -> None: ...

    def recent(
        self,
        limit: int | None = None,
    ) -> tuple[CognitiveStateTransition, ...]: ...

    def clear(self) -> bool: ...


class JsonCognitiveStateTransitionStore:
    """Atomic JSON storage retaining only the most recent transitions."""

    def __init__(
        self,
        path: Path | str | None = None,
        *,
        capacity: int = 50,
    ) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 1:
            raise ValueError("capacity must be at least one")
        self.path = Path(path) if path is not None else self.default_path()
        self.capacity = capacity

    @staticmethod
    def default_path() -> Path:
        return Path.cwd() / ".roby" / "cognitive_state_history.json"

    def append(self, transition: CognitiveStateTransition) -> None:
        if not isinstance(transition, CognitiveStateTransition):
            raise TypeError("transition must be a CognitiveStateTransition")
        transitions = list(self.recent())
        transitions.append(transition)
        self._write(transitions[-self.capacity :])

    def recent(
        self,
        limit: int | None = None,
    ) -> tuple[CognitiveStateTransition, ...]:
        if limit is not None:
            if isinstance(limit, bool) or not isinstance(limit, int):
                raise TypeError("limit must be an integer or None")
            if limit < 0:
                raise ValueError("limit must not be negative")
        transitions = self._load()
        if limit is None:
            return transitions
        if limit == 0:
            return ()
        return transitions[-limit:]

    def clear(self) -> bool:
        if not self.path.exists():
            return False
        self.path.unlink()
        return True

    def _load(self) -> tuple[CognitiveStateTransition, ...]:
        if not self.path.exists():
            return ()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return _decode_history(payload)
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            message = f"invalid cognitive state history file: {self.path}"
            raise ValueError(message) from error

    def _write(self, transitions: list[CognitiveStateTransition]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "schema_version": _SCHEMA_VERSION,
            "transitions": [_encode_transition(item) for item in transitions],
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


def _encode_transition(transition: CognitiveStateTransition) -> dict[str, object]:
    return {
        "before": _encode_state(transition.before),
        "after": _encode_state(transition.after),
        "recorded_at": transition.recorded_at.isoformat(),
        "reason": transition.reason,
    }


def _decode_history(payload: object) -> tuple[CognitiveStateTransition, ...]:
    if not isinstance(payload, dict):
        raise ValueError("cognitive state history document must be an object")
    if set(payload) != {"schema_version", "transitions"}:
        raise ValueError("cognitive state history document has invalid fields")
    if payload["schema_version"] != _SCHEMA_VERSION:
        raise ValueError("unsupported cognitive state history schema")
    raw_transitions = payload["transitions"]
    if not isinstance(raw_transitions, list):
        raise ValueError("cognitive state transitions must be a list")
    return tuple(_decode_transition(item) for item in raw_transitions)


def _decode_transition(payload: object) -> CognitiveStateTransition:
    if not isinstance(payload, dict) or set(payload) != _TRANSITION_FIELDS:
        raise ValueError("cognitive state transition has invalid fields")
    before = _decode_document(
        {"schema_version": 1, "state": payload["before"]}
    )
    after = _decode_document(
        {"schema_version": 1, "state": payload["after"]}
    )
    recorded_at = payload["recorded_at"]
    reason = payload["reason"]
    if not isinstance(recorded_at, str):
        raise ValueError("transition timestamp must be text")
    if not isinstance(reason, str):
        raise ValueError("transition reason must be text")
    return CognitiveStateTransition(
        before=before,
        after=after,
        recorded_at=datetime.fromisoformat(recorded_at),
        reason=reason,
    )
