from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityRegistryEngine,
    CapabilityRegistryManager,
    CapabilityRegistrySignal,
    CapabilityRisk,
    PermissionScope,
    default_semantic_capabilities,
)
from core.tool_gateway import ToolGatewayManager


def test_capability_descriptor_accepts_semantic_descriptors():
    descriptor = CapabilityDescriptor(
        "weather.current",
        "Responde clima actual y recomendaciones inmediatas.",
        kind=CapabilityKind.WEATHER,
        risk=CapabilityRisk.LOW,
        permission_scope=PermissionScope.NETWORK,
        tags=("weather", "clima"),
        semantic_triggers=("frío", "paraguas"),
        supported_intents=("weather_query", "clothing_advice"),
        example_utterances=("ROBY, qué frío hace",),
    )

    assert "frío" in descriptor.semantic_terms()
    assert "weather_query" in descriptor.to_dict()["supported_intents"]
    assert "semantic_triggers" in descriptor.to_tool_capability_kwargs()["metadata"]


def test_capability_registry_engine_discovers_by_natural_weather_phrase():
    capabilities = {
        descriptor.name: descriptor for descriptor in default_semantic_capabilities()
    }

    snapshot = CapabilityRegistryEngine().evaluate_turn(
        "ROBY, qué frío hace, necesito abrigo?",
        capabilities=capabilities,
        gateway_compatible=True,
    )

    assert "weather.current" in snapshot.requested_capabilities
    assert CapabilityRegistrySignal.SEMANTIC_MATCH in snapshot.normalized_signals
    assert "weather.current" in snapshot.semantic_matches


def test_capability_registry_engine_discovers_mail_without_command_syntax():
    capabilities = {
        descriptor.name: descriptor for descriptor in default_semantic_capabilities()
    }

    snapshot = CapabilityRegistryEngine().evaluate_turn(
        "ROBY, hay algo urgente en el correo?",
        capabilities=capabilities,
        gateway_compatible=True,
    )

    assert "mail.read" in snapshot.requested_capabilities
    assert snapshot.semantic_matches["mail.read"]


def test_capability_registry_engine_discovers_camera_by_visual_language():
    capabilities = {
        descriptor.name: descriptor for descriptor in default_semantic_capabilities()
    }

    snapshot = CapabilityRegistryEngine().evaluate_turn(
        "ROBY, mirá esto, qué ves?",
        capabilities=capabilities,
        gateway_compatible=True,
    )

    assert "camera.capture" in snapshot.requested_capabilities


def test_default_semantic_catalog_covers_major_phase_vi_families():
    descriptors = default_semantic_capabilities()
    kinds = {descriptor.normalized_kind for descriptor in descriptors}

    assert CapabilityKind.WEATHER in kinds
    assert CapabilityKind.MAIL in kinds
    assert CapabilityKind.CAMERA in kinds
    assert CapabilityKind.FILES in kinds
    assert CapabilityKind.CALENDAR in kinds
    assert CapabilityKind.WEB in kinds


def test_semantic_search_returns_descriptors_not_technical_ids_only():
    manager = CapabilityRegistryManager()
    manager.register_many(default_semantic_capabilities())

    matches = manager.semantic_search("ROBY, resumime este PDF")

    assert tuple(descriptor.name for descriptor in matches) == ("files.read",)
    assert matches[0].normalized_kind is CapabilityKind.FILES


def test_tool_gateway_uses_semantic_registry_terms_for_requested_capabilities():
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    gateway = ToolGatewayManager(capability_registry=registry)

    snapshot = gateway.observe_turn("ROBY, me llevo paraguas?")

    assert "weather.current" in snapshot.requested_capabilities


def test_semantic_matches_are_exposed_to_system_prompt_and_dict():
    manager = CapabilityRegistryManager()
    manager.register_many(default_semantic_capabilities())

    snapshot = manager.observe_turn(
        "ROBY, buscá noticias actualizadas",
        gateway_compatible=True,
    )

    prompt = "\n".join(snapshot.system_prompt_lines())
    payload = snapshot.to_dict()

    assert "web.search" in snapshot.requested_capabilities
    assert "Coincidencia semántica: web.search" in prompt
    assert "web.search" in payload["semantic_matches"]
