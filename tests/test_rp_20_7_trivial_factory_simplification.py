from __future__ import annotations

import ast
from pathlib import Path


def test_official_runtime_composition_avoids_trivial_runtime_builders() -> None:
    source = Path("app/official_runtime_composition.py").read_text(encoding="utf-8")

    assert "build_official_conversation_gateway" not in source
    assert "build_runtime_health_readiness" not in source
    assert "build_runtime_operational_snapshot" not in source
    assert "build_runtime_recovery_plan" not in source
    assert "build_unified_runtime_observability_snapshot" not in source


def test_official_runtime_owns_reusable_stateless_collaborators() -> None:
    tree = ast.parse(
        Path("app/official_runtime_composition.py").read_text(encoding="utf-8")
    )
    runtime_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "OfficialROBYRuntime"
    )
    init_method = next(
        node
        for node in runtime_class.body
        if isinstance(node, ast.FunctionDef) and node.name == "__init__"
    )
    assignments = {
        ast.unparse(target)
        for node in ast.walk(init_method)
        if isinstance(node, ast.Assign)
        for target in node.targets
    }

    assert {
        "self._snapshot_builder",
        "self._readiness_service",
        "self._recovery_planner",
        "self._observability_reader",
    } <= assignments
