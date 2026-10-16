from __future__ import annotations

import ast
from pathlib import Path


def _class_node(path: str, class_name: str) -> ast.ClassDef:
    module = ast.parse(Path(path).read_text(encoding="utf-8"))
    return next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )


def test_recall_result_has_no_memories_projection_property() -> None:
    class_node = _class_node(
        "core/cognitive_memory_recall.py",
        "CognitiveMemoryRecallResult",
    )

    public_methods = {
        node.name
        for node in class_node.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }

    assert "memories" not in public_methods


def test_recall_items_remain_the_canonical_result_surface() -> None:
    source = Path("core/cognitive_memory_recall.py").read_text(encoding="utf-8")

    assert "items: tuple[CognitiveMemoryRecallItem, ...]" in source
    assert "tuple(item.memory for item in self.items)" not in source


def test_policy_bearing_collection_conversions_remain_available() -> None:
    capability_source = Path("app/runtime_capability_registry.py").read_text(
        encoding="utf-8"
    )
    identity_source = Path("core/identity.py").read_text(encoding="utf-8")

    assert "def capability_names" in capability_source
    assert "def member_names" in identity_source
