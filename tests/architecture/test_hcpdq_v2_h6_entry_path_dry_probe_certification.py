from __future__ import annotations

from scripts.hcpdq_v2_h6_entry_path_dry_probe_certification import (
    certify_h6_entry_path_dry_probes,
)


def test_three_non_held_out_dry_probes_certify_existing_h6_entry_path():
    report = certify_h6_entry_path_dry_probes()
    assert report["dry_probe_count"] == 3
    assert report["dry_probes_are_held_out"] is False
    assert report["entry_path_certified"] is True
    assert all(
        item["intake_status"] == "complete"
        for item in report["dry_probe_records"]
    )


def test_dry_probes_reach_productive_path_without_runtime_fallback():
    report = certify_h6_entry_path_dry_probes()
    assert all(
        item["runtime_fallback_reached"] is False
        for item in report["dry_probe_records"]
    )
    assert all(
        item["productive_response_captured"] is True
        for item in report["dry_probe_records"]
    )


def test_dry_probe_certification_authorizes_independent_construction():
    report = certify_h6_entry_path_dry_probes()
    assert report["status"] == (
        "DRY_PROBES_CERTIFIED_CONSTRUCTION_AUTHORIZED"
    )
    assert report["construction_authorized"] is True
    assert report["ground_truth_construction_authorized"] is True


def test_certification_does_not_authorize_exposure_or_execution():
    report = certify_h6_entry_path_dry_probes()
    assert report["held_out_exposure_authorized"] is False
    assert report["roby_held_out_execution_authorized"] is False
    assert report["primary_execution_authorized"] is False


def test_dry_probes_cannot_be_reused_and_no_benchmark_changes_are_allowed():
    report = certify_h6_entry_path_dry_probes()
    assert report["dry_probe_reuse_as_held_out_authorized"] is False
    assert report["old_consumed_case_reuse_authorized"] is False
    assert report["production_change_authorized"] is False
    assert report["benchmark_translation_authorized"] is False
    assert report["benchmark_router_authorized"] is False
