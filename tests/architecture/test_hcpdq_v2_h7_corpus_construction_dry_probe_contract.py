from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = (
    ROOT / "benchmarks" / "HCPDQ_V2_H7_CORPUS_CONSTRUCTION_DRY_PROBE_CONTRACT.json"
)


def _contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_construction_contract_and_dry_probe_are_certified():
    contract = _contract()
    assert contract["status"] == ("CONSTRUCTION_CONTRACT_FROZEN_DRY_PROBE_CERTIFIED_GO")
    assert contract["go_no_go"]["construction_contract"] == "GO"
    assert contract["go_no_go"]["dry_probe"] == "GO"


def test_corpus_namespace_and_target_balance_are_independent():
    contract = _contract()
    assert contract["corpus_namespace"] == "V2I-H7"
    balance = contract["construction_balance"]
    assert balance["target_case_count"] == 12
    assert balance["difficulty_counts"] == {"D1": 4, "D2": 4, "D3": 4}
    assert balance["positive_vs_fail_closed"] == {
        "PLANNED": 6,
        "FAIL_CLOSED": 6,
    }


def test_dry_probe_does_not_query_roby_or_planning():
    probe = _contract()["dry_probe"]
    assert probe["roby_invocations"] == 0
    assert probe["planning_invocations"] == 0
    assert probe["candidate_cases_materialized"] is False
    assert probe["observed_roby_outputs_used"] is False


def test_positive_cases_remain_inside_certified_h7_surface():
    requirements = " ".join(_contract()["positive_case_requirements"])
    assert "multi-step evidence-acquisition" in requirements
    assert "certified planning re-entry surface" in requirements
    assert "one existing planning invocation" in requirements
    assert "must not imply action execution" in requirements


def test_fail_closed_dimensions_match_existing_input_guards():
    dimensions = _contract()["fail_closed_dimensions"]
    assert "continuation not planning-eligible" in dimensions
    assert "episode not READY_FOR_PLANNING" in dimensions
    assert "bounded step-two shape is violated" in dimensions
    assert "required lineage is missing or mismatched" in dimensions
    assert "prior plan reuse is present" in dimensions


def test_construction_guards_forbid_h6_prior_h7_and_roby_leakage():
    guards = " ".join(_contract()["independence_guards"])
    assert "H6 held-out/scoring" in guards
    assert "prior H7 held-out or calibration prompts" in guards
    assert "ROBY output" in guards
    assert "V2I-H7 namespace" in guards


def test_ground_truth_stays_separate_from_roby_facing_corpus():
    contract = _contract()
    schema = contract["construction_unit_schema"]
    assert schema["ground_truth_detail"] == ("withheld from ROBY-facing corpus")
    assert contract["dry_probe"]["ground_truth_opened_to_roby"] is False


def test_exposure_execution_and_scoring_remain_blocked():
    gates = _contract()["go_no_go"]
    assert gates["freeze_certification"] == "REQUIRED_BEFORE_EXPOSURE"
    assert gates["roby_exposure"] == "NO_GO"
    assert gates["primary_execution"] == "NO_GO"
    assert gates["scoring"] == "NO_GO"
    assert gates["production_change"] == "NO_GO"
