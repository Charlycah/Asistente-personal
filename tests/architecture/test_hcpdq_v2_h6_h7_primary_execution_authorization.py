from __future__ import annotations

from scripts.hcpdq_v2_h6_h7_primary_execution_authorization import (
    authorize_primary_execution,
)


def test_primary_execution_authorization_is_go_for_one_run_only():
    report = authorize_primary_execution()
    assert report["status"] == "GO_SINGLE_PRIMARY_HELD_OUT_EXECUTION"
    assert report["preconditions_passed"] is True
    assert report["primary_execution_authorized"] is True
    assert report["authorized_run_count"] == 1
    assert report["authorization_reusable"] is False


def test_authorization_is_bound_to_exact_frozen_h6_h7_manifest():
    report = authorize_primary_execution()
    assert report["manifest_stable"] is True
    assert report["authorized_scope"] == ["H6", "H7"]
    assert report["authorized_case_count"] == 30
    assert len(report["authorized_case_order"]) == 30


def test_authorization_preserves_case_isolation_and_zero_retries():
    report = authorize_primary_execution()
    assert report["retries_per_case"] == 0
    assert report["fresh_context_per_case"] is True
    assert report["cross_case_result_visibility"] is False
    assert report["raw_capture_required_before_scoring"] is True


def test_authorization_keeps_ground_truth_and_state_writes_closed():
    report = authorize_primary_execution()
    assert report["ground_truth_available_to_subject"] is False
    assert report["ground_truth_loaded_by_subject_adapter"] is False
    assert report["memory_writes_authorized"] is False
    assert report["learning_writes_authorized"] is False
    assert report["adaptation_authorized"] is False
    assert report["persistent_state_writes_authorized"] is False


def test_authorization_does_not_execute_or_enable_comparison_or_changes():
    report = authorize_primary_execution()
    assert report["execution_occurred"] is False
    assert report["production_changes_authorized"] is False
    assert report["human_comparison_authorized"] is False
