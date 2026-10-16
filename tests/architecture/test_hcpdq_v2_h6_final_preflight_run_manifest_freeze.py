from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmarks"
MANIFEST = BENCH / "HCPDQ_V2_H6_PRIMARY_RUN_MANIFEST.json"
CASES = BENCH / "hcpdq_v2_h6_entry_path_equivalent_held_out_cases.json"
TRUTH = BENCH / "hcpdq_v2_h6_entry_path_equivalent_ground_truth.json"
ADAPTER = ROOT / "app/hcpdq_v2_h6_entry_path_isolation_adapter.py"
PROTOCOL = BENCH / "HCPDQ_V2_H6_EXPOSURE_ISOLATION_PROTOCOL.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_manifest_freezes_exact_twelve_case_order():
    manifest = _load(MANIFEST)
    assert manifest["case_count"] == 12
    assert manifest["case_order"] == [
        f"V2E-H6-{number:03d}" for number in range(1, 13)
    ]
    assert manifest["case_order_policy"] == (
        "exact frozen corpus order; no shuffle"
    )


def test_manifest_hash_binds_corpus_truth_adapter_and_protocol():
    manifest = _load(MANIFEST)
    assert manifest["corpus_sha256"] == _sha(CASES)
    assert manifest["ground_truth_sha256"] == _sha(TRUTH)
    assert manifest["adapter_sha256"] == _sha(ADAPTER)
    assert manifest["protocol_sha256"] == _sha(PROTOCOL)


def test_manifest_freezes_one_attempt_fresh_context_and_raw_capture():
    manifest = _load(MANIFEST)
    assert manifest["attempt_policy"] == (
        "exactly one attempt per case; retries prohibited"
    )
    assert "fresh isolated context per case" in manifest["context_policy"]
    assert "immutable raw unscored response" in manifest["capture_policy"]


def test_manifest_keeps_ground_truth_scoring_learning_outside_execution():
    manifest = _load(MANIFEST)
    assert "never load or expose" in manifest["ground_truth_policy"]
    assert "prohibited until all raw captures" in manifest["scoring_policy"]
    assert "learning/adaptation" in manifest["learning_policy"]
    assert "no benchmark-derived persistent writes" == (
        manifest["persistence_policy"]
    )


def test_manifest_is_frozen_but_primary_execution_remains_blocked():
    manifest = _load(MANIFEST)
    assert manifest["manifest_frozen"] is True
    assert manifest["manifest_mutation_authorized"] is False
    assert manifest["held_out_execution_occurred"] is False
    assert manifest["ground_truth_exposure_occurred"] is False
    assert manifest["primary_execution_authorized"] is False
    assert manifest["authorization_gate_required"] is True


def test_manifest_next_gate_is_explicit_execution_authorization():
    manifest = _load(MANIFEST)
    assert manifest["next_gate"].endswith(
        "Primary Execution Authorization / Go-No-Go"
    )
