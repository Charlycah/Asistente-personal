from datetime import datetime, timezone

import pytest

from core.architectural_principle import ArchitecturalPrincipleManager
from core.attention import AttentionManager
from core.cognitive_cycle import CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.mental_state import ROBYMentalState
from core.tool_gateway import (
    ToolCapability,
    ToolGatewayEngine,
    ToolGatewayManager,
    ToolGatewayPolicy,
    ToolGatewaySignal,
    ToolGatewaySnapshot,
    ToolGatewayStatus,
    ToolRequest,
)
from core.working_memory import WorkingMemoryManager


def test_tool_gateway_policy_validates_contract():
    with pytest.raises(ValueError):
        ToolGatewayPolicy(readiness_threshold=-0.1)

    with pytest.raises(ValueError):
        ToolGatewayPolicy(readiness_threshold=0.9, routed_threshold=0.7)

    with pytest.raises(ValueError):
        ToolGatewayPolicy(max_audit_entries=0)

    policy = ToolGatewayPolicy(readiness_threshold=0.6)

    assert policy.readiness_threshold == 0.6


def test_tool_gateway_snapshot_validates_contract():
    with pytest.raises(ValueError):
        ToolGatewaySnapshot(
            (),
            ToolGatewayStatus.READY,
            0.5,
            (),
            (),
            (),
            False,
        )

    with pytest.raises(ValueError):
        ToolGatewaySnapshot(
            (ToolGatewaySignal.GATEWAY_REQUIRED,),
            ToolGatewayStatus.READY,
            1.2,
            (),
            (),
            (),
            False,
        )

    with pytest.raises(ValueError):
        ToolGatewaySnapshot(
            (ToolGatewaySignal.GATEWAY_REQUIRED,),
            ToolGatewayStatus.READY,
            0.5,
            (" ",),
            (),
            (),
            False,
        )


def test_tool_gateway_registers_and_executes_capability():
    manager = ToolGatewayManager()
    capability = ToolCapability(
        "weather.current",
        "Consulta clima actual sin acoplar APIs al pipeline.",
    )
    manager.register_capability(
        capability,
        lambda payload: {"city": payload["city"], "temperature": "21C"},
    )

    result = manager.execute(ToolRequest("weather.current", {"city": "Buenos Aires"}))

    assert result.succeeded is True
    assert result.output["city"] == "Buenos Aires"
    assert manager.audit_log == (result,)


def test_tool_gateway_blocks_unknown_capability_by_default():
    manager = ToolGatewayManager()

    result = manager.execute(ToolRequest("mail.read", {"limit": 5}))

    assert result.normalized_status is ToolGatewayStatus.BLOCKED
    assert result.error == "capability_not_registered"
    assert result.succeeded is False


def test_tool_gateway_waits_when_handler_is_not_registered():
    manager = ToolGatewayManager()
    manager.register_capability(
        ToolCapability("camera.capture", "Captura cámara local con permiso."),
    )

    result = manager.execute(ToolRequest("camera.capture"))

    assert result.normalized_status is ToolGatewayStatus.WAITING_FOR_CAPABILITY
    assert result.error == "handler_not_registered"


def test_tool_gateway_engine_detects_requested_weather_capability():
    manager = ArchitecturalPrincipleManager()
    manager.observe_turn("M60 principio arquitectónico", cognitive_cycle=None)
    capabilities = {
        "weather.current": ToolCapability(
            "weather.current",
            "Consulta clima actual.",
        )
    }

    snapshot = ToolGatewayEngine().evaluate_turn(
        "ROBY, cómo está el clima hoy en Buenos Aires?",
        capabilities=capabilities,
        architectural_principle=manager,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )

    assert ToolGatewaySignal.CAPABILITY_REQUESTED in snapshot.normalized_signals
    assert "weather.current" in snapshot.requested_capabilities
    assert snapshot.normalized_status is ToolGatewayStatus.WAITING_FOR_CAPABILITY
    assert snapshot.architectural_anchor_present is True
    assert "Tool Gateway M61:" in snapshot.system_prompt_lines()


def test_tool_gateway_manager_keeps_history_after_observing_turn():
    manager = ToolGatewayManager()
    manager.register_capability(
        ToolCapability("mail.read", "Lee correos en modo lectura."),
    )

    first = manager.observe_turn("ROBY, revisa mi correo")
    second = manager.observe_turn("sin herramientas ahora")

    assert manager.history == (first, second)
    assert manager.last_snapshot is second
    assert "mail.read" in first.requested_capabilities


def test_cognitive_pipeline_includes_m61_tool_gateway(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    tool_gateway = ToolGatewayManager()
    tool_gateway.register_capability(
        ToolCapability("weather.current", "Consulta clima actual."),
    )
    architectural_principle = ArchitecturalPrincipleManager()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        identity=ROBYIdentity(),
        mental_state=ROBYMentalState(),
        attention=AttentionManager(),
        working_memory=WorkingMemoryManager(),
        cognitive_cycle=CognitiveCycleManager(),
        architectural_principle=architectural_principle,
        tool_gateway=tool_gateway,
    )

    result = pipeline.process_turn(
        "ROBY, cómo va a estar el clima hoy?",
        call_llm=False,
    )

    assert result.tool_gateway is tool_gateway
    assert tool_gateway.last_snapshot is not None
    assert "weather.current" in tool_gateway.last_snapshot.requested_capabilities
    assert "Tool Gateway M61:" in result.system_prompt
