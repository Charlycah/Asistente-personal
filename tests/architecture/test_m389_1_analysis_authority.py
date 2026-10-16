from pathlib import Path

from app.cognitive_analysis_authority import CognitiveAnalysisAuthority

ROOT = Path(__file__).resolve().parents[2]


def test_m389_1_declares_one_cognitive_analysis_authority() -> None:
    sources = tuple((ROOT / "app").glob("*.py"))
    declarations = sum(
        path.read_text(encoding="utf-8").count("class CognitiveAnalysisAuthority:")
        for path in sources
    )
    assert declarations == 1
    assert CognitiveAnalysisAuthority.AUTHORITY_KEY == "cognitive_analysis_authority"


def test_m389_1_analysis_is_not_added_to_decision_authority_map() -> None:
    source = (ROOT / "app" / "cognitive_authority_map.py").read_text(
        encoding="utf-8"
    )
    assert CognitiveAnalysisAuthority.AUTHORITY_KEY not in source


def test_m389_1_preserves_canonical_core_constructor_line() -> None:
    lines = (ROOT / "app" / "official_conversation_gateway.py").read_text(
        encoding="utf-8"
    ).splitlines()
    assert lines[51].strip().endswith("CanonicalCognitiveCore(")

