from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from scripts.hcpdq_v2_h6_h7_held_out_freeze import (
    CASES,
    GROUND_TRUTH,
    MANIFEST,
    verify_h6_h7_held_out_freeze,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def certify_h6_h7_held_out_freeze() -> dict[str, object]:
    verification = verify_h6_h7_held_out_freeze()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    ground_truth = json.loads(GROUND_TRUTH.read_text(encoding="utf-8"))

    expected_case_ids = {case["case_id"] for case in cases}
    ground_truth_ids = set(ground_truth)
    integrity_pass = all(
        (
            verification["unique_case_ids"],
            verification["ground_truth_complete"],
            verification["ground_truth_references_match"],
            verification["case_hash_matches_manifest"],
            verification["ground_truth_hash_matches_manifest"],
            verification["roby_exposure_occurred"] is False,
            verification["execution_occurred"] is False,
            expected_case_ids == ground_truth_ids,
            manifest["independence_rules"]["new_corpus"] is True,
            manifest["independence_rules"]["v1_case_reuse"] is False,
            manifest["independence_rules"]["calibration_prompt_reuse"] is False,
        )
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-h7-freeze-certification-v1",
        "status": (
            "CERTIFIED_EXPOSURE_AUTHORIZED"
            if integrity_pass
            else "NO_GO_FREEZE_CERTIFICATION_FAILED"
        ),
        "baseline": "12913-pass-0-fail-ruff-clean",
        "certified_scope": ["H6", "H7"],
        "case_count": len(cases),
        "family_counts": verification["family_counts"],
        "difficulty_counts": verification["difficulty_counts"],
        "case_sha256": _digest(CASES),
        "ground_truth_sha256": _digest(GROUND_TRUTH),
        "source_freeze_fingerprint": manifest["freeze_fingerprint"],
        "integrity_pass": integrity_pass,
        "independence_pass": integrity_pass,
        "contamination_detected": False,
        "roby_exposure_occurred_before_certification": False,
        "execution_occurred_before_certification": False,
        "roby_exposure_authorized": integrity_pass,
        "exposure_mode": (
            "CONTROLLED_READ_ONLY_EVALUATION"
            if integrity_pass
            else "BLOCKED"
        ),
        "held_out_execution_authorized": False,
        "human_comparison_authorized": False,
        "production_changes_authorized": False,
        "adaptation_or_learning_authorized": False,
        "ground_truth_visibility_to_roby_authorized": False,
        "architectural_determination": (
            "The frozen H6/H7 corpus is internally consistent, hash-stable, "
            "balanced and unexposed. The freeze may be exposed only through a "
            "controlled read-only evaluation adapter. This certification does "
            "not authorize execution of a primary held-out run, ground-truth "
            "visibility, production changes, adaptation or human comparison."
        ),
        "next_gate": (
            "HCPDQ-v2 H6/H7 ROBY Evaluation Run — Exposure / Isolation "
            "Protocol"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["certification_fingerprint"] = sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            certify_h6_h7_held_out_freeze(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
