from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS = ROOT / "benchmarks"
CORPUS = BENCHMARKS / "HCPDQ_V2_H7_ENTRY_EQUIVALENT_CORPUS_V2.json"
TRUTH = BENCHMARKS / "HCPDQ_V2_H7_ENTRY_EQUIVALENT_GROUND_TRUTH_V2.json"
PREFLIGHT = BENCHMARKS / "HCPDQ_V2_H7V2_PREFLIGHT_PRIMARY_EXECUTION.json"
RUN = BENCHMARKS / "HCPDQ_V2_H7V2_FIRST_PRIMARY_EXECUTION.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_h7v2_preflight_binds_exact_frozen_corpus_and_sealed_truth():
    preflight = _load(PREFLIGHT)
    corpus = _load(CORPUS)
    assert preflight["status"] == "PREFLIGHT_PASS_PRIMARY_EXECUTION_AUTHORIZED"
    assert hashlib.sha256(CORPUS.read_bytes()).hexdigest() == (
        preflight["corpus_file_sha256"]
    )
    assert preflight["corpus_freeze_sha256"] == corpus["freeze_sha256"]
    assert hashlib.sha256(TRUTH.read_bytes()).hexdigest() == (
        preflight["ground_truth_file_sha256"]
    )


def test_h7v2_ground_truth_was_frozen_before_primary_execution():
    preflight = _load(PREFLIGHT)
    truth = _load(TRUTH)
    assert truth["status"] == "FROZEN_SEALED_BEFORE_PRIMARY_EXECUTION"
    assert preflight["ground_truth_sealed_before_execution"] is True
    assert preflight["ground_truth_access_during_execution"] is False


def test_h7v2_primary_execution_completed_all_cases_once():
    run = _load(RUN)
    assert run["status"] == "PRIMARY_EXECUTION_COMPLETE_RAW_SEALED"
    assert run["case_count"] == 12
    assert run["sealed_raw_capture_count"] == 12
    assert run["attempts_per_case"] == 1
    assert run["retries"] == 0
    assert len(run["captures"]) == 12


def test_h7v2_primary_execution_preserved_exact_case_order():
    run = _load(RUN)
    preflight = _load(PREFLIGHT)
    assert run["case_order"] == preflight["case_order"]
    assert run["case_order"] == [
        f"V2I-H7V2-{number:03d}" for number in range(1, 13)
    ]


def test_h7v2_every_raw_capture_is_individually_hash_sealed():
    run = _load(RUN)
    for capture in run["captures"]:
        assert hashlib.sha256(
            capture["raw_result"].encode()
        ).hexdigest() == capture["raw_result_sha256"]


def test_h7v2_aggregate_raw_run_seal_is_reproducible():
    run = _load(RUN)
    material = json.dumps(
        [
            {
                "case_id": item["case_id"],
                "raw_result_sha256": item["raw_result_sha256"],
            }
            for item in run["captures"]
        ],
        sort_keys=True,
        separators=(",", ":"),
    )
    assert hashlib.sha256(material.encode()).hexdigest() == (
        run["aggregate_raw_run_sha256"]
    )


def test_h7v2_execution_did_not_score_learn_or_load_truth():
    run = _load(RUN)
    assert run["ground_truth_loaded_during_execution"] is False
    assert run["scoring_performed_during_execution"] is False
    assert run["learning_or_writeback_performed"] is False


def test_h7v2_single_primary_authorization_is_consumed():
    run = _load(RUN)
    assert run["authorization_consumed"] is True
    assert run["authorization_reusable"] is False
    assert run["next_gate"].endswith("Ground-Truth Scoring + Cognitive Audit")
