from app.cognitive_analysis_authority import CognitiveAnalysisAuthority
from tests.architecture.m389_1_support import cognitive_dossier


def test_m389_1_same_dossier_produces_exactly_same_report() -> None:
    authority = CognitiveAnalysisAuthority()
    dossier = cognitive_dossier()
    first = authority.analyze(dossier)
    second = authority.analyze(dossier)
    assert first == second
    assert first.analysis_fingerprint == second.analysis_fingerprint

