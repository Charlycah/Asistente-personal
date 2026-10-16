from pathlib import Path

from app.cognitive_analysis_authority import CognitiveAnalysisAuthority
from tests.architecture.m389_1_support import cognitive_dossier

ROOT = Path(__file__).resolve().parents[2]


def test_m389_1_analysis_has_no_hidden_effects_or_operational_imports() -> None:
    source = (ROOT / "app" / "cognitive_analysis_authority.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "OfficialMemoryGateway",
        "CanonicalPlanningFacade",
        "CanonicalDecisionFacade",
        "ToolGateway",
        "LearningCandidate",
        "credentials.json",
    )
    assert all(name not in source for name in forbidden)


def test_m389_1_analysis_does_not_create_files_or_change_turn_identity(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    dossier = cognitive_dossier()
    before = tuple(tmp_path.iterdir())
    report = CognitiveAnalysisAuthority().analyze(dossier)
    assert tuple(tmp_path.iterdir()) == before
    assert report.cycle_id == dossier.cycle_id
    assert report.dossier_id == dossier.dossier_id

