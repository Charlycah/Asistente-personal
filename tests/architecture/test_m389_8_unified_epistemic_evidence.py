from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.cognitive_maturity import (
    EpistemicLevel,
    ExecutiveFinding,
    ExecutiveReport,
    ExecutiveReportStatus,
    UnifiedEpistemicCategory,
    UnifiedEpistemicEvidenceAuthority,
    UnifiedEpistemicStatus,
)

ROOT = Path(__file__).resolve().parents[2]


def _executive_report(*findings: ExecutiveFinding) -> ExecutiveReport:
    return ExecutiveReport(
        report_id="executive-report-m3898source",
        status=ExecutiveReportStatus.COMPLETE,
        audience_codes=("carlos", "cristina"),
        source_assessment_count=0,
        source_reflection_ids=(),
        source_history_id=None,
        source_psychology_id=None,
        source_pending_matters_id=None,
        source_periodic_reflection_id=None,
        findings=findings,
        open_matter_count=0,
        uncertainty_codes=(),
        recommendation_codes=(),
        evidence_codes=("certified_source",),
        risk_codes=(),
        source_fingerprint="m3898-source-fingerprint",
    )


def _finding(code: str, level: EpistemicLevel) -> ExecutiveFinding:
    return ExecutiveFinding(
        finding_code=code,
        source_authority="synthetic_certified_authority",
        source_reference="synthetic-report",
        epistemic_level=level,
        evidence_codes=("synthetic_coded_evidence",),
    )


def test_m389_8_has_one_read_only_unification_authority() -> None:
    authority = UnifiedEpistemicEvidenceAuthority()
    assert authority.authority_id == "unified_epistemic_evidence"


def test_m389_8_normalizes_all_epistemic_levels() -> None:
    report = UnifiedEpistemicEvidenceAuthority().unify(
        _executive_report(
            _finding("observed", EpistemicLevel.FACT),
            _finding("inferred", EpistemicLevel.INFERENCE),
            _finding("possible", EpistemicLevel.HYPOTHESIS),
            _finding("unknown", EpistemicLevel.UNKNOWN),
        )
    )
    categories = {item.statement_code: item.category for item in report.records}
    assert categories == {
        "observed": UnifiedEpistemicCategory.OBSERVED,
        "inferred": UnifiedEpistemicCategory.INFERRED,
        "possible": UnifiedEpistemicCategory.POSSIBLE,
        "unknown": UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION,
    }


def test_m389_8_public_language_is_explicit_and_prudent() -> None:
    report = UnifiedEpistemicEvidenceAuthority().unify(
        _executive_report(_finding("possible", EpistemicLevel.HYPOTHESIS))
    )
    record = report.records[0]
    assert record.public_statement == "Esta es solamente una posibilidad."
    assert record.allows_fact_statement is False
    assert record.requires_human_review is True


def test_m389_8_empty_sources_report_insufficient_evidence() -> None:
    report = UnifiedEpistemicEvidenceAuthority().unify(None)
    assert report.status is UnifiedEpistemicStatus.INSUFFICIENT_EVIDENCE
    assert report.records == ()


def test_m389_8_detects_conflicting_categories_without_resolving_them() -> None:
    report = UnifiedEpistemicEvidenceAuthority().unify(
        _executive_report(
            _finding("shared_statement", EpistemicLevel.FACT),
            ExecutiveFinding(
                finding_code="shared_statement",
                source_authority="second_certified_authority",
                source_reference="second-report",
                epistemic_level=EpistemicLevel.HYPOTHESIS,
                evidence_codes=("second_coded_evidence",),
            ),
        )
    )
    assert report.status is UnifiedEpistemicStatus.CONFLICT_REVIEW_REQUIRED
    assert report.conflict_codes == ("epistemic_conflict:shared_statement",)


def test_m389_8_report_has_no_side_effects() -> None:
    report = UnifiedEpistemicEvidenceAuthority().unify(None)
    assert report.read_only is True
    assert report.grants_authority is False
    assert report.contains_conversation_content is False
    assert report.creates_memory is False
    assert report.modifies_memory is False
    assert report.modifies_learning is False
    assert report.modifies_planning is False
    assert report.modifies_permissions is False
    assert report.creates_task is False
    assert report.creates_reminder is False
    assert report.schedules_action is False
    assert report.executes_action is False


def test_m389_8_report_is_deterministic_and_immutable() -> None:
    authority = UnifiedEpistemicEvidenceAuthority()
    source = _executive_report(_finding("observed", EpistemicLevel.FACT))
    report = authority.unify(source)
    assert report == authority.unify(source)
    with pytest.raises(FrozenInstanceError):
        report.status = UnifiedEpistemicStatus.DEGRADED


def test_m389_8_safe_failure_degrades_without_authority() -> None:
    class BrokenAuthority(UnifiedEpistemicEvidenceAuthority):
        def unify(self, executive_report, assessments=()):
            raise RuntimeError("synthetic failure")

    report = BrokenAuthority().unify_safely(None)
    assert report.status is UnifiedEpistemicStatus.DEGRADED
    assert report.risk_codes == ("unified_epistemic_evidence_failure",)
    assert report.grants_authority is False


def test_m389_8_source_avoids_sensitive_and_governed_domains() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "unified_epistemic_evidence.py"
    source = path.read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source
    forbidden_names = (
        "memory_store",
        "learning_engine",
        "planner",
        "permission_manager",
    )
    for forbidden in forbidden_names:
        assert forbidden not in source


def test_m389_8_gateway_constructor_remains_only_on_line_52() -> None:
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
