from __future__ import annotations

import ast
from importlib import import_module
from pathlib import Path

cert = import_module(
    "scripts.whole_system_cross_capability_cognitive_integration_transfer_certification"
)

ROOT = Path(__file__).resolve().parents[2]
HARNESS = (
    ROOT
    / "scripts"
    / "whole_system_cross_capability_cognitive_integration_transfer_certification.py"
)


def _report():
    return cert.run_certification(ROOT)


def test_certification_has_exactly_ten_cross_capability_scenarios():
    report = _report()
    assert len(report.scenarios) == 10
    assert [item.scenario_id for item in report.scenarios] == [
        f"CCI-{i:02d}" for i in range(1, 11)
    ]


def test_status_vocabulary_is_frozen():
    assert {item.value for item in cert.CertificationStatus} == {
        "PASS",
        "PASS_BY_DESIGN",
        "PARTIAL",
        "FAIL",
    }


def test_current_baseline_closes_all_cross_capability_scenarios():
    report = _report()
    assert report.overall_status is cert.CertificationStatus.PASS
    assert report.status_counts["FAIL"] == 0
    assert report.status_counts["PARTIAL"] == 0


def test_learning_reuse_mental_model_reflection_and_transfer_are_reachable():
    by_id = {item.scenario_id: item for item in _report().scenarios}
    assert by_id["CCI-01"].status is cert.CertificationStatus.PASS
    assert by_id["CCI-02"].status is cert.CertificationStatus.PASS
    assert by_id["CCI-03"].status is cert.CertificationStatus.PASS
    assert by_id["CCI-04"].status is cert.CertificationStatus.PASS
    assert by_id["CCI-05"].status is cert.CertificationStatus.PASS
    assert by_id["CCI-06"].status is cert.CertificationStatus.PASS


def test_personality_and_irrelevant_memory_controls_pass_by_design():
    by_id = {item.scenario_id: item for item in _report().scenarios}
    assert by_id["CCI-08"].status is cert.CertificationStatus.PASS_BY_DESIGN
    assert by_id["CCI-09"].status is cert.CertificationStatus.PASS_BY_DESIGN


def test_changed_condition_replanning_advisory_is_reachable():
    by_id = {item.scenario_id: item for item in _report().scenarios}
    scenario = by_id["CCI-10"]
    assert scenario.status is cert.CertificationStatus.PASS
    assert scenario.missing_stages == ()


def test_harness_is_read_only_and_defines_no_power_role():
    report = _report()
    assert report.diagnostic_only
    assert report.production_roots_modified_by_harness == ()
    tree = ast.parse(HARNESS.read_text(encoding="utf-8"))
    class_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    }
    forbidden = {
        "CognitiveAuthority",
        "CognitiveManager",
        "CognitiveGateway",
        "AutonomousExecutor",
        "PersistenceManager",
    }
    assert class_names.isdisjoint(forbidden)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "subprocess" not in imports
    assert "sqlite3" not in imports


def test_report_fingerprints_are_stable_for_same_logical_state():
    first = _report()
    second = _report()
    assert first.inventory_fingerprint == second.inventory_fingerprint
    assert first.report_fingerprint == second.report_fingerprint


def test_harness_contains_no_production_write_target():
    source = HARNESS.read_text(encoding="utf-8")
    for target in ('Path("app/")', 'Path("core/")', 'Path("domain/")'):
        assert target not in source
