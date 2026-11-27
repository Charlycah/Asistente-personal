"""Temporary, opt-in GUI-06 diagnostic observation primitives.

No persistence, provider calls, logging, or runtime mutation.
Do not include raw conversation text in diagnostic records.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator, Mapping, Sequence


REFERENCE_PREVIOUS = "FARO AZUL 27"
REFERENCE_CURRENT = "LUNA COBRE 84"
PERSONALITY_MARKER = "CANONICAL STABLE PERSONALITY EXPRESSION"

_ALLOWED_STAGES = frozenset(
    {
        "P1",
        "P2",
        "P3",
        "P4a",
        "P4b",
        "P5a",
        "P5b",
    }
)


@dataclass(frozen=True)
class DiagnosticPresence:
    previous_reference: bool
    current_reference: bool
    personality_marker: bool


@dataclass(frozen=True)
class DiagnosticMessageObservation:
    role: str
    presence: DiagnosticPresence


@dataclass(frozen=True)
class DiagnosticStageObservation:
    stage: str
    presence: DiagnosticPresence | None
    messages: tuple[DiagnosticMessageObservation, ...]


def inspect_text(text: str) -> DiagnosticPresence:
    """Return only marker-presence flags; never retain source text."""
    return DiagnosticPresence(
        previous_reference=REFERENCE_PREVIOUS in text,
        current_reference=REFERENCE_CURRENT in text,
        personality_marker=PERSONALITY_MARKER in text,
    )


def inspect_messages(
    messages: Sequence[Mapping[str, str]],
) -> tuple[DiagnosticMessageObservation, ...]:
    """Summarize effective message roles and diagnostic marker presence."""
    allowed_roles = frozenset({"system", "user", "assistant", "tool"})

    return tuple(
        DiagnosticMessageObservation(
            role=(
                str(message.get("role", "")).lower()
                if str(message.get("role", "")).lower() in allowed_roles
                else "unknown"
            ),
            presence=inspect_text(str(message.get("content", ""))),
        )
        for message in messages
    )


def observe_stage(
    stage: str,
    *,
    text: str | None = None,
    messages: Sequence[Mapping[str, str]] | None = None,
) -> DiagnosticStageObservation:
    """Build an immutable, non-persistent stage observation."""
    if stage not in _ALLOWED_STAGES:
        raise ValueError("Unsupported diagnostic stage")

    if text is not None and messages is not None:
        raise ValueError("Specify text or messages, not both")

    return DiagnosticStageObservation(
        stage=stage,
        presence=inspect_text(text) if text is not None else None,
        messages=inspect_messages(messages) if messages is not None else (),
    )


class DiagnosticRecorder:
    """Bounded, explicitly enabled, in-memory diagnostic recorder."""

    def __init__(self, *, capacity: int = 64) -> None:
        if capacity < 1 or capacity > 256:
            raise ValueError("Diagnostic capacity must be between 1 and 256")
        self._capacity = capacity
        self._enabled = False
        self._next_turn = 0
        self._records: list[tuple[int, DiagnosticStageObservation]] = []

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False
        self.clear()

    def clear(self) -> None:
        self._records.clear()

    def begin_turn(self) -> int | None:
        if not self._enabled:
            return None
        self._next_turn += 1
        return self._next_turn

    def record(
        self,
        turn_id: int | None,
        observation: DiagnosticStageObservation,
    ) -> None:
        if not self._enabled or turn_id is None:
            return
        if not isinstance(turn_id, int) or turn_id < 1:
            raise ValueError("Invalid diagnostic turn identifier")
        if not isinstance(observation, DiagnosticStageObservation):
            raise TypeError("Invalid diagnostic observation")
        self._records.append((turn_id, observation))
        if len(self._records) > self._capacity:
            del self._records[:-self._capacity]

    def snapshot(self) -> tuple[tuple[int, DiagnosticStageObservation], ...]:
        return tuple(self._records)

_ACTIVE_DIAGNOSTIC_TURN: ContextVar[int | None] = ContextVar(
    "gui06_active_diagnostic_turn",
    default=None,
)


def current_diagnostic_turn() -> int | None:
    """Return the diagnostic turn bound to this execution context."""
    return _ACTIVE_DIAGNOSTIC_TURN.get()


@contextmanager
def diagnostic_turn_context(turn_id: int | None) -> Iterator[None]:
    """Bind and restore a diagnostic turn without changing runtime requests."""
    if turn_id is not None and (
        not isinstance(turn_id, int)
        or isinstance(turn_id, bool)
        or turn_id < 1
    ):
        raise ValueError("Invalid diagnostic turn identifier")

    token = _ACTIVE_DIAGNOSTIC_TURN.set(turn_id)
    try:
        yield
    finally:
        _ACTIVE_DIAGNOSTIC_TURN.reset(token)

_DIAGNOSTIC_RECORDER = DiagnosticRecorder()


def diagnostic_recorder() -> DiagnosticRecorder:
    """Return the shared, initially disabled diagnostic recorder."""
    return _DIAGNOSTIC_RECORDER


def capture_diagnostic_request(stage: str, request: object) -> None:
    """Observe a structured request only while diagnostics are active."""
    try:
        recorder = _DIAGNOSTIC_RECORDER
        if not recorder.enabled:
            return

        turn_id = current_diagnostic_turn()
        if turn_id is None:
            return

        system_prompt = getattr(request, "system_prompt", None)
        structured_messages = getattr(request, "messages", ())

        messages = []

        if isinstance(system_prompt, str) and system_prompt:
            messages.append(
                {"role": "system", "content": system_prompt}
            )

        for message in structured_messages:
            role = getattr(message, "role", "")
            content = getattr(message, "content", "")

            if not isinstance(role, str) or not isinstance(content, str):
                continue

            messages.append(
                {"role": role, "content": content}
            )

        capture_diagnostic_stage(stage, messages=tuple(messages))
    except Exception:
        return


def capture_diagnostic_stage(
    stage: str,
    *,
    text: str | None = None,
    messages: Sequence[Mapping[str, str]] | None = None,
) -> None:
    """Capture bounded metadata without affecting operational execution."""
    try:
        recorder = _DIAGNOSTIC_RECORDER
        if not recorder.enabled:
            return

        turn_id = current_diagnostic_turn()
        if turn_id is None:
            return

        observation = observe_stage(
            stage,
            text=text,
            messages=messages,
        )
        recorder.record(turn_id, observation)
    except Exception:
        # Diagnostic failures must not alter operational outcomes.
        return