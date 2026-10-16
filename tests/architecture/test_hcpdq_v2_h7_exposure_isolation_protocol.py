from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "benchmarks" / "HCPDQ_V2_H7_EXPOSURE_ISOLATION_PROTOCOL.json"


def _protocol():
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def test_protocol_is_frozen_to_exact_h7_corpus():
    protocol = _protocol()
    binding = protocol["input_binding"]
    assert protocol["status"] == "EXPOSURE_ISOLATION_PROTOCOL_FROZEN"
    assert binding["authorized_corpus_file"] == ("HCPDQ_V2_H7_INDEPENDENT_CORPUS.json")
    assert binding["case_count"] == 12
    assert binding["case_ids"] == [f"V2I-H7-{number:03d}" for number in range(1, 13)]


def test_roby_facing_payload_excludes_ground_truth_fields():
    boundary = _protocol()["isolation_boundary"]
    excluded = set(boundary["roby_facing_payload_must_exclude"])
    assert "expected_class" in excluded
    assert "decisive_condition" in excluded
    assert "expected_planning_invocation_count" in excluded
    assert "required_authority" in excluded


def test_protocol_forbids_truth_scoring_learning_and_writeback():
    boundary = _protocol()["isolation_boundary"]
    assert boundary["ground_truth_load_during_exposure"] is False
    assert boundary["ground_truth_load_during_primary_execution"] is False
    assert boundary["scoring_during_exposure"] is False
    assert boundary["scoring_during_primary_execution"] is False
    assert boundary["learning_or_adaptation"] is False
    assert boundary["memory_writeback"] is False
    assert boundary["world_model_writeback"] is False
    assert boundary["benchmark_feedback"] is False


def test_case_execution_contract_is_single_attempt_fresh_context():
    contract = _protocol()["case_execution_contract"]
    assert contract["fresh_isolated_context_per_case"] is True
    assert contract["attempts_per_case"] == 1
    assert contract["retries"] == 0
    assert contract["raw_capture_required"] is True
    assert contract["raw_capture_must_be_sealed_before_next_phase"] is True


def test_planning_is_observable_but_not_intervened_on():
    contract = _protocol()["case_execution_contract"]
    assert contract["planning_invocation_observation_allowed"] is True
    assert contract["planning_invocation_intervention_allowed"] is False
    assert contract["action_execution_allowed"] is False


def test_adapter_contract_cannot_read_truth_or_route_on_answers():
    adapter = _protocol()["adapter_contract"]
    assert adapter["may_read_corpus"] is True
    assert adapter["may_read_ground_truth"] is False
    assert adapter["may_route_on_expected_class"] is False
    assert adapter["may_create_planning_authority"] is False
    assert adapter["may_directly_instantiate_internal_planner_for_benchmark"] is False


def test_adapter_must_use_existing_productive_entry_path():
    adapter = _protocol()["adapter_contract"]
    assert adapter["must_use_existing_productive_entry_path"] is True
    assert adapter["may_mutate_corpus"] is False
    assert adapter["may_mutate_ground_truth"] is False


def test_protocol_does_not_authorize_primary_execution_yet():
    gates = _protocol()["go_no_go"]
    assert gates["protocol_freeze"] == "GO"
    assert gates["preimplementation_red_contracts"] == "GO"
    assert gates["primary_execution"] == "NO_GO"
    assert gates["ground_truth_opening"] == "NO_GO"
    assert gates["scoring"] == "NO_GO"
    assert gates["production_change"] == "NO_GO"
