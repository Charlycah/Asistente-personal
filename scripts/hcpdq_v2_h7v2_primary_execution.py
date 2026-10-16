from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from scripts.hcpdq_v2_h7_entry_equivalent_corpus_v2_freeze import (
    materialize_and_probe,
)

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"
CORPUS = BENCHMARKS / "HCPDQ_V2_H7_ENTRY_EQUIVALENT_CORPUS_V2.json"
PREFLIGHT = BENCHMARKS / "HCPDQ_V2_H7V2_PREFLIGHT_PRIMARY_EXECUTION.json"


def execute():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    assert preflight["status"] == "PREFLIGHT_PASS_PRIMARY_EXECUTION_AUTHORIZED"
    assert [case["case_id"] for case in corpus["cases"]] == (
        preflight["case_order"]
    )

    captures = []
    for case in corpus["cases"]:
        result = materialize_and_probe(case)
        raw = json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        captures.append(
            {
                "run_id": preflight["run_id"],
                "case_id": case["case_id"],
                "attempt": 1,
                "raw_result": raw,
                "raw_result_sha256": sha256(raw.encode()).hexdigest(),
            }
        )

    aggregate_material = json.dumps(
        [
            {
                "case_id": item["case_id"],
                "raw_result_sha256": item["raw_result_sha256"],
            }
            for item in captures
        ],
        sort_keys=True,
        separators=(",", ":"),
    )
    aggregate = sha256(aggregate_material.encode()).hexdigest()
    payload = {
        "schema_version": "hcpdq-v2-h7v2-primary-execution-v1",
        "status": "PRIMARY_EXECUTION_COMPLETE_RAW_SEALED",
        "run_id": preflight["run_id"],
        "authorization_consumed": True,
        "authorization_reusable": False,
        "case_count": len(captures),
        "case_order": [item["case_id"] for item in captures],
        "attempts_per_case": 1,
        "retries": 0,
        "fresh_materialization_per_case": True,
        "sealed_raw_capture_count": len(captures),
        "aggregate_raw_run_sha256": aggregate,
        "ground_truth_loaded_during_execution": False,
        "scoring_performed_during_execution": False,
        "learning_or_writeback_performed": False,
        "captures": captures,
        "next_gate": "HCPDQ-v2 H7 — Ground-Truth Scoring + Cognitive Audit",
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["run_evidence_fingerprint"] = sha256(
        canonical.encode()
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(json.dumps(execute(), ensure_ascii=False, indent=2, sort_keys=True))
