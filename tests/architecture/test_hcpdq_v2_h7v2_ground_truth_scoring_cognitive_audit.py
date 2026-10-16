from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS = ROOT / "benchmarks"
TRUTH = BENCHMARKS / "HCPDQ_V2_H7_ENTRY_EQUIVALENT_GROUND_TRUTH_V2.json"
RUN = BENCHMARKS / "HCPDQ_V2_H7V2_FIRST_PRIMARY_EXECUTION.json"
AUDIT = BENCHMARKS / "HCPDQ_V2_H7V2_GROUND_TRUTH_SCORING_COGNITIVE_AUDIT.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_h7v2_scoring_is_bound_to_sealed_truth_and_raw_run():
    audit = _load(AUDIT)
    run = _load(RUN)
    assert (
        hashlib.sha256(TRUTH.read_bytes()).hexdigest()
        == (audit["ground_truth_file_sha256"])
    )
    assert audit["aggregate_raw_run_sha256"] == run["aggregate_raw_run_sha256"]
    assert audit["sealed_inputs_verified_before_scoring"] is True


def test_h7v2_scores_all_twelve_held_out_cases():
    audit = _load(AUDIT)
    assert audit["case_count"] == 12
    assert len(audit["case_scores"]) == 12
    assert audit["correct_cases"] + audit["incorrect_cases"] == 12


def test_h7v2_all_cases_match_every_frozen_scoring_field():
    audit = _load(AUDIT)
    assert audit["correct_cases"] == 12
    assert audit["incorrect_cases"] == 0
    assert audit["accuracy"] == 1.0
    assert all(case["all_expected_fields_match"] for case in audit["case_scores"])


def test_h7v2_each_causal_family_scores_four_of_four():
    families = _load(AUDIT)["family_scores"]
    assert families == {
        "D1": {"correct": 4, "total": 4},
        "D2": {"correct": 4, "total": 4},
        "D3": {"correct": 4, "total": 4},
    }


def test_h7v2_scoring_checks_decision_eligibility_status_and_invocation():
    fields = set(_load(AUDIT)["scoring_fields"])
    assert fields == {
        "continuation_decision",
        "planning_reentry_status",
        "planning_invocation_count",
        "eligible_for_existing_planning",
    }


def test_h7v2_cognitive_audit_detects_no_productive_gap():
    audit = _load(AUDIT)
    assert audit["cognitive_gap_detected"] is False
    assert audit["productive_change_required"] is False
    assert audit["closure_decision"] == "H7_CLOSED_PASS"


def test_h7v2_scoring_performs_no_learning_or_writeback():
    audit = _load(AUDIT)
    assert audit["learning_or_writeback_performed"] is False
    assert audit["historical_failed_h7_run_reinterpreted"] is False
