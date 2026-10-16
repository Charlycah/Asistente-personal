from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.external_resource_registry import (
    ExternalResourceAuthorizationDecision,
    ExternalResourceAuthorizationState,
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


def _authorize(
    authority: ExternalResourceRegistryAuthority,
) -> ExternalResourceRegistration:
    return authority.authorize(
        "camera-living",
        source="explicit_user_policy",
        authorized_by="owner",
        authorized_at="2026-08-08T13:40:00-03:00",
        reason="Lectura futura expresamente permitida",
    )


def test_m394_4_new_registration_starts_unknown_authorization() -> None:
    registration = _registration()

    assert (
        registration.authorization_state
        is ExternalResourceAuthorizationState.UNKNOWN
    )
    assert registration.authorization_history == ()


def test_m394_4_authorize_records_explicit_governed_decision() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())

    updated = _authorize(authority)

    assert updated.authorization_state is ExternalResourceAuthorizationState.AUTHORIZED
    assert authority.authorization_state("camera-living") is updated.authorization_state
    assert len(updated.authorization_history) == 1
    decision = updated.authorization_history[0]
    assert decision.source == "explicit_user_policy"
    assert decision.authorized_by == "owner"
    assert decision.decided_at == "2026-08-08T13:40:00-03:00"
    assert decision.reason == "Lectura futura expresamente permitida"
    assert decision.revision == 1


def test_m394_4_authorization_does_not_change_identity_or_resource_state() -> None:
    authority = ExternalResourceRegistryAuthority()
    original = authority.register(_registration())
    available = authority.declare_state(original.resource_id, "available")

    authorized = _authorize(authority)

    assert authorized.identity == available.identity
    assert authorized.state is ExternalResourceRegistryState.AVAILABLE


def test_m394_4_revoke_records_denied_and_preserves_history() -> None:
    authority = ExternalResourceRegistryAuthority()
    authority.register(_registration())
    first = _authorize(authority)

    revoked = authority.revoke_authorization(
        "camera-living",
        source="explicit_user_policy",
        authorized_by="owner",
        authorized_at="2026-08-08T13:41:00-03:00",
        reason="Permiso retirado",
    )

    assert first.authorization_state is ExternalResourceAuthorizationState.AUTHORIZED
    assert revoked.authorization_state is ExternalResourceAuthorizationState.DENIED
    assert tuple(item.state for item in revoked.authorization_history) == (
        ExternalResourceAuthorizationState.AUTHORIZED,
        ExternalResourceAuthorizationState.DENIED,
    )
    assert tuple(item.revision for item in revoked.authorization_history) == (1, 2)
    assert (
        authority.authorization_history("camera-living")
        == revoked.authorization_history
    )


def test_m394_4_authorization_requires_registered_resource() -> None:
    authority = ExternalResourceRegistryAuthority()

    with pytest.raises(KeyError, match="not registered"):
        authority.authorization_state("missing")
    with pytest.raises(KeyError, match="not registered"):
        authority.authorize(
            "missing",
            source="policy",
            authorized_by="owner",
            authorized_at="2026-08-08T13:40:00-03:00",
        )


def test_m394_4_explicit_decision_requires_governed_evidence() -> None:
    with pytest.raises(ValueError, match="cannot be unknown"):
        ExternalResourceAuthorizationDecision(
            state="unknown",
            source="policy",
            authorized_by="owner",
            decided_at="2026-08-08T13:40:00-03:00",
        )
    with pytest.raises(ValueError, match="source"):
        ExternalResourceAuthorizationDecision(
            state="authorized",
            source="",
            authorized_by="owner",
            decided_at="2026-08-08T13:40:00-03:00",
        )


def test_m394_4_authorization_decisions_are_immutable() -> None:
    decision = ExternalResourceAuthorizationDecision(
        state="authorized",
        source="policy",
        authorized_by="owner",
        decided_at="2026-08-08T13:40:00-03:00",
    )

    with pytest.raises(FrozenInstanceError):
        decision.reason = "changed"  # type: ignore[misc]


def test_m394_4_rejects_inconsistent_embedded_authorization_history() -> None:
    decision = ExternalResourceAuthorizationDecision(
        state="authorized",
        source="policy",
        authorized_by="owner",
        decided_at="2026-08-08T13:40:00-03:00",
    )

    with pytest.raises(ValueError, match="match latest decision"):
        ExternalResourceRegistration(
            resource_id="camera-living",
            label="Cámara living",
            kind="camera",
            source_authority="official_device_gateway",
            authorization_state="denied",
            authorization_history=(decision,),
        )


def test_m394_4_same_authority_owns_authorization_without_parallel_manager() -> None:
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
    assert "AuthorizationManager" not in source
    assert "PermissionController" not in source


def test_m394_4_authorization_performs_no_external_operations() -> None:
    source = (ROOT / "core/external_resource_registry.py").read_text(encoding="utf-8")

    assert "socket" not in source
    assert "requests" not in source
    assert "subprocess" not in source
    assert "OfficialDeviceGateway(" not in source
    assert "credentials.json" not in source


def test_m394_4_preserves_existing_gateway_and_canonical_core_contracts() -> None:
    gateway = (ROOT / "app/device_gateway.py").read_text(encoding="utf-8")
    assert "class OfficialDeviceGateway" in gateway
    assert "ExternalResourceRegistryAuthority" not in gateway

    occurrences = 0
    for path in (ROOT / "app").rglob("*.py"):
        occurrences += path.read_text(encoding="utf-8").count("CanonicalCognitiveCore(")
    assert occurrences >= 1


def test_m394_4_documentation_is_synchronized() -> None:
    document_path = ROOT / "docs/M394_4_GOVERNED_EXTERNAL_RESOURCE_AUTHORIZATION.md"
    document = document_path.read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    external = (ROOT / "external_capabilities.md").read_text(encoding="utf-8")
    decision = (ROOT / "integration_decision.md").read_text(encoding="utf-8")

    assert "M394.4" in document
    assert ".roby/credentials.json" in document
    assert "## Milestone M394.4" in readme
    assert "## M394.4" in changelog
    assert "M394.4" in rules
    assert "M394.4" in external
    assert "M394.4" in decision
