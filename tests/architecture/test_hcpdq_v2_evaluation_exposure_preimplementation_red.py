from __future__ import annotations

import importlib
import inspect
from dataclasses import FrozenInstanceError, fields

import pytest

MODULE_NAME = "scripts.hcpdq_v2_evaluation_exposure"


def _module():
    try:
        return importlib.import_module(MODULE_NAME)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: missing HCPDQ-v2 read-only evaluation exposure layer",
            pytrace=False,
        )


def test_e1_exposure_policy_grants_zero_authority():
    module = _module()
    policy = module.default_exposure_policy()
    assert policy.grants_decision_authority is False
    assert policy.grants_routing_authority is False
    assert policy.grants_planning_authority is False
    assert policy.grants_reasoning_authority is False
    assert policy.grants_learning_authority is False
    assert policy.grants_autonomy is False
    assert getattr(policy, "__dataclass_params__").frozen is True


def test_e2_existing_authority_identity_is_preserved_not_relabelled():
    module = _module()
    evidence = module.ExposureEvidence(
        family="H4",
        existing_authority="GovernedStructuralKnowledgeTransferMatcher",
        existing_productive_path="existing_structural_transfer_path",
        authority_participation_evidence=("matcher-participated",),
        status="completed",
        response_path="existing",
        degradation_reason="not_applicable",
        rationale=("existing-authority",),
        side_effect_evidence=(),
        latency_ms=1.0,
        measurement_validity="valid",
    )
    assert evidence.existing_authority == (
        "GovernedStructuralKnowledgeTransferMatcher"
    )
    assert "benchmark" not in evidence.existing_authority.casefold()


def test_e3_exposure_layer_does_not_directly_instantiate_internal_authorities():
    module = _module()
    source = inspect.getsource(module)
    forbidden = (
        "CognitivePlanner(",
        "GovernedStructuralKnowledgeTransferMatcher(",
        "GovernedTargetProblemStructuralProjector(",
        "GovernedContextualCaseRoleGrounder(",
        "CanonicalDecisionFacade(",
        "CanonicalPlanningFacade(",
    )
    assert all(token not in source for token in forbidden)


def test_e4_family_mapping_is_metadata_only_not_semantic_prompt_routing():
    module = _module()
    signature = inspect.signature(module.exposure_for_family)
    assert tuple(signature.parameters) == ("family",)
    source = inspect.getsource(module.exposure_for_family)
    assert "prompt" not in source
    assert "classify" not in source
    assert "semantic" not in source.casefold()


def test_e5_ground_truth_firewall_is_structural():
    module = _module()
    names = {item.name for item in fields(module.ExposureRequest)}
    assert {"family", "case_id", "input_payload"}.issubset(names)
    forbidden = {
        "expected",
        "expected_answer",
        "ground_truth",
        "rubric",
        "human_answer",
        "score",
        "previous_score",
        "held_out_solution",
    }
    assert forbidden.isdisjoint(names)
    assert getattr(module.ExposureRequest, "__dataclass_params__").frozen is True


def test_e6_exposure_policy_forbids_persistence_and_adaptation():
    module = _module()
    policy = module.default_exposure_policy()
    assert policy.allow_memory_writes is False
    assert policy.allow_learning_writes is False
    assert policy.allow_goal_task_project_writes is False
    assert policy.allow_threshold_adaptation is False
    assert policy.allow_benchmark_state is False
    with pytest.raises(FrozenInstanceError):
        policy.allow_memory_writes = True


def test_e7_valid_measurement_requires_causal_authority_evidence():
    module = _module()
    incomplete = module.ExposureEvidence(
        family="H3",
        existing_authority="CognitivePlanner",
        existing_productive_path="",
        authority_participation_evidence=(),
        status="completed",
        response_path="existing",
        degradation_reason="not_applicable",
        rationale=(),
        side_effect_evidence=(),
        latency_ms=1.0,
        measurement_validity="unclassifiable",
    )
    assert module.authority_exposure_certified(incomplete) is False


def test_e8_shadow_equivalence_requires_same_cognitive_result():
    module = _module()
    assert module.shadow_equivalent(
        production_result="same-result",
        observed_result="same-result",
    )
    assert not module.shadow_equivalent(
        production_result="same-result",
        observed_result="changed-result",
    )


def test_e9_family_exclusion_is_fail_closed_and_non_cognitive():
    module = _module()
    exclusion = module.exclude_unmeasurable_family(
        family="H5",
        reason="would require benchmark-specific authority",
    )
    assert exclusion.family == "H5"
    assert exclusion.held_out_authorized is False
    assert exclusion.capability_absent is False
    assert exclusion.classification == "NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2"


def test_e10_held_out_remains_no_go_until_every_included_family_is_certified():
    module = _module()
    coverage = {
        "H6": True,
        "H2": False,
    }
    assert module.held_out_authorized(coverage) is False
    assert module.held_out_authorized({"H6": True}) is True


def test_exposure_evidence_schema_is_read_only_observational_only():
    module = _module()
    names = {item.name for item in fields(module.ExposureEvidence)}
    required = {
        "family",
        "existing_authority",
        "existing_productive_path",
        "authority_participation_evidence",
        "status",
        "response_path",
        "degradation_reason",
        "rationale",
        "side_effect_evidence",
        "latency_ms",
        "measurement_validity",
    }
    assert required.issubset(names)
    assert getattr(module.ExposureEvidence, "__dataclass_params__").frozen is True


def test_h1_h2_h3_h4_h5_h7_h8_begin_uncertified_and_calibration_only():
    module = _module()
    registry = module.default_exposure_registry()
    remaining = {"H1", "H2", "H3", "H4", "H5", "H7", "H8"}
    assert remaining.issubset(registry)
    for family in remaining:
        item = registry[family]
        assert item.calibration_only is True
        assert item.exposure_certified is False
        assert item.held_out_authorized is False


def test_h6_existing_certification_is_not_reimplemented_by_exposure_layer():
    module = _module()
    registry = module.default_exposure_registry()
    h6 = registry["H6"]
    assert h6.exposure_certified is True
    assert h6.reuse_existing_certification is True
    assert h6.new_exposure_required is False


def test_no_family_can_be_made_green_by_benchmark_specific_binding():
    module = _module()
    source = inspect.getsource(module)
    forbidden = (
        ".bind_planner(",
        "bind_planner=",
        "benchmark_router",
        "BenchmarkRouter",
        "HCPDQRouter",
        "EvaluationDecisionEngine",
    )
    assert all(token not in source for token in forbidden)


def test_exposure_contract_does_not_authorize_v2_held_out_construction():
    module = _module()
    policy = module.default_exposure_policy()
    assert policy.allow_held_out_construction is False
    assert policy.allow_human_comparison is False
