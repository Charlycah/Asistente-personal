from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app" / "cognitive_core_runtime.py"


def _class_node(name: str) -> ast.ClassDef:
    module = ast.parse(SOURCE.read_text(encoding="utf-8"))
    return next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == name
    )


def test_cognitive_core_components_does_not_reintroduce_as_mapping() -> None:
    node = _class_node("CognitiveCoreComponents")
    methods = {item.name for item in node.body if isinstance(item, ast.FunctionDef)}
    assert "as_mapping" not in methods


def test_component_fields_remain_the_canonical_surface() -> None:
    node = _class_node("CognitiveCoreComponents")
    fields = {
        item.target.id
        for item in node.body
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)
    }
    assert fields == {
        "continuous_loop",
        "agenda_manager",
        "agenda_reasoner",
        "reflection_engine",
        "thought_stream",
        "hypothesis_workspace",
        "world_model",
        "episodic_memory",
        "self_model",
    }


def test_cognitive_core_module_no_longer_imports_mapping() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    assert "from typing import Mapping" not in source
