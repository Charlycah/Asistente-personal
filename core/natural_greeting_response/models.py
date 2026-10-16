from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.conversation_entry_point import ConversationEntryKind, ConversationEntryResult


class GreetingPeriod(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    NEUTRAL = "neutral"


class NaturalGreetingStatus(str, Enum):
    GENERATED = "generated"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class NaturalGreetingAction(str, Enum):
    DELIVER = "deliver"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class NaturalGreetingConfig:
    assistant_name: str = "Roby"
    use_owner_name: bool = True
    allow_time_aware_greetings: bool = True
    recent_response_window: int = 3
    max_response_length: int = 120

    def __post_init__(self) -> None:
        assistant_name = self.assistant_name.strip()
        if not assistant_name:
            raise ValueError("assistant name must not be blank")
        if self.recent_response_window < 0:
            raise ValueError("recent response window must not be negative")
        if self.max_response_length < 1:
            raise ValueError("maximum response length must be positive")
        object.__setattr__(self, "assistant_name", assistant_name)


@dataclass(frozen=True)
class NaturalGreetingRequest:
    owner: str
    entry_result: ConversationEntryResult
    greeting_requested: bool = True
    session_id: str = "default"
    recent_responses: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        recent = tuple(item.strip() for item in self.recent_responses)
        if not owner:
            raise ValueError("greeting owner must not be blank")
        if not session_id:
            raise ValueError("greeting session id must not be blank")
        entry_owner = self.entry_result.request.owner
        if entry_owner.casefold() != owner.casefold():
            raise ValueError("greeting owner must match conversation entry owner")
        if any(not item for item in recent):
            raise ValueError("recent greeting responses must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "recent_responses", recent)


@dataclass(frozen=True)
class NaturalGreetingResult:
    request: NaturalGreetingRequest
    status: NaturalGreetingStatus | str
    action: NaturalGreetingAction | str
    response_text: str
    period: GreetingPeriod | str
    variant_key: str
    natural: bool
    repeated_recent_response: bool
    provider_call_allowed: bool
    network_access_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    greeting_id: str = ""

    def __post_init__(self) -> None:
        status = NaturalGreetingStatus(self.status)
        action = NaturalGreetingAction(self.action)
        period = GreetingPeriod(self.period)
        response = self.response_text.strip()
        variant_key = self.variant_key.strip()
        rationale = tuple(self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("natural greeting timestamp must be timezone-aware")
        if not rationale or any(not item.strip() for item in rationale):
            raise ValueError("natural greeting rationale must not be empty")
        if any(
            (
                self.provider_call_allowed,
                self.network_access_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M164 cannot authorize external side effects")
        if status is NaturalGreetingStatus.GENERATED:
            if not response or not variant_key:
                raise ValueError("generated greeting requires text and variant key")
            if action is not NaturalGreetingAction.DELIVER or not self.natural:
                raise ValueError("generated greeting must be natural and deliverable")
        elif response or variant_key:
            raise ValueError("inactive greeting cannot expose response content")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "period", period)
        object.__setattr__(self, "response_text", response)
        object.__setattr__(self, "variant_key", variant_key)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.greeting_id and self.greeting_id != expected:
            raise ValueError("natural greeting id is inconsistent")
        object.__setattr__(self, "greeting_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.session_id,
                self.request.entry_result.entry_id,
                self.status.value,
                self.action.value,
                self.response_text,
                self.period.value,
                self.variant_key,
                str(self.repeated_recent_response),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class NaturalGreetingRepository(Protocol):
    def add(self, result: NaturalGreetingResult) -> None: ...

    def get(self, greeting_id: str) -> NaturalGreetingResult | None: ...

    def list_all(self) -> tuple[NaturalGreetingResult, ...]: ...


class InMemoryNaturalGreetingRepository:
    def __init__(self) -> None:
        self._items: dict[str, NaturalGreetingResult] = {}

    def add(self, result: NaturalGreetingResult) -> None:
        if result.greeting_id in self._items:
            raise ValueError("natural greeting result already exists")
        self._items[result.greeting_id] = result

    def get(self, greeting_id: str) -> NaturalGreetingResult | None:
        return self._items.get(greeting_id)

    def list_all(self) -> tuple[NaturalGreetingResult, ...]:
        return tuple(self._items.values())


def entry_allows_greeting(result: ConversationEntryResult) -> bool:
    return (
        result.kind is ConversationEntryKind.GREETING
        and result.conversational
        and not result.response_generation_allowed
    )
