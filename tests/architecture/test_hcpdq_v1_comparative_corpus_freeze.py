from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.hcpdq_v1_corpus_freeze import (
    DIFFICULTIES,
    FAMILIES,
    build_freeze_manifest,
    fingerprint_payload,
    subject_payload,
    validate_split,
)

ROOT = Path(__file__).resolve().parents[2]


def _case(index: int, family: str, difficulty: str, split: str) -> dict[str, str]:
    prefix = "CAL" if split == "calibration" else "HO"
    scoring_mode = "rubric" if family == "complex_multicriteria_decision" else "exact"
    return {
        "case_id": f"{prefix}-{index:03d}",
        "family": family,
        "difficulty": difficulty,
        "prompt": f"Case {index}",
        "scoring_mode": scoring_mode,
        "ground_truth_reference": f"GT-{prefix}-{index:03d}",
    }


def _split(size: int, split: str) -> list[dict[str, str]]:
    return [
        _case(
            index + 1,
            FAMILIES[index % len(FAMILIES)],
            ("D1", "D2", "D3")[index % 3],
            split,
        )
        for index in range(size)
    ]


def test_hcpdq_corrected_harness_is_canonical():
    source = (ROOT / "scripts/hcpdq_v1_benchmark_harness.py").read_text(
        encoding="utf-8"
    )
    assert "from typing import Callable\n" in source
    assert "Mapping" not in source


def test_hcpdq_calibration_corpus_has_contractual_size_and_coverage():
    cases = json.loads(
        (ROOT / "benchmarks/hcpdq_v1_calibration_cases.json").read_text(
            encoding="utf-8"
        )
    )
    result = validate_split(cases, split="calibration")
    assert result.case_count == 30
    assert result.freeze_ready is True
    assert set(result.difficulties) == DIFFICULTIES
    assert {family for family, count in result.family_counts if count} == set(FAMILIES)


def test_hcpdq_subject_payload_excludes_ground_truth_and_scoring():
    case = _case(1, FAMILIES[0], "D1", "calibration")
    payload = subject_payload(case)
    assert set(payload) == {"case_id", "family", "difficulty", "prompt"}
    assert "ground_truth_reference" not in payload
    assert "scoring_mode" not in payload


def test_hcpdq_fingerprint_is_canonical_and_deterministic():
    payload = [{"b": 2, "a": 1}]
    assert fingerprint_payload(payload) == fingerprint_payload([{"a": 1, "b": 2}])


def test_hcpdq_held_out_template_is_not_misrepresented_as_frozen():
    held_out = json.loads(
        (ROOT / "benchmarks/hcpdq_v1_held_out_template.json").read_text(
            encoding="utf-8"
        )
    )
    with pytest.raises(ValueError, match="non-empty"):
        validate_split(held_out, split="held_out")


def test_hcpdq_freeze_requires_exact_30_120_split_sizes():
    with pytest.raises(ValueError, match="not freeze-ready"):
        validate_split(_split(29, "calibration"), split="calibration")
    with pytest.raises(ValueError, match="not freeze-ready"):
        validate_split(_split(119, "held_out"), split="held_out")


def test_hcpdq_freeze_requires_all_ground_truth_keys():
    calibration = _split(30, "calibration")
    held_out = _split(120, "held_out")
    all_cases = calibration + held_out
    ground_truth = {
        case["case_id"]: {
            "expected": "correct",
            "ground_truth_reference": case["ground_truth_reference"],
        }
        for case in all_cases[:-1]
    }
    rubrics = {
        case["case_id"]: {"dimensions": ["quality"]}
        for case in all_cases
        if case["scoring_mode"] == "rubric"
    }
    with pytest.raises(ValueError, match="ground truth keys"):
        build_freeze_manifest(calibration, held_out, ground_truth, rubrics)


def test_hcpdq_freeze_requires_exact_rubric_case_coverage():
    calibration = _split(30, "calibration")
    held_out = _split(120, "held_out")
    all_cases = calibration + held_out
    ground_truth = {
        case["case_id"]: {
            "expected": "correct",
            "ground_truth_reference": case["ground_truth_reference"],
        }
        for case in all_cases
    }
    with pytest.raises(ValueError, match="rubric keys"):
        build_freeze_manifest(calibration, held_out, ground_truth, {})


