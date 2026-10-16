from datetime import datetime, timezone

import pytest

from core.attention import AttentionManager
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityRegistryEngine,
    CapabilityRegistryManager,
    CapabilityRegistryPolicy,
    CapabilityRegistrySignal,
    CapabilityRegistrySnapshot,
    CapabilityRisk,
    PermissionScope,
)
from core.cognitive_cycle import CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.mental_state import ROBYMentalState
from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus, ToolRequest
from core.working_memory import WorkingMemoryManager


def test_capability_registry_policy_validates_contract():
    with pytest.raises(ValueError):
        CapabilityRegistryPolicy(max_capabilities=0)

    policy = CapabilityRegistryPolicy(max_capabilities=2)

    assert policy.max_capabilities == 2
    assert policy.allow_duplicate_registration is False


def test_capability_descriptor_validates_and_serializes_contract():
    with pytest.raises(ValueError):
        CapabilityDescriptor(" ", "Descripción")

    with pytest.raises(ValueError):
        CapabilityDescriptor("weather.current", " ")

    with pytest.raises(ValueError):
        CapabilityDescriptor(
            "weather.current",
            "Consulta clima actual.",
            kind="unknown",
        )

    descriptor = CapabilityDescriptor(
        "weather.current",
        "Consulta clima actual.",
        kind=CapabilityKind.WEATHER,
        risk=CapabilityRisk.LOW,
        permission_scope=PermissionScope.NETWORK,
        tags=("weather", "current"),
    )

    assert descriptor.normalized_kind is CapabilityKind.WEATHER
    assert descriptor.to_dict()["permission_scope"] == "network"
    assert descriptor.to_tool_capability_kwargs()["name"] == "weather.current"


def test_capability_registry_snapshot_validates_contract():
    with pytest.raises(ValueError):
        CapabilityRegistrySnapshot(
            (),
            0,
            (),
            (),
            (),
            False,
        )

    with pytest.raises(ValueError):
        CapabilityRegistrySnapshot(
            (CapabilityRegistrySignal.REGISTRY_READY,),
            -1,
            (),
            (),
            (),
            False,
        )

    snapshot = CapabilityRegistrySnapshot(
        (CapabilityRegistrySignal.REGISTRY_READY,),
        1,
        ("weather.current",),
        (),
        (CapabilityKind.WEATHER,),
        True,
    )

    assert snapshot.gateway_compatible is True
    assert "Capability Registry M62:" in snapshot.system_prompt_lines()


def test_capability_registry_manager_registers_and_filters_by_kind():
    manager = CapabilityRegistryManager()
    weather = CapabilityDescriptor(
        "weather.current",
        "Consulta clima actual.",
        kind=CapabilityKind.WEATHER,
        permission_scope=PermissionScope.NETWORK,
    )
    mail = CapabilityDescriptor(
        "mail.read",
        "Lee correos en modo lectura.",
        kind=CapabilityKind.MAIL,
        permission_scope=PermissionScope.READ,
    )
    manager.register(weather)
    manager.register(mail)

    assert manager.get("weather.current") is weather
    assert manager.enabled_names() == ("mail.read", "weather.current")
    assert manager.by_kind(CapabilityKind.WEATHER) == (weather,)

    with pytest.raises(ValueError):
        manager.register(weather)


def test_capability_registry_respects_capacity_limit():
    manager = CapabilityRegistryManager(CapabilityRegistryPolicy(max_capabilities=1))
    manager.register(CapabilityDescriptor("one", "Primera capacidad."))

    with pytest.raises(ValueError):
        manager.register(CapabilityDescriptor("two", "Segunda capacidad."))


def test_capability_registry_engine_discovers_relevant_capabilities():
    capabilities = {
        "weather.current": CapabilityDescriptor(
            "weather.current",
            "Consulta clima actual.",
            kind=CapabilityKind.WEATHER,
        ),
        "weather.forecast": CapabilityDescriptor(
            "weather.forecast",
            "Consulta pronóstico extendido.",
            kind=CapabilityKind.WEATHER,
        ),
    }

    snapshot = CapabilityRegistryEngine().evaluate_turn(
        "ROBY, me decís el clima y el extendido?",
        capabilities=capabilities,
        gateway_compatible=True,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )

    assert CapabilityRegistrySignal.CAPABILITY_DISCOVERED in snapshot.normalized_signals
    assert snapshot.requested_capabilities == (
        "weather.current",
        "weather.forecast",
    )
    assert snapshot.normalized_kinds == (CapabilityKind.WEATHER,)


def test_tool_gateway_can_use_capability_registry_without_direct_registration():
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            "weather.current",
            "Consulta clima actual.",
            kind=CapabilityKind.WEATHER,
            permission_scope=PermissionScope.NETWORK,
        )
    )
    gateway = ToolGatewayManager(capability_registry=registry)

    snapshot = gateway.observe_turn("ROBY, cómo está el clima hoy?")
    result = gateway.execute(ToolRequest("weather.current"))

    assert "weather.current" in snapshot.requested_capabilities
    assert "weather.current" in gateway.capabilities
    assert result.normalized_status is ToolGatewayStatus.WAITING_FOR_CAPABILITY
    assert result.error == "handler_not_registered"


def test_cognitive_pipeline_includes_m62_capability_registry(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            "weather.current",
            "Consulta clima actual.",
            kind=CapabilityKind.WEATHER,
            permission_scope=PermissionScope.NETWORK,
        )
    )
    gateway = ToolGatewayManager(capability_registry=registry)
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        identity=ROBYIdentity(),
        mental_state=ROBYMentalState(),
        attention=AttentionManager(),
        working_memory=WorkingMemoryManager(),
        cognitive_cycle=CognitiveCycleManager(),
        tool_gateway=gateway,
        capability_registry=registry,
    )

    result = pipeline.process_turn(
        "ROBY, cómo va a estar el clima hoy?",
        call_llm=False,
    )

    assert result.capability_registry is registry
    assert registry.last_snapshot is not None
    assert "weather.current" in registry.last_snapshot.requested_capabilities
    assert "Capability Registry M62:" in result.system_prompt
    assert "Tool Gateway M61:" in result.system_prompt
