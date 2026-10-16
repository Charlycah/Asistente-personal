from __future__ import annotations

from scripts.hcpdq_v2_calibration_path_coverage_certification import (
    certify_calibration_path_coverage,
)


def test_h6_positive_calibration_reaches_existing_productive_authority():
    report = certify_calibration_path_coverage()
    h6 = report["family_results"]["H6"]
    probe = report["h6_positive_probe"]
    assert h6["authority_path_certified"] is True
    assert h6["verdict"] == "CERTIFIED_CALIBRATION_PATH"
    assert probe["validity"] == "valid"
    assert probe["response_path"] == "interceptor"
    assert probe["runtime_fallback_calls"] == 0
    assert "governed_complex_decision_reasoning" in probe["rationale"]


def test_uncertified_families_fail_closed():
    report = certify_calibration_path_coverage()
    for family in ("H1", "H2", "H3", "H4", "H5", "H7", "H8"):
        item = report["family_results"][family]
        assert item["authority_exists"] is True
        assert item["authority_path_certified"] is False
        assert item["held_out_authorized"] is False
        assert item["verdict"] == "NO_GO"


def test_hcpdq_v2_held_out_remains_no_go_until_all_eight_are_certified():
    report = certify_calibration_path_coverage()
    assert report["certified_family_count"] == 1
    assert report["required_family_count"] == 8
    assert report["held_out_construction_authorized"] is False
    assert report["human_comparison_authorized"] is False
    assert report["production_changes_authorized"] is False


def test_certification_has_stable_fingerprint():
    first = certify_calibration_path_coverage()
    second = certify_calibration_path_coverage()
    assert first["certification_fingerprint"] == second["certification_fingerprint"]
