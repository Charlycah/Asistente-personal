from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "benchmarks" / "HCPDQ_V2_H7_EXPOSURE_ISOLATION_PROTOCOL.json"


def _protocol():
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def test_red_h7_minimal_isolation_adapter_exists():
    assert importlib.util.find_spec("app.hcpdq_v2_h7_isolation_adapter") is not None


def test_red_contract_keeps_ground_truth_outside_adapter_boundary():
    adapter = _protocol()["adapter_contract"]
    boundary = _protocol()["isolation_boundary"]
    assert adapter["may_read_ground_truth"] is False
    assert boundary["ground_truth_load_during_exposure"] is False
    assert boundary["ground_truth_load_during_primary_execution"] is False


def test_red_contract_requires_existing_productive_entry_path():
    adapter = _protocol()["adapter_contract"]
    assert adapter["must_use_existing_productive_entry_path"] is True
    assert adapter["may_create_planning_authority"] is False
    assert adapter["may_directly_instantiate_internal_planner_for_benchmark"] is False


def test_red_contract_is_single_attempt_and_retry_free():
    contract = _protocol()["case_execution_contract"]
    assert contract["fresh_isolated_context_per_case"] is True
    assert contract["attempts_per_case"] == 1
    assert contract["retries"] == 0


def test_red_contract_requires_raw_capture_without_scoring():
    contract = _protocol()["case_execution_contract"]
    boundary = _protocol()["isolation_boundary"]
    assert contract["raw_capture_required"] is True
    assert contract["raw_capture_must_be_sealed_before_next_phase"] is True
    assert boundary["scoring_during_exposure"] is False
    assert boundary["scoring_during_primary_execution"] is False


def test_red_contract_forbids_expected_answer_routing_and_mutation():
    adapter = _protocol()["adapter_contract"]
    assert adapter["may_route_on_expected_class"] is False
    assert adapter["may_mutate_corpus"] is False
    assert adapter["may_mutate_ground_truth"] is False
