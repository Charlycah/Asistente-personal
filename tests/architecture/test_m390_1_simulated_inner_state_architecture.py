from __future__ import annotations

import ast
from pathlib import Path

from core.cognitive_maturity import SimulatedInnerStateAuthority

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "core" / "cognitive_maturity" / "simulated_inner_state.py"


def test_m390_1_has_one_canonical_simulated_inner_state_authority() -> None:
    assert SimulatedInnerStateAuthority.authority_id == "simulated_inner_state"
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"), filename=str(SOURCE_PATH))
    authorities = [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name.endswith("Authority")
    ]
    assert authorities == ["SimulatedInnerStateAuthority"]


def test_m390_1_source_does_not_create_parallel_governed_systems() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    forbidden = (
        "EmotionManager",
        "MoodManager",
        "FeelingEngine",
        "EmotionalBrain",
        "InnerWorldManager",
        "memory_store",
        "learning_engine",
        "permission_manager",
        "OfficialConversationGateway",
        "UnifiedBrain",
    )
    for name in forbidden:
        assert name not in source


def test_m390_1_source_has_no_sensitive_or_persistence_access() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source
    assert "open(" not in source
    assert "Path(" not in source
    assert "sqlite" not in source.lower()


def test_m390_1_does_not_parse_conversation_or_call_models() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8").lower()
    forbidden = ("conversationturn", "llm", "openai", "prompt", "transcript")
    for name in forbidden:
        assert name not in source


def test_m390_1_gateway_constructor_remains_only_on_line_52() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert lines == [52]
