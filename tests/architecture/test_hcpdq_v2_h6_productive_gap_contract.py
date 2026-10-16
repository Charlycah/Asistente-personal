from __future__ import annotations

from scripts.hcpdq_v2_h6_productive_gap_contract import (
    freeze_h6_productive_gap_contract,
)


def test_contract_emits_limited_general_productive_go():
    report = freeze_h6_productive_gap_contract()
    assert report["status"] == "LIMITED_PRODUCTIVE_CHANGE_AUTHORIZED_GO"
    assert report["production_implementation_authorized"] is True
    assert report["implementation_must_be_general"] is True


def test_contract_preserves_required_constraint_blocking():
    report = freeze_h6_productive_gap_contract()
    rules = report["contract_rules"]
    assert "continues to BLOCK" in rules["R1"]
    assert report["required_constraint_weakening_authorized"] is False


def test_contract_distinguishes_missing_from_negative_evidence():
    report = freeze_h6_productive_gap_contract()
    rules = report["contract_rules"]
    assert "not negative evidence" in rules["R2"]
    assert "normally remains INSUFFICIENT" in rules["R3"]


def test_contract_allows_only_sole_required_constraint_survivor():
    report = freeze_h6_productive_gap_contract()
    rules = report["contract_rules"]
    assert "exactly one option survives" in rules["R4"]
    assert "every competing option is BLOCKED" in rules["R4"]
    assert "sole required-criterion survivor" in rules["R5"]


def test_contract_does_not_authorize_generic_incomplete_dominance():
    report = freeze_h6_productive_gap_contract()
    assert report["generic_missing_evidence_relaxation_authorized"] is False
    assert "No recommendation is authorized merely" in (
        report["contract_rules"]["R6"]
    )


def test_contract_separates_first_six_from_required_cases():
    report = freeze_h6_productive_gap_contract()
    disposition = report["hcpdq_case_disposition"]
    assert disposition["V2E-H6-001_to_006"].startswith(
        "NO_CHANGE_AUTHORIZED"
    )
    assert disposition["V2E-H6-007_to_012"].startswith("IN_SCOPE")


def test_contract_forbids_benchmark_boundary_changes_and_rerun():
    report = freeze_h6_productive_gap_contract()
    assert report["benchmark_specific_behavior_authorized"] is False
    assert report["adapter_change_authorized"] is False
    assert report["entry_path_change_authorized"] is False
    assert report["scoring_change_authorized"] is False
    assert report["ground_truth_change_authorized"] is False
    assert report["held_out_rerun_authorized"] is False
    assert report["rescoring_old_primary_result_authorized"] is False
