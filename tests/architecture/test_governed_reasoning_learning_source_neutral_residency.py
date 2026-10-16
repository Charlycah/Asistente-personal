from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_governed_reasoning_learning_residency_is_source_neutral() -> None:
    old_path = ROOT / "core/governed_reasoning/abstraction_learning_bridge.py"
    new_path = ROOT / "app/governed_relational_abstraction_learning_bridge.py"

    assert not old_path.exists()
    assert new_path.exists()

    source = new_path.read_text(encoding="utf-8")
    assert "GovernedLearningCandidateM369EvaluationV1" in source
    assert "LearningFoundation" in source
    assert "PreferenceLearning" not in source
    assert "CuriosityM369" not in source

    for path in (ROOT / "core").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (
                    node.level == 0
                    and node.module is not None
                    and (
                        node.module == "app"
                        or node.module.startswith("app.")
                    )
                ), path
            elif isinstance(node, ast.Import):
                assert not any(
                    alias.name == "app" or alias.name.startswith("app.")
                    for alias in node.names
                ), path
