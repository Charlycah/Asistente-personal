from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "benchmarks" / "HCPDQ_V2_H6_FIRST_GROUND_TRUTH_SCORING.json"


def _result():
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_scoring_consumes_single_use_authorization():
    result = _result()
    assert result["scoring_authorization_consumed"] is True
    assert result["scoring_authorization_reusable"] is False


def test_scoring_covers_exactly_twelve_sealed_cases():
    result = _result()
    assert result["case_count"] == 12
    assert len(result["records"]) == 12
    assert [item["case_id"] for item in result["records"]] == [
        f"V2E-H6-{number:03d}" for number in range(1, 13)
    ]


def test_frozen_scoring_rule_yields_zero_of_twelve_passes():
    result = _result()
    assert result["pass_count"] == 0
    assert result["fail_count"] == 12
    assert result["accuracy"] == 0.0
    assert all(item["outcome"] == "FAIL" for item in result["records"])


def test_scoring_does_not_mutate_or_rerun_roby():
    result = _result()
    assert result["raw_capture_mutation_performed"] is False
    assert result["ground_truth_mutation_performed"] is False
    assert result["roby_rerun_performed"] is False


def test_scoring_does_not_enable_learning_feedback_or_tuning():
    result = _result()
    assert result["learning_or_adaptation_performed"] is False
    assert result["memory_writeback_performed"] is False
    assert result["benchmark_feedback_performed"] is False
    assert result["production_tuning_performed"] is False


def test_scoring_result_is_sealed_and_moves_to_result_audit():
    result = _result()
    assert result["results_sealed"] is True
    assert result["status"] == "SCORING_COMPLETED_RESULTS_SEALED"
    assert result["next_gate"].endswith("Scoring Post-Mortem / Cognitive Result Audit")
