import ast
from pathlib import Path

from core.cognitive_maturity import ConversationReflectionAuthority

ROOT = Path(__file__).resolve().parents[2]


def test_m390_7_reuses_existing_reflection_authority() -> None:
    authority = ConversationReflectionAuthority()
    assert authority.authority_id == "conversation_reflection"
    path = ROOT / "core" / "cognitive_maturity" / "conversation_reflection.py"
    source = path.read_text(encoding="utf-8")
    assert "InnerStateReflectionAuthority" not in source
    assert "inner_reflection" not in source


def test_m390_7_remains_read_only_and_without_runtime_wiring() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "conversation_reflection.py"
    source = path.read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source
    gateway = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(gateway.read_text(encoding="utf-8"), filename=str(gateway))
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert lines == [52]
