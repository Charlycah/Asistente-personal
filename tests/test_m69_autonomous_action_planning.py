from __future__ import annotations

from pathlib import Path

import pytest

from core.autonomous_action_planning import (
    AutonomousActionPlan,
    AutonomousActionPlanningManager,
    AutonomousActionPlanningPolicy,
    AutonomousActionPlanningSignal,
    AutonomousActionPlanStatus,
    AutonomousActionStep,
)
from core.capability_registry import (
    CapabilityRegistryManager,
    default_semantic_capabilities,
)
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.permission_consent import PermissionConsentManager, PermissionGrant
from core.tool_gateway import ToolGatewayManager
from infrastructure.camera.camera_adapter import CameraAdapter
from infrastructure.mail.mail_action_adapter import MailActionAdapter
from infrastructure.weather.weather_adapter import WeatherAdapter
from tests.test_m65_weather_adapter import FakeWeatherProvider
from tests.test_m67_mail_action_adapter import FakeMailActionProvider
from tests.test_m68_camera_adapter import FakeCameraProvider


def build_registry() -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    return registry


def test_autonomous_action_policy_forbids_direct_execution():
    with pytest.raises(ValueError, match="direct autonomous execution"):
        AutonomousActionPlanningPolicy(allow_direct_execution=True)

    policy = AutonomousActionPlanningPolicy(max_steps=3)

    assert policy.max_steps == 3


def test_action_step_validates_contract():
    with pytest.raises(ValueError, match="capability"):
        AutonomousActionStep(" ", "consultar")

    step = AutonomousActionStep("weather.current", "consultar clima")

    assert step.to_dict()["capability"] == "weather.current"


def test_action_plan_requires_steps():
    with pytest.raises(ValueError, match="at least one step"):
        AutonomousActionPlan(
            "Plan vacío",
            "sin pasos",
            (),
            AutonomousActionPlanStatus.PROPOSED,
            True,
        )


def test_manager_starts_idle_without_requested_capabilities():
    manager = AutonomousActionPlanningManager()

    snapshot = manager.observe_turn("ROBY, charlemos un rato")

    assert snapshot.normalized_status is AutonomousActionPlanStatus.IDLE
    assert snapshot.proposed_plans == ()
    assert snapshot.execution_deferred is False


def test_manager_proposes_weather_plan_from_natural_language():
    manager = AutonomousActionPlanningManager()

    snapshot = manager.observe_turn("ROBY, qué frío hace, necesito abrigo?")

    assert snapshot.normalized_status is AutonomousActionPlanStatus.PROPOSED
    assert snapshot.execution_deferred is True
    assert "weather.current" in snapshot.requested_capabilities
    assert snapshot.proposed_plans[0].steps[0].capability_name == "weather.current"
    assert snapshot.proposed_plans[0].user_confirmation_required is True
    assert (
        AutonomousActionPlanningSignal.EXECUTION_DEFERRED in snapshot.normalized_signals
    )


def test_manager_combines_mail_read_and_mail_action_plan():
    manager = AutonomousActionPlanningManager()

    snapshot = manager.observe_turn(
        "ROBY, revisá el correo y redactá una respuesta para Carlos"
    )

    assert snapshot.normalized_status is AutonomousActionPlanStatus.PROPOSED
    assert "mail.read" in snapshot.requested_capabilities
    assert "mail.send" in snapshot.requested_capabilities
    assert len(snapshot.proposed_plans[0].steps) == 2


def test_manager_marks_consent_required_capabilities():
    registry = build_registry()
    permissions = PermissionConsentManager()
    capability_snapshot = registry.observe_turn("ROBY, mirá esto con la cámara")
    permission_snapshot = permissions.observe_turn(
        "ROBY, mirá esto con la cámara",
        capabilities=registry.capabilities,
        requested_capabilities=capability_snapshot.requested_capabilities,
    )
    manager = AutonomousActionPlanningManager()

    snapshot = manager.observe_turn(
        "ROBY, mirá esto con la cámara",
        capabilities=registry.capabilities,
        capability_snapshot=capability_snapshot,
        permission_snapshot=permission_snapshot,
    )

    assert snapshot.normalized_status is AutonomousActionPlanStatus.AWAITING_CONSENT
    assert "camera.capture" in snapshot.consent_required_capabilities
    assert snapshot.proposed_plans[0].steps[0].requires_consent is True
    assert AutonomousActionPlanningSignal.CONSENT_AWARE in snapshot.normalized_signals


def test_manager_uses_registry_snapshot_over_heuristics():
    registry = build_registry()
    capability_snapshot = registry.observe_turn("ROBY, me llevo paraguas?")
    manager = AutonomousActionPlanningManager()

    snapshot = manager.observe_turn(
        "ROBY, me llevo paraguas?",
        capability_snapshot=capability_snapshot,
        capabilities=registry.capabilities,
    )

    assert snapshot.requested_capabilities == ("weather.current",)
    assert snapshot.proposed_plans[0].title == "Consultar clima antes de responder"


def test_manager_caps_steps_by_policy():
    manager = AutonomousActionPlanningManager(
        AutonomousActionPlanningPolicy(max_steps=1)
    )

    snapshot = manager.observe_turn(
        "ROBY, revisá el correo, redactá respuesta y mirá la cámara"
    )

    assert len(snapshot.proposed_plans[0].steps) == 1


def test_system_prompt_exposes_autonomous_planning_rules():
    manager = AutonomousActionPlanningManager()
    manager.observe_turn("ROBY, tengo correos nuevos?")

    lines = manager.system_prompt_lines()

    assert "Autonomous Action Planning M69:" in lines
    assert any("no ejecuta" in line for line in lines)
    assert any("Plan propuesto" in line for line in lines)


def test_to_dict_is_auditable():
    manager = AutonomousActionPlanningManager()
    snapshot = manager.observe_turn("ROBY, me llevo paraguas?")

    data = snapshot.to_dict()

    assert data["status"] == "proposed"
    assert data["execution_deferred"] is True
    assert data["proposed_plans"][0]["steps"][0]["capability"] == "weather.current"


def test_pipeline_integrates_m69_without_executing_tools(tmp_path: Path):
    registry = build_registry()
    permissions = PermissionConsentManager()
    gateway = ToolGatewayManager(
        capability_registry=registry,
        permission_consent=permissions,
    )
    WeatherAdapter(FakeWeatherProvider()).register_with_gateway(gateway)
    MailActionAdapter(FakeMailActionProvider()).register_with_gateway(gateway)
    CameraAdapter(FakeCameraProvider()).register_with_gateway(gateway)
    permissions.grant(PermissionGrant("camera.capture", "device"))
    manager = AutonomousActionPlanningManager()
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        capability_registry=registry,
        permission_consent=permissions,
        tool_gateway=gateway,
        autonomous_action_planning=manager,
    )

    result = pipeline.process_turn(
        "ROBY, revisá el correo y redactá una respuesta",
        call_llm=False,
    )

    assert result.autonomous_action_planning is manager
    assert manager.last_snapshot is not None
    assert manager.last_snapshot.execution_deferred is True
    assert gateway.audit_log == ()
    assert "Autonomous Action Planning M69:" in result.system_prompt
