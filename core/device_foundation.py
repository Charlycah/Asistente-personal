from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol, runtime_checkable

from core.device_capabilities import DeviceCapabilityDescriptor
from core.device_continuity import DeviceIdentity


class DeviceCategory(str, Enum):
    COMPUTER = "computer"
    MOBILE = "mobile"
    WEARABLE = "wearable"
    AUDIO = "audio"
    VIDEO = "video"
    PRINTER = "printer"
    HOME_APPLIANCE = "home_appliance"
    SENSOR = "sensor"
    CONTROLLER = "controller"
    UNKNOWN = "unknown"


class DeviceTransport(str, Enum):
    BLUETOOTH = "bluetooth"
    USB = "usb"
    WIFI = "wifi"
    LAN = "lan"
    CLOUD = "cloud"
    LOCAL_API = "local_api"
    SERIAL = "serial"
    VIRTUAL = "virtual"
    UNKNOWN = "unknown"


class DeviceOperationalState(str, Enum):
    AVAILABLE = "available"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    SLEEPING = "sleeping"
    BUSY = "busy"
    CHARGING = "charging"
    DEGRADED = "degraded"
    ERROR = "error"
    UNKNOWN = "unknown"


class DeviceActionRisk(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE = "reversible"
    SENSITIVE = "sensitive"
    DESTRUCTIVE = "destructive"


@dataclass(frozen=True)
class DeviceProfile:
    identity: DeviceIdentity
    category: DeviceCategory | str
    transports: tuple[DeviceTransport | str, ...]
    manufacturer: str = ""
    model: str = ""
    firmware_version: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        category = DeviceCategory(self.category)
        transports = tuple(DeviceTransport(item) for item in self.transports)
        if not transports:
            raise ValueError("device profile requires at least one transport")
        if len(transports) != len(set(transports)):
            raise ValueError("device transports must be unique")
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "transports", transports)
        object.__setattr__(self, "manufacturer", self.manufacturer.strip())
        object.__setattr__(self, "model", self.model.strip())
        object.__setattr__(self, "firmware_version", self.firmware_version.strip())


@dataclass(frozen=True)
class DeviceObservation:
    device_id: str
    state: DeviceOperationalState | str
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active_transport: DeviceTransport | str | None = None
    battery_percent: int | None = None
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.device_id.strip():
            raise ValueError("device observation requires a device id")
        if self.observed_at.tzinfo is None:
            raise ValueError("device observation timestamp must be aware")
        if self.battery_percent is not None and not 0 <= self.battery_percent <= 100:
            raise ValueError("battery percentage must be between zero and one hundred")
        if any(not item.strip() for item in self.diagnostics):
            raise ValueError("device diagnostics must not contain blank entries")
        object.__setattr__(self, "state", DeviceOperationalState(self.state))
        if self.active_transport is not None:
            object.__setattr__(
                self,
                "active_transport",
                DeviceTransport(self.active_transport),
            )


@dataclass(frozen=True)
class DeviceActionRequest:
    device_id: str
    capability: str
    action: str
    risk: DeviceActionRisk | str
    user_requested: bool
    explicit_user_consent: bool = False
    confirmation: bool = False
    parameters: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (self.device_id, self.capability, self.action)
        ):
            raise ValueError("device action fields must not be blank")
        object.__setattr__(self, "capability", self.capability.strip().casefold())
        object.__setattr__(self, "action", self.action.strip().casefold())
        object.__setattr__(self, "risk", DeviceActionRisk(self.risk))


@dataclass(frozen=True)
class DeviceActionPlan:
    request: DeviceActionRequest
    known_device: bool
    declared_capability: bool
    authorized: bool
    executable: bool
    rationale: tuple[str, ...]


@runtime_checkable
class DeviceProfileRepository(Protocol):
    def add(self, profile: DeviceProfile) -> None: ...
    def get(self, device_id: str) -> DeviceProfile | None: ...
    def list_all(self) -> tuple[DeviceProfile, ...]: ...


class InMemoryDeviceProfileRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, DeviceProfile] = {}

    def add(self, profile: DeviceProfile) -> None:
        device_id = profile.identity.device_id
        if device_id in self._profiles:
            raise ValueError("device profile already exists")
        self._profiles[device_id] = profile

    def get(self, device_id: str) -> DeviceProfile | None:
        return self._profiles.get(device_id)

    def list_all(self) -> tuple[DeviceProfile, ...]:
        return tuple(
            sorted(
                self._profiles.values(),
                key=lambda item: item.identity.label.casefold(),
            )
        )


@dataclass(frozen=True)
class DeviceRegistration:
    profile: DeviceProfile
    capabilities: tuple[DeviceCapabilityDescriptor, ...]
