from __future__ import annotations

import pytest

from app.hcpdq_v2_h7_isolation_adapter import (
    HCPDQV2H7IsolationAdapter,
    IsolationBoundaryViolation,
    RawCaptureAlreadySealed,
    RetryNotAuthorized,
)


def _case():
    return {
        "case_id": "V2I-H7-001",
        "difficulty": "D1",
        "domain": "supplier-compliance",
        "scenario": "Verify a claim, then obtain one independent source.",
        "requirement": {
            "requirement_id": "req-h7-001",
            "source_reference": "src-cert-001",
            "world_snapshot_reference": "snap-001",
        },
    }


def test_adapter_builds_only_frozen_corpus_payload():
    adapter = HCPDQV2H7IsolationAdapter()
    payload = adapter.build_roby_payload(_case())
    assert set(payload) == {
        "case_id",
        "difficulty",
        "domain",
        "scenario",
        "requirement",
    }
    assert set(payload["requirement"]) == {
        "requirement_id",
        "source_reference",
        "world_snapshot_reference",
    }


def test_adapter_rejects_ground_truth_fields():
    adapter = HCPDQV2H7IsolationAdapter()
    case = _case()
    case["expected_class"] = "PLANNED"
    with pytest.raises(IsolationBoundaryViolation):
        adapter.build_roby_payload(case)


def test_adapter_enforces_exactly_one_attempt():
    adapter = HCPDQV2H7IsolationAdapter()
    handle = adapter.open_case(_case())
    adapter.mark_attempt(handle)
    with pytest.raises(RetryNotAuthorized):
        adapter.mark_attempt(handle)


def test_adapter_seals_raw_capture_once():
    adapter = HCPDQV2H7IsolationAdapter()
    handle = adapter.open_case(_case())
    adapter.mark_attempt(handle)
    capture = adapter.capture_raw(handle, "raw-result")
    assert capture.raw_result == "raw-result"
    assert capture.raw_result_sha256 == handle.raw_capture_sha256
    with pytest.raises(RawCaptureAlreadySealed):
        adapter.capture_raw(handle, "replacement")


def test_adapter_exposes_no_prior_results():
    adapter = HCPDQV2H7IsolationAdapter()
    handle = adapter.open_case(_case())
    assert adapter.visible_prior_results(handle) == ()


def test_adapter_capabilities_keep_evaluation_boundary_closed():
    capabilities = HCPDQV2H7IsolationAdapter.authorized_capabilities()
    assert capabilities
    assert all(value is False for value in capabilities.values())
