from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.device_gateway import OfficialDeviceGateway
from core.device_capabilities import (
    DeviceCapabilityDescriptor,
    DeviceCapabilityKind,
)
from core.device_continuity import DeviceIdentity, DeviceKind
from core.device_foundation import (
    DeviceActionRequest,
    DeviceActionRisk,
    DeviceCategory,
    DeviceObservation,
    DeviceOperationalState,
    DeviceProfile,
    DeviceRegistration,
    DeviceTransport,
)


def _registration() -> DeviceRegistration:
    identity = DeviceIdentity(
        device_id="robot-vacuum-1",
        owner="hogar",
        kind=DeviceKind.AMBIENT,
        label="Aspiradora del living",
        capabilities=("battery", "clean_room", "return_to_base"),
        registered_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
    )
    profile = DeviceProfile(
        identity=identity,
        category=DeviceCategory.HOME_APPLIANCE,
        transports=(DeviceTransport.WIFI, DeviceTransport.LOCAL_API),
        manufacturer="Example",
        model="Vacuum 1",
    )
    capabilities = (
        DeviceCapabilityDescriptor("battery", DeviceCapabilityKind.SENSOR),
        DeviceCapabilityDescriptor("clean_room", DeviceCapabilityKind.OUTPUT),
        DeviceCapabilityDescriptor(
            "return_to_base",
            DeviceCapabilityKind.OUTPUT,
        ),
    )
    return DeviceRegistration(profile, capabilities)


def test_gateway_registers_transport_neutral_device_profiles() -> None:
    gateway = OfficialDeviceGateway()
    profile = gateway.register(_registration())
    assert profile.category is DeviceCategory.HOME_APPLIANCE
    assert profile.transports == (
        DeviceTransport.WIFI,
        DeviceTransport.LOCAL_API,
    )
    assert gateway.list_devices() == (profile,)


def test_registration_requires_capabilities_to_match_identity() -> None:
    registration = _registration()
    invalid = DeviceRegistration(
        registration.profile,
        registration.capabilities[:-1],
    )
    with pytest.raises(ValueError, match="must match device identity"):
        OfficialDeviceGateway().register(invalid)


def test_observation_must_use_declared_transport() -> None:
    gateway = OfficialDeviceGateway()
    gateway.register(_registration())
    with pytest.raises(ValueError, match="not declared"):
        gateway.observe(
            DeviceObservation(
                device_id="robot-vacuum-1",
                state=DeviceOperationalState.CONNECTED,
                active_transport=DeviceTransport.BLUETOOTH,
            )
        )


def test_gateway_records_uniform_device_diagnostics() -> None:
    gateway = OfficialDeviceGateway()
    gateway.register(_registration())
    observation = DeviceObservation(
        device_id="robot-vacuum-1",
        state=DeviceOperationalState.CHARGING,
        active_transport=DeviceTransport.WIFI,
        battery_percent=72,
        diagnostics=("dock_connected",),
    )
    gateway.observe(observation)
    assert gateway.latest_observation("robot-vacuum-1") == observation


def test_reversible_device_action_is_prepared_but_not_executed() -> None:
    gateway = OfficialDeviceGateway()
    gateway.register(_registration())
    plan = gateway.prepare_action(
        DeviceActionRequest(
            device_id="robot-vacuum-1",
            capability="clean_room",
            action="living",
            risk=DeviceActionRisk.REVERSIBLE,
            user_requested=True,
        )
    )
    assert plan.known_device is True
    assert plan.declared_capability is True
    assert plan.authorized is True
    assert plan.executable is False


def test_destructive_action_requires_consent_and_confirmation() -> None:
    gateway = OfficialDeviceGateway()
    gateway.register(_registration())
    request = DeviceActionRequest(
        device_id="robot-vacuum-1",
        capability="clean_room",
        action="reset_map",
        risk=DeviceActionRisk.DESTRUCTIVE,
        user_requested=True,
        explicit_user_consent=True,
        confirmation=False,
    )
    assert gateway.prepare_action(request).authorized is False


def test_m364_documentation_declares_single_gateway_and_no_execution() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M364_DEVICE_CAPABILITY_FOUNDATION.md").read_text(
        encoding="utf-8"
    )
    assert "OfficialDeviceGateway" in document
    assert "executable=False" in document
    assert "ToolGateway" in document
    assert "Bluetooth" in document
    assert "USB" in document
    assert "aspiradora robot" in document


def test_root_documents_preserve_m364_as_validated_predecessor() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "docs/M364_DEVICE_CAPABILITY_FOUNDATION.md" in readme
    assert "## M364 — Device Capability Foundation" in changelog
