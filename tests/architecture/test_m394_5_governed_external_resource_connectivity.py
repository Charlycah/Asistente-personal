from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.external_resource_registry import (
    ExternalResourceAuthorizationState,
    ExternalResourceConnectivityDeclaration,
    ExternalResourceConnectivityState,
    ExternalResourceIdentity,
    ExternalResourceKind,
    ExternalResourceRegistration,
    ExternalResourceRegistryAuthority,
    ExternalResourceRegistryState,
)

ROOT = Path(__file__).resolve().parents[2]


def _registration() -> ExternalResourceRegistration:
    return ExternalResourceRegistration(
        resource_id="camera-living",
        label="Cámara living",
        kind=ExternalResourceKind.CAMERA,
        source_authority="official_device_gateway",
        identity=ExternalResourceIdentity("home.camera", "camera-living"),
    )


def _configure(
    authority: ExternalResourceRegistryAuthority,
) -> ExternalResourceRegistration:
    return authority.declare_connectivity(
        "camera-living",
        state="configured",
        transport_type="ip",
        endpoint_reference="local://camera-living",
        source="explicit_configuration",
        declared_at="2026-08-08T13:55:00-03:00",
    )


def test_m394_5_new_registration_starts_unknown_connectivity() -> None:
    registration = _registration()

    assert registration.connectivity_state is ExternalResourceConnectivityState.UNKNOWN
    assert registration.connectivity_history == ()


def test_m394_5_configured_connectivity_records_explicit_profile() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())

    updated = _configure(authority)
    profile = authority.connection_profile("camera-living")

    assert updated.connectivity_state is ExternalResourceConnectivityState.CONFIGURED
    assert authority.connectivity_state("camera-living") is updated.connectivity_state
    assert profile is updated.connectivity_history[-1]
    assert profile.transport_type == "ip"
    assert profile.endpoint_reference == "local://camera-living"
    assert profile.source == "explicit_configuration"
    assert profile.declared_at == "2026-08-08T13:55:00-03:00"
    assert profile.revision == 1


def test_m394_5_connectivity_does_not_change_other_dimensions() -> None:
    authority = ExternalResourceRegistryAuthority()
    original = authority.register(_registration())
    available = authority.declare_state(original.resource_id, "available")
    authorized = authority.authorize(
        original.resource_id,
        source="explicit_user_policy",
        authorized_by="owner",
        authorized_at="2026-08-08T13:54:00-03:00",
    )

    configured = _configure(authority)

    assert configured.identity == available.identity
    assert configured.state is ExternalResourceRegistryState.AVAILABLE
    assert (
        configured.authorization_state
        is ExternalResourceAuthorizationState.AUTHORIZED
    )
    assert configured.authorization_history == authorized.authorization_history


def test_m394_5_unavailable_connectivity_preserves_revision_history() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())
    configured = _configure(authority)

    unavailable = authority.declare_connectivity(
        "camera-living",
        state="unavailable",
        source="explicit_configuration",
        declared_at="2026-08-08T13:56:00-03:00",
    )

    assert configured.connectivity_state is ExternalResourceConnectivityState.CONFIGURED
    assert (
        unavailable.connectivity_state
        is ExternalResourceConnectivityState.UNAVAILABLE
    )
    assert tuple(item.revision for item in unavailable.connectivity_history) == (1, 2)
    assert authority.connection_profile("camera-living") is None
    assert (
        authority.connectivity_history("camera-living")
        == unavailable.connectivity_history
    )


def test_m394_5_connectivity_requires_registered_resource() -> None:
    authority = ExternalResourceRegistryAuthority()

    with pytest.raises(KeyError, match="not registered"):
        authority.connectivity_state("missing")
    with pytest.raises(KeyError, match="not registered"):
        authority.declare_connectivity(
            "missing",
            state="configured",
            transport_type="ip",
            endpoint_reference="local://missing",
            source="explicit_configuration",
            declared_at="2026-08-08T13:55:00-03:00",
        )


