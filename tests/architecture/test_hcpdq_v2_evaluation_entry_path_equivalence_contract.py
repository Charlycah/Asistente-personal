from __future__ import annotations

from scripts.hcpdq_v2_evaluation_entry_path_equivalence_contract import (
    evaluate_entry_path_equivalence,
)


def test_entry_path_equivalence_is_mandatory_and_current_freeze_is_no_go():
    report = evaluate_entry_path_equivalence()
    assert report["entry_path_equivalence_certified"] is False
    assert report["status"] == "NO_GO_REFREEZE_REQUIRED"
    assert report["current_h6_h7_freeze_reusable"] is False


def test_h6_and_h7_both_fail_entry_path_equivalence():
    report = evaluate_entry_path_equivalence()
    assert report["family_results"]["H6"]["entry_path_equivalent"] is False
    assert report["family_results"]["H7"]["entry_path_equivalent"] is False
    assert report["family_results"]["H6"]["go"] is False
    assert report["family_results"]["H7"]["go"] is False


def test_contract_forbids_router_translation_and_production_changes():
    report = evaluate_entry_path_equivalence()
    assert report["benchmark_specific_translation_authorized"] is False
    assert report["benchmark_specific_router_authorized"] is False
    assert report["production_change_authorized"] is False


def test_contract_forbids_retry_and_semantic_rewrite_of_consumed_freeze():
    report = evaluate_entry_path_equivalence()
    assert report["held_out_retry_authorized"] is False
    assert report["new_primary_execution_authorized"] is False
    assert report["corpus_semantic_rewrite_authorized"] is False


def test_contract_allows_only_recontract_and_new_independent_freeze():
    report = evaluate_entry_path_equivalence()
    assert report["recontract_authorized"] is True
    assert "new independent freeze" in report["recontract_scope"]
    assert report["ground_truth_change_authorized"] is False
