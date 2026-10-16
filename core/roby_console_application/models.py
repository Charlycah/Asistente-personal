from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.conversation_entry_point import ConversationEntryResult
from core.natural_greeting_response import NaturalGreetingResult
from core.roby_voice_style_policy import ROBYVoiceStyleResult
from core.runtime_readiness_gate import RuntimeReadinessResult


class ConsoleApplicationStatus(str, Enum):
    STARTED = "started"
    STOPPED = "stopped"
    BLOCKED = "blocked"


class ConsoleTurnStatus(str, Enum):
    DELIVERED = "delivered"
    ROUTED = "routed"
    INCOMPLETE = "incomplete"
    WITHHELD = "withheld"


class ConsoleTurnAction(str, Enum):
    WRITE_RESPONSE = "write_response"
    AWAIT_PIPELINE = "await_pipeline"
    REQUEST_COMPLETION = "request_completion"
    STOP_SESSION = "stop_session"
    WITHHOLD = "withhold"


@dataclass(frozen=True)
class ROBYConsoleConfig:
    prompt: str = "Tu: "
    assistant_prefix: str = "ROBY: "
    exit_commands: tuple[str, ...] = ("salir", "exit", "quit")
    incomplete_response: str = "Te escucho. Completa la idea."
    pending_response: str = "Entendido. Ese flujo aun no esta conectado."
    blocked_response: str = "ROBY no esta listo para conversar."
    max_turns: int = 1000

    def __post_init__(self) -> None:
        prompt = self.prompt
        prefix = self.assistant_prefix
        commands = tuple(item.strip().casefold() for item in self.exit_commands)
        if not prompt or not prefix:
            raise ValueError("console prompt and assistant prefix must not be blank")
        if not commands or any(not item for item in commands):
            raise ValueError("console exit commands must not be blank")
        if len(commands) != len(set(commands)):
            raise ValueError("console exit commands must be unique")
        if self.max_turns < 1:
            raise ValueError("console maximum turns must be positive")
        for value in (
            self.incomplete_response,
            self.pending_response,
            self.blocked_response,
        ):
            if not value.strip():
                raise ValueError("console responses must not be blank")
        object.__setattr__(self, "exit_commands", commands)


@dataclass(frozen=True)
class ROBYConsoleSessionRequest:
    owner: str
    readiness_result: RuntimeReadinessResult
    session_id: str = "console"

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        if not owner:
            raise ValueError("console owner must not be blank")
        if not session_id:
            raise ValueError("console session id must not be blank")
        if self.readiness_result.request.owner.casefold() != owner.casefold():
            raise ValueError("console owner must match readiness owner")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)


@dataclass(frozen=True)
class ROBYConsoleTurn:
    owner: str
    session_id: str
    sequence: int
    input_text: str
    status: ConsoleTurnStatus | str
    action: ConsoleTurnAction | str
    response_text: str
    entry_result: ConversationEntryResult | None
    greeting_result: NaturalGreetingResult | None
    voice_result: ROBYVoiceStyleResult | None
    provider_call_performed: bool
    network_access_performed: bool
    platform_mutation_performed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    turn_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        text = self.input_text.strip()
        response = self.response_text.strip()
        status = ConsoleTurnStatus(self.status)
        action = ConsoleTurnAction(self.action)
        rationale = tuple(self.rationale)
        if not owner or not session_id:
            raise ValueError("console turn identity must not be blank")
        if self.sequence < 1:
            raise ValueError("console turn sequence must be positive")
        if self.created_at.tzinfo is None:
            raise ValueError("console turn timestamp must be timezone-aware")
        if not rationale or any(not item.strip() for item in rationale):
            raise ValueError("console turn rationale must not be empty")
        if any(
            (
                self.provider_call_performed,
                self.network_access_performed,
                self.platform_mutation_performed,
            )
        ):
            raise ValueError("M172 cannot perform external side effects")
        if status is ConsoleTurnStatus.DELIVERED:
            if not response or self.voice_result is None:
                raise ValueError("delivered console turn requires styled response")
        if action is ConsoleTurnAction.STOP_SESSION and response:
            raise ValueError("console exit turn cannot expose response text")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "input_text", text)
        object.__setattr__(self, "response_text", response)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.turn_id and self.turn_id != expected:
            raise ValueError("console turn id is inconsistent")
        object.__setattr__(self, "turn_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.owner.casefold(),
                self.session_id,
                str(self.sequence),
                self.input_text,
                self.status.value,
                self.action.value,
                self.response_text,
                self.entry_result.entry_id if self.entry_result else "",
                self.voice_result.policy_id if self.voice_result else "",
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@dataclass(frozen=True)
class ROBYConsoleSession:
    request: ROBYConsoleSessionRequest
    status: ConsoleApplicationStatus | str
    turns: tuple[ROBYConsoleTurn, ...]
    started_at: datetime
    ended_at: datetime
    rationale: tuple[str, ...]
    session_record_id: str = ""

    def __post_init__(self) -> None:
        status = ConsoleApplicationStatus(self.status)
        turns = tuple(self.turns)
        rationale = tuple(self.rationale)
        if self.started_at.tzinfo is None or self.ended_at.tzinfo is None:
            raise ValueError("console session timestamps must be timezone-aware")
        if self.ended_at < self.started_at:
            raise ValueError("console session cannot end before it starts")
        if not rationale or any(not item.strip() for item in rationale):
            raise ValueError("console session rationale must not be empty")
        if tuple(item.sequence for item in turns) != tuple(range(1, len(turns) + 1)):
            raise ValueError("console turns must have contiguous sequence")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "turns", turns)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.session_record_id and self.session_record_id != expected:
            raise ValueError("console session id is inconsistent")
        object.__setattr__(self, "session_record_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.session_id,
                self.request.readiness_result.readiness_id,
                self.status.value,
                ";".join(item.turn_id for item in self.turns),
                self.started_at.isoformat(),
                self.ended_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class ConsoleIO(Protocol):
    def read(self, prompt: str) -> str | None: ...

    def write(self, text: str) -> None: ...


@runtime_checkable
class ROBYConsoleRepository(Protocol):
    def add(self, session: ROBYConsoleSession) -> None: ...

    def list_all(self) -> tuple[ROBYConsoleSession, ...]: ...


class InMemoryROBYConsoleRepository:
    def __init__(self) -> None:
        self._items: list[ROBYConsoleSession] = []

    def add(self, session: ROBYConsoleSession) -> None:
        if any(
            item.session_record_id == session.session_record_id for item in self._items
        ):
            raise ValueError("console session already exists")
        self._items.append(session)

    def list_all(self) -> tuple[ROBYConsoleSession, ...]:
        return tuple(self._items)
