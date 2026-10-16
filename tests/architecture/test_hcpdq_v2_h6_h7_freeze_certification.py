from __future__ import annotations

from scripts.hcpdq_v2_h6_h7_freeze_certification import (
    certify_h6_h7_held_out_freeze,
)


def test_freeze_certification_passes_integrity_and_independence():
    report = certify_h6_h7_held_out_freeze()
    assert report["integrity_pass"] is True
    assert report["independence_pass"] is True
    assert report["contamination_detected"] is False


def test_certification_preserves_frozen_scope_and_distribution():
    report = certify_h6_h7_held_out_freeze()
    assert report["certified_scope"] == ["H6", "H7"]
    assert report["case_count"] == 30
    assert report["family_counts"] == {"H6": 15, "H7": 15}
    assert report["difficulty_counts"] == {"D1": 10, "D2": 10, "D3": 10}


def test_certification_authorizes_only_controlled_read_only_exposure():
    report = certify_h6_h7_held_out_freeze()
    assert report["status"] == "CERTIFIED_EXPOSURE_AUTHORIZED"
    assert report["roby_exposure_authorized"] is True
    assert report["exposure_mode"] == "CONTROLLED_READ_ONLY_EVALUATION"


def test_certification_does_not_authorize_primary_execution_or_comparison():
    report = certify_h6_h7_held_out_freeze()
    assert report["held_out_execution_authorized"] is False
    assert report["human_comparison_authorized"] is False
    assert report["ground_truth_visibility_to_roby_authorized"] is False


def test_certification_forbids_production_change_adaptation_and_learning():
    report = certify_h6_h7_held_out_freeze()
    assert report["production_changes_authorized"] is False
    assert report["adaptation_or_learning_authorized"] is False
