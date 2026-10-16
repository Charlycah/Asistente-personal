from __future__ import annotations

import importlib
import inspect
from dataclasses import FrozenInstanceError, fields

import pytest

MODULE_NAME = "scripts.hcpdq_v2_evaluation_boundary"


class _Turn:
    response_text = ""
    status = "withheld"
    response_path = "degraded"
    degradation_reason = "provider_unavailable"
    rationale = ("insufficient verified evidence",)
    provider_call_performed = False
    retrieval_performed = True
    network_access_performed = False


class _Dossier:
    participated_node_ids = ("conversation_ingress", "unified_coordination")
    first_interruption_node_id = "memory_recall"
    evidence_fingerprint = "a" * 64


class _Gateway:
    def converse(self, text: str):
        return _Turn()

    @property
    def cognitive_turn_dossiers(self):
        class _Snapshot:
            latest_dossier = _Dossier()

        return _Snapshot()


def _module():
    try:
        return importlib.import_module(MODULE_NAME)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: missing HCPDQ-v2 evaluation-boundary observability layer",
            pytrace=False,
        )


def test_o1_raw_observation_preserves_turn_status():
    module = _module()
    observation = module.capture_observable_turn(
        case_id="CAL-H2-POS-01",
        family="H2",
        gateway=_Gateway(),
        prompt="synthetic calibration only",
    )
    assert observation.turn_status == "withheld"


def test_o2_raw_observation_preserves_response_path():
    module = _module()
    observation = module.capture_observable_turn(
        case_id="CAL-H6-POS-01",
        family="H6",
        gateway=_Gateway(),
        prompt="synthetic calibration only",
    )
    assert observation.response_path == "degraded"


def test_o3_raw_observation_preserves_degradation_reason():
    module = _module()
    observation = module.capture_observable_turn(
        case_id="CAL-H8-BND-01",
        family="H8",
        gateway=_Gateway(),
        prompt="synthetic calibration only",
    )
    assert observation.degradation_reason == "provider_unavailable"


def test_o4_raw_observation_preserves_rationale_and_runtime_flags():
    module = _module()
    observation = module.capture_observable_turn(
        case_id="CAL-H1-POS-01",
        family="H1",
        gateway=_Gateway(),
        prompt="synthetic calibration only",
    )
    assert observation.rationale == ("insufficient verified evidence",)
    assert observation.provider_call_performed is False
    assert observation.retrieval_performed is True
    assert observation.network_access_performed is False


def test_o5_authority_path_evidence_comes_from_existing_dossier():
    module = _module()
    observation = module.capture_observable_turn(
        case_id="CAL-H4-POS-01",
        family="H4",
        gateway=_Gateway(),
        prompt="synthetic calibration only",
    )
    evidence = observation.authority_path_evidence
    assert evidence.participated_node_ids == (
        "conversation_ingress",
        "unified_coordination",
    )
    assert evidence.first_interruption_node_id == "memory_recall"
    assert evidence.evidence_fingerprint == "a" * 64
    assert evidence.read_only is True
    assert evidence.grants_authority is False


def test_o6_measurement_validity_precedes_cognitive_scoring():
    module = _module()
    empty = module.ObservableTurn(
        case_id="CAL-H2-POS-01",
        family="H2",
        raw_response="",
        turn_status="withheld",
        response_path="degraded",
        degradation_reason="provider_unavailable",
        rationale=("insufficient verified evidence",),
        provider_call_performed=False,
        retrieval_performed=True,
        network_access_performed=False,
        latency_ms=1.0,
        authority_path_evidence=None,
        authority_violation=False,
        unauthorized_side_effect=False,
        infrastructure_error=None,
        timeout=False,
    )
    validity = module.classify_measurement_validity(empty)
    assert validity != module.MeasurementValidity.VALID
    assert module.cognitive_scoring_allowed(validity) is False


def test_o7_timeout_contract_is_mechanically_enforced():
    module = _module()
    source = inspect.getsource(module.execute_with_timeout)
    assert "timeout_seconds" in inspect.signature(
        module.execute_with_timeout
    ).parameters
    assert (
        "future.result(timeout=" in source
        or ".join(timeout=" in source
        or "communicate(timeout=" in source
        or "wait(timeout=" in source
    )
    with pytest.raises(module.EvaluationTimeout):
        module.execute_with_timeout(lambda: __import__("time").sleep(0.05), 0.001)


