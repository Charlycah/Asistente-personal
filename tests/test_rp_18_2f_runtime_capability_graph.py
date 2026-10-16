from __future__ import annotations

import pytest

from app.runtime_capability_graph import (
    RuntimeCapabilityGraph,
    RuntimeCapabilityNode,
)
from app.runtime_health_readiness import (
    RuntimeCapabilityAvailability,
    RuntimeCapabilityRequirement,
    RuntimeHealthReadinessService,
)
from tests.test_rp_18_2e_runtime_health_readiness import _resident, _snapshot


def _node(
    capability_id: str,
    *,
    required_residents: tuple[str, ...] = (),
    optional_residents: tuple[str, ...] = (),
    required_capabilities: tuple[str, ...] = (),
    optional_capabilities: tuple[str, ...] = (),
) -> RuntimeCapabilityNode:
    return RuntimeCapabilityNode(
        RuntimeCapabilityRequirement(
            capability_id,
            required_residents=required_residents,
            optional_residents=optional_residents,
        ),
        required_capabilities=required_capabilities,
        optional_capabilities=optional_capabilities,
    )


def test_graph_rejects_duplicate_capabilities_case_insensitively() -> None:
    with pytest.raises(ValueError, match="únicas"):
        RuntimeCapabilityGraph((_node("Memory"), _node("memory")))


def test_node_rejects_self_dependency() -> None:
    with pytest.raises(ValueError, match="sí misma"):
        _node("memory", required_capabilities=("MEMORY",))


def test_node_rejects_required_optional_overlap() -> None:
    with pytest.raises(ValueError, match="requerida y opcional"):
        _node(
            "conversation",
            required_capabilities=("memory",),
            optional_capabilities=("MEMORY",),
        )


def test_graph_rejects_unknown_dependency() -> None:
    with pytest.raises(ValueError, match="no registrada"):
        RuntimeCapabilityGraph(
            (_node("conversation", required_capabilities=("memory",)),)
        )


def test_graph_rejects_cycles() -> None:
    with pytest.raises(ValueError, match="ciclo"):
        RuntimeCapabilityGraph(
            (
                _node("a", required_capabilities=("b",)),
                _node("b", required_capabilities=("a",)),
            )
        )


def test_order_places_dependencies_before_dependents() -> None:
    graph = RuntimeCapabilityGraph(
        (
            _node("conversation", required_capabilities=("memory",)),
            _node("memory"),
        )
    )
    assert tuple(item.capability_id for item in graph.ordered()) == (
        "memory",
        "conversation",
    )


def test_dependents_can_be_transitive() -> None:
    graph = RuntimeCapabilityGraph(
        (
            _node("memory"),
            _node("reasoning", required_capabilities=("memory",)),
            _node("conversation", required_capabilities=("reasoning",)),
        )
    )
    assert graph.dependents("memory") == ("conversation", "reasoning")
    assert graph.dependents("memory", transitive=False) == ("reasoning",)


def test_resident_impact_includes_transitive_dependents() -> None:
    graph = RuntimeCapabilityGraph(
        (
            _node("memory", required_residents=("memory_runtime",)),
            _node("reasoning", required_capabilities=("memory",)),
            _node("conversation", required_capabilities=("reasoning",)),
        )
    )
    assert graph.impacted_by_resident("memory_runtime") == (
        "conversation",
        "memory",
        "reasoning",
    )


def test_required_capability_dependency_blocks_dependent() -> None:
    graph = RuntimeCapabilityGraph(
        (
            _node("memory", required_residents=("memory_runtime",)),
            _node("conversation", required_capabilities=("memory",)),
        )
    )
    report = RuntimeHealthReadinessService().evaluate_graph(_snapshot(), graph)
    conversation = report.capability("conversation")
    assert conversation is not None
    assert conversation.availability is RuntimeCapabilityAvailability.UNAVAILABLE
    assert "capability:memory:unavailable" in conversation.blockers


def test_optional_capability_dependency_only_degrades() -> None:
    graph = RuntimeCapabilityGraph(
        (
            _node("voice", required_residents=("voice_runtime",)),
            _node("conversation", optional_capabilities=("voice",)),
        )
    )
    report = RuntimeHealthReadinessService().evaluate_graph(_snapshot(), graph)
    conversation = report.capability("conversation")
    assert conversation is not None
    assert conversation.availability is RuntimeCapabilityAvailability.DEGRADED
    assert conversation.ready
    assert "capability:voice:unavailable" in conversation.warnings


def test_degraded_required_dependency_degrades_dependent() -> None:
    graph = RuntimeCapabilityGraph(
        (
            _node("memory", optional_residents=("memory_cache",)),
            _node("reasoning", required_capabilities=("memory",)),
        )
    )
    report = RuntimeHealthReadinessService().evaluate_graph(_snapshot(), graph)
    reasoning = report.capability("reasoning")
    assert reasoning is not None
    assert reasoning.availability is RuntimeCapabilityAvailability.DEGRADED
    assert "capability:memory:degraded" in reasoning.warnings


def test_satisfied_graph_is_fully_available() -> None:
    graph = RuntimeCapabilityGraph(
        (
            _node("memory", required_residents=("memory_runtime",)),
            _node("conversation", required_capabilities=("memory",)),
        )
    )
    report = RuntimeHealthReadinessService().evaluate_graph(
        _snapshot(residents=(_resident("memory_runtime"),)), graph
    )
    assert all(
        item.availability is RuntimeCapabilityAvailability.AVAILABLE
        for item in report.capabilities
    )
