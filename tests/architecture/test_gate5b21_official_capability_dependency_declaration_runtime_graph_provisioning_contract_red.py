from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

import pytest

from app.official_runtime_composition import OfficialROBYRuntime
from app.runtime_capability_graph import RuntimeCapabilityGraph, RuntimeCapabilityNode
from app.runtime_capability_registry import (
    OfficialRuntimeCapabilityRegistry,
    RuntimeCapabilityRegistration,
)
from app.runtime_health_readiness import RuntimeCapabilityRequirement

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_SOURCE = PROJECT_ROOT / "app" / "runtime_capability_registry.py"
COMPOSITION_SOURCE = PROJECT_ROOT / "app" / "official_runtime_composition.py"
OBSERVABILITY_SOURCE = PROJECT_ROOT / "app" / "unified_runtime_observability.py"
CONFIG_PATH = PROJECT_ROOT / ".roby" / "config.json"
EXPECTED_CONFIG_SHA256 = (
    "11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5"
)
EXPECTED_OBSERVABILITY_SHA256 = hashlib.sha256(
    OBSERVABILITY_SOURCE.read_bytes()
).hexdigest()


def _dependency_declaration_type():
    from app import runtime_capability_registry as module

    declaration_type = getattr(module, "RuntimeCapabilityDependencyDeclaration", None)
    assert declaration_type is not None
    return declaration_type


def _declared_nodes(registry: OfficialRuntimeCapabilityRegistry):
    reader = getattr(registry, "declared_capability_nodes", None)
    assert reader is not None
    return reader()


def test_red_typed_dependency_declaration_value_object_exists():
    declaration_type = _dependency_declaration_type()
    fields = declaration_type.__dataclass_fields__

    assert tuple(fields) == (
        "required_capabilities",
        "optional_capabilities",
        "required_residents",
        "optional_residents",
        "requires_runtime",
        "requires_supervisor",
    )
    assert declaration_type.__dataclass_params__.frozen is True


def test_red_runtime_registration_preserves_explicit_dependency_declaration():
    assert (
        "dependency_declaration" in RuntimeCapabilityRegistration.__dataclass_fields__
    )


def test_red_register_accepts_typed_dependency_declaration_without_metadata_encoding():
    parameters = inspect.signature(
        OfficialRuntimeCapabilityRegistry.register
    ).parameters

    assert "dependency_declaration" in parameters


def test_red_register_descriptor_accepts_same_typed_dependency_declaration_contract():
    parameters = inspect.signature(
        OfficialRuntimeCapabilityRegistry.register_descriptor
    ).parameters

    assert "dependency_declaration" in parameters


def test_red_registry_exposes_read_only_declared_nodes_not_a_second_graph_authority():
    assert hasattr(OfficialRuntimeCapabilityRegistry, "declared_capability_nodes")
    assert not hasattr(OfficialRuntimeCapabilityRegistry, "capability_graph")
    assert not hasattr(OfficialRuntimeCapabilityRegistry, "build_capability_graph")


def test_red_undeclared_is_distinct_from_explicit_empty_dependency_declaration():
    declaration_type = _dependency_declaration_type()
    registry = OfficialRuntimeCapabilityRegistry()

    registry.register(
        name="cap.undeclared",
        description="Undeclared dependency metadata",
        interceptor=object(),
    )
    registry.register(
        name="cap.explicit_empty",
        description="Explicitly independent capability",
        interceptor=object(),
        dependency_declaration=declaration_type(),
    )

    nodes = _declared_nodes(registry)

    assert tuple(node.capability_id for node in nodes) == ("cap.explicit_empty",)


def test_red_typed_declaration_materializes_exact_existing_runtime_capability_node():
    declaration_type = _dependency_declaration_type()
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="cap.base",
        description="Base capability",
        interceptor=object(),
        dependency_declaration=declaration_type(),
    )
    registry.register(
        name="cap.consumer",
        description="Consumer capability",
        interceptor=object(),
        dependency_declaration=declaration_type(
            required_capabilities=("cap.base",),
            optional_capabilities=(),
            required_residents=("resident.alpha",),
            optional_residents=("resident.beta",),
            requires_runtime=True,
            requires_supervisor=False,
        ),
    )

    nodes = _declared_nodes(registry)
    graph = RuntimeCapabilityGraph(nodes)
    node = graph.node("cap.consumer")

    assert node is not None
    assert node.required_capabilities == ("cap.base",)
    assert node.optional_capabilities == ()
    assert node.requirement.required_residents == ("resident.alpha",)
    assert node.requirement.optional_residents == ("resident.beta",)
    assert node.requirement.requires_runtime is True
    assert node.requirement.requires_supervisor is False
    assert node.requirement.description == "Consumer capability"


def test_red_official_runtime_owns_at_most_one_canonical_capability_graph_instance():
    assert hasattr(OfficialROBYRuntime, "capability_graph")
    parameters = inspect.signature(OfficialROBYRuntime.__init__).parameters

    assert "capability_graph" in parameters


def test_red_runtime_factory_provisions_graph_from_explicit_registry_nodes():
    source = COMPOSITION_SOURCE.read_text(encoding="utf-8")

    assert "declared_capability_nodes" in source
    assert "RuntimeCapabilityGraph(" in source
    assert "capability_graph=" in source


def test_existing_graph_fails_closed_on_unknown_capability_reference():
    node = RuntimeCapabilityNode(
        RuntimeCapabilityRequirement("cap.consumer"),
        required_capabilities=("cap.missing",),
    )

    with pytest.raises(ValueError, match="capacidad dependiente no registrada"):
        RuntimeCapabilityGraph((node,))


def test_existing_graph_fails_closed_on_self_dependency_and_cycles():
    with pytest.raises(ValueError, match="no puede depender de sí misma"):
        RuntimeCapabilityNode(
            RuntimeCapabilityRequirement("cap.a"),
            required_capabilities=("cap.a",),
        )

    a = RuntimeCapabilityNode(
        RuntimeCapabilityRequirement("cap.a"),
        required_capabilities=("cap.b",),
    )
    b = RuntimeCapabilityNode(
        RuntimeCapabilityRequirement("cap.b"),
        required_capabilities=("cap.a",),
    )
    with pytest.raises(ValueError, match="contiene un ciclo"):
        RuntimeCapabilityGraph((a, b))


def test_red_contract_does_not_introduce_parallel_dependency_authority():
    source = REGISTRY_SOURCE.read_text(encoding="utf-8")
    forbidden = (
        "DependencyRegistry",
        "CapabilityDependencyManager",
        "TechnicalInventoryManager",
        "AnalysisDependencyManager",
    )

    assert not any(name in source for name in forbidden)


def test_red_observability_stays_same_until_graph_certified():
    assert (
        hashlib.sha256(OBSERVABILITY_SOURCE.read_bytes()).hexdigest()
        == EXPECTED_OBSERVABILITY_SHA256
    )

