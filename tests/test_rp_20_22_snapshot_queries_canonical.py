from __future__ import annotations

import ast
from pathlib import Path

from app.cognitive_core_runtime import CognitiveCoreRuntime

SOURCE = Path("app/cognitive_core_runtime.py")


def test_cognitive_core_runtime_does_not_repeat_snapshot_state() -> None:
    assert not hasattr(CognitiveCoreRuntime, "is_running")
    assert not hasattr(CognitiveCoreRuntime, "is_healthy")


def test_cognitive_core_runtime_keeps_canonical_surface() -> None:
    assert isinstance(CognitiveCoreRuntime.snapshot, property)
    assert callable(CognitiveCoreRuntime.start)
    assert callable(CognitiveCoreRuntime.stop)


def test_removed_snapshot_aliases_are_absent_from_source() -> None:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    runtime = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "CognitiveCoreRuntime"
    )
    methods = {
        node.name
        for node in runtime.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "is_running" not in methods
    assert "is_healthy" not in methods
    assert {"snapshot", "start", "stop"} <= methods
