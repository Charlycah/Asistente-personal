from __future__ import annotations

import ast
from pathlib import Path

from core.cognitive_maturity import ExplicitInnerContinuityEvaluator

ROOT = Path(__file__).resolve().parents[2]


def test_m390_3_evaluator_is_not_a_parallel_authority() -> None:
    evaluator = ExplicitInnerContinuityEvaluator()
    assert evaluator.evaluator_id == "explicit_inner_continuity"
    assert not hasattr(evaluator, "authority_id")


def test_m390_3_only_compares_existing_simulated_snapshots() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "explicit_inner_continuity.py"
    source = path.read_text(encoding="utf-8")
    assert "SimulatedInnerStateSnapshot" in source
    assert "SimulatedInnerStateAuthority" not in source
    assert "GovernedAffectiveEvaluator" not in source
    assert "FunctionalPsychologyAuthority" not in source
    assert "UnifiedEpistemicEvidenceAuthority" not in source


def test_m390_3_has_no_persistence_clock_or_runtime_dependencies() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "explicit_inner_continuity.py"
    source = path.read_text(encoding="utf-8")
    forbidden = (
        "datetime",
        "time.time",
        "sqlite",
        "credentials.json",
        ".roby",
        "UnifiedBrain",
        "official_conversation_gateway",
        "memory.store",
        "learn(",
        "execute_action",
    )
    for item in forbidden:
        assert item not in source


def test_m390_3_preserves_canonical_core_constructor_line() -> None:
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
