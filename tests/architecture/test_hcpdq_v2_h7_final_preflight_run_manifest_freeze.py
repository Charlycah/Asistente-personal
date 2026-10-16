from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "benchmarks" / "HCPDQ_V2_H7_PRIMARY_RUN_MANIFEST.json"


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _sha(relative_path):
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def test_h7_manifest_is_frozen_to_exact_inputs():
    manifest = _manifest()
    frozen = manifest["frozen_inputs"]
    assert manifest["status"] == (
        "FINAL_PREFLIGHT_FROZEN_AWAITING_EXECUTION_AUTHORIZATION"
    )
    assert _sha(frozen["corpus_file"]) == frozen["corpus_file_sha256"]
    assert _sha(frozen["protocol_file"]) == frozen["protocol_file_sha256"]
    assert _sha(frozen["adapter_file"]) == frozen["adapter_file_sha256"]
    assert (
        _sha(frozen["recertification_file"]) == (frozen["recertification_file_sha256"])
    )


def test_h7_manifest_freezes_exact_case_order():
    manifest = _manifest()
    assert manifest["execution_order"] == [
        f"V2I-H7-{number:03d}" for number in range(1, 13)
    ]
    assert manifest["execution_invariants"]["case_count"] == 12


def test_h7_manifest_requires_fresh_single_attempt_cases():
    invariants = _manifest()["execution_invariants"]
    assert invariants["fresh_isolated_context_per_case"] is True
    assert invariants["attempts_per_case"] == 1
    assert invariants["retries"] == 0
    assert invariants["visible_prior_results"] is False


def test_h7_manifest_keeps_truth_scoring_and_learning_closed():
    invariants = _manifest()["execution_invariants"]
    assert invariants["ground_truth_access"] is False
    assert invariants["scoring"] is False
    assert invariants["learning_or_adaptation"] is False
    assert invariants["memory_writeback"] is False
    assert invariants["world_model_writeback"] is False
    assert invariants["expected_answer_routing"] is False


def test_h7_manifest_freezes_raw_capture_and_aggregate_seal():
    capture = _manifest()["raw_capture_contract"]
    assert capture["one_capture_per_case"] is True
    assert capture["attempt_value"] == 1
    assert capture["seal_algorithm"] == "SHA-256"
    assert capture["aggregate_run_seal_required"] is True
    assert capture["aggregate_run_seal_before_ground_truth_opening"] is True


def test_h7_manifest_seals_ground_truth_before_execution():
    truth = _manifest()["sealed_truth_reference"]
    assert _sha(truth["file"]) == truth["file_sha256"]
    assert truth["access_before_raw_run_seal"] == "FORBIDDEN"


def test_h7_manifest_has_fail_closed_abort_conditions():
    conditions = " ".join(_manifest()["abort_conditions"])
    assert "frozen input hash mismatch" in conditions
    assert "ground truth is loaded" in conditions
    assert "retry or second execution" in conditions
    assert "prior-case result becomes visible" in conditions
    assert "scoring or expected-answer routing" in conditions


def test_h7_preflight_does_not_authorize_primary_execution():
    state = _manifest()["authorization_state"]
    assert state["final_preflight"] == "PASS"
    assert state["manifest_freeze"] == "FROZEN"
    assert state["primary_execution"] == ("NO_GO_PENDING_SEPARATE_AUTHORIZATION")
    assert state["ground_truth_opening"] == "NO_GO"
    assert state["scoring"] == "NO_GO"
    assert state["production_change"] == "NO_GO"
