from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "scripts" / "whole_personal_system_e2e_certification.py"
REPORT = ROOT / "docs" / "quality" / "WHOLE_PERSONAL_SYSTEM_E2E_CERTIFICATION.json"


def _module():
    spec = importlib.util.spec_from_file_location("whole_personal_system_e2e", HARNESS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_whole_personal_system_contract_is_diagnostic_and_complete():
    module = _module()
    report = module.run_certification()
    assert report.schema_version == "whole-personal-system-e2e-certification-v1"
    assert report.diagnostic_only is True
    assert report.production_roots_modified_by_harness == ()
    assert len(report.scenarios) == 10
    assert len(report.negative_controls) == 4


def test_whole_personal_system_all_personal_flows_are_certified():
    module = _module()
    report = module.run_certification()
    statuses = {item.scenario_id: item.status.value for item in report.scenarios}
    assert statuses == {
        "WPS-01": "PASS",
        "WPS-02": "PASS",
        "WPS-03": "PASS",
        "WPS-04": "PASS",
        "WPS-05": "PASS",
        "WPS-06": "PASS",
        "WPS-07": "PASS",
        "WPS-08": "PASS",
        "WPS-09": "PASS",
        "WPS-10": "PASS_BY_DESIGN",
    }
    assert report.overall_status.value == "PASS"
    assert report.primary_gap == "none_within_certified_whole_personal_system_contract"
    wps_01 = next(item for item in report.scenarios if item.scenario_id == "WPS-01")
    assert wps_01.reached_stages == (
        "identity_provisioning",
        "identity_selection",
        "runtime_binding",
        "conversation",
        "session_scope",
    )
    assert wps_01.evidence_paths == (
        "app/household_always_on_bootstrap.py",
        "app/personal_profile_factory.py",
        "app/local_runtime_entrypoint.py",
        "app/local_conversation_factory.py",
        "core/end_to_end_local_conversation/runtime.py",
    )
    assert (
        "core/personal_identity_and_session_profiles/registry.py"
        not in wps_01.evidence_paths
    )
    wps_06 = next(item for item in report.scenarios if item.scenario_id == "WPS-06")
    assert "do not imply durable personal commitment continuity" in wps_06.name
    source = HARNESS.read_text(encoding="utf-8")
    assert "compatibility-only continuity boundary" in source


def test_whole_personal_system_negative_controls_preserve_governance():
    module = _module()
    report = module.run_certification()
    assert all(
        item.status.value == "PASS_BY_DESIGN" for item in report.negative_controls
    )
    source = HARNESS.read_text(encoding="utf-8")
    for forbidden_write_target in ('Path("app/")', 'Path("core/")', 'Path("domain/")'):
        assert forbidden_write_target not in source


def test_frozen_whole_personal_system_report_matches_current_contract():
    module = _module()
    current = module.run_certification()
    frozen = json.loads(REPORT.read_text(encoding="utf-8"))
    assert frozen["schema_version"] == current.schema_version
    assert frozen["diagnostic_only"] is True
    assert frozen["production_roots_modified_by_harness"] == []
    assert frozen["status_counts"] == {
        "PASS": 9,
        "PASS_BY_DESIGN": 1,
        "PARTIAL": 0,
        "FAIL": 0,
    }
    assert frozen["overall_status"] == "PASS"
    assert (
        frozen["primary_gap"]
        == "none_within_certified_whole_personal_system_contract"
    )
    assert [item["scenario_id"] for item in frozen["scenarios"]] == [
        f"WPS-{index:02d}" for index in range(1, 11)
    ]


def test_governed_documentation_records_whole_personal_system_e2e():
    for filename in (
        "docs/history/ESTADO_MAESTRO_INTEGRAL.md",
        "README.md",
        "CHANGELOG.md",
        "architecture_rules.md",
    ):
        source = (ROOT / filename).read_text(encoding="utf-8")
        assert "Whole Personal System E2E" in source
