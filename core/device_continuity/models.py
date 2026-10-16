from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable


class DeviceKind(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    VEHICLE = "vehicle"
    AMBIENT = "ambient"
    UNKNOWN = "unknown"


class DeviceTrustLevel(str, Enum):
    UNTRUSTED = "untrusted"
    RECOGNIZED = "recognized"
    TRUSTED = "trusted"


class SessionContinuityStatus(str, Enum):
    READY = "ready"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class SessionContinuityAction(str, Enum):
    RESUME = "resume"
    CONFIRM = "confirm"
    STAY = "stay"
    NONE = "none"


@dataclass(frozen=True)
class DeviceIdentity:
    device_id: str
    owner: str
    kind: DeviceKind | str
    label: str
    trust_level: DeviceTrustLevel | str = DeviceTrustLevel.RECOGNIZED
    capabilities: tuple[str, ...] = ()
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", DeviceKind(self.kind))
        object.__setattr__(self, "trust_level", DeviceTrustLevel(self.trust_level))
        if (
            not self.device_id.strip()
            or not self.owner.strip()
            or not self.label.strip()
        ):
            raise ValueError("device identity fields must not be blank")
        normalized = tuple(item.strip().casefold() for item in self.capabilities)
        if any(not item for item in normalized):
            raise ValueError("device capabilities must not be blank")
        if len(normalized) != len(set(normalized)):
            raise ValueError("device capabilities must be unique")
        object.__setattr__(self, "capabilities", normalized)
        if self.registered_at.tzinfo is None:
            raise ValueError("device registration timestamp must be aware")


@dataclass(frozen=True)
class CompanionSession:
    session_id: str
    owner: str
    active_device_id: str
    conversation_reference_id: str
    revision: int = 1
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.session_id,
                self.owner,
                self.active_device_id,
                self.conversation_reference_id,
            )
        ):
            raise ValueError("companion session fields must not be blank")
        if self.revision < 1:
            raise ValueError("session revision must be positive")
        if self.started_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("session timestamps must be aware")
        if self.updated_at < self.started_at:
            raise ValueError("session update cannot precede its start")


@dataclass(frozen=True)
class DeviceSessionEndpoint:
    device: DeviceIdentity
    local_session_id: str
    observed_at: datetime
    available: bool = True
    authenticated: bool = True

    def __post_init__(self) -> None:
        if not self.local_session_id.strip():
            raise ValueError("local session id must not be blank")
        if self.observed_at.tzinfo is None:
            raise ValueError("endpoint observation timestamp must be aware")


@dataclass(frozen=True)
class SessionContinuityPolicy:
    require_trusted_target: bool = True
    require_authenticated_endpoints: bool = True
    max_observation_age_seconds: float = 300.0
    allow_same_device_resume: bool = False

    def __post_init__(self) -> None:
        if self.max_observation_age_seconds <= 0:
            raise ValueError("maximum observation age must be positive")


@dataclass(frozen=True)
class SessionContinuityRequest:
    owner: str
    session: CompanionSession
    source: DeviceSessionEndpoint
    target: DeviceSessionEndpoint
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("continuity owner must not be blank")
        if self.requested_at.tzinfo is None:
            raise ValueError("continuity request timestamp must be aware")


@dataclass(frozen=True)
class SessionContinuityDecision:
    request: SessionContinuityRequest
    status: SessionContinuityStatus | str
    action: SessionContinuityAction | str
    eligible_for_handoff: bool
    resume_cursor: str | None
    required_capabilities: tuple[str, ...]
    rationale: tuple[str, ...]
    created_at: datetime
    decision_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", SessionContinuityStatus(self.status))
        object.__setattr__(self, "action", SessionContinuityAction(self.action))
        if self.created_at.tzinfo is None:
            raise ValueError("continuity decision timestamp must be aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("continuity rationale must not be empty")
        if self.eligible_for_handoff != (self.status is SessionContinuityStatus.READY):
            raise ValueError("only ready decisions may be eligible for handoff")
        if self.eligible_for_handoff != (self.resume_cursor is not None):
            raise ValueError("handoff eligibility and resume cursor must agree")
        expected = sha256(
            "|".join(
                (
                    self.request.session.session_id,
                    self.request.source.device.device_id,
                    self.request.target.device.device_id,
                    self.status.value,
                    self.action.value,
                    self.resume_cursor or "",
                    ";".join(self.required_capabilities),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("continuity decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)


@runtime_checkable
class SessionContinuityRepository(Protocol):
    def add(self, decision: SessionContinuityDecision) -> None: ...
    def get(self, decision_id: str) -> SessionContinuityDecision | None: ...
    def list_all(self) -> tuple[SessionContinuityDecision, ...]: ...


class InMemorySessionContinuityRepository:
    def __init__(self) -> None:
        self._items: dict[str, SessionContinuityDecision] = {}

    def add(self, decision: SessionContinuityDecision) -> None:
        if decision.decision_id in self._items:
            raise ValueError("session continuity decision already exists")
        self._items[decision.decision_id] = decision

    def get(self, decision_id: str) -> SessionContinuityDecision | None:
        return self._items.get(decision_id)

    def list_all(self) -> tuple[SessionContinuityDecision, ...]:
        return tuple(self._items.values())
