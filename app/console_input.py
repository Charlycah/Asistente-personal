from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar

T = TypeVar("T")


class ConsoleInputKind(str, Enum):
    EMPTY = "empty"
    EXIT = "exit"
    COMMAND = "command"
    RESERVED = "reserved"
    CONVERSATION = "conversation"


@dataclass(frozen=True)
class ConsoleInput:
    raw: str
    normalized: str
    kind: ConsoleInputKind


class ConsoleInputParser:
    """Classify terminal input before it can enter the conversation runtime."""

    _EXIT_COMMANDS = frozenset({"/exit", "/quit", "/salir", "exit", "quit", "salir"})
    _RESERVED_PREFIXES = (
        "obs>",
        "roby>",
        "sys>",
        "trace>",
        "system:",
        "assistant:",
        "user:",
    )

    def parse(self, text: str) -> ConsoleInput:
        stripped = text.strip()
        normalized = stripped.casefold()
        if not stripped:
            kind = ConsoleInputKind.EMPTY
        elif normalized in self._EXIT_COMMANDS:
            kind = ConsoleInputKind.EXIT
        elif self._is_reserved(normalized):
            kind = ConsoleInputKind.RESERVED
        elif normalized.startswith("/") and not normalized.startswith("/tool"):
            kind = ConsoleInputKind.COMMAND
        else:
            kind = ConsoleInputKind.CONVERSATION
        return ConsoleInput(raw=text, normalized=normalized, kind=kind)

    def _is_reserved(self, normalized: str) -> bool:
        return normalized.startswith(self._RESERVED_PREFIXES)


class ConsoleInputBoundary:
    """Forward conversation input only after independent classification."""

    def __init__(self, parser: ConsoleInputParser | None = None) -> None:
        self.parser = parser or ConsoleInputParser()

    def classify(self, text: str) -> ConsoleInput:
        return self.parser.parse(text)

    def forward(self, parsed: ConsoleInput, submit: Callable[[str], T]) -> T | None:
        if parsed.kind is not ConsoleInputKind.CONVERSATION:
            return None
        return submit(parsed.raw)
