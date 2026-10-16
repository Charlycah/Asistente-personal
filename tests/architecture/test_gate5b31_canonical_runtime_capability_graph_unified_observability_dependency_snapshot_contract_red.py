from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from app.runtime_capability_graph import RuntimeCapabilityGraph, RuntimeCapabilityNode
from app.runtime_health_readiness import RuntimeCapabilityRequirement
from app.unified_runtime_observability import (
    UnifiedRuntimeObservability,
    UnifiedRuntimeObservabilitySnapshot,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OBSERVABILITY_SOURCE = PROJECT_ROOT / "app" / "unified_runtime_observability.py"
CONVERSATION_SOURCE = PROJECT_ROOT / "app" / "official_conversation_gateway.py"
CONFIG_PATH = PROJECT_ROOT / ".roby" / "config.json"
EXPECTED_CONFIG_SHA256 = (
    "11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5"
)


class _ResidentRegistry:
    def registration_for(self, component_id: str):
        assert component_id == "cognitive_core_runtime"
        return None


class _CapabilityRegistry:
    capability_names = ()
    gateway = None

    def __init__(self) -> None:
        self.declared_node_reads = 0

    def interface_snapshot(self):
        return ()

    def declared_capability_nodes(self):
        self.declared_node_reads += 1
        raise AssertionError(
            "observability must not reconstruct dependencies from the registry"
        )


class _Runtime:
    def __init__(
        self,
        *,
        capability_graph: RuntimeCapabilityGraph | None,
        registry: _CapabilityRegistry | None = None,
    ) -> None:
        self.capability_graph = capability_graph
        self.root = SimpleNamespace(
            dependencies=SimpleNamespace(official_capability_registry=registry)
        )
        self.resident_registry = _ResidentRegistry()
        self.conversation = SimpleNamespace(snapshot=SimpleNamespace(submitted_turns=0))
        self.readiness_calls = 0
        self.readiness_graph_calls = 0
        self.recovery_plan_calls = 0

    def snapshot(self, *, now):
        return SimpleNamespace(generated_at=now)

    def readiness(self, *, now):
        self.readiness_calls += 1
        return SimpleNamespace(generated_at=now)

    def readiness_graph(self, graph, *, now):
        self.readiness_graph_calls += 1
        raise AssertionError(
            "dependency projection must not execute readiness graph evaluation"
        )

    def recovery_plan(self, graph, *, capabilities, now):
        self.recovery_plan_calls += 1
        return SimpleNamespace(graph=graph, capabilities=capabilities, generated_at=now)


def _graph() -> RuntimeCapabilityGraph:
    base = RuntimeCapabilityNode(
        RuntimeCapabilityRequirement(
            "cap.Base",
            description="Canonical base capability",
        )
    )
    optional = RuntimeCapabilityNode(
        RuntimeCapabilityRequirement(
            "cap.Optional",
            description="Canonical optional capability",
        )
    )
    consumer = RuntimeCapabilityNode(
        RuntimeCapabilityRequirement(
            "cap.Consumer",
            description="Canonical consumer capability",
        ),
        required_capabilities=("cap.Base",),
        optional_capabilities=("cap.Optional",),
    )
    return RuntimeCapabilityGraph((consumer, optional, base))


def _alternate_graph() -> RuntimeCapabilityGraph:
    return RuntimeCapabilityGraph(
        (
            RuntimeCapabilityNode(
                RuntimeCapabilityRequirement(
                    "cap.Alternate",
                    description="Caller supplied recovery-only graph",
                )
            ),
        )
    )


def test_red_unified_snapshot_exposes_read_only_capability_dependency_projection():
    fields = UnifiedRuntimeObservabilitySnapshot.__dataclass_fields__

    assert "capability_dependencies" in fields
    assert UnifiedRuntimeObservabilitySnapshot.__dataclass_params__.frozen is True


def test_red_not_provisioned_graph_is_none_not_empty_projection():
    runtime = _Runtime(capability_graph=None)

    snapshot = UnifiedRuntimeObservability().snapshot(runtime)

    assert snapshot.capability_dependencies is None


def test_red_explicitly_provisioned_empty_graph_remains_empty_not_none():
    runtime = _Runtime(capability_graph=RuntimeCapabilityGraph(()))

    snapshot = UnifiedRuntimeObservability().snapshot(runtime)

    assert snapshot.capability_dependencies == ()
    assert snapshot.capability_dependencies is not None


def test_red_projection_preserves_exact_canonical_snapshot_ids_and_edges():
    graph = _graph()
    canonical_snapshot = graph.snapshot()
    runtime = _Runtime(capability_graph=graph)

    snapshot = UnifiedRuntimeObservability().snapshot(runtime)

    assert snapshot.capability_dependencies == canonical_snapshot
    assert tuple(node.capability_id for node in snapshot.capability_dependencies) == (
        "cap.Base",
        "cap.Consumer",
        "cap.Optional",
    )
    consumer = snapshot.capability_dependencies[1]
    assert consumer.required_capabilities == ("cap.Base",)
    assert consumer.optional_capabilities == ("cap.Optional",)
    assert all(
        projected is canonical
        for projected, canonical in zip(
            snapshot.capability_dependencies,
            canonical_snapshot,
            strict=True,
        )
    )


def test_red_projection_reads_only_runtime_graph_not_registry_reconstruction():
    registry = _CapabilityRegistry()
    graph = _graph()
    runtime = _Runtime(capability_graph=graph, registry=registry)

    snapshot = UnifiedRuntimeObservability().snapshot(runtime)

    assert snapshot.capability_dependencies == graph.snapshot()
    assert registry.declared_node_reads == 0


def test_red_caller_supplied_recovery_graph_cannot_override_canonical_projection():
    canonical_graph = _graph()
    alternate_graph = _alternate_graph()
    runtime = _Runtime(capability_graph=canonical_graph)

    snapshot = UnifiedRuntimeObservability().snapshot(runtime, graph=alternate_graph)

    assert snapshot.capability_dependencies == canonical_graph.snapshot()
    assert snapshot.capability_dependencies != alternate_graph.snapshot()


def test_red_dependency_projection_does_not_execute_readiness_graph_or_recovery():
    runtime = _Runtime(capability_graph=_graph())

    snapshot = UnifiedRuntimeObservability().snapshot(runtime)

    assert snapshot.capability_dependencies == runtime.capability_graph.snapshot()
    assert runtime.readiness_calls == 1
    assert runtime.readiness_graph_calls == 0
    assert runtime.recovery_plan_calls == 0


def test_red_observability_source_does_not_construct_or_infer_a_second_graph():
    source = OBSERVABILITY_SOURCE.read_text(encoding="utf-8")

    assert "declared_capability_nodes" not in source
    assert "RuntimeCapabilityGraph(" not in source
    assert ".readiness_graph(" not in source


def test_red_official_conversation_gateway_analysis_mode_remains_byte_identical():
    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source

