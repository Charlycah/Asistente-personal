from __future__ import annotations

import ast
from pathlib import Path

from scripts.whole_system_e2e_reachability_coherence_certification import (
    CertificationStatus,
    run_certification,
)

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "scripts/whole_system_e2e_reachability_coherence_certification.py"


def _report():
    return run_certification(ROOT)


def test_whole_system_harness_certifies_exactly_16_e2e_chains():
    report = _report()
    assert len(report.chains) == 16
    assert [item.chain_id for item in report.chains] == [
        f"E2E-{index:02d}" for index in range(1, 17)
    ]
    assert all(
        item.status in {CertificationStatus.PASS, CertificationStatus.PASS_BY_DESIGN}
        for item in report.chains
    )
    assert report.overall_status is CertificationStatus.PASS


def test_whole_system_harness_certifies_exactly_8_non_escalation_controls():
    report = _report()
    assert len(report.negative_controls) == 8
    assert [item.control_id for item in report.negative_controls] == [
        f"NEG-{index:02d}" for index in range(1, 9)
    ]
    assert all(
        item.status is CertificationStatus.PASS_BY_DESIGN
        for item in report.negative_controls
    )


def test_every_chain_measures_entry_authority_consumer_and_observable():
    for item in _report().chains:
        assert item.entry.strip()
        assert item.authority_or_capability.strip()
        assert item.productive_consumer.strip()
        assert item.authorized_observable.strip()
        assert item.reachable_stages == item.total_stages


def test_every_chain_preserves_provenance_scope_and_historical_requirements():
    for item in _report().chains:
        assert item.provenance_preserved
        assert item.scope_preserved
        assert item.historical_route_preserved
        assert item.missing_evidence == ()


def test_status_vocabulary_is_frozen():
    assert {item.value for item in CertificationStatus} == {
        "PASS",
        "PASS_BY_DESIGN",
        "PARTIAL",
        "FAIL",
    }


def test_harness_is_diagnostic_and_defines_no_production_power_role():
    report = _report()
    assert report.diagnostic_only
    assert report.production_roots_modified_by_harness == ()

    tree = ast.parse(HARNESS.read_text(encoding="utf-8"))
    class_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    }
    forbidden_classes = {
        "WholeSystemAuthority",
        "WholeSystemManager",
        "WholeSystemGateway",
        "AutonomousExecutor",
        "PersistenceManager",
    }
    assert class_names.isdisjoint(forbidden_classes)

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


def test_harness_does_not_require_changes_inside_production_roots():
    source = HARNESS.read_text(encoding="utf-8")
    for forbidden_write_target in (
        'Path("app/")',
        'Path("core/")',
        'Path("domain/")',
    ):
        assert forbidden_write_target not in source


def test_root_documentation_records_the_frozen_certification_contract():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    assert "Whole-System E2E Reachability & Coherence Certification" in readme
    assert "Whole-System E2E Reachability & Coherence Certification" in changelog
    assert "Whole-System E2E Reachability & Coherence Certification" in rules
    assert readme.startswith("## Milestone M393.1")
    assert changelog.startswith("# M347.15 — Estabilización de la serie")
