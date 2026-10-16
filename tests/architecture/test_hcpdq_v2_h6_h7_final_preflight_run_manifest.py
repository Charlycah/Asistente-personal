from __future__ import annotations

from scripts.hcpdq_v2_h6_h7_final_preflight_run_manifest import (
    freeze_final_run_manifest,
)


def test_final_preflight_binds_exact_h6_h7_scope_and_thirty_cases():
    report = freeze_final_run_manifest()
    assert report["preflight_passed"] is True
    assert report["scope"] == ["H6", "H7"]
    assert report["case_count"] == 30
    assert len(report["case_order"]) == 30


def test_final_preflight_freezes_order_and_zero_retry_policy():
    report = freeze_final_run_manifest()
    assert report["case_order"] == sorted(report["case_order"])
    assert report["ordering_rule"] == "lexicographic_case_id"
    assert report["retries_per_case"] == 0


def test_final_preflight_preserves_case_and_ground_truth_isolation():
    report = freeze_final_run_manifest()
    assert report["fresh_context_per_case"] is True
    assert report["cross_case_result_visibility"] is False
    assert report["ground_truth_available_to_subject"] is False
    assert report["ground_truth_loaded_by_subject_adapter"] is False


def test_final_preflight_preserves_zero_write_and_adaptation_policy():
    report = freeze_final_run_manifest()
    assert report["memory_writes_authorized"] is False
    assert report["learning_writes_authorized"] is False
    assert report["adaptation_authorized"] is False
    assert report["persistent_state_writes_authorized"] is False
    assert report["production_changes_authorized"] is False


def test_manifest_freeze_does_not_self_authorize_primary_execution():
    report = freeze_final_run_manifest()
    assert report["status"] == (
        "RUN_MANIFEST_FROZEN_EXECUTION_AUTHORIZATION_PENDING"
    )
    assert report["primary_execution_authorized"] is False
    assert report["execution_authorization_pending"] is True
    assert report["human_comparison_authorized"] is False
