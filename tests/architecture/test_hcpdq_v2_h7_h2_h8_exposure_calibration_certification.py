from __future__ import annotations

from scripts.hcpdq_v2_h7_h2_h8_exposure_calibration_certification import (
    certify_wave1_calibration,
)


def test_h7_real_productive_calibration_path_is_certified():
    report = certify_wave1_calibration()
    h7 = report["families"]["H7"]
    probe = report["h7_positive_probe"]
    assert h7["exposure_certified"] is True
    assert h7["verdict"] == "CERTIFIED_CALIBRATION_EXPOSURE"
    assert probe["planning_authority"] == "planning_foundation"
    assert probe["planning_invocation_count"] == 1
    assert probe["execution_authorized"] is False


def test_h2_remains_fail_closed_without_shared_causal_lineage():
    report = certify_wave1_calibration()
    h2 = report["families"]["H2"]
    assert h2["existing_productive_path_observed"] is True
    assert h2["causal_join_observed"] is False
    assert h2["exposure_certified"] is False
    assert h2["verdict"] == "NO_GO_UNJOINED_EXISTING_EVIDENCE"


def test_h8_remains_fail_closed_without_shared_causal_lineage():
    report = certify_wave1_calibration()
    h8 = report["families"]["H8"]
    assert h8["existing_productive_path_observed"] is True
    assert h8["causal_join_observed"] is False
    assert h8["exposure_certified"] is False
    assert h8["verdict"] == "NO_GO_UNJOINED_EXISTING_EVIDENCE"


def test_wave1_calibration_certifies_only_h7():
    report = certify_wave1_calibration()
    assert report["newly_exposure_certified_families"] == ["H7"]
    assert report["remaining_uncertified_families"] == ["H2", "H8"]


def test_wave1_calibration_keeps_all_global_gates_closed():
    report = certify_wave1_calibration()
    assert report["production_change_authorized"] is False
    assert report["new_authority_authorized"] is False
    assert report["held_out_construction_authorized"] is False
    assert report["human_comparison_authorized"] is False
