from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.cognitive_maturity import (
    ExecutiveReportingAuthority,
    ExecutiveReportStatus,
)

ROOT = Path(__file__).resolve().parents[2]


def test_m389_7_has_one_read_only_executive_authority() -> None:
    authority = ExecutiveReportingAuthority()
    assert authority.authority_id == "executive_reporting"


def test_m389_7_empty_sources_report_insufficient_evidence() -> None:
    report = ExecutiveReportingAuthority().compile((), (), None, None, None, None)
    assert report.status is ExecutiveReportStatus.INSUFFICIENT_EVIDENCE
    assert report.audience_codes == ("carlos", "cristina")
    assert report.read_only is True


def test_m389_7_report_has_no_side_effects() -> None:
    report = ExecutiveReportingAuthority().compile((), (), None, None, None, None)
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
    assert report.executes_recommendation is False


def test_m389_7_report_is_deterministic() -> None:
    authority = ExecutiveReportingAuthority()
    args = ((), (), None, None, None, None)
    assert authority.compile(*args) == authority.compile(*args)


def test_m389_7_report_is_immutable() -> None:
    report = ExecutiveReportingAuthority().compile((), (), None, None, None, None)
    with pytest.raises(FrozenInstanceError):
        report.status = ExecutiveReportStatus.COMPLETE


def test_m389_7_safe_failure_degrades_without_authority() -> None:
    class BrokenAuthority(ExecutiveReportingAuthority):
        def compile(self, *args, **kwargs):
            raise RuntimeError("synthetic failure")

    report = BrokenAuthority().compile_safely((), (), None, None, None, None)
    assert report.status is ExecutiveReportStatus.DEGRADED
    assert report.risk_codes == ("executive_reporting_failure",)
    assert report.grants_authority is False


def test_m389_7_source_avoids_sensitive_and_governed_domains() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "executive_reporting.py"
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


def test_m389_7_gateway_constructor_remains_only_on_line_52() -> None:
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
