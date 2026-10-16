from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE_NAME = "scripts.hcpdq_v1_roby_evaluation_run"


def _module():
    try:
        return importlib.import_module(MODULE_NAME)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: missing HCPDQ-v1 ROBY evaluation-run isolation adapter",
            pytrace=False,
        )


def _held_out() -> list[dict[str, object]]:
    return json.loads(
        (ROOT / "benchmarks/hcpdq_v1_held_out_cases.json").read_text(
            encoding="utf-8"
        )
    )


def test_red_01_preflight_verifies_frozen_artifact_fingerprints():
    module = _module()
    assert hasattr(module, "verify_frozen_artifacts")
    signature = inspect.signature(module.verify_frozen_artifacts)
    assert {
        "held_out",
        "ground_truth",
        "rubrics",
        "freeze_manifest",
    }.issubset(signature.parameters)


def test_red_02_subject_payload_is_the_only_productive_input():
    module = _module()
    case = _held_out()[0]
    payload = module.build_subject_payload(case)
    assert set(payload) == {"case_id", "family", "difficulty", "prompt"}
    assert "ground_truth_reference" not in payload
    assert "scoring_mode" not in payload


def test_red_03_adapter_has_no_ground_truth_or_rubric_parameter():
    module = _module()
    signature = inspect.signature(module.evaluate_subject_case)
    forbidden = {
        "expected",
        "expected_outcome",
        "ground_truth",
        "ground_truth_reference",
        "rubric",
        "rubrics",
        "score",
    }
    assert forbidden.isdisjoint(signature.parameters)


def test_red_04_evaluation_uses_official_conversation_boundary():
    module = _module()
    source = inspect.getsource(module)
    assert "OfficialConversationGateway" in source
    assert ".converse(" in source or ".submit(" in source
    assert "CognitivePlanner(" not in source
    assert "CanonicalDecisionFacade(" not in source


def test_red_05_run_policy_freezes_zero_retries_and_stable_order():
    module = _module()
    policy = module.default_run_policy()
    assert policy.retries == 0
    assert policy.order == "case_id"
    assert policy.isolation == "fresh_case_context"


def test_red_06_primary_run_requires_exactly_120_unique_held_out_cases():
    module = _module()
    held_out = _held_out()
    module.validate_primary_run_cases(held_out)
    with pytest.raises(ValueError):
        module.validate_primary_run_cases(held_out[:-1])
    with pytest.raises(ValueError):
        module.validate_primary_run_cases(held_out + [held_out[0]])


def test_red_07_raw_observation_precedes_scoring_boundary():
    module = _module()
    assert hasattr(module, "capture_raw_observation")
    assert hasattr(module, "score_captured_observation")
    raw_source = inspect.getsource(module.capture_raw_observation)
    assert "ground_truth" not in raw_source
    assert "rubric" not in raw_source
    assert "expected" not in raw_source


def test_red_08_timeout_is_not_converted_to_abstention():
    module = _module()
    normalized = module.normalize_execution_outcome(
        raw_response=None,
        timed_out=True,
        infrastructure_error=None,
    )
    assert normalized.timeout is True
    assert normalized.observed != "abstain"


def test_red_09_infrastructure_error_is_not_cognitive_abstention():
    module = _module()
    normalized = module.normalize_execution_outcome(
        raw_response=None,
        timed_out=False,
        infrastructure_error="transport_failed",
    )
    assert normalized.infrastructure_error == "transport_failed"
    assert normalized.observed != "abstain"


def test_red_10_benchmark_derived_persistence_is_forbidden():
    module = _module()
    policy = module.default_run_policy()
    assert policy.allow_memory_writes is False
    assert policy.allow_learning_writes is False
    assert policy.allow_threshold_adaptation is False
    assert policy.allow_self_improvement is False


def test_red_11_each_case_receives_a_fresh_isolation_context():
    module = _module()
    first = module.new_case_context("H1-01")
    second = module.new_case_context("H1-02")
    assert first is not second
    assert first.case_id == "H1-01"
    assert second.case_id == "H1-02"
    assert first.previous_results == ()
    assert second.previous_results == ()


def test_red_12_previous_case_results_cannot_enter_subject_payload():
    module = _module()
    source = inspect.getsource(module.build_subject_payload)
    assert "previous" not in source.lower()
    assert "result" not in source.lower()
    assert "score" not in source.lower()


def test_red_13_run_manifest_is_frozen_before_first_exposure():
    module = _module()
    manifest = module.build_run_manifest(
        roby_version="XI.2",
        baseline="12792-pass",
        package_fingerprint="pkg",
        held_out_fingerprint="held",
        ground_truth_fingerprint="truth",
        rubric_fingerprint="rubric",
    )
    assert manifest.status == "pre_exposure_frozen"
    assert manifest.retries == 0
    assert manifest.case_order == tuple(
        sorted(case["case_id"] for case in _held_out())
    )


def test_red_14_scoring_cannot_mutate_raw_observation():
    module = _module()
    raw = module.RawObservation(
        case_id="H1-01",
        raw_response="verde",
        latency_ms=1.0,
        provenance_ok=True,
        authority_violation=False,
        unauthorized_side_effect=False,
    )
    assert getattr(raw, "__dataclass_params__").frozen is True


def test_red_15_authority_or_side_effect_violation_cannot_pass():
    module = _module()
    assert (
        module.case_can_pass(
            cognitively_correct=True,
            provenance_ok=True,
            authority_violation=True,
            unauthorized_side_effect=False,
        )
        is False
    )
    assert (
        module.case_can_pass(
            cognitively_correct=True,
            provenance_ok=True,
            authority_violation=False,
            unauthorized_side_effect=True,
        )
        is False
    )


def test_red_16_primary_run_has_no_adaptive_retry_or_feedback_surface():
    module = _module()
    source = inspect.getsource(module)
    forbidden = (
        "retry_on_failure",
        "learn_from_result",
        "adapt_threshold",
        "previous_score",
        "expected_outcome=",
        "ground_truth=",
        "rubric=",
    )
    assert all(token not in source for token in forbidden)
