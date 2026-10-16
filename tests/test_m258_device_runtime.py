from datetime import datetime, timezone

import pytest

from app.device_runtime import OfficialDeviceRuntimeGateway
from app.runtime_root_factory import build_runtime_root
from core.device_capabilities import CapabilityMatchStatus
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

NOW = datetime(2026, 7, 15, 20, 0, tzinfo=timezone.utc)


def request(text: str):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="m258", text=text
    )


def test_registers_device_and_declares_capabilities_without_hardware_access():
    runtime = OfficialDeviceRuntimeGateway()
    device = runtime.register_device(
        owner="Carlos",
        device_id="desktop-1",
        label="Desktop",
        kind="desktop",
        capabilities=("camera.capture", "speaker.output"),
        now=NOW,
    )
    assert device.device_id == "desktop-1"
    assert runtime.snapshot.registered_devices == 1
    assert runtime.snapshot.registered_capabilities == 2


def test_sensitive_capability_requires_review_by_default():
    runtime = OfficialDeviceRuntimeGateway()
    runtime.register_device(
        owner="Carlos",
        device_id="desktop-1",
        label="Desktop",
        kind="desktop",
        capabilities=("camera.capture",),
        now=NOW,
    )
    match = runtime.evaluate(
        owner="Carlos",
        device_id="desktop-1",
        required_capabilities=("camera.capture",),
        now=NOW,
    )
    assert match.status is CapabilityMatchStatus.REVIEW_REQUIRED


def test_owner_isolation_is_enforced():
    runtime = OfficialDeviceRuntimeGateway()
    runtime.register_device(
        owner="Carlos",
        device_id="desktop-1",
        label="Desktop",
        kind="desktop",
        capabilities=("speaker.output",),
        now=NOW,
    )
    with pytest.raises(ValueError, match="owner"):
        runtime.evaluate(
            owner="Other", device_id="desktop-1", required_capabilities=(), now=NOW
        )


def test_runtime_audit_is_explicit_and_non_operational():
    runtime = OfficialDeviceRuntimeGateway()
    result = runtime.intercept(request("Auditá runtime de dispositivos"), now=NOW)
    assert result is not None
    assert "Acceso físico a hardware: no ejecutado" in result.response_text
    assert "Sensores, red y automatización: no ejecutados" in result.response_text


def test_runtime_root_registers_same_official_device_gateway(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    registration = next(
        item
        for item in registry.registrations
        if item.descriptor.name == "device.runtime"
    )
    assert registration.interceptor is root.dependencies.device_runtime
