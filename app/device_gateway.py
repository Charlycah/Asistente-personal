from __future__ import annotations

from core.device_foundation import (
    DeviceActionPlan,
    DeviceActionRequest,
    DeviceActionRisk,
    DeviceObservation,
    DeviceProfile,
    DeviceProfileRepository,
    DeviceRegistration,
    InMemoryDeviceProfileRepository,
)


class OfficialDeviceGateway:
    """Single governed boundary for describing devices and preparing actions."""

    def __init__(
        self,
        *,
        repository: DeviceProfileRepository | None = None,
    ) -> None:
        self.repository = repository or InMemoryDeviceProfileRepository()
        self._capabilities: dict[str, tuple[str, ...]] = {}
        self._observations: dict[str, DeviceObservation] = {}

    def register(self, registration: DeviceRegistration) -> DeviceProfile:
        device_id = registration.profile.identity.device_id
        declared = tuple(item.name for item in registration.capabilities)
        if set(declared) != set(registration.profile.identity.capabilities):
            raise ValueError(
                "registered capability descriptors must match device identity"
            )
        self.repository.add(registration.profile)
        self._capabilities[device_id] = declared
        return registration.profile

    def get(self, device_id: str) -> DeviceProfile | None:
        return self.repository.get(device_id)

    def list_devices(self) -> tuple[DeviceProfile, ...]:
        return self.repository.list_all()

    def observe(self, observation: DeviceObservation) -> None:
        profile = self.repository.get(observation.device_id)
        if profile is None:
            raise ValueError("cannot observe an unregistered device")
        if (
            observation.active_transport is not None
            and observation.active_transport not in profile.transports
        ):
            raise ValueError("active transport is not declared by the device")
        self._observations[observation.device_id] = observation

    def latest_observation(self, device_id: str) -> DeviceObservation | None:
        return self._observations.get(device_id)

    def prepare_action(self, request: DeviceActionRequest) -> DeviceActionPlan:
        profile = self.repository.get(request.device_id)
        known_device = profile is not None
        capabilities = self._capabilities.get(request.device_id, ())
        declared_capability = request.capability in capabilities
        authorized = known_device and declared_capability and request.user_requested
        rationale = [
            "known_device_required",
            "declared_capability_required",
            "explicit_user_request_required",
        ]
        if request.risk in {
            DeviceActionRisk.SENSITIVE,
            DeviceActionRisk.DESTRUCTIVE,
        }:
            authorized = authorized and request.explicit_user_consent
            rationale.append("explicit_consent_required")
        if request.risk is DeviceActionRisk.DESTRUCTIVE:
            authorized = authorized and request.confirmation
            rationale.append("confirmation_required")
        rationale.extend(
            (
                "m364_foundation_does_not_execute_device_actions",
                "future_execution_must_use_tool_gateway",
            )
        )
        return DeviceActionPlan(
            request=request,
            known_device=known_device,
            declared_capability=declared_capability,
            authorized=authorized,
            executable=False,
            rationale=tuple(rationale),
        )
