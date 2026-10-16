from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

import app.runtime_environment_ports as environment_ports
import app.runtime_root_factory as runtime_factory

PORT_NAMES = (
    "EnvironmentReadinessPort",
    "ProviderObservationsPort",
    "ConversationWorkloadPort",
    "EnvironmentInferenceRequestPort",
    "DailyBriefingConversationInterceptionPort",
    "ReminderConversationInterceptionPort",
)


def test_runtime_factory_preserves_public_environment_port_names() -> None:
    for name in PORT_NAMES:
        assert getattr(runtime_factory, name) is getattr(environment_ports, name)


def test_runtime_factory_no_longer_defines_environment_ports() -> None:
    tree = ast.parse(Path("app/runtime_root_factory.py").read_text(encoding="utf-8"))
    defined_classes = {
        node.name for node in tree.body if isinstance(node, ast.ClassDef)
    }
    assert defined_classes.isdisjoint(PORT_NAMES)


def test_production_import_graph_has_no_cycles() -> None:
    modules: dict[str, Path] = {}
    for path in Path(".").rglob("*.py"):
        if "tests" in path.parts or path.name == "__init__.py":
            continue
        modules[".".join(path.with_suffix("").parts)] = path

    edges: dict[str, set[str]] = defaultdict(set)
    for module, path in modules.items():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in modules:
                        edges[module].add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module in modules:
                    edges[module].add(node.module)
                for alias in node.names:
                    candidate = f"{node.module}.{alias.name}"
                    if candidate in modules:
                        edges[module].add(candidate)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(module: str) -> None:
        if module in visiting:
            raise AssertionError(f"production import cycle detected at {module}")
        if module in visited:
            return
        visiting.add(module)
        for dependency in edges[module]:
            visit(dependency)
        visiting.remove(module)
        visited.add(module)

    for module in modules:
        visit(module)
