from __future__ import annotations

from scripts.hcpdq_v2_h6_h7_isolation_adapter_recertification import (
    recertify_h6_h7_isolation_adapter,
)


def test_adapter_is_causally_recertified_without_new_authority():
    report = recertify_h6_h7_isolation_adapter()
    assert report["causal_recertification_passed"] is True
    assert report["new_authority_detected"] is False
    assert report["production_cognitive_change_detected"] is False


def test_adapter_preserves_minimal_envelope_and_zero_write_capabilities():
    report = recertify_h6_h7_isolation_adapter()
    assert report["minimal_envelope_preserved"] is True
    assert report["zero_write_capabilities"] is True


def test_adapter_has_no_ground_truth_loader_or_filesystem_write_path():
    report = recertify_h6_h7_isolation_adapter()
    assert report["no_ground_truth_loader"] is True
    assert report["no_filesystem_write_path"] is True


def test_adapter_preserves_case_isolation_and_raw_before_scoring():
    report = recertify_h6_h7_isolation_adapter()
    assert report["cross_case_results_hidden"] is True
    assert report["raw_capture_precedes_scoring"] is True


def test_adapter_keeps_primary_execution_and_comparison_no_go():
    report = recertify_h6_h7_isolation_adapter()
    assert report["primary_execution_raises"] is True
    assert report["primary_execution_authorized"] is False
    assert report["ground_truth_visibility_authorized"] is False
    assert report["learning_or_adaptation_authorized"] is False
    assert report["human_comparison_authorized"] is False
