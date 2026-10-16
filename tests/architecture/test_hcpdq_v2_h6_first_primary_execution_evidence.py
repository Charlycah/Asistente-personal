from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = (
    ROOT
    / "benchmarks"
    / "HCPDQ_V2_H6_FIRST_PRIMARY_HELD_OUT_EXECUTION.json"
)


def _evidence():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_primary_authorization_is_consumed_once():
    evidence = _evidence()
    assert evidence["authorization_consumed"] is True
    assert evidence["authorization_reusable"] is False


def test_primary_run_has_exactly_twelve_ordered_single_attempt_records():
    evidence = _evidence()
    assert evidence["case_count"] == 12
    assert evidence["case_order"] == [
        f"V2E-H6-{number:03d}" for number in range(1, 13)
    ]
    assert all(item["attempt_count"] == 1 for item in evidence["records"])
    assert evidence["retries_per_case"] == 0


def test_all_raw_captures_are_sealed_without_infrastructure_error():
    evidence = _evidence()
    assert evidence["sealed_raw_capture_count"] == 12
    assert evidence["infrastructure_error_count"] == 0
    assert evidence["raw_captures_sealed"] is True
    assert all(item["raw_response"] for item in evidence["records"])


def test_ground_truth_and_scoring_remained_outside_primary_execution():
    evidence = _evidence()
    assert evidence["ground_truth_loaded_during_execution"] is False
    assert evidence["scoring_performed_during_execution"] is False
    assert all(item["ground_truth_loaded"] is False for item in evidence["records"])
    assert all(item["scoring_performed"] is False for item in evidence["records"])


def test_learning_memory_and_feedback_remained_disabled():
    evidence = _evidence()
    assert evidence["learning_or_adaptation_performed"] is False
    assert evidence["memory_writeback_performed"] is False
    assert evidence["benchmark_feedback_performed"] is False


def test_execution_artifact_does_not_authorize_scoring_itself():
    evidence = _evidence()
    assert evidence["cognitive_scoring_authorized_in_this_artifact"] is False
    assert evidence["status"] == "PRIMARY_RUN_COMPLETED_RAW_CAPTURES_SEALED"
    assert evidence["next_gate"].endswith(
        "Post-Mortem / Evaluation-Boundary Audit"
    )
