from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.external_resource_registry import (
    ExternalResourceIdentity,
    ExternalResourceKind,
    ExternalResourceRegistration,
    ExternalResourceRegistryAuthority,
    ExternalResourceRegistryState,
)

ROOT = Path(__file__).resolve().parents[2]


def _registration(
    *,
    resource_id: str = "camera-living",
    namespace: str = "home.camera",
    local_id: str = "living-primary",
) -> ExternalResourceRegistration:
    return ExternalResourceRegistration(
        resource_id=resource_id,
        label="Cámara living",
        kind=ExternalResourceKind.CAMERA,
        source_authority="official_device_gateway",
        identity=ExternalResourceIdentity(namespace=namespace, local_id=local_id),
    )


def test_m394_2_identity_is_stable_and_independent_from_human_label() -> None:
    identity = ExternalResourceIdentity(
        namespace=" Home.Camera ",
        local_id=" living-primary ",
    )
    registration = ExternalResourceRegistration(
        resource_id="camera-living",
        label="Cámara principal del living",
        kind="camera",
        source_authority="official_device_gateway",
        identity=identity,
    )

    assert registration.identity.canonical_id == "home.camera:living-primary"
    assert registration.label == "Cámara principal del living"
    assert registration.state is ExternalResourceRegistryState.KNOWN


def test_m394_2_m394_1_registration_gets_backward_compatible_identity() -> None:
    registration = ExternalResourceRegistration(
        resource_id="legacy-resource",
        label="Recurso M394.1",
        kind="device",
        source_authority="official_device_gateway",
    )

    assert registration.identity == ExternalResourceIdentity(
        namespace="roby.external",
        local_id="legacy-resource",
    )


def test_m394_2_registry_resolves_governed_identity() -> None:
    authority = ExternalResourceRegistryAuthority()
    registration = authority.register(_registration())

    resolved = authority.resolve_identity(
        ExternalResourceIdentity("HOME.CAMERA", "living-primary")
    )

    assert resolved is registration


def test_m394_2_rejects_duplicate_canonical_identity() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration(resource_id="camera-a"))

    with pytest.raises(ValueError, match="identity is already registered"):
        authority.register(_registration(resource_id="camera-b"))


def test_m394_2_identity_is_immutable() -> None:
    identity = ExternalResourceIdentity("home.camera", "living-primary")

    with pytest.raises(FrozenInstanceError):
        identity.local_id = "changed"  # type: ignore[misc]


def test_m394_2_identity_rejects_blank_or_ambiguous_namespace() -> None:
    with pytest.raises(ValueError, match="namespace"):
        ExternalResourceIdentity("", "camera-1")
    with pytest.raises(ValueError, match="spaces"):
        ExternalResourceIdentity("home camera", "camera-1")
    with pytest.raises(ValueError, match="local id"):
        ExternalResourceIdentity("home.camera", "")


def test_m394_2_identity_does_not_add_operational_state() -> None:
    registration = _registration()

    assert registration.state is ExternalResourceRegistryState.KNOWN
    assert not hasattr(registration.identity, "available")
    assert not hasattr(registration.identity, "connected")
    assert not hasattr(registration.identity, "authorized")
    assert not hasattr(registration.identity, "active")


def test_m394_2_same_authority_owns_registration_and_identity_resolution() -> None:
    public_methods = {
        name
        for name, value in vars(ExternalResourceRegistryAuthority).items()
        if callable(value) and not name.startswith("_")
    }

    required_m394_2_methods = {
        "get",
        "list_resources",
        "register",
        "resolve_identity",
        "snapshot",
    }

    assert required_m394_2_methods <= public_methods
    assert public_methods - required_m394_2_methods <= {
        "audit_history",
        "audit_revision",
        "latest_audit",
        "record_audit_event",
        "recover_resource_snapshot",
        "validate_recovery",
        "authorization_history",
        "authorization_state",
        "authorize",
        "connection_profile",
        "connectivity_history",
        "connectivity_state",
        "declare_connectivity",
        "declare_state",
        "revoke_authorization",
    }


def test_m394_2_preserves_existing_device_gateway_authority() -> None:
    source = (ROOT / "app/device_gateway.py").read_text(encoding="utf-8")

    assert "class OfficialDeviceGateway" in source
    assert "ExternalResourceRegistryAuthority" not in source


def test_m394_2_canonical_core_contract_remains_present() -> None:
    occurrences = 0
    for path in (ROOT / "app").rglob("*.py"):
        occurrences += path.read_text(encoding="utf-8").count("CanonicalCognitiveCore(")

    assert occurrences >= 1


def test_m394_2_credentials_file_remains_outside_increment_contract() -> None:
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")
    document = (ROOT / "docs/M394_2_GOVERNED_EXTERNAL_RESOURCE_IDENTITY.md").read_text(
        encoding="utf-8"
    )

    assert "credentials.json" not in source
    assert ".roby/credentials.json" in document


def test_m394_2_documentation_is_synchronized() -> None:
    document = (ROOT / "docs/M394_2_GOVERNED_EXTERNAL_RESOURCE_IDENTITY.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    external = (ROOT / "external_capabilities.md").read_text(encoding="utf-8")
    decision = (ROOT / "integration_decision.md").read_text(encoding="utf-8")

    assert "M394.2" in document
    assert "## Milestone M394.2" in readme
    assert "## M394.2" in changelog
    assert "M394.2" in rules
    assert "M394.2" in external
    assert "M394.2" in decision
