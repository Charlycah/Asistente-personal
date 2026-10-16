from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.runtime_readiness_gate import RuntimeReadinessResult, RuntimeReadinessStatus


class ConversationEntryKind(str, Enum):
    GREETING = "greeting"
    QUESTION = "question"
    REQUEST = "request"
    CONTINUATION = "continuation"
    COMMENT = "comment"
    ATTENTION = "attention"
    FAREWELL = "farewell"
    INCOMPLETE = "incomplete"
    NOT_APPLICABLE = "not_applicable"


class ConversationEntryAction(str, Enum):
    ROUTE_TO_GREETING = "route_to_greeting"
    ROUTE_TO_REASONING = "route_to_reasoning"
    ROUTE_TO_ACTION = "route_to_action"
    ROUTE_TO_CONTEXT = "route_to_context"
    ROUTE_TO_DIALOGUE = "route_to_dialogue"
    ROUTE_TO_ATTENTION = "route_to_attention"
    ROUTE_TO_FAREWELL = "route_to_farewell"
    REQUEST_COMPLETION = "request_completion"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class ConversationEntryConfig:
    assistant_names: tuple[str, ...] = ("roby",)
    minimum_text_length: int = 1

    def __post_init__(self) -> None:
        names = tuple(name.strip().casefold() for name in self.assistant_names)
        if not names or any(not name for name in names):
            raise ValueError("assistant names must not be empty")
        if len(names) != len(set(names)):
            raise ValueError("assistant names must be unique")
        if self.minimum_text_length < 1:
            raise ValueError("minimum text length must be positive")
        object.__setattr__(self, "assistant_names", names)


@dataclass(frozen=True)
class ConversationEntryRequest:
    owner: str
    text: str
    readiness_result: RuntimeReadinessResult
    conversation_requested: bool = True
    session_id: str = "default"

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        text = self.text.strip()
        session_id = self.session_id.strip()
        if not owner:
            raise ValueError("conversation owner must not be blank")
        if not session_id:
            raise ValueError("conversation session id must not be blank")
        readiness_owner = self.readiness_result.request.owner
        if readiness_owner.casefold() != owner.casefold():
            raise ValueError("conversation owner must match readiness owner")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "session_id", session_id)


@dataclass(frozen=True)
class ConversationEntryResult:
    request: ConversationEntryRequest
    kind: ConversationEntryKind | str
    action: ConversationEntryAction | str
    normalized_text: str
    addressed_to_roby: bool
    conversational: bool
    response_generation_allowed: bool
    provider_call_allowed: bool
    network_access_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    entry_id: str = ""

    def __post_init__(self) -> None:
        kind = ConversationEntryKind(self.kind)
        action = ConversationEntryAction(self.action)
        normalized = self.normalized_text.strip()
        rationale = tuple(self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("conversation entry timestamp must be timezone-aware")
        if not rationale or any(not item.strip() for item in rationale):
            raise ValueError("conversation entry rationale must not be empty")
        if any(
            (
                self.response_generation_allowed,
                self.provider_call_allowed,
                self.network_access_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M163 cannot authorize response execution")
        if kind is ConversationEntryKind.NOT_APPLICABLE and normalized:
            raise ValueError("inactive conversation entry cannot expose text")
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "normalized_text", normalized)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.entry_id and self.entry_id != expected:
            raise ValueError("conversation entry id is inconsistent")
        object.__setattr__(self, "entry_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.session_id,
                self.request.readiness_result.readiness_id,
                self.kind.value,
                self.action.value,
                self.normalized_text,
                str(self.addressed_to_roby),
                str(self.conversational),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class ConversationEntryRepository(Protocol):
    def add(self, result: ConversationEntryResult) -> None: ...

    def get(self, entry_id: str) -> ConversationEntryResult | None: ...

    def list_all(self) -> tuple[ConversationEntryResult, ...]: ...


class InMemoryConversationEntryRepository:
    def __init__(self) -> None:
        self._items: dict[str, ConversationEntryResult] = {}

    def add(self, result: ConversationEntryResult) -> None:
        if result.entry_id in self._items:
            raise ValueError("conversation entry result already exists")
        self._items[result.entry_id] = result

    def get(self, entry_id: str) -> ConversationEntryResult | None:
        return self._items.get(entry_id)

    def list_all(self) -> tuple[ConversationEntryResult, ...]:
        return tuple(self._items.values())


def readiness_allows_entry(result: RuntimeReadinessResult) -> bool:
    return result.status in {
        RuntimeReadinessStatus.READY,
        RuntimeReadinessStatus.DEGRADED,
    }
