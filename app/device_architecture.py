from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class DeviceStatus(str, Enum):
    AVAILABLE = "disponible"
    UNAVAILABLE = "no disponible"
    DISABLED = "deshabilitado"
    ERROR = "error"


@dataclass(frozen=True)
class DeviceCapability:
    name: str
    description: str = ""
    readable: bool = True
    writable: bool = False


@dataclass(frozen=True)
class DeviceDescriptor:
    device_id: str
    name: str
    category: str
    status: DeviceStatus
    capabilities: tuple[DeviceCapability, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DeviceCommand:
    device_id: str
    capability: str
    action: str
    payload: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DeviceCommandResult:
    accepted: bool
    message: str
    data: dict[str, str] = field(default_factory=dict)


class DeviceAdapter(Protocol):
    def describe(self) -> DeviceDescriptor: ...

    def execute(self, command: DeviceCommand) -> DeviceCommandResult: ...


class SimulatedDeviceAdapter:
    """In-memory adapter for development and contract tests."""

    def __init__(
        self,
        descriptor: DeviceDescriptor,
        responses: dict[tuple[str, str], DeviceCommandResult] | None = None,
    ) -> None:
        self._descriptor = descriptor
        self._responses = responses or {}
        self.commands: list[DeviceCommand] = []

    def describe(self) -> DeviceDescriptor:
        return self._descriptor

    def execute(self, command: DeviceCommand) -> DeviceCommandResult:
        self.commands.append(command)
        key = (command.capability, command.action)
        return self._responses.get(
            key,
            DeviceCommandResult(
                accepted=True,
                message=(
                    f"Acción simulada '{command.action}' aceptada por "
                    f"{self._descriptor.name}."
                ),
            ),
        )


class DeviceRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, DeviceAdapter] = {}

    def register(self, adapter: DeviceAdapter) -> DeviceDescriptor:
        descriptor = adapter.describe()
        if not descriptor.device_id.strip():
            raise ValueError("El dispositivo necesita un identificador.")
        if descriptor.device_id in self._adapters:
            raise ValueError(
                f"Ya existe el dispositivo '{descriptor.device_id}'."
            )
        self._adapters[descriptor.device_id] = adapter
        return descriptor

    def unregister(self, device_id: str) -> bool:
        return self._adapters.pop(device_id, None) is not None

    def get(self, device_id: str) -> DeviceDescriptor | None:
        adapter = self._adapters.get(device_id)
        return adapter.describe() if adapter else None

    def list_devices(
        self,
        *,
        status: DeviceStatus | None = None,
        capability: str | None = None,
    ) -> tuple[DeviceDescriptor, ...]:
        devices = [adapter.describe() for adapter in self._adapters.values()]
        if status is not None:
            devices = [device for device in devices if device.status is status]
        if capability:
            target = capability.casefold()
            devices = [
                device
                for device in devices
                if any(
                    item.name.casefold() == target
                    for item in device.capabilities
                )
            ]
        return tuple(sorted(devices, key=lambda item: item.name.casefold()))

    def execute(self, command: DeviceCommand) -> DeviceCommandResult:
        adapter = self._adapters.get(command.device_id)
        if adapter is None:
            return DeviceCommandResult(
                accepted=False,
                message=f"No existe el dispositivo '{command.device_id}'.",
            )
        descriptor = adapter.describe()
        if descriptor.status is not DeviceStatus.AVAILABLE:
            return DeviceCommandResult(
                accepted=False,
                message=(
                    f"{descriptor.name} está {descriptor.status.value}; "
                    "no se ejecutó ninguna acción."
                ),
            )
        capability = next(
            (
                item
                for item in descriptor.capabilities
                if item.name.casefold() == command.capability.casefold()
            ),
            None,
        )
        if capability is None:
            return DeviceCommandResult(
                accepted=False,
                message=(
                    f"{descriptor.name} no declara la capacidad "
                    f"'{command.capability}'."
                ),
            )
        if command.action.casefold() not in {"leer", "consultar"}:
            if not capability.writable:
                return DeviceCommandResult(
                    accepted=False,
                    message=(
                        f"La capacidad '{capability.name}' es de solo lectura."
                    ),
                )
        return adapter.execute(command)


@dataclass(frozen=True)
class DeviceArchitectureResponse:
    handled: bool
    response: str


class DeviceArchitectureService:
    _LIST_PATTERNS = (
        r"\bdispositivos disponibles\b",
        r"\barquitectura de dispositivos\b",
        r"\blistar dispositivos\b",
    )

    def __init__(self, registry: DeviceRegistry | None = None) -> None:
        self.registry = registry or DeviceRegistry()

    def prepare(self, text: str) -> DeviceArchitectureResponse:
        normalized = " ".join(text.strip().casefold().split())
        if not any(re.search(pattern, normalized) for pattern in self._LIST_PATTERNS):
            return DeviceArchitectureResponse(False, "")
        devices = self.registry.list_devices()
        if not devices:
            return DeviceArchitectureResponse(
                True,
                (
                    "La arquitectura para dispositivos está disponible, "
                    "pero no hay dispositivos registrados. Los adaptadores "
                    "de hardware permanecen desactivados por defecto."
                ),
            )
        lines = ["Dispositivos registrados:"]
        for device in devices:
            capabilities = ", ".join(
                capability.name for capability in device.capabilities
            )
            lines.append(
                f"- {device.name} [{device.device_id}] · "
                f"{device.status.value} · {capabilities or 'sin capacidades'}"
            )
        lines.append(
            "ROBY solo usa capacidades declaradas por cada adaptador y no "
            "activa hardware automáticamente."
        )
        return DeviceArchitectureResponse(True, "\n".join(lines))
