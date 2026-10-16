from pathlib import Path

import pytest

from core.architectural_principle import ArchitecturalPrincipleManager
from core.attention import AttentionManager
from core.autonomous_action_planning import AutonomousActionPlanningManager
from core.capability_registry import (
    CapabilityRegistryManager,
    default_semantic_capabilities,
)
from core.cognitive_cycle import CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.governed_autonomy import (
    GovernedAutonomyDecision,
    GovernedAutonomyManager,
    GovernedAutonomyPolicy,
    GovernedAutonomySignal,
    GovernedAutonomySnapshot,
    GovernedAutonomyStatus,
)
from core.identity import ROBYIdentity
from core.mental_state import ROBYMentalState
from core.permission_consent import PermissionConsentManager
from core.tool_gateway import ToolGatewayManager, ToolGatewaySnapshot, ToolGatewayStatus
from core.working_memory import WorkingMemoryManager


def build_registry() -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    return registry


def test_governed_autonomy_policy_forbids_unattended_execution():
    with pytest.raises(ValueError, match="unattended"):
        GovernedAutonomyPolicy(allow_unattended_execution=True)

    with pytest.raises(ValueError, match="audit"):
        GovernedAutonomyPolicy(max_audit_records=0)

    policy = GovernedAutonomyPolicy()

    assert policy.allow_unattended_execution is False


def test_governed_autonomy_decision_never_executes_directly():
    with pytest.raises(ValueError, match="must not execute"):
        GovernedAutonomyDecision(
            GovernedAutonomyStatus.PROPOSAL_ALLOWED,
            ("weather.current",),
            ("weather.current",),
            (),
            (),
            (),
            "propuesta",
            can_execute=True,
        )

    decision = GovernedAutonomyDecision(
        GovernedAutonomyStatus.PROPOSAL_ALLOWED,
        ("weather.current",),
        ("weather.current",),
        (),
        (),
        (),
        "propuesta gobernada",
    )

    assert decision.can_execute is False
    assert decision.to_dict()["status"] == "proposal_allowed"


def test_governed_autonomy_snapshot_exposes_contract():
    decision = GovernedAutonomyDecision(
        GovernedAutonomyStatus.REVIEW_REQUIRED,
        ("mail.send",),
        (),
        ("mail.send",),
        (),
        (),
        "requiere revisión",
    )
    snapshot = GovernedAutonomySnapshot(
        (GovernedAutonomySignal.GOVERNANCE_LAYER_READY,),
        GovernedAutonomyStatus.REVIEW_REQUIRED,
        decision,
        ("audit:1",),
        ("ROBY propone antes de actuar.",),
    )

    prompt = "\n".join(snapshot.system_prompt_lines())

    assert "Governed Autonomy M70:" in prompt
    assert "Revisión requerida: mail.send" in prompt


def test_manager_starts_passive_without_external_capability():
    manager = GovernedAutonomyManager()

    snapshot = manager.observe_turn("ROBY, conversemos un rato")

    assert snapshot.normalized_status is GovernedAutonomyStatus.PASSIVE
    assert snapshot.decision.requested_capabilities == ()
    assert snapshot.decision.can_execute is False


def test_manager_allows_weather_proposal_without_sensitive_consent():
    registry = build_registry()
    capability_snapshot = registry.observe_turn("ROBY, me llevo paraguas?")
    planning = AutonomousActionPlanningManager()
    planning_snapshot = planning.observe_turn(
        "ROBY, me llevo paraguas?",
        capability_snapshot=capability_snapshot,
        capabilities=registry.capabilities,
    )
    manager = GovernedAutonomyManager()

    snapshot = manager.observe_turn(
        "ROBY, me llevo paraguas?",
        capability_snapshot=capability_snapshot,
        planning_snapshot=planning_snapshot,
    )

    assert snapshot.normalized_status is GovernedAutonomyStatus.PROPOSAL_ALLOWED
    assert snapshot.decision.permitted_capabilities == ("weather.current",)
    assert snapshot.decision.can_execute is False


