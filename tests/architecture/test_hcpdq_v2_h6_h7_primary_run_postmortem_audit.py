from __future__ import annotations

from scripts.hcpdq_v2_h6_h7_primary_run_postmortem_audit import (
    audit_primary_run_evaluation_boundary,
)


def test_postmortem_rejects_primary_run_as_performance_evidence():
    report = audit_primary_run_evaluation_boundary()
    assert report["cognitive_scoring_valid"] is False
    assert report["performance_conclusion_authorized"] is False
    assert report["roby_cognitive_failure_demonstrated"] is False


def test_h6_failure_is_calibration_to_prompt_grammar_mismatch():
    report = audit_primary_run_evaluation_boundary()
    assert report["h6_all_frozen_prompts_not_envelope"] is True
    assert set(report["h6_prompt_statuses"].values()) == {"not_envelope"}
    assert report["families"]["H6"]["held_out_entry_equivalent"] is False


def test_h7_failure_is_internal_reentry_not_conversational_equivalence():
    report = audit_primary_run_evaluation_boundary()
    assert report["h7_gateway_canonical_planning_bound"] is False
    assert report["families"]["H7"]["held_out_entry_equivalent"] is False
    assert "planning re-entry" in (
        report["families"]["H7"]["certified_path_kind"]
    )


def test_postmortem_does_not_blame_corpus_truth_or_authorize_retries():
    report = audit_primary_run_evaluation_boundary()
    assert report["corpus_content_invalid"] is False
    assert report["ground_truth_invalid"] is False
    assert report["held_out_retry_authorized"] is False
    assert report["new_primary_execution_authorized"] is False


def test_postmortem_forbids_product_changes_and_benchmark_router():
    report = audit_primary_run_evaluation_boundary()
    assert report["production_change_authorized"] is False
    assert report["benchmark_specific_router_authorized"] is False
    assert report["status"] == "EVALUATION_DESIGN_INVALID_RECONTRACT_REQUIRED"
