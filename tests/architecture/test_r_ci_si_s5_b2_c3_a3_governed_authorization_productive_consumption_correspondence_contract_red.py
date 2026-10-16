from __future__ import annotations

from dataclasses import fields
from importlib import import_module
from unittest.mock import patch

import pytest

from app.governed_independence_authorization_productive_consumption import (
    GovernedIndependenceAuthorizationProductiveConsumption,
    GovernedIndependenceAuthorizationProductiveConsumptionV1,
)

MODULE = "app.governed_epistemic_authorization_productive_consumption_binding"
A2_MODULE = "app.governed_epistemic_authorization_result_binding"
A2_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_b2_c3_a2_governed_authorization_"
    "invocation_result_binding_contract_red"
)


def _contract():
    return import_module(MODULE)


def _a2_binding():
    a2 = import_module(A2_MODULE)
    fixtures = import_module(A2_TEST_MODULE)
    correspondence = fixtures._correspondence()
    boundary = fixtures._boundary()
    result = a2.GovernedEpistemicAuthorizationResultBindingBridgeV1().bind(
        correspondence,
        boundary,
    )
    assert result is not None
    return result


def _consume(contract, binding):
    return contract.GovernedEpistemicAuthorizationProductiveConsumptionBridgeV1().bind(
        binding
    )


def test_r1_requires_actual_a2_binding_and_preserves_s5_anchors() -> None:
    contract = _contract()
    binding = _a2_binding()

    result = _consume(contract, binding)

    assert result is not None
    assert result.authorization_result_binding is binding
    assert result.correspondence is binding.correspondence
    assert result.selection is binding.selection
    assert result.selected_path_eligibility is binding.selected_path_eligibility
    with pytest.raises(TypeError):
        _consume(contract, binding.authorization_report)
    with pytest.raises(TypeError):
        _consume(contract, object())


def test_r2_calls_existing_productive_owner_once_with_exact_a2_report() -> None:
    contract = _contract()
    binding = _a2_binding()
    owner = GovernedIndependenceAuthorizationProductiveConsumptionV1
    original = owner.consume

    with patch.object(owner, "consume", wraps=original) as consume:
        result = _consume(contract, binding)

    assert result is not None
    consume.assert_called_once_with(binding.authorization_report)


def test_r3_preserves_exact_existing_productive_consumption() -> None:
    contract = _contract()
    binding = _a2_binding()
    expected = GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(
        binding.authorization_report
    )

    with patch.object(
        GovernedIndependenceAuthorizationProductiveConsumptionV1,
        "consume",
        return_value=expected,
    ):
        result = _consume(contract, binding)

    assert result is not None
    assert result.productive_consumption is expected
    assert result.authorization_report is binding.authorization_report
    assert result.authorization_decision is expected.decision
    assert result.independence_level is expected.independence_level
    assert result.authorization_id == expected.authorization_id
    assert result.authorization_requirement_id == expected.requirement_id
    assert result.authorization_plan_id == expected.plan_id
    assert result.rationale_codes == expected.rationale_codes
    assert result.productive_source_fingerprint == expected.source_fingerprint


def test_r4_rejects_inconsistent_product_without_repair() -> None:
    contract = _contract()
    binding = _a2_binding()
    product = GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(
        binding.authorization_report
    )
    other_binding = _a2_binding()
    mismatch_specs = (
        ("authorization_report", other_binding.authorization_report),
        ("authorization_id", "other-authorization"),
        ("capability_name", "other-capability"),
        ("source_reference", "other-source"),
        ("world_snapshot_id", "other-snapshot"),
    )
    mismatches = []
    for name, value in mismatch_specs:
        mismatch = object.__new__(
            GovernedIndependenceAuthorizationProductiveConsumption
        )
        for item in fields(product):
            object.__setattr__(mismatch, item.name, getattr(product, item.name))
        object.__setattr__(mismatch, name, value)
        mismatches.append(mismatch)

    for mismatch in mismatches:
        with patch.object(
            GovernedIndependenceAuthorizationProductiveConsumptionV1,
            "consume",
            return_value=mismatch,
        ):
            assert _consume(contract, binding) is None


def test_r5_exposes_only_owner_derived_next_gate_eligibility() -> None:
    contract = _contract()
    binding = _a2_binding()

    result = _consume(contract, binding)

    assert result is not None
    assert result.eligible_for_next_governed_gate is (
        result.productive_consumption.eligible_for_next_governed_gate
    )
    assert result.execution_authorized is False
    result_fields = {
        item.name
        for item in fields(
            contract.GovernedEpistemicAuthorizationProductiveConsumptionBinding
        )
    }
    for forbidden in (
        "authorized_for_execution",
        "executable",
        "acquire_now",
        "authorization_score",
    ):
        assert forbidden not in result_fields


def test_r6_preserves_direct_owner_ids_without_s5_or_planning_rewrite() -> None:
    contract = _contract()
    binding = _a2_binding()

    result = _consume(contract, binding)

    assert result is not None
    assert result.requirement_identity == binding.requirement_identity
    assert result.authorization_requirement_id == binding.authorization_requirement_id
    assert result.authorization_plan_id == binding.authorization_plan_id
    assert result.authorization_requirement_id != result.requirement_identity
    assert result.direct_ids_are_s5_lineage is False
    assert result.synthesizes_planning is False


def test_r7_owner_failure_or_invalid_output_cannot_create_binding() -> None:
    contract = _contract()
    binding = _a2_binding()
    bridge = contract.GovernedEpistemicAuthorizationProductiveConsumptionBridgeV1()
    owner = GovernedIndependenceAuthorizationProductiveConsumptionV1

    with patch.object(
        owner,
        "consume",
        side_effect=RuntimeError("owner failure"),
    ) as consume:
        with pytest.raises(RuntimeError, match="owner failure"):
            bridge.bind(binding)
        consume.assert_called_once_with(binding.authorization_report)

    for invalid in (None, object()):
        with patch.object(owner, "consume", return_value=invalid) as consume:
            assert bridge.bind(binding) is None
            consume.assert_called_once_with(binding.authorization_report)

    assert bridge.retries_productive_owner is False
    assert bridge.fabricates_productive_consumption is False


def test_r8_binding_is_nonexecutive_and_stops_after_productive_consumption() -> None:
    contract = _contract()
    binding = _a2_binding()
    bridge = contract.GovernedEpistemicAuthorizationProductiveConsumptionBridgeV1()

    result = bridge.bind(binding)

    assert result is not None
    assert isinstance(
        result.productive_consumption,
        GovernedIndependenceAuthorizationProductiveConsumption,
    )
    assert result.read_only is True
    assert result.derivational is True
    assert result.execution_authorized is False
    inert_flags = (
        "queries_capability_registry",
        "queries_official_runtime",
        "reruns_a1_admission",
        "reruns_a2_authorization",
        "reconstructs_selection",
        "reconstructs_eligibility",
        "ranks_paths",
        "reselects_paths",
        "plans_acquisition",
        "acquires_evidence",
        "invokes_selected_capability",
        "queries_selected_source",
        "invokes_execution_gateway",
        "authorizes_execution",
        "executes_actions",
        "asks_human",
        "creates_questions",
        "assigns_relevance",
        "invokes_curiosity",
        "invokes_initiative",
        "invokes_conversation",
        "persists_results",
        "creates_learning_candidate",
        "modifies_memory",
        "modifies_world_model",
        "creates_cognitive_authority",
        "claims_subjective_experience",
        "claims_consciousness",
    )
    for flag in inert_flags:
        assert getattr(bridge, flag) is False
