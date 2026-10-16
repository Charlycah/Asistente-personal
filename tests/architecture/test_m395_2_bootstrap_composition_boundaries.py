from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.runtime_bootstrap_contract import OFFICIAL_RUNTIME_FACTORY
from app.runtime_root_factory import OFFICIAL_RUNTIME_FACTORY as FACTORY_REEXPORT
from core.runtime_composition_root import RuntimeCompositionRoot

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_MODULES = (
    "app.roby_config",
    "app.runtime_environment_wiring",
    "app.runtime_root_factory",
    "app.unified_runtime_integration",
    "app.voice_input",
)


def _module_path(module: str) -> Path:
    return ROOT.joinpath(*module.split(".")).with_suffix(".py")


def _direct_imports(module: str) -> set[str]:
    tree = ast.parse(_module_path(module).read_text(encoding="utf-8"))
    package = module.split(".")[:-1]
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            if node.level:
                base = package[: max(0, len(package) - node.level + 1)]
                imports.add(".".join((*base, node.module)))
            else:
                imports.add(node.module)
    return imports


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
            if target in graph and visit(target):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def test_m395_2_bootstrap_identifier_is_neutral_and_stable() -> None:
    assert OFFICIAL_RUNTIME_FACTORY == "app.runtime_root_factory:build_runtime_root"
    assert FACTORY_REEXPORT == OFFICIAL_RUNTIME_FACTORY
    assert _direct_imports("app.runtime_bootstrap_contract") == {
        "__future__",
    }


def test_m395_2_config_does_not_import_runtime_factory_implementation() -> None:
    assert "app.runtime_root_factory" not in _direct_imports("app.roby_config")


def test_m395_2_certified_bootstrap_cluster_is_acyclic() -> None:
    graph = {
        module: _direct_imports(module).intersection(BOOTSTRAP_MODULES)
        for module in BOOTSTRAP_MODULES
    }
    assert not _has_cycle(graph)


def test_m395_2_composition_root_remains_single_public_root() -> None:
    source = (ROOT / "core/runtime_composition_root/root.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    roots = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "RuntimeCompositionRoot"
    ]
    assert len(roots) == 1


def test_m395_2_compose_is_a_thin_orchestration_surface() -> None:
    lines = inspect.getsource(RuntimeCompositionRoot.compose).splitlines()
    assert len(lines) <= 100
