from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from core.device_capabilities import (
    DeviceCapabilityAccess,
    DeviceCapabilityDescriptor,
    DeviceCapabilityKind,
    DeviceCapabilityRegistry,
    DeviceCapabilityRequirement,
    DeviceCapabilityState,
    RegisteredDeviceCapability,
)
from core.device_continuity import DeviceIdentity, DeviceKind, DeviceTrustLevel
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class DeviceRuntimeSnapshot:
    owner: str
    registered_devices: int
    registered_capabilities: int
    last_device_id: str | None
    last_evaluation_status: str | None


class OfficialDeviceRuntimeGateway:
    """Official declarative device runtime; it never accesses physical hardware."""

    _STATUS_TRIGGERS = (
        "estado del runtime de dispositivos",
        "estado de dispositivos",
        "estado del device runtime",
    )
    _AUDIT_TRIGGERS = (
        "auditá runtime de dispositivos",
        "audita runtime de dispositivos",
        "evaluá runtime de dispositivos",
        "evalua runtime de dispositivos",
    )

    def __init__(self) -> None:
        self._registry = DeviceCapabilityRegistry()
        self._devices: dict[str, DeviceIdentity] = {}
        self._last_status: str | None = None
        self._last_device_id: str | None = None

    @property
    def snapshot(self) -> DeviceRuntimeSnapshot:
        capabilities = self._registry.repository.list_all()
        owners = {device.owner for device in self._devices.values()}
        owner = (
            next(iter(owners)) if len(owners) == 1 else "multiple" if owners else "none"
        )
        return DeviceRuntimeSnapshot(
            owner=owner,
            registered_devices=len(self._devices),
            registered_capabilities=len(capabilities),
            last_device_id=self._last_device_id,
            last_evaluation_status=self._last_status,
        )

    def register_device(
        self,
        *,
        owner: str,
        device_id: str,
        label: str,
        kind: DeviceKind | str,
        capabilities: tuple[str, ...],
        trust_level: DeviceTrustLevel | str = DeviceTrustLevel.RECOGNIZED,
        now: datetime | None = None,
    ) -> DeviceIdentity:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("device runtime timestamp must be timezone-aware")
        identity = DeviceIdentity(
            device_id=device_id,
            owner=owner,
            kind=kind,
            label=label,
            trust_level=trust_level,
            capabilities=capabilities,
            registered_at=timestamp,
        )
        if identity.device_id in self._devices:
            raise ValueError("device is already registered")
        self._devices[identity.device_id] = identity
        for name in identity.capabilities:
            self._registry.register(
                RegisteredDeviceCapability(
                    device=identity,
                    descriptor=DeviceCapabilityDescriptor(
                        name=name,
                        kind=self._kind_for(name),
                    ),
                    state=DeviceCapabilityState.AVAILABLE,
                    access=DeviceCapabilityAccess.CONSENT_REQUIRED,
                    observed_at=timestamp,
                )
            )
        self._last_device_id = identity.device_id
        return identity

    def evaluate(
        self,
        *,
        owner: str,
        device_id: str,
        required_capabilities: tuple[str, ...],
        now: datetime | None = None,
    ):
        device = self._devices.get(device_id)
        if device is None:
            raise ValueError("device is not registered")
        if device.owner.casefold() != owner.casefold():
            raise ValueError("device owner is inconsistent")
        match = self._registry.evaluate(
            device_id,
            tuple(
                DeviceCapabilityRequirement(name=name) for name in required_capabilities
            ),
            now=now,
        )
        self._last_device_id = device_id
        self._last_status = match.status.value
        return match

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        del now
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._status_response(),
                rationale="official_device_runtime_status_completed",
            )
        if not any(trigger in normalized for trigger in self._AUDIT_TRIGGERS):
            return None
        snapshot = self.snapshot
        return GovernedOperationalInterception(
            response_text="\n".join(
                (
                    "Auditoría del Device Runtime:",
                    f"- Dispositivos registrados: {snapshot.registered_devices}",
                    f"- Capacidades declaradas: {snapshot.registered_capabilities}",
                    "- Acceso físico a hardware: no ejecutado.",
                    "- Sensores, red y automatización: no ejecutados.",
                    "- Toda capacidad sensible requiere consentimiento explícito.",
                )
            ),
            rationale="official_device_runtime_audit_completed",
        )

    def _status_response(self) -> str:
        snapshot = self.snapshot
        return "\n".join(
            (
                "Estado del Device Runtime:",
                f"- Dispositivos registrados: {snapshot.registered_devices}",
                f"- Capacidades declaradas: {snapshot.registered_capabilities}",
                f"- Último dispositivo: {snapshot.last_device_id or 'ninguno'}",
                f"- Última evaluación: {snapshot.last_evaluation_status or 'ninguna'}",
                "- Modo: declarativo, gobernado y sin acceso directo al hardware.",
            )
        )

    @staticmethod
    def _kind_for(name: str) -> DeviceCapabilityKind:
        normalized = name.casefold()
        if any(term in normalized for term in ("camera", "sensor", "gps")):
            return DeviceCapabilityKind.SENSOR
        if any(term in normalized for term in ("microphone", "keyboard", "input")):
            return DeviceCapabilityKind.INPUT
        if any(term in normalized for term in ("speaker", "screen", "output")):
            return DeviceCapabilityKind.OUTPUT
        if any(term in normalized for term in ("network", "bluetooth", "wifi")):
            return DeviceCapabilityKind.CONNECTIVITY
        return DeviceCapabilityKind.COMPUTE
