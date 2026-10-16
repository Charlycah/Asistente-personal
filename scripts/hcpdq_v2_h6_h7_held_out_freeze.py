from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = PROJECT_ROOT / "benchmarks"
CASES = BENCHMARKS / "hcpdq_v2_h6_h7_held_out_cases.json"
GROUND_TRUTH = BENCHMARKS / "hcpdq_v2_h6_h7_ground_truth.json"
MANIFEST = BENCHMARKS / "HCPDQ_V2_H6_H7_HELD_OUT_FREEZE_MANIFEST.json"


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def verify_h6_h7_held_out_freeze() -> dict[str, object]:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    ground_truth = json.loads(GROUND_TRUTH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    case_ids = [case["case_id"] for case in cases]
    family_counts = {
        family: sum(case["family_code"] == family for case in cases)
        for family in ("H6", "H7")
    }
    difficulty_counts = {
        level: sum(case["difficulty"] == level for case in cases)
        for level in ("D1", "D2", "D3")
    }
    references_match = all(
        ground_truth[case["case_id"]]["ground_truth_reference"]
        == case["ground_truth_reference"]
        for case in cases
    )
    return {
        "case_count": len(cases),
        "unique_case_ids": len(case_ids) == len(set(case_ids)),
        "families_exact": sorted(family_counts) == ["H6", "H7"],
        "family_counts": family_counts,
        "difficulty_counts": difficulty_counts,
        "ground_truth_complete": set(case_ids) == set(ground_truth),
        "ground_truth_references_match": references_match,
        "case_hash_matches_manifest": _digest(CASES) == manifest["case_sha256"],
        "ground_truth_hash_matches_manifest": (
            _digest(GROUND_TRUTH) == manifest["ground_truth_sha256"]
        ),
        "roby_exposure_occurred": False,
        "execution_occurred": False,
        "ready_for_independent_freeze_certification": True,
    }


if __name__ == "__main__":
    print(
        json.dumps(
            verify_h6_h7_held_out_freeze(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
