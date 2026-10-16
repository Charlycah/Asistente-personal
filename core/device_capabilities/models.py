from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.device_continuity import DeviceIdentity


class DeviceCapabilityKind(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    SENSOR = "sensor"
    COMPUTE = "compute"
    CONNECTIVITY = "connectivity"
    CONTEXT = "context"


class DeviceCapabilityState(str, Enum):
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class DeviceCapabilityAccess(str, Enum):
    ALLOWED = "allowed"
    CONSENT_REQUIRED = "consent_required"
    DENIED = "denied"


class CapabilityMatchStatus(str, Enum):
    SATISFIED = "satisfied"
    REVIEW_REQUIRED = "review_required"
    UNSATISFIED = "unsatisfied"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class DeviceCapabilityDescriptor:
    name: str
    kind: DeviceCapabilityKind | str
    version: str = "1"
    features: tuple[str, ...] = ()
    sensitive: bool = False

    def __post_init__(self) -> None:
        name = self.name.strip().casefold()
        version = self.version.strip()
        features = tuple(item.strip().casefold() for item in self.features)
        if not name or not version:
            raise ValueError("capability name and version must not be blank")
        if any(not item for item in features) or len(features) != len(set(features)):
            raise ValueError("capability features must be non-blank and unique")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "kind", DeviceCapabilityKind(self.kind))
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "features", features)


@dataclass(frozen=True)
class RegisteredDeviceCapability:
    device: DeviceIdentity
    descriptor: DeviceCapabilityDescriptor
    state: DeviceCapabilityState | str
    access: DeviceCapabilityAccess | str
    observed_at: datetime
    confidence: float = 1.0
    registration_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "state", DeviceCapabilityState(self.state))
        object.__setattr__(self, "access", DeviceCapabilityAccess(self.access))
        if self.observed_at.tzinfo is None:
            raise ValueError("capability observation timestamp must be aware")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("capability confidence must be between zero and one")
        expected = sha256(
            "|".join(
                (
                    self.device.device_id,
                    self.descriptor.name,
                    self.descriptor.version,
                    self.state.value,
                    self.access.value,
                    self.observed_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.registration_id and self.registration_id != expected:
            raise ValueError("capability registration id is inconsistent")
        object.__setattr__(self, "registration_id", expected)


@dataclass(frozen=True)
class DeviceCapabilityRequirement:
    name: str
    minimum_version: str | None = None
    required_features: tuple[str, ...] = ()
    allow_degraded: bool = False
    require_access: bool = True

    def __post_init__(self) -> None:
        name = self.name.strip().casefold()
        features = tuple(item.strip().casefold() for item in self.required_features)
        version = self.minimum_version.strip() if self.minimum_version else None
        if not name or (self.minimum_version is not None and not version):
            raise ValueError("capability requirement fields must not be blank")
        if any(not item for item in features) or len(features) != len(set(features)):
            raise ValueError("required features must be non-blank and unique")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "minimum_version", version)
        object.__setattr__(self, "required_features", features)


@dataclass(frozen=True)
class DeviceCapabilityRegistryPolicy:
    max_observation_age_seconds: float = 300.0
    minimum_confidence: float = 0.7
    allow_consent_required: bool = False

    def __post_init__(self) -> None:
        if self.max_observation_age_seconds <= 0:
            raise ValueError("maximum observation age must be positive")
        if not 0.0 <= self.minimum_confidence <= 1.0:
            raise ValueError("minimum confidence must be between zero and one")


@dataclass(frozen=True)
class DeviceCapabilityMatch:
    device: DeviceIdentity
    requirements: tuple[DeviceCapabilityRequirement, ...]
    matched_registration_ids: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    review_capabilities: tuple[str, ...]
    status: CapabilityMatchStatus | str
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    match_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", CapabilityMatchStatus(self.status))
        if self.created_at.tzinfo is None:
            raise ValueError("capability match timestamp must be aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("capability match rationale must not be empty")
        expected = sha256(
            "|".join(
                (
                    self.device.device_id,
                    self.status.value,
                    ";".join(item.name for item in self.requirements),
                    ";".join(self.matched_registration_ids),
                    ";".join(self.missing_capabilities),
                    ";".join(self.review_capabilities),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.match_id and self.match_id != expected:
            raise ValueError("capability match id is inconsistent")
        object.__setattr__(self, "match_id", expected)


@runtime_checkable
class DeviceCapabilityRegistryRepository(Protocol):
    def add(self, item: RegisteredDeviceCapability) -> None: ...
    def get(self, registration_id: str) -> RegisteredDeviceCapability | None: ...
    def list_for_device(
        self, device_id: str
    ) -> tuple[RegisteredDeviceCapability, ...]: ...
    def list_all(self) -> tuple[RegisteredDeviceCapability, ...]: ...


class InMemoryDeviceCapabilityRegistryRepository:
    def __init__(self) -> None:
        self._items: dict[str, RegisteredDeviceCapability] = {}

    def add(self, item: RegisteredDeviceCapability) -> None:
        if item.registration_id in self._items:
            raise ValueError("device capability registration already exists")
        self._items[item.registration_id] = item

    def get(self, registration_id: str) -> RegisteredDeviceCapability | None:
        return self._items.get(registration_id)

    def list_for_device(self, device_id: str) -> tuple[RegisteredDeviceCapability, ...]:
        return tuple(
            item for item in self._items.values() if item.device.device_id == device_id
        )

    def list_all(self) -> tuple[RegisteredDeviceCapability, ...]:
        return tuple(self._items.values())
