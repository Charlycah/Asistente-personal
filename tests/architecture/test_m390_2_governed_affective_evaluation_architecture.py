from __future__ import annotations

import ast
from pathlib import Path

from core.cognitive_maturity import GovernedAffectiveEvaluator

ROOT = Path(__file__).resolve().parents[2]


def test_m390_2_evaluator_is_not_a_parallel_authority() -> None:
    evaluator = GovernedAffectiveEvaluator()
    assert evaluator.evaluator_id == "governed_affective_evaluation"
    assert not hasattr(evaluator, "authority_id")


def test_m390_2_source_only_depends_on_certified_reports_and_signal_contract() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "governed_affective_evaluation.py"
    source = path.read_text(encoding="utf-8")
    assert "FunctionalPsychologyReport" in source
    assert "PendingMattersReport" in source
    assert "UnifiedEpistemicReport" in source
    assert "SimulatedInnerStateSignal" in source
    assert "ConversationReflectionAuthority" not in source
    assert "HistoricalAnalysisAuthority" not in source
    assert "CognitiveAnalysisAuthority" not in source


def test_m390_2_has_no_sensitive_or_governed_side_effect_dependencies() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "governed_affective_evaluation.py"
    source = path.read_text(encoding="utf-8")
    forbidden = (
        "credentials.json",
        ".roby",
        "memory.store",
        "learn(",
        "plan(",
        "grant_permission",
        "create_task(",
        "schedule_action",
        "execute_action",
    )
    for item in forbidden:
        assert item not in source


def test_m390_2_does_not_wire_runtime_or_gateway() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "governed_affective_evaluation.py"
    source = path.read_text(encoding="utf-8")
    assert "UnifiedBrain" not in source
    assert "official_conversation_gateway" not in source


def test_m390_2_preserves_canonical_core_constructor_line() -> None:
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
