from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_historical_internal_knowledge_alias_is_removed() -> None:
    module = ROOT / "app" / "runtime_environment_ports.py"
    tree = ast.parse(module.read_text(encoding="utf-8"))
    assigned_names = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    assert "InternalKnowledgeNeedPort" not in assigned_names


def test_runtime_factory_uses_canonical_knowledge_gateway() -> None:
    source = (ROOT / "app" / "runtime_root_factory.py").read_text(encoding="utf-8")
    assert "InternalKnowledgeNeedPort" not in source
    assert "OfficialKnowledgeRuntimeGateway()" in source
