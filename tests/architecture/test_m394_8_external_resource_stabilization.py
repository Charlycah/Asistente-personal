from __future__ import annotations

from pathlib import Path

from core.external_resource_registry import (
    ExternalResourceAuthorizationState,
    ExternalResourceConnectivityState,
    ExternalResourceRecoveryStatus,
    ExternalResourceRegistration,
    ExternalResourceRegistryAuthority,
    ExternalResourceRegistryState,
)

ROOT = Path(__file__).resolve().parents[2]


def _authority() -> ExternalResourceRegistryAuthority:
    authority = ExternalResourceRegistryAuthority()
    authority.register(
        ExternalResourceRegistration(
            resource_id="camera-living",
            label="Cámara living",
            kind="camera",
            source_authority="official_device_gateway",
            capabilities=("video",),
        )
    )
    return authority


def test_m394_8_end_to_end_contract_is_coherent() -> None:
    authority = _authority()
    authority.declare_state("camera-living", "available")
    authority.authorize(
        "camera-living",
        source="owner",
        authorized_by="owner",
        authorized_at="2026-08-08T14:40:00-03:00",
        reason="explicit test authorization",
    )
    authority.declare_connectivity(
        "camera-living",
        state="configured",
        transport_type="ip",
        endpoint_reference="local://camera-living",
        source="owner",
        declared_at="2026-08-08T14:41:00-03:00",
    )
    event = authority.record_audit_event(
        "camera-living",
        event_type="stabilization",
        new_value="coherent",
        declared_by="owner",
        declared_at="2026-08-08T14:42:00-03:00",
    )
    recovered = authority.recover_resource_snapshot("camera-living")

    resource = authority.get("camera-living")
    assert resource is not None
    assert resource.state is ExternalResourceRegistryState.AVAILABLE
    assert (
        authority.authorization_state("camera-living")
        is ExternalResourceAuthorizationState.AUTHORIZED
    )
    assert (
        authority.connectivity_state("camera-living")
        is ExternalResourceConnectivityState.CONFIGURED
    )
    assert recovered.recovery_status is ExternalResourceRecoveryStatus.AUDITED
    assert recovered.latest_audit_id == event.audit_id
    assert authority.validate_recovery(recovered) is True


def test_m394_8_stabilized_reads_are_deterministic() -> None:
    authority = _authority()
    assert authority.snapshot() == authority.snapshot()
    first = authority.recover_resource_snapshot("camera-living")
    second = authority.recover_resource_snapshot("camera-living")
    assert first == second


def test_m394_8_stabilization_adds_no_new_public_api() -> None:
    expected = {
        "audit_history",
        "audit_revision",
        "authorization_history",
        "authorization_state",
        "authorize",
        "connection_profile",
        "connectivity_history",
        "connectivity_state",
        "declare_connectivity",
        "declare_state",
        "get",
        "latest_audit",
        "list_resources",
        "record_audit_event",
        "recover_resource_snapshot",
        "register",
        "resolve_identity",
        "revoke_authorization",
        "snapshot",
        "validate_recovery",
    }
    public_methods = {
        name
        for name, value in vars(ExternalResourceRegistryAuthority).items()
        if callable(value) and not name.startswith("_")
    }
    assert public_methods == expected


def test_m394_8_stabilization_keeps_external_operations_out_of_scope() -> None:
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")
    forbidden = (
        "import socket",
        "import requests",
        "import subprocess",
        "def connect(",
        "OfficialDeviceGateway(",
        "credentials.json",
        "RecoveryManager",
        "AuditManager",
    )
    assert all(token not in source for token in forbidden)


def test_m394_8_gateway_contract_remains_separate() -> None:
    gateway = (ROOT / "app/device_gateway.py").read_text(encoding="utf-8")
    assert "class OfficialDeviceGateway" in gateway
    assert "ExternalResourceRegistryAuthority" not in gateway


def test_m394_8_canonical_core_contract_remains_present_once() -> None:
    occurrences = 0
    for path in (ROOT / "app").rglob("*.py"):
        occurrences += path.read_text(encoding="utf-8").count("CanonicalCognitiveCore(")
    assert occurrences == 1


def test_m394_8_credentials_contract_is_preserved() -> None:
    registry_source = (ROOT / "core/external_resource_registry.py").read_text(
        encoding="utf-8"
    )

    assert "credentials.json" not in registry_source


def test_m394_8_series_documentation_is_synchronized() -> None:
    document = (ROOT / "docs/M394_8_EXTERNAL_RESOURCE_STABILIZATION.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    external = (ROOT / "external_capabilities.md").read_text(encoding="utf-8")
    decision = (ROOT / "integration_decision.md").read_text(encoding="utf-8")

    assert "M394.8" in document
    assert "serie M394" in document
    assert "## Milestone M394.8" in readme
    assert "## M394.8" in changelog
    assert "M394.8" in rules
    assert "M394.8" in external
    assert "M394.8" in decision
    assert readme.startswith("## Milestone M393.1")
