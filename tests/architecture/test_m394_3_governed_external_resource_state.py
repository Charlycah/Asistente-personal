from __future__ import annotations

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


def _registration(resource_id: str = "camera-living") -> ExternalResourceRegistration:
    return ExternalResourceRegistration(
        resource_id=resource_id,
        label="Cámara living",
        kind=ExternalResourceKind.CAMERA,
        source_authority="official_device_gateway",
        identity=ExternalResourceIdentity("home.camera", resource_id),
    )


def test_m394_3_registration_still_starts_known() -> None:
    registration = _registration()

    assert registration.state is ExternalResourceRegistryState.KNOWN


def test_m394_3_same_authority_declares_available_state() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())

    updated = authority.declare_state("camera-living", "available")

    assert updated.state is ExternalResourceRegistryState.AVAILABLE
    assert authority.get("camera-living") is updated
    assert authority.resolve_identity(
        ExternalResourceIdentity("HOME.CAMERA", "camera-living")
    ) is updated


def test_m394_3_same_authority_declares_unavailable_state() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())

    updated = authority.declare_state(
        "camera-living", ExternalResourceRegistryState.UNAVAILABLE
    )

    assert updated.state is ExternalResourceRegistryState.UNAVAILABLE
    assert authority.snapshot().resources == (updated,)


def test_m394_3_state_declaration_is_idempotent() -> None:
    authority = ExternalResourceRegistryAuthority()
    registration = authority.register(_registration())

    assert authority.declare_state("camera-living", "known") is registration


def test_m394_3_state_requires_registered_resource() -> None:
    authority = ExternalResourceRegistryAuthority()

    with pytest.raises(KeyError, match="not registered"):
        authority.declare_state("missing", "available")


def test_m394_3_rejects_states_reserved_for_later_increments() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())

    for state in ("connected", "authorized", "active"):
        with pytest.raises(ValueError):
            authority.declare_state("camera-living", state)


def test_m394_3_state_does_not_perform_external_operations() -> None:
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")

    assert "socket" not in source
    assert "requests" not in source
    assert "subprocess" not in source
    assert "OfficialDeviceGateway(" not in source


def test_m394_3_same_authority_owns_registration_identity_and_state() -> None:
    public_methods = {
        name
        for name, value in vars(ExternalResourceRegistryAuthority).items()
        if callable(value) and not name.startswith("_")
    }

    required_m394_3_methods = {
        "declare_state",
        "get",
        "list_resources",
        "register",
        "resolve_identity",
        "snapshot",
    }

    assert required_m394_3_methods <= public_methods
    assert public_methods - required_m394_3_methods <= {
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
        "revoke_authorization",
    }


def test_m394_3_preserves_existing_device_gateway_authority() -> None:
    source = (ROOT / "app/device_gateway.py").read_text(encoding="utf-8")

    assert "class OfficialDeviceGateway" in source
    assert "ExternalResourceRegistryAuthority" not in source


def test_m394_3_canonical_core_contract_remains_present() -> None:
    occurrences = 0
    for path in (ROOT / "app").rglob("*.py"):
        occurrences += path.read_text(encoding="utf-8").count("CanonicalCognitiveCore(")

    assert occurrences >= 1


def test_m394_3_credentials_file_remains_outside_increment_contract() -> None:
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")
    document = (ROOT / "docs/M394_3_GOVERNED_EXTERNAL_RESOURCE_STATE.md").read_text(
        encoding="utf-8"
    )

    assert "credentials.json" not in source
    assert ".roby/credentials.json" in document


def test_m394_3_documentation_is_synchronized() -> None:
    document = (ROOT / "docs/M394_3_GOVERNED_EXTERNAL_RESOURCE_STATE.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    external = (ROOT / "external_capabilities.md").read_text(encoding="utf-8")
    decision = (ROOT / "integration_decision.md").read_text(encoding="utf-8")

    assert "M394.3" in document
    assert "## Milestone M394.3" in readme
    assert "## M394.3" in changelog
    assert "M394.3" in rules
    assert "M394.3" in external
    assert "M394.3" in decision
