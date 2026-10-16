from __future__ import annotations

from dataclasses import fields
from importlib import import_module

import pytest

MODULE = "app.governed_self_epistemic_need_to_ask"
B1_MODULE = "app.governed_authorized_epistemic_acquisition_route_determination"
B1_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_b2_c3_b1_governed_authorized_epistemic_"
    "acquisition_route_determination_contract_red"
)


def _contract():
    return import_module(MODULE)


def _b1_determination():
    b1 = import_module(B1_MODULE)
    fixtures = import_module(B1_TEST_MODULE)
    binding = fixtures._a3_binding()
    return b1.GovernedAuthorizedEpistemicAcquisitionRouteDeterminationV1().determine(
        binding
    )


def _determine(contract, route):
    owner = contract.GovernedSelfEpistemicNeedToAskDeterminationV1()
    return owner.determine(route)


def test_r1_requires_actual_b1_and_preserves_all_upstream_anchors() -> None:
    contract = _contract()
    route = _b1_determination()

    result = _determine(contract, route)

    binding = route.authorization_productive_binding
    assert result.route_determination is route
    assert result.authorization_productive_binding is binding
    assert result.authorization_result_binding is route.authorization_result_binding
    assert result.correspondence is route.correspondence
    assert result.selection is route.selection
    assert result.selected_path_eligibility is route.selected_path_eligibility
    assert result.productive_consumption is route.productive_consumption
    assert result.authorization_report is route.authorization_report
    with pytest.raises(TypeError):
        _determine(contract, binding)
    with pytest.raises(TypeError):
        _determine(contract, object())


def test_r2_preserves_exact_self_epistemic_and_authorization_lineage() -> None:
    contract = _contract()
    route = _b1_determination()

    result = _determine(contract, route)

    assert result.capability_name == route.capability_name
    assert result.source_reference == route.source_reference
    assert result.world_snapshot_id == route.world_snapshot_id
    assert result.requirement_identity == route.requirement_identity
    assert result.authorization_decision is route.authorization_decision
    assert result.independence_level is route.independence_level
    assert result.authorization_id == route.authorization_id
    assert result.authorization_requirement_id == route.authorization_requirement_id
    assert result.authorization_plan_id == route.authorization_plan_id
    assert result.route_status is route.status
    assert result.route_rationale_codes == route.rationale_codes


def test_r3_need_to_ask_is_not_question_worthiness_or_ask_now() -> None:
    contract = _contract()
    route = _b1_determination()

    result = _determine(contract, route)

    assert result.status is contract.GovernedSelfEpistemicNeedToAskStatus.NEED_TO_ASK
    assert result.question_worthiness_determined is False
    assert result.question_candidate is None
    assert result.target_person is None
    assert result.ask_now is False
    assert result.human_required is False
    result_fields = {
        item.name
        for item in fields(contract.GovernedSelfEpistemicNeedToAskDetermination)
    }
    assert "question" not in result_fields


def test_r4_preserves_no_route_facts_without_fabricating_resolution() -> None:
    contract = _contract()
    route = _b1_determination()

    result = _determine(contract, route)

    assert result.compatible_route is None
    assert result.acquisition_authorized is False
    assert result.execution_authorized is False
    assert result.has_actual_planning_product is False
    assert result.direct_ids_are_planning_lineage is False
    assert result.synthesizes_planning is False
    assert result.autonomous_resolution_currently_proven is False
    assert result.creates_epistemic_conclusion is False
    assert result.fabricates_fallback_route is False


def test_r5_authorization_decision_is_preserved_not_used_as_ask_now_rule() -> None:
    contract = _contract()
    route = _b1_determination()
    owner = contract.GovernedSelfEpistemicNeedToAskDeterminationV1()

    result = owner.determine(route)

    assert result.authorization_decision is route.authorization_decision
    assert owner.maps_must_ask_to_ask_now is False
    assert owner.maps_may_initiate_to_no_need_to_ask is False
    assert owner.maps_must_abstain_to_question is False
    assert owner.maps_review_required_to_question is False
    assert owner.reruns_authorization is False
    assert owner.reruns_productive_authorization_consumption is False


def test_r6_preserves_existing_question_and_conversation_authorities() -> None:
    contract = _contract()
    owner = contract.GovernedSelfEpistemicNeedToAskDeterminationV1()

    inert_flags = (
        "assigns_question_worthiness",
        "assigns_relevance",
        "invokes_curiosity",
        "invokes_initiative",
        "invokes_conversation",
        "asks_human",
        "creates_questions",
        "invokes_human_question_transport",
        "invokes_human_answer_learning",
    )
    for flag in inert_flags:
        assert getattr(owner, flag) is False


def test_r7_is_deterministic_explicit_and_heuristic_free() -> None:
    contract = _contract()
    route = _b1_determination()
    owner = contract.GovernedSelfEpistemicNeedToAskDeterminationV1()

    first = owner.determine(route)
    second = owner.determine(route)

    assert first.status is second.status
    assert first.rationale_codes == second.rationale_codes
    assert "need_to_ask:self_epistemic_lineage" in first.rationale_codes
    assert "need_to_ask:no_compatible_canonical_route" in first.rationale_codes
    assert owner.infers_from_text is False
    assert owner.uses_semantic_matching is False
    assert owner.uses_llm is False
    assert owner.uses_retrieval is False
    assert owner.matches_by_capability_name is False


def test_r8_stops_before_question_worthiness_relevance_and_curiosity() -> None:
    contract = _contract()
    route = _b1_determination()
    owner = contract.GovernedSelfEpistemicNeedToAskDeterminationV1()

    result = owner.determine(route)

    assert result.read_only is True
    assert result.derivational is True
    inert_flags = (
        "selects_capability",
        "ranks_capabilities",
        "reselects_epistemic_path",
        "plans_acquisition",
        "acquires_evidence",
        "queries_selected_source",
        "authorizes_execution",
        "executes_actions",
        "persists_results",
        "creates_learning_candidate",
        "modifies_memory",
        "modifies_world_model",
        "creates_cognitive_authority",
        "creates_question_worthiness_authority",
        "creates_relevance_authority",
        "creates_curiosity_authority",
        "creates_initiative_authority",
        "creates_conversation_authority",
    )
    for flag in inert_flags:
        assert getattr(owner, flag) is False
