from __future__ import annotations

import json

from scripts.hcpdq_v2_h6_h7_exposure_isolation_protocol import (
    CASES,
    build_subject_envelope,
    default_isolation_policy,
    freeze_exposure_isolation_protocol,
    subject_envelope_contains_ground_truth,
)


def test_subject_envelope_exposes_only_identity_scope_difficulty_and_prompt():
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    envelope = build_subject_envelope(cases[0])
    assert set(envelope.__dict__) == {
        "case_id",
        "family",
        "difficulty",
        "prompt",
    }
    assert subject_envelope_contains_ground_truth(envelope) is False


def test_protocol_keeps_ground_truth_and_scoring_outside_subject_boundary():
    report = freeze_exposure_isolation_protocol()
    assert report["ground_truth_available_to_subject"] is False
    assert report["ground_truth_loaded_by_subject_adapter"] is False
    assert report["scoring_occurs_after_raw_capture"] is True


def test_protocol_forbids_writes_learning_adaptation_and_primary_execution():
    policy = default_isolation_policy()
    assert policy.allow_memory_writes is False
    assert policy.allow_learning_writes is False
    assert policy.allow_threshold_adaptation is False
    assert policy.allow_self_improvement is False
    assert policy.allow_persistent_state_writes is False
    assert policy.allow_primary_execution is False


def test_protocol_requires_fresh_case_isolation_without_cross_case_results():
    report = freeze_exposure_isolation_protocol()
    assert report["fresh_case_context_required"] is True
    assert report["cross_case_result_visibility"] is False
    assert report["retries"] == 0
    assert report["order"] == "case_id"


def test_protocol_authorizes_red_but_not_primary_execution():
    report = freeze_exposure_isolation_protocol()
    assert report["status"] == "PROTOCOL_FROZEN_PREEXECUTION_RED_AUTHORIZED"
    assert report["controlled_exposure_authorized"] is True
    assert report["preexecution_red_tests_authorized"] is True
    assert report["primary_execution_authorized"] is False
    assert report["human_comparison_authorized"] is False
