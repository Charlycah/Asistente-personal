from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .runtime_health_readiness import RuntimeCapabilityRequirement


@dataclass(frozen=True)
class RuntimeCapabilityNode:
    requirement: RuntimeCapabilityRequirement
    required_capabilities: tuple[str, ...] = ()
    optional_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required = _normalized_ids(self.required_capabilities)
        optional = _normalized_ids(self.optional_capabilities)
        capability_id = self.requirement.capability_id.casefold()
        dependencies = {item.casefold() for item in required + optional}
        if capability_id in dependencies:
            raise ValueError("una capacidad no puede depender de sí misma")
        if {item.casefold() for item in required} & {
            item.casefold() for item in optional
        }:
            raise ValueError("una capacidad no puede ser requerida y opcional")
        object.__setattr__(self, "required_capabilities", required)
        object.__setattr__(self, "optional_capabilities", optional)

    @property
    def capability_id(self) -> str:
        return self.requirement.capability_id

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RuntimeCapabilityGraph:
    """Immutable declarative graph of operational capability dependencies."""

    def __init__(self, nodes: Iterable[RuntimeCapabilityNode] = ()) -> None:
        items = tuple(nodes)
        by_id: dict[str, RuntimeCapabilityNode] = {}
        for node in items:
            key = node.capability_id.casefold()
            if key in by_id:
                raise ValueError("las capacidades del grafo deben ser únicas")
            by_id[key] = node
        self._nodes = by_id
        self._validate_references()
        self._validate_acyclic()

    def node(self, capability_id: str) -> RuntimeCapabilityNode | None:
        return self._nodes.get(capability_id.strip().casefold())

    def snapshot(self) -> tuple[RuntimeCapabilityNode, ...]:
        return tuple(self._nodes[key] for key in sorted(self._nodes))

    def ordered(self) -> tuple[RuntimeCapabilityNode, ...]:
        visited: set[str] = set()
        ordered: list[RuntimeCapabilityNode] = []

        def visit(key: str) -> None:
            if key in visited:
                return
            node = self._nodes[key]
            for dependency in node.required_capabilities + node.optional_capabilities:
                visit(dependency.casefold())
            visited.add(key)
            ordered.append(node)

        for key in sorted(self._nodes):
            visit(key)
        return tuple(ordered)

    def requirements(self) -> tuple[RuntimeCapabilityRequirement, ...]:
        return tuple(node.requirement for node in self.ordered())

    def dependents(
        self, capability_id: str, *, transitive: bool = True
    ) -> tuple[str, ...]:
        target = capability_id.strip().casefold()
        if target not in self._nodes:
            return ()
        found: set[str] = set()
        frontier = [target]
        while frontier:
            current = frontier.pop()
            for key, node in self._nodes.items():
                dependencies = {
                    item.casefold()
                    for item in (
                        node.required_capabilities + node.optional_capabilities
                    )
                }
                if current in dependencies and key not in found:
                    found.add(key)
                    if transitive:
                        frontier.append(key)
        return tuple(self._nodes[key].capability_id for key in sorted(found))

    def impacted_by_resident(self, component_id: str) -> tuple[str, ...]:
        resident = component_id.strip().casefold()
        direct = {
            key
            for key, node in self._nodes.items()
            if resident
            in {
                item.casefold()
                for item in (
                    node.requirement.required_residents
                    + node.requirement.optional_residents
                )
            }
        }
        impacted = set(direct)
        for key in tuple(direct):
            impacted.update(
                item.casefold() for item in self.dependents(key, transitive=True)
            )
        return tuple(self._nodes[key].capability_id for key in sorted(impacted))

    def _validate_references(self) -> None:
        for node in self._nodes.values():
            for dependency in node.required_capabilities + node.optional_capabilities:
                if dependency.casefold() not in self._nodes:
                    raise ValueError(
                        f"capacidad dependiente no registrada: {dependency}"
                    )

    def _validate_acyclic(self) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(key: str) -> None:
            if key in visiting:
                raise ValueError("el grafo de capacidades contiene un ciclo")
            if key in visited:
                return
            visiting.add(key)
            node = self._nodes[key]
            for dependency in node.required_capabilities + node.optional_capabilities:
                visit(dependency.casefold())
            visiting.remove(key)
            visited.add(key)

        for key in self._nodes:
            visit(key)


def _normalized_ids(values: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(item.strip() for item in values)
    if any(not item for item in normalized):
        raise ValueError("los identificadores de capacidad no pueden estar vacíos")
    folded = tuple(item.casefold() for item in normalized)
    if len(folded) != len(set(folded)):
        raise ValueError("las dependencias de capacidad deben ser únicas")
    return normalized
