from __future__ import annotations

import inspect
from pathlib import Path

from scripts.advanced_capability_5a_autonomy_boundary_certification import (
    run_certification,
)

ROOT = Path(__file__).resolve().parents[2]


def _report():
    return run_certification(ROOT)


def test_5a_certification_passes_all_frozen_boundary_checks():
    report = _report()
    assert report.status == "pass"
    assert len(report.checks) == 10
    assert all(item.passed for item in report.checks)
    assert report.authority_violations == 0
    assert report.unauthorized_executions == 0
    assert report.autonomy_escalations == 0


def test_5a_inventory_classifies_autonomy_per_capability_not_globally():
    report = _report()
    levels = {entry.capability: entry.autonomy_level for entry in report.entries}
    assert levels["governed_reasoning"] == "A1_ANALYZE"
    assert levels["gcdr.advisory"] == "A2_RECOMMEND"
    assert levels["self_diagnostics.proposal"] == "A3_PREPARE"
    assert levels["mail.send"] == "A4_EXECUTE_WITH_APPROVAL"
    assert levels["self_improvement.apply"] == "A5_NOT_AUTHORIZED"


def test_5a_mutating_execution_requires_exact_consent_and_gateway():
    report = _report()
    checks = {item.check_id: item for item in report.checks}
    assert checks["5A-04"].passed
    assert "handler_calls=0" in checks["5A-04"].observed
    assert checks["5A-05"].passed
    assert "handler_calls=1" in checks["5A-05"].observed
    assert checks["5A-06"].passed
    assert "handler_calls=0" in checks["5A-06"].observed


def test_5a_unregistered_and_disabled_capabilities_fail_closed():
    report = _report()
    checks = {item.check_id: item for item in report.checks}
    assert "capability_not_registered" in checks["5A-07"].observed
    assert "capability_disabled" in checks["5A-08"].observed
    assert checks["5A-07"].passed
    assert checks["5A-08"].passed


def test_5a_self_improvement_remains_approval_not_application():
    report = _report()
    checks = {item.check_id: item for item in report.checks}
    assert checks["5A-09"].passed
    assert checks["5A-10"].passed
    entry = next(
        item for item in report.entries if item.capability == "self_improvement.apply"
    )
    assert entry.default_enabled is False
    assert entry.execution_boundary == "none"
    assert entry.autonomy_level == "A5_NOT_AUTHORIZED"


def test_5a_harness_is_diagnostic_and_does_not_define_execution_authority():
    import scripts.advanced_capability_5a_autonomy_boundary_certification as module

    source = inspect.getsource(module)
    assert "class AutonomyAuthority" not in source
    assert "class AutonomousExecutor" not in source
    assert "allow_unattended_execution=True" in source
    for forbidden_import in (
        "import requests",
        "import httpx",
        "import subprocess",
        "import os",
        "from app.official_memory_gateway",
    ):
        assert forbidden_import not in source


def test_5a_report_fingerprint_is_stable_for_same_logical_state():
    first = _report()
    second = _report()
    assert first.inventory_fingerprint == second.inventory_fingerprint
    assert first.report_fingerprint == second.report_fingerprint


def test_5a_documentation_preserves_historical_headers():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    assert readme.startswith("## Milestone M393.1")
    assert changelog.startswith("# M347.15 — Estabilización de la serie")
    assert "Advanced Capability 5A" in readme
    assert "Advanced Capability 5A" in changelog
    assert "Advanced Capability 5A" in rules
