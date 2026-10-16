from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.external_resource_registry import (
    ExternalResourceRecoverySnapshot,
    ExternalResourceRecoveryStatus,
    ExternalResourceRegistration,
    ExternalResourceRegistryAuthority,
)

ROOT = Path(__file__).resolve().parents[2]


def _registration() -> ExternalResourceRegistration:
    return ExternalResourceRegistration(
        resource_id="camera-living",
        label="Cámara living",
        kind="camera",
        source_authority="official_device_gateway",
        capabilities=("video",),
    )


def _authority_with_resource() -> ExternalResourceRegistryAuthority:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())
    return authority


def test_m394_7_recovery_is_registered_only_without_audit() -> None:
    authority = _authority_with_resource()

    recovered = authority.recover_resource_snapshot("camera-living")

    assert recovered.resource == authority.get("camera-living")
    assert recovered.recovery_status is ExternalResourceRecoveryStatus.REGISTERED_ONLY
    assert recovered.audit_revision == 0
    assert recovered.latest_audit_id == ""
    assert authority.validate_recovery(recovered) is True


def test_m394_7_recovery_carries_latest_audit_evidence() -> None:
    authority = _authority_with_resource()
    first = authority.record_audit_event(
        "camera-living",
        event_type="state",
        new_value="available",
        declared_by="owner",
        declared_at="2026-08-08T14:25:00-03:00",
    )
    second = authority.record_audit_event(
        "camera-living",
        event_type="authorization",
        new_value="authorized",
        declared_by="owner",
        declared_at="2026-08-08T14:26:00-03:00",
    )

    recovered = authority.recover_resource_snapshot("camera-living")

    assert recovered.recovery_status is ExternalResourceRecoveryStatus.AUDITED
    assert recovered.audit_revision == 2
    assert recovered.latest_audit_id == second.audit_id
    assert first.audit_id != recovered.latest_audit_id
    assert authority.validate_recovery(recovered) is True


def test_m394_7_recovery_is_read_only_and_idempotent() -> None:
    authority = _authority_with_resource()
    before = authority.snapshot()
    audit_before = authority.audit_history("camera-living")

    first = authority.recover_resource_snapshot("camera-living")
    second = authority.recover_resource_snapshot("camera-living")

    assert first == second
    assert authority.snapshot() == before
    assert authority.audit_history("camera-living") == audit_before


def test_m394_7_snapshot_becomes_stale_after_governed_change() -> None:
    authority = _authority_with_resource()
    recovered = authority.recover_resource_snapshot("camera-living")

    authority.declare_state("camera-living", "available")

    assert authority.validate_recovery(recovered) is False


def test_m394_7_snapshot_becomes_stale_after_new_audit_evidence() -> None:
    authority = _authority_with_resource()
    recovered = authority.recover_resource_snapshot("camera-living")

    authority.record_audit_event(
        "camera-living",
        event_type="state",
        new_value="known",
        declared_by="owner",
        declared_at="2026-08-08T14:27:00-03:00",
    )

    assert authority.validate_recovery(recovered) is False


def test_m394_7_recovery_snapshot_is_immutable() -> None:
    authority = _authority_with_resource()
    recovered = authority.recover_resource_snapshot("camera-living")

    with pytest.raises(FrozenInstanceError):
        recovered.audit_revision = 99  # type: ignore[misc]


def test_m394_7_recovery_requires_registered_resource() -> None:
    authority = ExternalResourceRegistryAuthority()

    with pytest.raises(KeyError, match="not registered"):
        authority.recover_resource_snapshot("missing")


def test_m394_7_recovery_snapshot_rejects_inconsistent_evidence() -> None:
    registration = _registration()

    with pytest.raises(ValueError, match="cannot reference an audit event"):
        ExternalResourceRecoverySnapshot(
            authority_id="external_resource_registry",
            resource=registration,
            recovery_status="registered_only",
            audit_revision=0,
            latest_audit_id="camera-living:audit:1",
        )
    with pytest.raises(ValueError, match="requires the latest audit id"):
        ExternalResourceRecoverySnapshot(
            authority_id="external_resource_registry",
            resource=registration,
            recovery_status="audited",
            audit_revision=1,
        )


def test_m394_7_same_authority_owns_recovery_without_parallel_manager() -> None:
    public_methods = {
        name
        for name, value in vars(ExternalResourceRegistryAuthority).items()
        if callable(value) and not name.startswith("_")
    }

    assert public_methods == {
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
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")
    assert "RecoveryManager" not in source
    assert "RestoreManager" not in source


def test_m394_7_recovery_performs_no_external_operations() -> None:
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")

    assert "import socket" not in source
    assert "import requests" not in source
    assert "import subprocess" not in source
    assert "OfficialDeviceGateway(" not in source
    assert "credentials.json" not in source
    assert "def connect(" not in source


def test_m394_7_preserves_gateway_and_canonical_core_contracts() -> None:
    gateway = (ROOT / "app/device_gateway.py").read_text(encoding="utf-8")
    assert "class OfficialDeviceGateway" in gateway
    assert "ExternalResourceRegistryAuthority" not in gateway

    occurrences = 0
    for path in (ROOT / "app").rglob("*.py"):
        occurrences += path.read_text(encoding="utf-8").count("CanonicalCognitiveCore(")
    assert occurrences >= 1


def test_m394_7_documentation_is_synchronized() -> None:
    document = (ROOT / "docs/M394_7_SAFE_EXTERNAL_RESOURCE_RECOVERY.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    external = (ROOT / "external_capabilities.md").read_text(encoding="utf-8")
    decision = (ROOT / "integration_decision.md").read_text(encoding="utf-8")

    assert "M394.7" in document
    assert "registered_only" in document
    assert ".roby/credentials.json" in document
    assert "## Milestone M394.7" in readme
    assert "## M394.7" in changelog
    assert "M394.7" in rules
    assert "M394.7" in external
    assert "M394.7" in decision
