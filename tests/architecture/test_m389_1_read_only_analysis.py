from app.cognitive_analysis_authority import CognitiveAnalysisAuthority
from tests.architecture.m389_1_support import cognitive_dossier


def test_m389_1_analysis_does_not_mutate_source_dossier() -> None:
    dossier = cognitive_dossier()
    before = repr(dossier)
    CognitiveAnalysisAuthority().analyze(dossier)
    assert repr(dossier) == before


def test_m389_1_authority_has_no_mutable_instance_state() -> None:
    authority = CognitiveAnalysisAuthority()
    before = vars(authority).copy()
    authority.analyze(cognitive_dossier())
    assert vars(authority) == before == {}