def test_manager_requires_consent_for_camera_and_blocks_execution():
    registry = build_registry()
    permissions = PermissionConsentManager()
    capability_snapshot = registry.observe_turn("ROBY, mirá esto con la cámara")
    permission_snapshot = permissions.observe_turn(
        "ROBY, mirá esto con la cámara",
        capabilities=registry.capabilities,
        requested_capabilities=capability_snapshot.requested_capabilities,
    )
    planning = AutonomousActionPlanningManager()
    planning_snapshot = planning.observe_turn(
        "ROBY, mirá esto con la cámara",
        capabilities=registry.capabilities,
        capability_snapshot=capability_snapshot,
        permission_snapshot=permission_snapshot,
    )
    manager = GovernedAutonomyManager()

    snapshot = manager.observe_turn(
        "ROBY, mirá esto con la cámara",
        capability_snapshot=capability_snapshot,
        permission_snapshot=permission_snapshot,
        planning_snapshot=planning_snapshot,
    )

    assert snapshot.normalized_status is GovernedAutonomyStatus.BLOCKED
    assert "camera.capture" in snapshot.decision.consent_required_capabilities
    assert "camera.capture" in snapshot.decision.blocked_capabilities


def test_manager_requires_review_for_mail_action():
    registry = build_registry()
    permissions = PermissionConsentManager()
    capability_snapshot = registry.observe_turn("ROBY, redactá una respuesta")
    permission_snapshot = permissions.observe_turn(
        "ROBY, redactá una respuesta",
        capabilities=registry.capabilities,
        requested_capabilities=capability_snapshot.requested_capabilities,
    )
    manager = GovernedAutonomyManager()

    snapshot = manager.observe_turn(
        "ROBY, redactá una respuesta",
        capability_snapshot=capability_snapshot,
        permission_snapshot=permission_snapshot,
    )

    assert snapshot.normalized_status is GovernedAutonomyStatus.BLOCKED
    assert "mail.send" in snapshot.decision.review_required_capabilities
    assert "mail.send" in snapshot.decision.consent_required_capabilities


def test_manager_applies_most_restrictive_gateway_block():
    manager = GovernedAutonomyManager()
    gateway_snapshot = ToolGatewaySnapshot(
        ("gateway_required",),
        ToolGatewayStatus.BLOCKED,
        0.1,
        (),
        ("weather.current",),
        ("adapter_unavailable",),
        True,
    )

    snapshot = manager.observe_turn(
        "ROBY, cómo está el clima?",
        gateway_snapshot=gateway_snapshot,
    )

    assert snapshot.normalized_status is GovernedAutonomyStatus.BLOCKED
    assert "weather.current" in snapshot.decision.blocked_capabilities
    assert (
        GovernedAutonomySignal.RESTRICTIVE_PRECEDENCE_APPLIED
        in snapshot.normalized_signals
    )


def test_manager_keeps_bounded_audit_history():
    manager = GovernedAutonomyManager(GovernedAutonomyPolicy(max_audit_records=2))

    first = manager.observe_turn("ROBY, clima")
    second = manager.observe_turn("ROBY, correo")
    third = manager.observe_turn("ROBY, mirá esto")

    assert manager.history == (second, third)
    assert first not in manager.history
    assert manager.last_snapshot is third


def test_system_prompt_exposes_governance_rules():
    manager = GovernedAutonomyManager()
    manager.observe_turn("ROBY, redactá un correo")

    prompt = "\n".join(manager.system_prompt_lines())

    assert "Governed Autonomy M70:" in prompt
    assert "política más restrictiva" in prompt
    assert "Capacidad gobernada: mail.send" in prompt


def test_cognitive_pipeline_includes_m70_governed_autonomy(tmp_path: Path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    registry = build_registry()
    permissions = PermissionConsentManager()
    gateway = ToolGatewayManager(
        capability_registry=registry,
        permission_consent=permissions,
    )
    planning = AutonomousActionPlanningManager()
    governance = GovernedAutonomyManager()
    architectural_principle = ArchitecturalPrincipleManager()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        identity=ROBYIdentity(),
        mental_state=ROBYMentalState(),
        attention=AttentionManager(),
        working_memory=WorkingMemoryManager(),
        cognitive_cycle=CognitiveCycleManager(),
        architectural_principle=architectural_principle,
        capability_registry=registry,
        permission_consent=permissions,
        tool_gateway=gateway,
        autonomous_action_planning=planning,
        governed_autonomy=governance,
    )

    result = pipeline.process_turn(
        "ROBY, mirá esto con la cámara",
        call_llm=False,
    )

    assert result.governed_autonomy is governance
    assert governance.last_snapshot is not None
    assert "camera.capture" in governance.last_snapshot.decision.requested_capabilities
    assert "Governed Autonomy M70:" in result.system_prompt


def test_m70_closes_phase_vi_governance_contract():
    manager = GovernedAutonomyManager()
    snapshot = manager.observe_turn("ROBY, revisá el correo y redactá respuesta")
    payload = snapshot.to_dict()

    assert payload["status"] in {"blocked", "review_required"}
    assert "decision" in payload
    assert any("Toda decisión" in line for line in snapshot.governance_contract)
