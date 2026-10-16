from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmarks"
CASES = BENCH / "hcpdq_v2_h6_entry_path_equivalent_held_out_cases.json"
TRUTH = BENCH / "hcpdq_v2_h6_entry_path_equivalent_ground_truth.json"
FREEZE = BENCH / "HCPDQ_V2_H6_ENTRY_PATH_EQUIVALENT_CORPUS_FREEZE.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_new_h6_corpus_and_ground_truth_are_frozen_and_hash_bound():
    freeze = _load(FREEZE)
    assert freeze["corpus_frozen"] is True
    assert freeze["ground_truth_frozen"] is True
    assert freeze["corpus_sha256"] == _sha(CASES)
    assert freeze["ground_truth_sha256"] == _sha(TRUTH)


def test_new_h6_corpus_has_new_ids_and_frozen_distribution():
    cases = _load(CASES)
    freeze = _load(FREEZE)
    assert len(cases) == 12
    assert len({case["case_id"] for case in cases}) == 12
    assert all(case["case_id"].startswith("V2E-H6-") for case in cases)
    assert freeze["difficulty_distribution"] == {"standard": 6, "hard": 6}


def test_every_case_uses_exact_structured_entry_sections():
    cases = _load(CASES)
    for case in cases:
        prompt = case["prompt"]
        assert prompt.startswith("Decisión:\n")
        assert "\nCriterios:\nLos criterios son " in prompt
        assert "\nEvidencia:\n" in prompt
        assert case["entry_form"] == "Decisión/Criterios/Evidencia"


def test_ground_truth_is_complete_and_case_aligned():
    cases = _load(CASES)
    truth = _load(TRUTH)
    assert [item["case_id"] for item in truth] == [
        case["case_id"] for case in cases
    ]
    assert all(item["expected_decision"] for item in truth)
    assert all(item["rationale"] for item in truth)


def test_freeze_keeps_exposure_execution_and_mutation_closed():
    freeze = _load(FREEZE)
    assert freeze["roby_exposure_occurred"] is False
    assert freeze["roby_execution_occurred"] is False
    assert freeze["ground_truth_exposed_to_roby"] is False
    assert freeze["exposure_authorized"] is False
    assert freeze["primary_execution_authorized"] is False
    assert freeze["corpus_mutation_authorized"] is False
    assert freeze["ground_truth_mutation_authorized"] is False


def test_freeze_records_independence_and_non_reuse():
    freeze = _load(FREEZE)
    assert freeze["independently_authored"] is True
    assert freeze["dry_probe_reuse"] is False
    assert freeze["consumed_v2_case_reuse"] is False
    assert freeze["consumed_v2_case_paraphrase"] is False