def test_o8_final_package_identity_must_be_exact_before_exposure():
    module = _module()
    assert module.verify_final_package_identity(
        expected_sha256="a" * 64,
        actual_sha256="a" * 64,
        baseline="12813-pass-0-fail-ruff-clean",
        manifest_baseline="12813-pass-0-fail-ruff-clean",
    )
    with pytest.raises(ValueError):
        module.verify_final_package_identity(
            expected_sha256="a" * 64,
            actual_sha256="b" * 64,
            baseline="12813-pass-0-fail-ruff-clean",
            manifest_baseline="12813-pass-0-fail-ruff-clean",
        )
    with pytest.raises(ValueError):
        module.verify_final_package_identity(
            expected_sha256="a" * 64,
            actual_sha256="a" * 64,
            baseline="12813-pass-0-fail-ruff-clean",
            manifest_baseline="12808-pass-0-fail-ruff-clean",
        )


def test_o9_h1_h8_calibration_coverage_map_is_explicit_and_fail_closed():
    module = _module()
    coverage = module.default_family_path_coverage()
    assert set(coverage) == {f"H{i}" for i in range(1, 9)}
    assert coverage["H1"].audit_state == "P1"
    assert coverage["H2"].audit_state == "P2"
    assert coverage["H3"].audit_state == "P1"
    assert coverage["H4"].audit_state == "P1"
    assert coverage["H5"].audit_state == "P1"
    assert coverage["H6"].audit_state == "P3"
    assert coverage["H7"].audit_state == "P2"
    assert coverage["H8"].audit_state == "P2"
    assert all(item.held_out_authorized is False for item in coverage.values())
    assert all(item.requires_calibration is True for item in coverage.values())


def test_o10_observability_is_read_only_and_forbids_benchmark_adaptation():
    module = _module()
    policy = module.default_observability_policy()
    assert policy.allow_memory_writes is False
    assert policy.allow_learning_writes is False
    assert policy.allow_threshold_adaptation is False
    assert policy.allow_self_improvement is False
    assert policy.allow_benchmark_semantic_routing is False
    assert policy.allow_held_out_construction is False
    assert policy.allow_human_comparison is False
    assert policy.calibration_only is True
    assert getattr(policy, "__dataclass_params__").frozen is True
    with pytest.raises(FrozenInstanceError):
        policy.allow_memory_writes = True


def test_observable_turn_schema_is_immutable_and_has_no_ground_truth():
    module = _module()
    names = {item.name for item in fields(module.ObservableTurn)}
    required = {
        "case_id",
        "family",
        "raw_response",
        "turn_status",
        "response_path",
        "degradation_reason",
        "rationale",
        "provider_call_performed",
        "retrieval_performed",
        "network_access_performed",
        "latency_ms",
        "authority_path_evidence",
        "authority_violation",
        "unauthorized_side_effect",
        "infrastructure_error",
        "timeout",
    }
    forbidden = {
        "expected",
        "expected_outcome",
        "ground_truth",
        "rubric",
        "score",
        "previous_result",
    }
    assert required.issubset(names)
    assert forbidden.isdisjoint(names)
    assert getattr(module.ObservableTurn, "__dataclass_params__").frozen is True


def test_empty_response_is_never_directly_equated_with_cognitive_failure():
    module = _module()
    source = inspect.getsource(module.classify_measurement_validity)
    assert "raw_response" in source
    assert "turn_status" in source
    assert "response_path" in source
    assert "degradation_reason" in source
    assert "cognitively_correct" not in source
    assert "ground_truth" not in source


def test_family_mapping_selects_only_frozen_existing_interface_metadata():
    module = _module()
    signature = inspect.signature(module.interface_for_family)
    assert tuple(signature.parameters) == ("family",)
    source = inspect.getsource(module.interface_for_family)
    assert "prompt" not in source
    assert "classify" not in source
    assert "CognitivePlanner(" not in source
    assert "CanonicalDecisionFacade(" not in source
    assert "CanonicalPlanningFacade(" not in source
