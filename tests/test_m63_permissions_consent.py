from datetime import datetime, timezone

import pytest

from core.attention import AttentionManager
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityRegistryManager,
    CapabilityRisk,
    PermissionScope,
)
from core.cognitive_cycle import CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.mental_state import ROBYMentalState
from core.permission_consent import (
    ConsentDecisionStatus,
    PermissionConsentEngine,
    PermissionConsentManager,
    PermissionConsentPolicy,
    PermissionConsentSignal,
    PermissionConsentSnapshot,
    PermissionGrant,
)
from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus, ToolRequest
from core.working_memory import WorkingMemoryManager


def test_permission_consent_policy_validates_contract():
    with pytest.raises(ValueError):
        PermissionConsentPolicy(max_grants=0)

    with pytest.raises(ValueError):
        PermissionConsentPolicy(explicit_consent_scopes=("invalid",))

    policy = PermissionConsentPolicy(explicit_consent_scopes=(PermissionScope.WRITE,))

    assert policy.normalized_explicit_consent_scopes == (PermissionScope.WRITE,)


def test_permission_grant_validates_contract():
    with pytest.raises(ValueError):
        PermissionGrant(" ", PermissionScope.READ)

    with pytest.raises(ValueError):
        PermissionGrant(
            "mail.read",
            PermissionScope.READ,
            granted_at=datetime(2026, 7, 9),
        )

    grant = PermissionGrant("mail.read", PermissionScope.READ)

    assert grant.normalized_scope is PermissionScope.READ
    assert grant.to_dict()["capability"] == "mail.read"


def test_permission_consent_snapshot_validates_contract():
    with pytest.raises(ValueError):
        PermissionConsentSnapshot((), (), (), (), (), ())

    with pytest.raises(ValueError):
        PermissionConsentSnapshot(
            (PermissionConsentSignal.PERMISSION_LAYER_READY,),
            (" ",),
            (),
            (),
            (),
            (),
        )

    snapshot = PermissionConsentSnapshot(
        (PermissionConsentSignal.PERMISSION_LAYER_READY,),
        (),
        (),
        (),
        (),
        (),
    )

    assert "Permissions & Consent M63:" in snapshot.system_prompt_lines()


def test_permission_consent_engine_allows_low_risk_read():
    decision = PermissionConsentEngine().evaluate_capability(
        "weather.current",
        scope=PermissionScope.NETWORK,
        risk_level="low",
        requires_confirmation=False,
        grants={},
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )

    assert decision.allowed is True
    assert decision.normalized_status is ConsentDecisionStatus.ALLOWED
    assert decision.reason == "low_risk_read_allowed"


def test_permission_consent_engine_requires_consent_for_device_scope():
    decision = PermissionConsentEngine().evaluate_capability(
        "camera.capture",
        scope=PermissionScope.DEVICE,
        risk_level="medium",
        requires_confirmation=False,
        grants={},
    )

    assert decision.normalized_status is ConsentDecisionStatus.REQUIRES_CONSENT
    assert decision.required_confirmation is True
    assert decision.reason == "scope_requires_explicit_consent:device"


def test_permission_consent_manager_grants_and_revokes_permission():
    manager = PermissionConsentManager()
    manager.grant(PermissionGrant("camera.capture", PermissionScope.DEVICE))

    decision = manager.authorize_capability(
        "camera.capture",
        scope=PermissionScope.DEVICE,
        risk_level="medium",
    )

    assert decision.allowed is True
    assert decision.grant_id is not None

    manager.revoke("camera.capture")
    decision = manager.authorize_capability(
        "camera.capture",
        scope=PermissionScope.DEVICE,
        risk_level="medium",
    )

    assert decision.normalized_status is ConsentDecisionStatus.REQUIRES_CONSENT


def test_tool_gateway_blocks_capability_when_consent_is_required():
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            "camera.capture",
            "Captura cámara local con permiso explícito.",
            kind=CapabilityKind.CAMERA,
            risk=CapabilityRisk.MEDIUM,
            permission_scope=PermissionScope.DEVICE,
        )
    )
    permissions = PermissionConsentManager()
    gateway = ToolGatewayManager(
        capability_registry=registry,
        permission_consent=permissions,
    )
    result = gateway.execute(ToolRequest("camera.capture"))

    assert result.normalized_status is ToolGatewayStatus.BLOCKED
    assert result.error == "consent_required:device"
    assert permissions.last_decision is not None


def test_cognitive_pipeline_includes_m63_permissions_consent(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            "mail.read",
            "Lee correos en modo lectura.",
            kind=CapabilityKind.MAIL,
            risk=CapabilityRisk.LOW,
            permission_scope=PermissionScope.READ,
        )
    )
    permissions = PermissionConsentManager()
    gateway = ToolGatewayManager(
        capability_registry=registry,
        permission_consent=permissions,
    )
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        identity=ROBYIdentity(),
        mental_state=ROBYMentalState(),
        attention=AttentionManager(),
        working_memory=WorkingMemoryManager(),
        cognitive_cycle=CognitiveCycleManager(),
        capability_registry=registry,
        permission_consent=permissions,
        tool_gateway=gateway,
    )

    result = pipeline.process_turn("ROBY, revisa mi correo", call_llm=False)

    assert result.permission_consent is permissions
    assert permissions.last_snapshot is not None
    assert "mail.read" in permissions.last_snapshot.allowed_capabilities
    assert "Permissions & Consent M63:" in result.system_prompt
