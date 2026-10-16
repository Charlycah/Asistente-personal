from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "benchmarks" / "HCPDQ_V2_H7_FIRST_PRIMARY_HELD_OUT_EXECUTION.json"


def _evidence():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_h7_single_authorized_primary_run_was_consumed_once():
    evidence = _evidence()
    assert evidence["authorization_consumed"] is True
    assert evidence["authorization_reusable"] is False
    assert evidence["execution_occurred"] is True
    assert evidence["retry_performed"] is False
    assert evidence["second_primary_run_authorized"] is False


def test_h7_primary_run_failed_closed_on_first_frozen_case():
    evidence = _evidence()
    assert evidence["status"] == ("PRIMARY_RUN_ABORTED_FAIL_CLOSED_RAW_RUN_NOT_SEALED")
    assert evidence["attempted_case_count"] == 1
    assert evidence["completed_case_count"] == 0
    assert evidence["abort_case_id"] == "V2I-H7-001"
    assert evidence["sealed_raw_capture_count"] == 0
    assert evidence["aggregate_raw_run_sha256"] is None


def test_h7_abort_is_evaluation_boundary_infrastructure_error():
    evidence = _evidence()
    assert evidence["measurement_validity"] == (
        "evaluation_boundary_infrastructure_error"
    )
    assert "req-h7-001" in evidence["infrastructure_error"]
    assert "discrimination-requirement-" in evidence["infrastructure_error"]


def test_h7_abort_kept_ground_truth_and_scoring_closed():
    evidence = _evidence()
    assert evidence["ground_truth_loaded_during_execution"] is False
    assert evidence["scoring_performed_during_execution"] is False
    assert evidence["ground_truth_opening_authorized"] is False
    assert evidence["scoring_authorized"] is False


def test_h7_abort_performed_no_learning_writeback_or_action():
    evidence = _evidence()
    assert evidence["learning_or_adaptation_performed"] is False
    assert evidence["memory_writeback_performed"] is False
    assert evidence["world_model_writeback_performed"] is False
    assert evidence["action_execution_performed"] is False


def test_h7_abort_authorizes_no_performance_or_production_conclusion():
    evidence = _evidence()
    assert evidence["cognitive_performance_conclusion_authorized"] is False
    assert evidence["production_change_authorized"] is False
    assert evidence["next_gate"].endswith("Post-Mortem / Evaluation-Boundary Audit")
