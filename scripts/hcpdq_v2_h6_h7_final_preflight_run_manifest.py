from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from scripts.hcpdq_v2_h6_h7_isolation_adapter_recertification import (
    recertify_h6_h7_isolation_adapter,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = PROJECT_ROOT / "benchmarks"
CASES = BENCHMARKS / "hcpdq_v2_h6_h7_held_out_cases.json"
GROUND_TRUTH = BENCHMARKS / "hcpdq_v2_h6_h7_ground_truth.json"
FREEZE = BENCHMARKS / "HCPDQ_V2_H6_H7_HELD_OUT_FREEZE_MANIFEST.json"
CERTIFICATION = BENCHMARKS / "HCPDQ_V2_H6_H7_HELD_OUT_FREEZE_CERTIFICATION.json"
RECERTIFICATION = (
    BENCHMARKS / "HCPDQ_V2_H6_H7_ISOLATION_ADAPTER_CAUSAL_RECERTIFICATION.json"
)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def freeze_final_run_manifest() -> dict[str, object]:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    certification = json.loads(CERTIFICATION.read_text(encoding="utf-8"))
    recertification = recertify_h6_h7_isolation_adapter()

    ordered_ids = sorted(case["case_id"] for case in cases)
    preconditions = (
        freeze["case_sha256"] == _digest(CASES),
        freeze["ground_truth_sha256"] == _digest(GROUND_TRUTH),
        certification["status"] == "CERTIFIED_EXPOSURE_AUTHORIZED",
        certification["integrity_pass"] is True,
        recertification["causal_recertification_passed"] is True,
        recertification["primary_execution_authorized"] is False,
        len(cases) == 30,
        {case["family_code"] for case in cases} == {"H6", "H7"},
    )
    ready = all(preconditions)

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-h7-final-run-manifest-v1",
        "status": (
            "RUN_MANIFEST_FROZEN_EXECUTION_AUTHORIZATION_PENDING"
            if ready
            else "NO_GO_PREFLIGHT_FAILED"
        ),
        "baseline": "12934-pass-0-fail-ruff-clean",
        "scope": ["H6", "H7"],
        "case_count": len(cases),
        "case_order": ordered_ids,
        "ordering_rule": "lexicographic_case_id",
        "retries_per_case": 0,
        "fresh_context_per_case": True,
        "cross_case_result_visibility": False,
        "subject_fields": ["case_id", "family", "difficulty", "prompt"],
        "raw_capture_required_before_scoring": True,
        "ground_truth_available_to_subject": False,
        "ground_truth_loaded_by_subject_adapter": False,
        "memory_writes_authorized": False,
        "learning_writes_authorized": False,
        "adaptation_authorized": False,
        "persistent_state_writes_authorized": False,
        "production_changes_authorized": False,
        "human_comparison_authorized": False,
        "cases_sha256": _digest(CASES),
        "ground_truth_sha256": _digest(GROUND_TRUTH),
        "freeze_manifest_sha256": _digest(FREEZE),
        "freeze_certification_sha256": _digest(CERTIFICATION),
        "adapter_recertification_sha256": _digest(RECERTIFICATION),
        "preflight_passed": ready,
        "primary_execution_authorized": False,
        "execution_authorization_pending": ready,
        "architectural_determination": (
            "All frozen corpus, certification and isolation preconditions pass. "
            "This manifest fixes the exact run scope, order and isolation "
            "conditions. It does not itself authorize primary held-out "
            "execution; an explicit execution-authorization gate remains "
            "required."
        ),
        "next_gate": (
            "HCPDQ-v2 H6/H7 ROBY Evaluation Run — "
            "Primary Execution Authorization / Go-No-Go"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["run_manifest_fingerprint"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            freeze_final_run_manifest(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
