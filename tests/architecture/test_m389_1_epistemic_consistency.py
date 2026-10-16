from app.cognitive_analysis_authority import CognitiveAnalysisAuthority
from tests.architecture.m389_1_support import cognitive_dossier


def test_m389_1_preserves_epistemic_categories_and_order() -> None:
    summary = CognitiveAnalysisAuthority().analyze(
        cognitive_dossier()
    ).epistemic_summary
    assert summary.levels_present == (
        "fact",
        "inference",
        "hypothesis",
        "unknown",
    )
    assert summary.unknown_present is True
    assert summary.reason_codes == ("epistemic:uncertainty_present",)


def test_m389_1_does_not_promote_unknown_to_fact() -> None:
    summary = CognitiveAnalysisAuthority().analyze(
        cognitive_dossier()
    ).epistemic_summary
    assert "epistemic:unknown" in summary.evidence_codes
    assert summary.evidence_codes.count("epistemic:fact") == 1

