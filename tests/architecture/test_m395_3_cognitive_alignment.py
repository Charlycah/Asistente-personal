from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

from app.canonical_cognitive_core import (
    CanonicalCognitiveCore,
    CanonicalCognitiveCoreDomain,
)
from app.canonical_cognitive_state_facade import CanonicalCognitiveStateFacade
from app.canonical_decision_facade import CanonicalDecisionFacade
from app.canonical_memory_facade import CanonicalMemoryFacade
from app.canonical_planning_facade import CanonicalPlanningFacade
from app.canonical_reflection_facade import CanonicalReflectionFacade
from app.cognitive_authority_map import CognitiveAuthority, CognitiveAuthorityMap
from app.cognitive_core_runtime import CognitiveCoreRuntime

ROOT = Path(__file__).resolve().parents[2]
MATURITY = ROOT / "core/cognitive_maturity"


class _ReflectionEngine:
    def __init__(self) -> None:
        self.calls: list[tuple[object, object, object]] = []

    def reflect(self, snapshot, deliberation, *, now=None):
        self.calls.append((snapshot, deliberation, now))
        return "resident-reflection"


class _Loop:
    def __init__(self) -> None:
        self.agenda_manager = None
        self.agenda_reasoner = object()
        self.reflection_engine = _ReflectionEngine()
        self.thought_stream = object()
        self.hypothesis_workspace = object()
        self.world_model = object()
        self.episodic_memory = object()
        self.self_model = object()
        self.snapshot = SimpleNamespace(status="stopped")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


def _maturity_import_graph() -> dict[str, set[str]]:
    modules = {
        path.stem: path for path in MATURITY.glob("*.py") if path.name != "__init__.py"
    }
    graph = {name: set() for name in modules}
    for name, path in modules.items():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            target = None
            if node.level == 1 and node.module:
                target = node.module.split(".")[0]
            elif node.module and node.module.startswith("core.cognitive_maturity."):
                target = node.module.rsplit(".", 1)[-1]
            if target in modules:
                graph[name].add(target)
    return graph


def _has_cycle(graph: dict[str, set[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for target in graph[node]:
            if visit(target):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def test_m395_3_canonical_core_is_observational_not_execution_authority() -> None:
    core = CanonicalCognitiveCore(
        memory=CanonicalMemoryFacade(),
        planning=CanonicalPlanningFacade(),
        decision=CanonicalDecisionFacade(),
        state=CanonicalCognitiveStateFacade(),
        reflection=CanonicalReflectionFacade(),
    )

    assert all(component.observational for component in core.snapshot.components)
    assert all(
        component.execution_authority is False for component in core.snapshot.components
    )


def test_m395_3_resident_reflection_primary_satisfies_reflection_contract() -> None:
    loop = _Loop()
    runtime = CognitiveCoreRuntime(loop)
    facade = CanonicalReflectionFacade(authority=runtime)

    result = facade.reflect("agenda", "deliberation", now="now")

    assert result == "resident-reflection"
    assert loop.reflection_engine.calls == [("agenda", "deliberation", "now")]


def test_m395_3_facade_primaries_match_authority_map() -> None:
    authority_map = CognitiveAuthorityMap()
    assert (
        authority_map.snapshot.authority_for(CognitiveAuthority.PLANNING).primary
        == CanonicalPlanningFacade.PRIMARY
    )
    assert (
        authority_map.snapshot.authority_for(CognitiveAuthority.DECISION).primary
        == CanonicalDecisionFacade.PRIMARY
    )
    assert (
        authority_map.snapshot.authority_for(CognitiveAuthority.REFLECTION).primary
        == CanonicalReflectionFacade.PRIMARY
    )


def test_m395_3_reflection_remains_one_resident_primary() -> None:
    snapshot = CanonicalReflectionFacade().snapshot
    primary = snapshot.component_for(snapshot.primary)

    assert snapshot.primary == "cognitive_core_resident"
    assert primary.path == "app.cognitive_core_runtime:CognitiveCoreRuntime"
    assert primary.operational is True


def test_m395_3_cognitive_maturity_import_graph_is_acyclic() -> None:
    assert not _has_cycle(_maturity_import_graph())


def test_m395_3_core_still_exposes_exactly_five_domains() -> None:
    core = CanonicalCognitiveCore(
        memory=CanonicalMemoryFacade(),
        planning=CanonicalPlanningFacade(),
        decision=CanonicalDecisionFacade(),
        state=CanonicalCognitiveStateFacade(),
        reflection=CanonicalReflectionFacade(),
    )
    assert tuple(component.domain for component in core.snapshot.components) == tuple(
        CanonicalCognitiveCoreDomain
    )
