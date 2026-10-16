from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS = ROOT / "benchmarks"
MANIFEST = BENCHMARKS / "HCPDQ_V2_H7_PRIMARY_RUN_MANIFEST.json"
AUTH = BENCHMARKS / "HCPDQ_V2_H7_PRIMARY_EXECUTION_AUTHORIZATION.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(relative_path):
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def test_h7_primary_execution_authorization_is_go_for_one_run_only():
    auth = _load(AUTH)
    assert auth["status"] == "PRIMARY_EXECUTION_AUTHORIZED_GO"
    assert auth["decision"] == "GO"
    scope = auth["authorization_scope"]
    assert scope["authorized_run_count"] == 1
    assert scope["authorized_case_count"] == 12


def test_h7_authorization_binds_exact_manifest_and_order():
    auth = _load(AUTH)
    manifest = _load(MANIFEST)
    assert auth["run_id"] == manifest["run_id"]
    assert auth["manifest_fingerprint"] == manifest["manifest_fingerprint"]
    assert (
        auth["authorization_scope"]["authorized_execution_order"]
        == (manifest["execution_order"])
    )


def test_h7_frozen_execution_input_hashes_have_no_drift():
    manifest = _load(MANIFEST)
    frozen = manifest["frozen_inputs"]
    assert _sha(frozen["corpus_file"]) == frozen["corpus_file_sha256"]
    assert _sha(frozen["protocol_file"]) == frozen["protocol_file_sha256"]
    assert _sha(frozen["adapter_file"]) == frozen["adapter_file_sha256"]
    assert (
        _sha(frozen["recertification_file"]) == (frozen["recertification_file_sha256"])
    )
    truth = manifest["sealed_truth_reference"]
    assert _sha(truth["file"]) == truth["file_sha256"]


def test_h7_execution_still_requires_single_attempt_fresh_isolation():
    scope = _load(AUTH)["authorization_scope"]
    assert scope["attempts_per_case"] == 1
    assert scope["retries"] == 0
    assert scope["fresh_isolated_context_per_case"] is True
    assert scope["raw_capture_required"] is True
    assert scope["aggregate_raw_run_seal_required"] is True


def test_h7_authorization_keeps_truth_scoring_and_mutation_forbidden():
    forbidden = _load(AUTH)["still_forbidden"]
    assert forbidden["ground_truth_opening"] is True
    assert forbidden["scoring"] is True
    assert forbidden["expected_answer_routing"] is True
    assert forbidden["learning_or_adaptation"] is True
    assert forbidden["memory_writeback"] is True
    assert forbidden["world_model_writeback"] is True
    assert forbidden["action_execution"] is True
    assert forbidden["production_change"] is True


def test_h7_authorization_does_not_consume_execution_in_this_gate():
    auth = _load(AUTH)
    assert auth["primary_execution_performed_in_this_gate"] is False
    assert auth["ground_truth_opened_in_this_gate"] is False
    assert auth["scoring_performed_in_this_gate"] is False


def test_h7_authorization_requires_raw_seal_before_future_scoring():
    auth = _load(AUTH)
    assert "Seal all 12 raw captures" in auth["post_run_requirement"]
    assert auth["next_gate"].endswith("First Primary Held-Out Execution")
