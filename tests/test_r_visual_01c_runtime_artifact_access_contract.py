"""Contract for governed runtime visual artifact access."""

from __future__ import annotations

import ast
from pathlib import Path

from app.desktop_visual_companion_runtime_binding import (
    DesktopVisualRuntimeTurn,
)
from app.desktop_external_image_presentation_composition import (
    DesktopVisualTurnCompanion,
)


def test_runtime_artifacts_are_nested_in_visual_companion() -> None:
    artifact = object()
    companion = DesktopVisualTurnCompanion(
        text="Marte",
        artifacts=(artifact,),
    )
    runtime = DesktopVisualRuntimeTurn(
        text="Marte",
        visual_companion=companion,
    )

    assert runtime.visual_companion.artifacts == (artifact,)


def test_desktop_ui_uses_actual_runtime_artifact_contract() -> None:
    path = Path("app/desktop_ui.py")
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))

    connections = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "connect_governed_floating_viewer"
    ]

    assert len(connections) == 1

    artifacts = next(
        keyword.value
        for keyword in connections[0].keywords
        if keyword.arg == "artifacts"
    )

    assert ast.unparse(artifacts) == (
        "visual_turn.visual_companion.artifacts"
    )