def test_m394_5_configured_connectivity_requires_profile_evidence() -> None:
    with pytest.raises(ValueError, match="transport type"):
        ExternalResourceConnectivityDeclaration(
            state="configured",
            transport_type="",
            endpoint_reference="local://camera-living",
            source="explicit_configuration",
            declared_at="2026-08-08T13:55:00-03:00",
        )
    with pytest.raises(ValueError, match="endpoint reference"):
        ExternalResourceConnectivityDeclaration(
            state="configured",
            transport_type="ip",
            endpoint_reference="",
            source="explicit_configuration",
            declared_at="2026-08-08T13:55:00-03:00",
        )


def test_m394_5_explicit_connectivity_cannot_be_unknown() -> None:
    with pytest.raises(ValueError, match="cannot be unknown"):
        ExternalResourceConnectivityDeclaration(
            state="unknown",
            transport_type="",
            endpoint_reference="",
            source="explicit_configuration",
            declared_at="2026-08-08T13:55:00-03:00",
        )


def test_m394_5_connectivity_declarations_are_immutable() -> None:
    declaration = ExternalResourceConnectivityDeclaration(
        state="configured",
        transport_type="ip",
        endpoint_reference="local://camera-living",
        source="explicit_configuration",
        declared_at="2026-08-08T13:55:00-03:00",
    )

    with pytest.raises(FrozenInstanceError):
        declaration.transport_type = "wifi"  # type: ignore[misc]


def test_m394_5_rejects_inconsistent_embedded_connectivity_history() -> None:
    declaration = ExternalResourceConnectivityDeclaration(
        state="configured",
        transport_type="ip",
        endpoint_reference="local://camera-living",
        source="explicit_configuration",
        declared_at="2026-08-08T13:55:00-03:00",
    )

    with pytest.raises(ValueError, match="match latest declaration"):
        ExternalResourceRegistration(
            resource_id="camera-living",
            label="Cámara living",
            kind="camera",
            source_authority="official_device_gateway",
            connectivity_state="unavailable",
            connectivity_history=(declaration,),
        )


def test_m394_5_same_authority_owns_connectivity_without_parallel_manager() -> None:
    public_methods = {
        name
        for name, value in vars(ExternalResourceRegistryAuthority).items()
        if callable(value) and not name.startswith("_")
    }

    assert public_methods == {
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
        "get",
        "list_resources",
        "register",
        "resolve_identity",
        "revoke_authorization",
        "snapshot",
    }
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")
    assert "ConnectivityManager" not in source
    assert "ConnectionManager" not in source


def test_m394_5_connectivity_performs_no_external_operations() -> None:
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")

    assert "import socket" not in source
    assert "import requests" not in source
    assert "import subprocess" not in source
    assert "OfficialDeviceGateway(" not in source
    assert "credentials.json" not in source
    assert "def connect(" not in source


def test_m394_5_preserves_gateway_and_canonical_core_contracts() -> None:
    gateway = (ROOT / "app/device_gateway.py").read_text(encoding="utf-8")
    assert "class OfficialDeviceGateway" in gateway
    assert "ExternalResourceRegistryAuthority" not in gateway

    occurrences = 0
    for path in (ROOT / "app").rglob("*.py"):
        occurrences += path.read_text(encoding="utf-8").count("CanonicalCognitiveCore(")
    assert occurrences >= 1


def test_m394_5_documentation_is_synchronized() -> None:
    document_path = ROOT / "docs/M394_5_GOVERNED_EXTERNAL_RESOURCE_CONNECTIVITY.md"
    document = document_path.read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    external = (ROOT / "external_capabilities.md").read_text(encoding="utf-8")
    decision = (ROOT / "integration_decision.md").read_text(encoding="utf-8")

    assert "M394.5" in document
    assert ".roby/credentials.json" in document
    assert "## Milestone M394.5" in readme
    assert "## M394.5" in changelog
    assert "M394.5" in rules
    assert "M394.5" in external
    assert "M394.5" in decision
