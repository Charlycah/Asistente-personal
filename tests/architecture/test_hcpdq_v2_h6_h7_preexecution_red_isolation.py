from __future__ import annotations

import importlib

import pytest

from scripts.hcpdq_v2_h6_h7_exposure_isolation_protocol import (
    SubjectEnvelope,
    default_isolation_policy,
)

ADAPTER_MODULE = "app.hcpdq_v2_h6_h7_isolation_adapter"


def _adapter_module():
    try:
        return importlib.import_module(ADAPTER_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "RED_CAUSE: missing HCPDQ-v2 H6/H7 isolation adapter"
        )


def _sample_envelope() -> SubjectEnvelope:
    return SubjectEnvelope(
        case_id="V2-H6-RED-001",
        family="H6",
        difficulty="D1",
        prompt="Choose the valid option under the stated hard constraint.",
    )


def test_red_requires_subject_adapter_with_minimal_envelope_boundary():
    module = _adapter_module()
    adapter = module.HCPDQV2H6H7IsolationAdapter(
        policy=default_isolation_policy()
    )
    request = adapter.build_subject_request(_sample_envelope())
    assert set(request) == {"case_id", "family", "difficulty", "prompt"}


def test_red_requires_adapter_to_reject_ground_truth_material():
    module = _adapter_module()
    adapter = module.HCPDQV2H6H7IsolationAdapter(
        policy=default_isolation_policy()
    )
    contaminated = {
        "case_id": "V2-H6-RED-002",
        "family": "H6",
        "difficulty": "D1",
        "prompt": "Evaluate this case.",
        "expected_outcome": "forbidden",
    }
    with pytest.raises(module.IsolationBoundaryViolation):
        adapter.validate_subject_request(contaminated)


def test_red_requires_no_write_or_adaptation_capabilities():
    module = _adapter_module()
    adapter = module.HCPDQV2H6H7IsolationAdapter(
        policy=default_isolation_policy()
    )
    capabilities = adapter.authorized_capabilities()
    assert capabilities["memory_write"] is False
    assert capabilities["learning_write"] is False
    assert capabilities["persistent_state_write"] is False
    assert capabilities["adaptation"] is False


def test_red_requires_fresh_case_context_and_no_cross_case_visibility():
    module = _adapter_module()
    adapter = module.HCPDQV2H6H7IsolationAdapter(
        policy=default_isolation_policy()
    )
    first = adapter.open_case(_sample_envelope())
    adapter.capture_raw(first, "raw-result-one")
    second = adapter.open_case(
        SubjectEnvelope(
            case_id="V2-H7-RED-002",
            family="H7",
            difficulty="D2",
            prompt="Produce a feasible plan.",
        )
    )
    assert second.case_id != first.case_id
    assert adapter.visible_prior_results(second) == ()


def test_red_requires_raw_capture_before_scoring_boundary_opens():
    module = _adapter_module()
    adapter = module.HCPDQV2H6H7IsolationAdapter(
        policy=default_isolation_policy()
    )
    handle = adapter.open_case(_sample_envelope())
    assert adapter.scoring_allowed(handle) is False
    adapter.capture_raw(handle, "raw-result")
    assert adapter.scoring_allowed(handle) is True


def test_red_keeps_primary_execution_blocked_by_policy():
    module = _adapter_module()
    adapter = module.HCPDQV2H6H7IsolationAdapter(
        policy=default_isolation_policy()
    )
    with pytest.raises(module.PrimaryExecutionNotAuthorized):
        adapter.execute_primary_run([_sample_envelope()])
