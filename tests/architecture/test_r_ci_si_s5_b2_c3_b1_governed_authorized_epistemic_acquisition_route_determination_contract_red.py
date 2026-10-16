from __future__ import annotations

from dataclasses import fields
from importlib import import_module

import pytest

MODULE = "app.governed_authorized_epistemic_acquisition_route_determination"
A3_MODULE = "app.governed_epistemic_authorization_productive_consumption_binding"
A3_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_b2_c3_a3_governed_authorization_"
    "productive_consumption_correspondence_contract_red"
)


def _contract():
    return import_module(MODULE)


def _a3_binding():
    a3 = import_module(A3_MODULE)
    fixtures = import_module(A3_TEST_MODULE)
    a2_binding = fixtures._a2_binding()
    result = a3.GovernedEpistemicAuthorizationProductiveConsumptionBridgeV1().bind(
        a2_binding
    )
    assert result is not None
    return result


def _determine(contract, binding):
    owner = contract.GovernedAuthorizedEpistemicAcquisitionRouteDeterminationV1()
    return owner.determine(binding)


def test_r1_requires_actual_a3_binding_and_preserves_upstream_anchors() -> None:
    contract = _contract()
    binding = _a3_binding()

    result = _determine(contract, binding)

    assert result.authorization_productive_binding is binding
    assert result.authorization_result_binding is binding.authorization_result_binding
    assert result.correspondence is binding.correspondence
    assert result.selection is binding.selection
    assert result.selected_path_eligibility is binding.selected_path_eligibility
    assert result.productive_consumption is binding.productive_consumption
    assert result.authorization_report is binding.authorization_report
    with pytest.raises(TypeError):
        _determine(contract, binding.authorization_result_binding)
    with pytest.raises(TypeError):
        _determine(contract, object())


def test_r2_preserves_selected_capability_and_exact_authorization_lineage() -> None:
    contract = _contract()
    binding = _a3_binding()

    result = _determine(contract, binding)

    product = binding.productive_consumption
    assert result.capability_name == product.capability_name
    assert result.source_reference == product.source_reference
    assert result.world_snapshot_id == product.world_snapshot_id
    assert result.authorization_decision is binding.authorization_decision
    assert result.independence_level is binding.independence_level
    assert result.authorization_id == binding.authorization_id
    assert result.authorization_requirement_id == binding.authorization_requirement_id
    assert result.authorization_plan_id == binding.authorization_plan_id
    assert result.requirement_identity == binding.requirement_identity


def test_r3_next_gate_eligibility_is_preserved_but_not_route_authority() -> None:
    contract = _contract()
    binding = _a3_binding()

    result = _determine(contract, binding)

    assert result.eligible_for_next_governed_gate is (
        binding.eligible_for_next_governed_gate
    )
    assert result.acquisition_authorized is False
    assert result.execution_authorized is False
    result_fields = {
        item.name
        for item in fields(
            contract.GovernedAuthorizedEpistemicAcquisitionRouteDetermination
        )
    }
    for forbidden in ("route_authorized", "acquire_now", "executable"):
        assert forbidden not in result_fields


def test_r4_direct_s5_lineage_has_no_compatible_level2_route() -> None:
    contract = _contract()
    binding = _a3_binding()

    result = _determine(contract, binding)

    assert result.status is (
        contract.GovernedAuthorizedEpistemicAcquisitionRouteStatus.
        NO_COMPATIBLE_CANONICAL_ROUTE
    )
    assert result.compatible_route is None
    assert result.has_actual_planning_product is False
    assert result.direct_ids_are_planning_lineage is False
    assert result.authorization_requirement_id != result.requirement_identity
    assert result.synthesizes_planning is False


def test_r5_does_not_infer_routes_from_runtime_registry_or_metadata() -> None:
    contract = _contract()
    owner = contract.GovernedAuthorizedEpistemicAcquisitionRouteDeterminationV1()

    assert owner.queries_capability_registry is False
    assert owner.queries_official_runtime is False
    assert owner.uses_evidence_reader_metadata is False
    assert owner.uses_capability_kind_as_route is False
    assert owner.uses_tags_as_route is False
    assert owner.uses_dependency_metadata_as_route is False
    assert owner.uses_permission_routing_as_epistemic_route is False
    assert owner.maintains_capability_route_table is False
    assert owner.uses_dynamic_route_discovery is False


def test_r6_specialized_integrations_are_not_generic_s5_routes() -> None:
    contract = _contract()
    binding = _a3_binding()
    owner = contract.GovernedAuthorizedEpistemicAcquisitionRouteDeterminationV1()

    result = owner.determine(binding)

    assert result.compatible_route is None
    assert owner.invokes_roby_initiated_library_access is False
    assert owner.invokes_local_library_conversation is False
    assert owner.invokes_specialized_capability_runtime is False
    assert owner.matches_route_by_capability_name is False


def test_r7_determination_is_deterministic_and_fail_closed() -> None:
    contract = _contract()
    binding = _a3_binding()
    owner = contract.GovernedAuthorizedEpistemicAcquisitionRouteDeterminationV1()

    first = owner.determine(binding)
    second = owner.determine(binding)

    assert first.status is second.status
    assert first.rationale_codes == second.rationale_codes
    assert first.compatible_route is None
    assert "route:no_compatible_canonical_route_proven" in first.rationale_codes
    assert first.authorization_decision is binding.authorization_decision
    assert first.creates_epistemic_conclusion is False
    assert first.fabricates_fallback_route is False


def test_r8_route_determination_stops_before_acquisition_or_execution() -> None:
    contract = _contract()
    binding = _a3_binding()
    owner = contract.GovernedAuthorizedEpistemicAcquisitionRouteDeterminationV1()

    result = owner.determine(binding)

    assert result.read_only is True
    assert result.derivational is True
    assert result.acquisition_authorized is False
    assert result.execution_authorized is False
    inert_flags = (
        "reruns_authorization",
        "reruns_productive_authorization_consumption",
        "selects_capability",
        "ranks_capabilities",
        "reselects_epistemic_path",
        "plans_acquisition",
        "acquires_evidence",
        "queries_selected_source",
        "invokes_specialized_capability_runtime",
        "invokes_execution_gateway",
        "invokes_official_capability_gateway",
        "authorizes_execution",
        "executes_actions",
        "asks_human",
        "creates_questions",
        "invokes_curiosity",
        "assigns_relevance",
        "invokes_initiative",
        "invokes_conversation",
        "persists_results",
        "creates_learning_candidate",
        "modifies_memory",
        "modifies_world_model",
        "creates_cognitive_authority",
        "creates_planning_authority",
        "creates_routing_authority",
        "creates_acquisition_authority",
        "creates_execution_authority",
    )
    for flag in inert_flags:
        assert getattr(owner, flag) is False
