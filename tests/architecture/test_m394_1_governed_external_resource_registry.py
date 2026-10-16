from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.external_resource_registry import (
    ExternalResourceKind,
    ExternalResourceRegistration,
    ExternalResourceRegistryAuthority,
    ExternalResourceRegistryState,
)

ROOT = Path(__file__).resolve().parents[2]


def _registration(
    *, resource_id: str = "camera-living", label: str = "Cámara living"
) -> ExternalResourceRegistration:
    return ExternalResourceRegistration(
        resource_id=resource_id,
        label=label,
        kind=ExternalResourceKind.CAMERA,
        source_authority="official_device_gateway",
        external_ref="device:camera-living",
        capabilities=("video.snapshot",),
        metadata={"zone": "living"},
    )


def test_m394_1_registration_means_known_only() -> None:
    registration = _registration()

    assert registration.state is ExternalResourceRegistryState.KNOWN
    assert not hasattr(registration, "available")
    assert not hasattr(registration, "connected")
    assert not hasattr(registration, "authorized")
    assert not hasattr(registration, "active")


def test_m394_1_registry_is_single_authority_for_resource_registration() -> None:
    authority = ExternalResourceRegistryAuthority()
    registration = authority.register(_registration())

    assert authority.authority_id == "external_resource_registry"
    assert authority.get("camera-living") is registration
    assert authority.snapshot().authority_id == authority.authority_id


def test_m394_1_registry_is_deterministic() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration(resource_id="sensor-2", label="Sensor terraza"))
    authority.register(_registration(resource_id="camera-1", label="Cámara living"))

    first = authority.snapshot()
    second = authority.snapshot()

    assert first == second
    assert tuple(item.resource_id for item in first.resources) == (
        "camera-1",
        "sensor-2",
    )


def test_m394_1_registration_is_immutable_including_metadata() -> None:
    registration = _registration()

    with pytest.raises(FrozenInstanceError):
        registration.label = "otra"  # type: ignore[misc]
    with pytest.raises(TypeError):
        registration.metadata["zone"] = "otra"  # type: ignore[index]


def test_m394_1_rejects_duplicate_resource_identity() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())

    with pytest.raises(ValueError, match="already registered"):
        authority.register(_registration(label="Misma identidad"))


def test_m394_1_rejects_implicit_operational_state() -> None:
    with pytest.raises(ValueError):
        ExternalResourceRegistration(
            resource_id="camera-living",
            label="Cámara living",
            kind="camera",
            source_authority="official_device_gateway",
            state="connected",
        )


def test_m394_1_registry_has_no_discovery_connection_or_execution_api() -> None:
    authority = ExternalResourceRegistryAuthority()

    forbidden = {
        "discover",
        "connect",
        "activate",
        "execute",
        "scan",
        "poll",
    }
    assert forbidden.isdisjoint(vars(type(authority)))


def test_m394_1_preserves_existing_device_gateway_authority() -> None:
    source = (ROOT / "app/device_gateway.py").read_text(encoding="utf-8")

    assert "class OfficialDeviceGateway" in source
    assert "ExternalResourceRegistryAuthority" not in source


def test_m394_1_canonical_core_contract_remains_present() -> None:
    occurrences = 0
    for path in (ROOT / "app").rglob("*.py"):
        occurrences += path.read_text(encoding="utf-8").count("CanonicalCognitiveCore(")

    assert occurrences >= 1


def test_m394_1_credentials_file_is_not_part_of_increment_contract() -> None:
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")
    document = (ROOT / "docs/M394_1_GOVERNED_EXTERNAL_RESOURCE_REGISTRY.md").read_text(
        encoding="utf-8"
    )

    assert "credentials.json" not in source
    assert ".roby/credentials.json" in document


def test_m394_1_documentation_is_synchronized() -> None:
    document = (ROOT / "docs/M394_1_GOVERNED_EXTERNAL_RESOURCE_REGISTRY.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    external = (ROOT / "external_capabilities.md").read_text(encoding="utf-8")
    decision = (ROOT / "integration_decision.md").read_text(encoding="utf-8")

    assert "M394.1" in document
    assert "## Milestone M394.1" in readme
    assert "## M394.1" in changelog
    assert "M394.1" in rules
    assert "M394.1" in external
    assert "M394.1" in decision
