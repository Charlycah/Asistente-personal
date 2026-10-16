from __future__ import annotations

from pathlib import Path

from core.cognitive_planning.explainability import CognitiveDecisionExplainer
from core.controlled_autonomy.advanced_explainability import (
    DeterministicAutonomyExplainer,
)
from core.controlled_autonomy.explainability import DeterministicDecisionExplainer
from core.governed_reasoning.explanations import ExplainableAnswerRenderer
from core.trust_explainability import TrustExplainabilityManager

ROOT = Path(__file__).resolve().parents[2]


def test_m378_retirement_preserves_source_owned_explainability() -> None:
    assert not (ROOT / "core/intelligent_explanations.py").exists()
    assert not (ROOT / "tests/test_m378_intelligent_explanations.py").exists()
    assert not (ROOT / "docs/M378_INTELLIGENT_EXPLANATIONS.md").exists()
    assert (
        ROOT
        / "docs/history/legacy-explainability/M378_INTELLIGENT_EXPLANATIONS.md"
    ).exists()

    assert ExplainableAnswerRenderer is not None
    assert CognitiveDecisionExplainer is not None
    assert DeterministicDecisionExplainer is not None
    assert DeterministicAutonomyExplainer is not None
    assert TrustExplainabilityManager is not None

    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    boundary = rules.split(
        "## M378 — Regla de explicabilidad propiedad de la fuente", maxsplit=1
    )[1].split("## M377 — Regla de personalidad adaptativa", maxsplit=1)[0]
    assert "IntelligentExplanationAuthority" in boundary
    assert "históricas M378 retiradas" in boundary
    assert "GlobalExplanationAuthority" in boundary
    assert "No se autoriza crear" in boundary
