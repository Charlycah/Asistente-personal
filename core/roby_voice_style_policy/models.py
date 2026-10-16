from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.natural_greeting_response import NaturalGreetingResult, NaturalGreetingStatus


class VoicePolicyStatus(str, Enum):
    APPLIED = "applied"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class VoicePolicyAction(str, Enum):
    DELIVER = "deliver"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class ROBYVoiceStyleConfig:
    assistant_name: str = "ROBY"
    colloquial: bool = True
    warm: bool = True
    concise: bool = True
    strip_diacritics: bool = True
    forbid_bureaucratic_phrases: bool = True
    max_response_length: int = 240

    def __post_init__(self) -> None:
        name = self.assistant_name.strip()
        if not name:
            raise ValueError("assistant name must not be blank")
        if self.max_response_length < 1:
            raise ValueError("maximum response length must be positive")
        object.__setattr__(self, "assistant_name", name)


@dataclass(frozen=True)
class ROBYVoiceStyleRequest:
    owner: str
    greeting_result: NaturalGreetingResult
    style_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("voice style owner must not be blank")
        source_owner = self.greeting_result.request.owner
        if source_owner.casefold() != owner.casefold():
            raise ValueError("voice style owner must match greeting owner")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class ROBYVoiceStyleResult:
    request: ROBYVoiceStyleRequest
    status: VoicePolicyStatus | str
    action: VoicePolicyAction | str
    original_text: str
    response_text: str
    normalized: bool
    natural: bool
    bureaucratic_phrase_detected: bool
    provider_call_allowed: bool
    network_access_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    policy_id: str = ""

    def __post_init__(self) -> None:
        status = VoicePolicyStatus(self.status)
        action = VoicePolicyAction(self.action)
        original = self.original_text.strip()
        response = self.response_text.strip()
        rationale = tuple(self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("voice policy timestamp must be timezone-aware")
        if not rationale or any(not item.strip() for item in rationale):
            raise ValueError("voice policy rationale must not be empty")
        if any(
            (
                self.provider_call_allowed,
                self.network_access_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M165 cannot authorize external side effects")
        if status is VoicePolicyStatus.APPLIED:
            if not original or not response:
                raise ValueError("applied voice policy requires response text")
            if action is not VoicePolicyAction.DELIVER or not self.natural:
                raise ValueError("applied voice policy must be natural and deliverable")
        elif response:
            raise ValueError("inactive voice policy cannot expose response text")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "original_text", original)
        object.__setattr__(self, "response_text", response)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.policy_id and self.policy_id != expected:
            raise ValueError("voice policy id is inconsistent")
        object.__setattr__(self, "policy_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.greeting_result.greeting_id,
                self.status.value,
                self.action.value,
                self.original_text,
                self.response_text,
                str(self.normalized),
                str(self.bureaucratic_phrase_detected),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class ROBYVoiceStyleRepository(Protocol):
    def add(self, result: ROBYVoiceStyleResult) -> None: ...

    def get(self, policy_id: str) -> ROBYVoiceStyleResult | None: ...

    def list_all(self) -> tuple[ROBYVoiceStyleResult, ...]: ...


class InMemoryROBYVoiceStyleRepository:
    def __init__(self) -> None:
        self._items: dict[str, ROBYVoiceStyleResult] = {}

    def add(self, result: ROBYVoiceStyleResult) -> None:
        if result.policy_id in self._items:
            raise ValueError("voice policy result already exists")
        self._items[result.policy_id] = result

    def get(self, policy_id: str) -> ROBYVoiceStyleResult | None:
        return self._items.get(policy_id)

    def list_all(self) -> tuple[ROBYVoiceStyleResult, ...]:
        return tuple(self._items.values())


def greeting_allows_style(result: NaturalGreetingResult) -> bool:
    return (
        result.status is NaturalGreetingStatus.GENERATED
        and bool(result.response_text)
        and result.natural
    )
