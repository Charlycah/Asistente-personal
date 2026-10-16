from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "benchmarks" / "HCPDQ_V2_H6_H7_FIRST_PRIMARY_HELD_OUT_EXECUTION.json"


def _evidence() -> dict[str, object]:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_primary_execution_consumed_single_use_authorization():
    report = _evidence()
    assert report["execution_occurred"] is True
    assert report["authorization_consumed"] is True
    assert report["authorization_reusable"] is False
    assert report["authorized_run_count"] == 1


def test_primary_execution_attempted_every_case_once_without_retries():
    report = _evidence()
    assert report["case_count"] == 30
    assert report["attempted_case_count"] == 30
    assert report["attempts_per_case"] == 1
    assert report["retries_per_case"] == 0
    assert all(item["attempt_count"] == 1 for item in report["records"])


def test_primary_execution_failed_closed_before_valid_raw_capture():
    report = _evidence()
    assert report["raw_capture_count"] == 0
    assert report["infrastructure_error_count"] == 30
    assert report["status"] == (
        "PRIMARY_RUN_COMPLETED_FAIL_CLOSED_EVALUATION_BOUNDARY_INVALID"
    )


def test_invalid_boundary_run_is_not_cognitive_scoring_evidence():
    report = _evidence()
    assert report["cognitive_scoring_performed"] is False
    assert report["ground_truth_loaded_during_execution"] is False
    assert report["human_comparison_performed"] is False


def test_failed_run_did_not_change_production_or_adapt_roby():
    report = _evidence()
    assert report["production_changes_performed"] is False
    assert report["learning_or_adaptation_performed"] is False
