from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from scripts.hcpdq_v2_h6_h7_final_preflight_run_manifest import (
    freeze_final_run_manifest,
)
from scripts.hcpdq_v2_h6_h7_isolation_adapter_recertification import (
    recertify_h6_h7_isolation_adapter,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = PROJECT_ROOT / "benchmarks"
PREFLIGHT_MANIFEST = BENCHMARKS / "HCPDQ_V2_H6_H7_FINAL_PREFLIGHT_RUN_MANIFEST.json"


def authorize_primary_execution() -> dict[str, object]:
    frozen = json.loads(PREFLIGHT_MANIFEST.read_text(encoding="utf-8"))
    current = freeze_final_run_manifest()
    adapter = recertify_h6_h7_isolation_adapter()

    manifest_stable = (
        frozen["run_manifest_fingerprint"] == current["run_manifest_fingerprint"]
    )
    preconditions = (
        frozen["status"] == "RUN_MANIFEST_FROZEN_EXECUTION_AUTHORIZATION_PENDING",
        frozen["preflight_passed"] is True,
        frozen["primary_execution_authorized"] is False,
        frozen["execution_authorization_pending"] is True,
        frozen["scope"] == ["H6", "H7"],
        frozen["case_count"] == 30,
        frozen["retries_per_case"] == 0,
        frozen["fresh_context_per_case"] is True,
        frozen["cross_case_result_visibility"] is False,
        frozen["ground_truth_available_to_subject"] is False,
        frozen["ground_truth_loaded_by_subject_adapter"] is False,
        frozen["memory_writes_authorized"] is False,
        frozen["learning_writes_authorized"] is False,
        frozen["adaptation_authorized"] is False,
        frozen["persistent_state_writes_authorized"] is False,
        adapter["causal_recertification_passed"] is True,
        adapter["primary_execution_raises"] is True,
        manifest_stable,
    )
    go = all(preconditions)

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-h7-primary-execution-authorization-v1",
        "status": (
            "GO_SINGLE_PRIMARY_HELD_OUT_EXECUTION" if go else "NO_GO_PRIMARY_EXECUTION"
        ),
        "baseline": "12939-pass-0-fail-ruff-clean",
        "authorized_manifest_fingerprint": frozen["run_manifest_fingerprint"],
        "authorized_scope": ["H6", "H7"],
        "authorized_case_count": 30,
        "authorized_case_order": frozen["case_order"],
        "authorized_run_count": 1 if go else 0,
        "retries_per_case": 0,
        "fresh_context_per_case": True,
        "cross_case_result_visibility": False,
        "raw_capture_required_before_scoring": True,
        "ground_truth_available_to_subject": False,
        "ground_truth_loaded_by_subject_adapter": False,
        "memory_writes_authorized": False,
        "learning_writes_authorized": False,
        "adaptation_authorized": False,
        "persistent_state_writes_authorized": False,
        "production_changes_authorized": False,
        "human_comparison_authorized": False,
        "manifest_stable": manifest_stable,
        "preconditions_passed": go,
        "primary_execution_authorized": go,
        "authorization_reusable": False,
        "execution_occurred": False,
        "architectural_determination": (
            "All frozen preflight, corpus and isolation conditions remain "
            "stable. One primary H6/H7 held-out execution is authorized under "
            "the exact frozen manifest. This authorization is single-use and "
            "does not permit retries, corpus changes, ground-truth visibility, "
            "learning, adaptation, persistence, production changes or human "
            "comparison."
        ),
        "next_gate": (
            "HCPDQ-v2 H6/H7 ROBY Evaluation Run — First Primary Held-Out Execution"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["authorization_fingerprint"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            authorize_primary_execution(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
