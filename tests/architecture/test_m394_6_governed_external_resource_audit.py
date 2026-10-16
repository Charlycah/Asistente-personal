from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.external_resource_registry import (
    ExternalResourceAuditEvent,
    ExternalResourceIdentity,
    ExternalResourceKind,
    ExternalResourceRegistration,
    ExternalResourceRegistryAuthority,
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


def _audit(authority: ExternalResourceRegistryAuthority) -> ExternalResourceAuditEvent:
    return authority.record_audit_event(
        "camera-living",
        event_type="authorization",
        previous_value="unknown",
        new_value="authorized",
        reason="Explicit owner decision",
        declared_by="owner",
        declared_at="2026-08-08T14:15:00-03:00",
    )


def test_m394_6_registered_resource_starts_with_empty_audit_history() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())

    assert authority.audit_history("camera-living") == ()
    assert authority.latest_audit("camera-living") is None
    assert authority.audit_revision("camera-living") == 0


def test_m394_6_records_explicit_immutable_audit_evidence() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())

    event = _audit(authority)

    assert event.audit_id == "camera-living:audit:1"
    assert event.resource_id == "camera-living"
    assert event.event_type == "authorization"
    assert event.previous_value == "unknown"
    assert event.new_value == "authorized"
    assert event.reason == "Explicit owner decision"
    assert event.declared_by == "owner"
    assert event.declared_at == "2026-08-08T14:15:00-03:00"
    assert event.revision == 1


def test_m394_6_audit_does_not_modify_registered_resource() -> None:
    authority = ExternalResourceRegistryAuthority()
    original = authority.register(_registration())

    _audit(authority)

    assert authority.get("camera-living") is original
    assert authority.snapshot().resources == (original,)


def test_m394_6_audit_history_is_append_only_and_revisioned() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())
    first = _audit(authority)
    second = authority.record_audit_event(
        "camera-living",
        event_type="connectivity",
        previous_value="unknown",
        new_value="configured",
        declared_by="owner",
        declared_at="2026-08-08T14:16:00-03:00",
    )

    assert authority.audit_history("camera-living") == (first, second)
    assert authority.latest_audit("camera-living") is second
    assert authority.audit_revision("camera-living") == 2
    assert second.audit_id == "camera-living:audit:2"
    assert second.revision == 2


def test_m394_6_audit_events_are_frozen() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())
    event = _audit(authority)

    with pytest.raises(FrozenInstanceError):
        event.reason = "changed"  # type: ignore[misc]


def test_m394_6_audit_requires_registered_resource() -> None:
    authority = ExternalResourceRegistryAuthority()

    with pytest.raises(KeyError, match="not registered"):
        authority.record_audit_event(
            "missing",
            event_type="state",
            declared_by="owner",
            declared_at="2026-08-08T14:15:00-03:00",
        )


def test_m394_6_audit_requires_explicit_governance_evidence() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())

    with pytest.raises(ValueError, match="event type"):
        authority.record_audit_event(
            "camera-living",
            event_type=" ",
            declared_by="owner",
            declared_at="2026-08-08T14:15:00-03:00",
        )
    with pytest.raises(ValueError, match="declarer"):
        authority.record_audit_event(
            "camera-living",
            event_type="state",
            declared_by=" ",
            declared_at="2026-08-08T14:15:00-03:00",
        )
    with pytest.raises(ValueError, match="timestamp"):
        authority.record_audit_event(
            "camera-living",
            event_type="state",
            declared_by="owner",
            declared_at=" ",
        )


def test_m394_6_same_authority_owns_audit_without_parallel_manager() -> None:
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
        "validate_recovery",
        "register",
        "resolve_identity",
        "revoke_authorization",
        "snapshot",
    }
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")
    assert "AuditManager" not in source
    assert "ResourceHistoryManager" not in source


def test_m394_6_audit_performs_no_external_operations() -> None:
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")

    assert "import socket" not in source
    assert "import requests" not in source
    assert "import subprocess" not in source
    assert "OfficialDeviceGateway(" not in source
    assert "credentials.json" not in source
    assert "def connect(" not in source


def test_m394_6_preserves_gateway_and_canonical_core_contracts() -> None:
    gateway = (ROOT / "app/device_gateway.py").read_text(encoding="utf-8")
    assert "class OfficialDeviceGateway" in gateway
    assert "ExternalResourceRegistryAuthority" not in gateway

    occurrences = 0
    for path in (ROOT / "app").rglob("*.py"):
        occurrences += path.read_text(encoding="utf-8").count("CanonicalCognitiveCore(")
    assert occurrences >= 1


def test_m394_6_documentation_is_synchronized() -> None:
    document = (ROOT / "docs/M394_6_GOVERNED_EXTERNAL_RESOURCE_AUDIT.md").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    external = (ROOT / "external_capabilities.md").read_text(encoding="utf-8")
    decision = (ROOT / "integration_decision.md").read_text(encoding="utf-8")

    assert "M394.6" in document
    assert ".roby/credentials.json" in document
    assert "## Milestone M394.6" in readme
    assert "## M394.6" in changelog
    assert "M394.6" in rules
    assert "M394.6" in external
    assert "M394.6" in decision
