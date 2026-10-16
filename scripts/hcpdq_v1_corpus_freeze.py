from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

CORPUS_SCHEMA_VERSION = "hcpdq-v1-comparative-corpus-v1"
FAMILIES = (
    "deterministic_reasoning",
    "insufficient_evidence",
    "noise_distractor_robustness",
    "structural_knowledge_transfer",
    "novel_generalization",
    "complex_multicriteria_decision",
    "constraint_heavy_planning",
    "conflicting_evidence_provenance",
)
DIFFICULTIES = frozenset({"D1", "D2", "D3"})
SCORING_MODES = frozenset({"exact", "structured", "rubric"})
EXPECTED_SPLIT_SIZES = {"calibration": 30, "held_out": 120}
HELD_OUT_CASES_PER_FAMILY = 15
HELD_OUT_CASES_PER_DIFFICULTY_PER_FAMILY = 5


@dataclass(frozen=True)
class CorpusValidation:
    split: str
    case_count: int
    family_counts: tuple[tuple[str, int], ...]
    difficulties: tuple[str, ...]
    fingerprint: str
    freeze_ready: bool


def _canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def fingerprint_payload(payload: Any) -> str:
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def subject_payload(case: dict[str, Any]) -> dict[str, Any]:
    allowed = ("case_id", "family", "difficulty", "prompt")
    return {key: case[key] for key in allowed}


def validate_split(
    cases: list[dict[str, Any]],
    *,
    split: str,
    require_freeze_size: bool = True,
) -> CorpusValidation:
    if split not in EXPECTED_SPLIT_SIZES:
        raise ValueError(f"unsupported HCPDQ split: {split}")
    if not isinstance(cases, list) or not cases:
        raise ValueError("HCPDQ split must be a non-empty JSON list")

    ids: set[str] = set()
    family_counts = {family: 0 for family in FAMILIES}
    difficulties: set[str] = set()
    family_difficulty_counts = {
        family: {difficulty: 0 for difficulty in DIFFICULTIES}
        for family in FAMILIES
    }
    prompts: set[str] = set()
    required = {
        "case_id",
        "family",
        "difficulty",
        "prompt",
        "scoring_mode",
        "ground_truth_reference",
    }

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each HCPDQ case must be an object")
        missing = required.difference(case)
        if missing:
            raise ValueError(f"missing required fields: {sorted(missing)}")
        case_id = str(case["case_id"]).strip()
        if not case_id or case_id in ids:
            raise ValueError(f"invalid or duplicate case_id: {case_id}")
        ids.add(case_id)

        family = str(case["family"])
        if family not in family_counts:
            raise ValueError(f"unsupported family: {family}")
        family_counts[family] += 1

        prompt = str(case["prompt"]).strip()
        if not prompt:
            raise ValueError(f"empty prompt: {case_id}")
        if prompt in prompts:
            raise ValueError(f"duplicate prompt: {case_id}")
        prompts.add(prompt)

        difficulty = str(case["difficulty"])
        if difficulty not in DIFFICULTIES:
            raise ValueError(f"unsupported difficulty: {difficulty}")
        difficulties.add(difficulty)
        family_difficulty_counts[family][difficulty] += 1

        scoring_mode = str(case["scoring_mode"])
        if scoring_mode not in SCORING_MODES:
            raise ValueError(f"unsupported scoring mode: {scoring_mode}")

        if not str(case["ground_truth_reference"]).strip():
            raise ValueError(f"empty ground_truth_reference: {case_id}")

    expected_size = EXPECTED_SPLIT_SIZES[split]
    held_out_balance_ok = True
    if split == "held_out":
        held_out_balance_ok = all(
            family_counts[family] == HELD_OUT_CASES_PER_FAMILY
            and all(
                family_difficulty_counts[family][difficulty]
                == HELD_OUT_CASES_PER_DIFFICULTY_PER_FAMILY
                for difficulty in DIFFICULTIES
            )
            for family in FAMILIES
        )
    freeze_ready = (
        len(cases) == expected_size
        and all(family_counts.values())
        and difficulties == DIFFICULTIES
        and held_out_balance_ok
    )
    if require_freeze_size and not freeze_ready:
        raise ValueError(
            f"{split} is not freeze-ready: "
            f"{len(cases)}/{expected_size} cases, "
            f"families={family_counts}, difficulties={sorted(difficulties)}"
        )

    return CorpusValidation(
        split=split,
        case_count=len(cases),
        family_counts=tuple(sorted(family_counts.items())),
        difficulties=tuple(sorted(difficulties)),
        fingerprint=fingerprint_payload(cases),
        freeze_ready=freeze_ready,
    )


def build_freeze_manifest(
    calibration: list[dict[str, Any]],
    held_out: list[dict[str, Any]],
    ground_truth: dict[str, Any],
    rubrics: dict[str, Any],
) -> dict[str, Any]:
    calibration_validation = validate_split(calibration, split="calibration")
    held_out_validation = validate_split(held_out, split="held_out")
    all_cases = calibration + held_out
    corpus_ids = {case["case_id"] for case in all_cases}
    if len(corpus_ids) != len(all_cases):
        raise ValueError("case_id collision across calibration and held-out splits")

    if set(ground_truth) != corpus_ids:
        raise ValueError("ground truth keys must exactly match all corpus case IDs")
    for case in all_cases:
        truth = ground_truth[case["case_id"]]
        if not isinstance(truth, dict):
            raise ValueError("ground truth entries must be objects")
        if (
            truth.get("ground_truth_reference")
            != case["ground_truth_reference"]
        ):
            raise ValueError("ground truth reference mismatch")

    rubric_case_ids = {
        case["case_id"]
        for case in all_cases
        if case["scoring_mode"] == "rubric"
    }
    if set(rubrics) != rubric_case_ids:
        raise ValueError("rubric keys must exactly match rubric-scored case IDs")

    return {
        "schema_version": CORPUS_SCHEMA_VERSION,
        "status": "frozen",
        "calibration": {
            "case_count": calibration_validation.case_count,
            "fingerprint": calibration_validation.fingerprint,
        },
        "held_out": {
            "case_count": held_out_validation.case_count,
            "fingerprint": held_out_validation.fingerprint,
            "family_counts": dict(held_out_validation.family_counts),
            "difficulties": list(held_out_validation.difficulties),
        },
        "ground_truth_fingerprint": fingerprint_payload(ground_truth),
        "rubric_fingerprint": fingerprint_payload(rubrics),
        "anti_contamination": {
            "development_against_held_out": False,
            "ground_truth_reaches_subject": False,
            "human_results_reach_roby": False,
            "benchmark_driven_learning": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate/freeze HCPDQ-v1 corpus")
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--held-out", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--rubrics", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = build_freeze_manifest(
        load_json(args.calibration),
        load_json(args.held_out),
        load_json(args.ground_truth),
        load_json(args.rubrics),
    )
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
