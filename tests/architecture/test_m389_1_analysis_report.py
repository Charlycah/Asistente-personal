from dataclasses import fields

from app.cognitive_analysis_authority import CognitiveAnalysisAuthority
from tests.architecture.m389_1_support import cognitive_dossier


def test_m389_1_report_is_structured_private_and_non_authoritative() -> None:
    report = CognitiveAnalysisAuthority().analyze(cognitive_dossier())
    assert report.schema_version == "m389.1"
    assert report.read_only is True
    assert report.deterministic is True
    assert report.grants_authority is False
    assert report.contains_conversation_content is False
    assert report.modifies_productive_state is False
    forbidden = {"response", "memory", "planning", "permission", "learning"}
    assert forbidden.isdisjoint({field.name for field in fields(report)})


def test_m389_1_report_keeps_source_lineage() -> None:
    dossier = cognitive_dossier()
    report = CognitiveAnalysisAuthority().analyze(dossier)
    assert report.dossier_id == dossier.dossier_id
    assert report.cycle_id == dossier.cycle_id
    assert report.source_evidence_fingerprint == dossier.evidence_fingerprint