def test_hcpdq_valid_complete_freeze_manifest_is_reproducible():
    calibration = _split(30, "calibration")
    held_out = _split(120, "held_out")
    all_cases = calibration + held_out
    ground_truth = {
        case["case_id"]: {
            "expected": "correct",
            "ground_truth_reference": case["ground_truth_reference"],
        }
        for case in all_cases
    }
    rubrics = {
        case["case_id"]: {"dimensions": ["quality"]}
        for case in all_cases
        if case["scoring_mode"] == "rubric"
    }
    first = build_freeze_manifest(calibration, held_out, ground_truth, rubrics)
    second = build_freeze_manifest(calibration, held_out, ground_truth, rubrics)
    assert first == second
    assert first["status"] == "frozen"
    assert first["calibration"]["case_count"] == 30
    assert first["held_out"]["case_count"] == 120
    assert first["anti_contamination"]["ground_truth_reaches_subject"] is False


def test_hcpdq_real_held_out_is_exactly_balanced_by_family_and_difficulty():
    held_out = json.loads(
        (ROOT / "benchmarks/hcpdq_v1_held_out_cases.json").read_text(
            encoding="utf-8"
        )
    )
    result = validate_split(held_out, split="held_out")
    counts = dict(result.family_counts)
    assert counts == {family: 15 for family in FAMILIES}
    for family in FAMILIES:
        family_cases = [case for case in held_out if case["family"] == family]
        assert {
            difficulty: sum(
                case["difficulty"] == difficulty for case in family_cases
            )
            for difficulty in DIFFICULTIES
        } == {"D1": 5, "D2": 5, "D3": 5}


def test_hcpdq_real_ground_truth_is_separate_and_exactly_linked():
    calibration = json.loads(
        (ROOT / "benchmarks/hcpdq_v1_calibration_cases.json").read_text(
            encoding="utf-8"
        )
    )
    held_out = json.loads(
        (ROOT / "benchmarks/hcpdq_v1_held_out_cases.json").read_text(
            encoding="utf-8"
        )
    )
    ground_truth = json.loads(
        (ROOT / "benchmarks/hcpdq_v1_ground_truth.json").read_text(
            encoding="utf-8"
        )
    )
    all_cases = calibration + held_out
    assert set(ground_truth) == {case["case_id"] for case in all_cases}
    assert all(
        ground_truth[case["case_id"]]["ground_truth_reference"]
        == case["ground_truth_reference"]
        for case in all_cases
    )


def test_hcpdq_real_rubrics_cover_only_rubric_scored_cases():
    calibration = json.loads(
        (ROOT / "benchmarks/hcpdq_v1_calibration_cases.json").read_text(
            encoding="utf-8"
        )
    )
    held_out = json.loads(
        (ROOT / "benchmarks/hcpdq_v1_held_out_cases.json").read_text(
            encoding="utf-8"
        )
    )
    rubrics = json.loads(
        (ROOT / "benchmarks/hcpdq_v1_rubrics.json").read_text(
            encoding="utf-8"
        )
    )
    rubric_ids = {
        case["case_id"]
        for case in calibration + held_out
        if case["scoring_mode"] == "rubric"
    }
    assert set(rubrics) == rubric_ids


def test_hcpdq_ground_truth_reference_mismatch_blocks_freeze():
    calibration = _split(30, "calibration")
    held_out = _split(120, "held_out")
    all_cases = calibration + held_out
    ground_truth = {
        case["case_id"]: {
            "expected": "correct",
            "ground_truth_reference": case["ground_truth_reference"],
        }
        for case in all_cases
    }
    ground_truth[all_cases[0]["case_id"]]["ground_truth_reference"] = "wrong"
    rubrics = {
        case["case_id"]: {"dimensions": ["quality"]}
        for case in all_cases
        if case["scoring_mode"] == "rubric"
    }
    with pytest.raises(ValueError, match="ground truth reference mismatch"):
        build_freeze_manifest(calibration, held_out, ground_truth, rubrics)
