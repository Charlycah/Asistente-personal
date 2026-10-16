from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _class(path: Path, name: str) -> ast.ClassDef:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == name
    )


def _method(class_node: ast.ClassDef, name: str) -> ast.FunctionDef:
    return next(
        node
        for node in class_node.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


def test_m395_5_gateway_constructor_stays_synthesized() -> None:
    path = PROJECT_ROOT / "app" / "official_conversation_gateway.py"
    gateway = _class(path, "OfficialConversationGateway")
    constructor = _method(gateway, "__init__")
    assert constructor.end_lineno is not None
    assert constructor.end_lineno - constructor.lineno + 1 <= 30


def test_m395_5_preserves_canonical_core_constructor_lineage() -> None:
    path = PROJECT_ROOT / "app" / "official_conversation_gateway.py"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert "CanonicalCognitiveCore(" in lines[51]


def test_m395_5_gateway_initialization_uses_private_phases_only() -> None:
    path = PROJECT_ROOT / "app" / "official_conversation_gateway.py"
    gateway = _class(path, "OfficialConversationGateway")
    methods = {node.name for node in gateway.body if isinstance(node, ast.FunctionDef)}
    assert "_initialize_cognitive_evidence" in methods
    assert "_initialize_governed_conversation_services" in methods
    top_level_classes = {
        node.name
        for node in ast.parse(path.read_text(encoding="utf-8")).body
        if isinstance(node, ast.ClassDef)
    }
    assert top_level_classes == {
        "ConversationOrigin",
        "OfficialConversationGatewaySnapshot",
        "OfficialConversationGateway",
    }


def test_m395_5_cognitive_process_turn_stays_synthesized() -> None:
    path = PROJECT_ROOT / "core" / "cognitive_pipeline.py"
    pipeline = _class(path, "CognitivePipeline")
    process_turn = _method(pipeline, "process_turn")
    assert process_turn.end_lineno is not None
    assert process_turn.end_lineno - process_turn.lineno + 1 <= 110


def test_m395_5_pre_memory_phase_remains_private_and_ordered() -> None:
    path = PROJECT_ROOT / "core" / "cognitive_pipeline.py"
    source = path.read_text(encoding="utf-8")
    pipeline = _class(path, "CognitivePipeline")
    methods = {node.name for node in pipeline.body if isinstance(node, ast.FunctionDef)}
    assert "_run_pre_memory_observations" in methods
    process_source = ast.get_source_segment(source, _method(pipeline, "process_turn"))
    assert process_source is not None
    assert process_source.index("_run_pre_memory_observations") < process_source.index(
        "memory_integration.process_turn"
    )


def test_m395_5_synthesis_adds_no_second_orchestrator_class() -> None:
    gateway_path = PROJECT_ROOT / "app" / "official_conversation_gateway.py"
    pipeline_path = PROJECT_ROOT / "core" / "cognitive_pipeline.py"
    gateway_classes = {
        node.name
        for node in ast.parse(gateway_path.read_text(encoding="utf-8")).body
        if isinstance(node, ast.ClassDef)
    }
    pipeline_classes = {
        node.name
        for node in ast.parse(pipeline_path.read_text(encoding="utf-8")).body
        if isinstance(node, ast.ClassDef)
    }
    assert "OfficialConversationGateway" in gateway_classes
    assert "CognitivePipeline" in pipeline_classes
    assert not any(name.endswith("Orchestrator") for name in gateway_classes)
    assert not any(name.endswith("Orchestrator") for name in pipeline_classes)
