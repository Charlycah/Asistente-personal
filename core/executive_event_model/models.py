from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, IntEnum
from types import MappingProxyType
from typing import Any, Mapping, TypeAlias
from uuid import uuid4

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | tuple["JsonValue", ...] | Mapping[str, "JsonValue"]


class EventKind(str, Enum):
    GENERIC_TEXT = "generic_text"
    BATTERY_LOW = "battery_low"
    REMINDER_DUE = "reminder_due"
    AMBIENT_OBSERVATION = "ambient_observation"
    VERIFIED_NEWS = "verified_news"
    IMPORTANT_EMAIL = "important_email"
    VISUAL_CAPTURE_RESULT = "visual_capture_result"


class EventSource(str, Enum):
    SYSTEM = "system"
    BATTERY = "battery"
    REMINDERS = "reminders"
    AMBIENT = "ambient"
    NEWS = "news"
    GMAIL = "gmail"
    VISION = "vision"


class EventPriority(IntEnum):
    BACKGROUND = 10
    LOW = 25
    NORMAL = 50
    HIGH = 75
    CRITICAL = 100


class PrivacyLevel(str, Enum):
    PUBLIC = "public"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class DeliveryRequirement(str, Enum):
    BEST_EFFORT = "best_effort"
    PRESENTATION_REQUIRED = "presentation_required"
    ACKNOWLEDGEMENT_REQUIRED = "acknowledgement_required"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _freeze_json(value: Any, *, path: str = "payload") -> JsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"{path} keys must be non-blank strings")
            frozen[key] = _freeze_json(item, path=f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_json(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        )
    value_type = type(value).__name__
    raise TypeError(
        f"{path} contains a non-JSON-compatible value: {value_type}"
    )


def _validate_optional_id(value: str | None, name: str) -> None:
    if value is not None and not value.strip():
        raise ValueError(f"{name} must not be blank")


@dataclass(frozen=True, kw_only=True)
class ExecutiveEvent:
    kind: EventKind | str
    source: EventSource | str
    priority: EventPriority | int = EventPriority.NORMAL
    privacy_level: PrivacyLevel | str = PrivacyLevel.PERSONAL
    delivery_requirement: DeliveryRequirement | str = DeliveryRequirement.BEST_EFFORT
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=utc_now)
    expires_at: datetime | None = None
    entity_id: str | None = None
    correlation_id: str | None = None
    conversation_reference: str | None = None
    payload: Mapping[str, JsonValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", EventKind(self.kind))
        object.__setattr__(self, "source", EventSource(self.source))
        object.__setattr__(self, "priority", EventPriority(self.priority))
        object.__setattr__(self, "privacy_level", PrivacyLevel(self.privacy_level))
        object.__setattr__(
            self,
            "delivery_requirement",
            DeliveryRequirement(self.delivery_requirement),
        )
        if not self.event_id.strip():
            raise ValueError("event_id must not be blank")
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")
        if self.expires_at is not None:
            if self.expires_at.tzinfo is None:
                raise ValueError("expires_at must be timezone-aware")
            if self.expires_at <= self.occurred_at:
                raise ValueError("expires_at must be after occurred_at")
        _validate_optional_id(self.entity_id, "entity_id")
        _validate_optional_id(self.correlation_id, "correlation_id")
        _validate_optional_id(
            self.conversation_reference,
            "conversation_reference",
        )
        frozen_payload = _freeze_json(self.payload)
        if not isinstance(frozen_payload, Mapping):
            raise TypeError("payload must be a mapping")
        object.__setattr__(self, "payload", frozen_payload)

    def is_expired(self, at: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        reference = at or utc_now()
        if reference.tzinfo is None:
            raise ValueError("expiry reference must be timezone-aware")
        return reference >= self.expires_at


@dataclass(frozen=True, kw_only=True)
class GenericTextEvent(ExecutiveEvent):
    kind: EventKind = field(default=EventKind.GENERIC_TEXT, init=False)
    source: EventSource | str = EventSource.SYSTEM
    text: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.text.strip():
            raise ValueError("text must not be blank")


@dataclass(frozen=True, kw_only=True)
class BatteryLowEvent(ExecutiveEvent):
    kind: EventKind = field(default=EventKind.BATTERY_LOW, init=False)
    source: EventSource = field(default=EventSource.BATTERY, init=False)
    battery_percent: int
    charging: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        if not 0 <= self.battery_percent <= 100:
            raise ValueError("battery_percent must be between 0 and 100")


@dataclass(frozen=True, kw_only=True)
class ReminderDueEvent(ExecutiveEvent):
    kind: EventKind = field(default=EventKind.REMINDER_DUE, init=False)
    source: EventSource = field(default=EventSource.REMINDERS, init=False)
    reminder_id: str
    title: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.reminder_id.strip() or not self.title.strip():
            raise ValueError("reminder identity and title must not be blank")


@dataclass(frozen=True, kw_only=True)
class AmbientObservationEvent(ExecutiveEvent):
    kind: EventKind = field(default=EventKind.AMBIENT_OBSERVATION, init=False)
    source: EventSource = field(default=EventSource.AMBIENT, init=False)
    observation: str
    confidence: float | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.observation.strip():
            raise ValueError("observation must not be blank")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True, kw_only=True)
class VerifiedNewsEvent(ExecutiveEvent):
    kind: EventKind = field(default=EventKind.VERIFIED_NEWS, init=False)
    source: EventSource = field(default=EventSource.NEWS, init=False)
    headline: str
    publisher: str
    url: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.headline.strip() or not self.publisher.strip():
            raise ValueError("news headline and publisher must not be blank")
        _validate_optional_id(self.url, "url")


@dataclass(frozen=True, kw_only=True)
class ImportantEmailEvent(ExecutiveEvent):
    kind: EventKind = field(default=EventKind.IMPORTANT_EMAIL, init=False)
    source: EventSource = field(default=EventSource.GMAIL, init=False)
    message_reference: str
    subject: str
    sender: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.message_reference.strip():
            raise ValueError("message_reference must not be blank")
        if not self.subject.strip() or not self.sender.strip():
            raise ValueError("email subject and sender must not be blank")


@dataclass(frozen=True, kw_only=True)
class VisualCaptureResultEvent(ExecutiveEvent):
    kind: EventKind = field(default=EventKind.VISUAL_CAPTURE_RESULT, init=False)
    source: EventSource = field(default=EventSource.VISION, init=False)
    description: str
    capture_reference: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.description.strip():
            raise ValueError("description must not be blank")
        _validate_optional_id(self.capture_reference, "capture_reference")
