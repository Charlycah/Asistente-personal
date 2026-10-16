from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmarks"
AUTH = BENCH / "HCPDQ_V2_H6_PRIMARY_EXECUTION_AUTHORIZATION.json"
MANIFEST = BENCH / "HCPDQ_V2_H6_PRIMARY_RUN_MANIFEST.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_authorization_is_bound_to_exact_frozen_manifest():
    auth = _load(AUTH)
    manifest = _load(MANIFEST)
    assert auth["run_manifest_fingerprint"] == (
        manifest["run_manifest_fingerprint"]
    )
    assert auth["run_manifest_sha256"] == _sha(MANIFEST)


def test_authorization_verifies_every_cryptographic_binding():
    auth = _load(AUTH)
    assert all(auth["cryptographic_bindings_verified"].values())


def test_authorization_scope_is_one_run_twelve_cases_one_attempt():
    auth = _load(AUTH)
    assert auth["case_count_authorized"] == 12
    assert auth["attempts_authorized_per_case"] == 1
    assert auth["retries_authorized"] is False
    assert "one primary held-out H6 run" in auth["authorization_scope"]


def test_authorization_keeps_truth_scoring_and_learning_outside_run():
    auth = _load(AUTH)
    assert auth["ground_truth_during_execution_authorized"] is False
    assert auth["scoring_during_execution_authorized"] is False
    assert auth["learning_or_adaptation_authorized"] is False
    assert auth["memory_writeback_authorized"] is False
    assert auth["benchmark_feedback_authorized"] is False


def test_authorization_gate_does_not_itself_execute_held_out():
    auth = _load(AUTH)
    assert auth["execution_performed_in_this_gate"] is False
    assert auth["manifest_mutation_authorized"] is False
    assert auth["corpus_mutation_authorized"] is False
    assert auth["ground_truth_mutation_authorized"] is False


def test_all_preconditions_produce_explicit_go():
    auth = _load(AUTH)
    assert all(auth["checks"].values())
    assert auth["go"] is True
    assert auth["status"] == "PRIMARY_EXECUTION_AUTHORIZED_GO"
    assert auth["next_gate"].endswith("First Primary Held-Out Execution")
