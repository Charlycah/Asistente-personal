from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS = ROOT / "benchmarks"
CORPUS = BENCHMARKS / "HCPDQ_V2_H7_INDEPENDENT_CORPUS.json"
TRUTH = BENCHMARKS / "HCPDQ_V2_H7_INDEPENDENT_GROUND_TRUTH.json"
FREEZE = BENCHMARKS / "HCPDQ_V2_H7_CORPUS_GROUND_TRUTH_FREEZE.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _content_hash(payload):
    clean = dict(payload)
    clean.pop("freeze_sha256", None)
    canonical = json.dumps(
        clean,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_h7_corpus_is_frozen_balanced_and_unexposed():
    corpus = _load(CORPUS)
    assert corpus["status"] == "CONSTRUCTED_FROZEN_UNEXPOSED"
    assert corpus["case_count"] == 12
    assert corpus["difficulty_counts"] == {"D1": 4, "D2": 4, "D3": 4}
    assert corpus["contains_ground_truth"] is False
    assert corpus["roby_exposed"] is False
    assert _content_hash(corpus) == corpus["freeze_sha256"]


def test_h7_ground_truth_is_separate_balanced_and_unexposed():
    truth = _load(TRUTH)
    assert truth["status"] == "GROUND_TRUTH_FROZEN_UNEXPOSED"
    assert truth["class_counts"] == {"PLANNED": 6, "FAIL_CLOSED": 6}
    assert truth["constructed_without_roby_outputs"] is True
    assert truth["roby_exposed"] is False
    assert _content_hash(truth) == truth["freeze_sha256"]


def test_h7_case_ids_match_exactly_across_corpus_and_truth():
    corpus_ids = [item["case_id"] for item in _load(CORPUS)["cases"]]
    truth_ids = [item["case_id"] for item in _load(TRUTH)["cases"]]
    assert corpus_ids == truth_ids
    assert corpus_ids == [f"V2I-H7-{index:03d}" for index in range(1, 13)]


def test_h7_roby_facing_corpus_contains_no_expected_answers():
    serialized = json.dumps(_load(CORPUS), sort_keys=True)
    assert "expected_class" not in serialized
    assert "decisive_condition" not in serialized
    assert "expected_planning_invocation_count" not in serialized


def test_h7_ground_truth_requires_existing_authority_and_nonexecution():
    cases = _load(TRUTH)["cases"]
    assert all(item["required_authority"] == "planning_foundation" for item in cases)
    assert all(item["expected_execution_authorized"] is False for item in cases)
    assert all(item["expected_state_mutation"] is False for item in cases)


def test_h7_freeze_attests_zero_roby_or_planning_construction_calls():
    freeze = _load(FREEZE)
    independence = freeze["independence_attestation"]
    assert independence["roby_invocations_during_construction"] == 0
    assert independence["planning_invocations_during_construction"] == 0
    assert independence["roby_outputs_used_for_authoring"] is False


def test_h7_freeze_hashes_bind_corpus_and_ground_truth():
    freeze = _load(FREEZE)
    corpus = _load(CORPUS)
    truth = _load(TRUTH)
    assert freeze["corpus_freeze_sha256"] == corpus["freeze_sha256"]
    assert freeze["ground_truth_freeze_sha256"] == truth["freeze_sha256"]
    assert truth["corpus_freeze_sha256"] == corpus["freeze_sha256"]


def test_h7_exposure_execution_and_scoring_remain_no_go():
    gates = _load(FREEZE)["go_no_go"]
    assert gates["construction"] == "COMPLETE"
    assert gates["ground_truth_freeze"] == "GO"
    assert gates["freeze_certification"] == "REQUIRED_NEXT"
    assert gates["roby_exposure"] == "NO_GO"
    assert gates["primary_execution"] == "NO_GO"
    assert gates["scoring"] == "NO_GO"
    assert gates["production_change"] == "NO_GO"
