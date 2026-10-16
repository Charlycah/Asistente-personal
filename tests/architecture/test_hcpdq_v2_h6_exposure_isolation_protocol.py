from __future__ import annotations

from scripts.hcpdq_v2_h6_exposure_isolation_protocol import (
    freeze_h6_exposure_isolation_protocol,
)


def test_exposure_isolation_protocol_freezes_exact_input_boundary():
    report = freeze_h6_exposure_isolation_protocol()
    protocol = report["protocol"]
    assert report["protocol_frozen"] is True
    assert "case_id plus frozen prompt only" in protocol["input_surface"]
    assert "delivered unchanged" in protocol["input_surface"]


def test_protocol_keeps_ground_truth_and_scoring_outside_boundary():
    report = freeze_h6_exposure_isolation_protocol()
    protocol = report["protocol"]
    assert "not loaded" in protocol["ground_truth_boundary"]
    assert "no scoring" in protocol["scoring_policy"]
    assert report["ground_truth_exposure_occurred"] is False
    assert report["scoring_occurred"] is False


def test_protocol_requires_case_isolation_one_attempt_and_fail_closed_capture():
    report = freeze_h6_exposure_isolation_protocol()
    protocol = report["protocol"]
    assert "fresh evaluation context per case" in protocol["case_isolation"]
    assert protocol["retry_policy"] == (
        "exactly one attempt per case; retries prohibited"
    )
    assert "recorded as-is" in protocol["failure_policy"]


def test_protocol_blocks_learning_memory_feedback_and_mutation():
    report = freeze_h6_exposure_isolation_protocol()
    assert report["learning_or_adaptation_authorized"] is False
    assert report["memory_writeback_authorized"] is False
    assert report["benchmark_feedback_authorized"] is False
    assert report["corpus_mutation_authorized"] is False
    assert report["ground_truth_mutation_authorized"] is False
    assert report["response_mutation_after_capture_authorized"] is False


def test_protocol_gate_performs_no_held_out_exposure_or_execution():
    report = freeze_h6_exposure_isolation_protocol()
    assert report["held_out_prompt_exposure_occurred"] is False
    assert report["primary_execution_authorized"] is False
    assert report["exposure_adapter_implemented"] is False


def test_protocol_requires_red_tests_before_adapter_implementation():
    report = freeze_h6_exposure_isolation_protocol()
    assert report["pre_execution_red_tests_written"] is False
    assert report["status"] == "PROTOCOL_FROZEN_PRE_EXECUTION_TESTS_REQUIRED"
    assert report["next_gate"].endswith(
        "Pre-Execution RED / Isolation Contract Tests"
    )
