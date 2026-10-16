from __future__ import annotations

from dataclasses import fields
from importlib import import_module

import pytest

MODULE = "core.cognitive_maturity.governed_epistemic_path_selection"
C2_A_MODULE = "core.cognitive_maturity.explicit_selection_determinacy_basis"
C2_A_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_b2_c2_a_explicit_selection_determinacy_basis_contract_red"
)


def _contract():
    return import_module(MODULE)


def _c2_a_contract():
    return import_module(C2_A_MODULE)


def _fixtures():
    return import_module(C2_A_TEST_MODULE)


def _determinacy_basis():
    contract = _c2_a_contract()
    preference_set = _fixtures()._preference_set()
    declaration = _fixtures()._declaration(contract, preference_set)
    result = _fixtures()._admit(contract, preference_set, declaration)
    assert result is not None
    return result


def _select(contract, determinacy_basis):
    return contract.GovernedEpistemicPathSelectionMaterialization().select(
        determinacy_basis
    )


def test_r1_requires_actual_c2_a_determinacy_basis_anchor() -> None:
    contract = _contract()
    determinacy_basis = _determinacy_basis()

    result = _select(contract, determinacy_basis)

    assert result is not None
    assert result.determinacy_basis is determinacy_basis
    with pytest.raises(TypeError):
        _select(contract, determinacy_basis.determined_path_eligibility)
    with pytest.raises(TypeError):
        _select(contract, determinacy_basis.preference_set)
    with pytest.raises(TypeError):
        _select(contract, object())


def test_r2_selected_path_is_exact_determined_path_by_identity() -> None:
    contract = _contract()
    determinacy_basis = _determinacy_basis()

    result = _select(contract, determinacy_basis)

    assert result is not None
    assert (
        result.selected_path_eligibility
        is determinacy_basis.determined_path_eligibility
    )
    assert result.selected_capability_name == (
        determinacy_basis.determined_path_eligibility.suitability.capability_name
    )
    assert result.selected_declared_evidence_output == (
        determinacy_basis.determined_path_eligibility.suitability
        .declared_evidence_output
    )


def test_r3_has_no_second_determination_or_winner_declaration() -> None:
    contract = _contract()
    determinacy_basis = _determinacy_basis()

    result = _select(contract, determinacy_basis)

    assert result is not None
    module_names = set(vars(contract))
    forbidden_names = {
        "GovernedEpistemicPathSelectionDeclaration",
        "EpistemicPathWinnerDeclaration",
        "SelectionWinnerDeclaration",
    }
    assert module_names.isdisjoint(forbidden_names)
    result_fields = {
        item.name for item in fields(contract.GovernedEpistemicPathSelection)
    }
    forbidden_fields = {
        "winner",
        "winning_path",
        "selection_declaration",
        "preference_count",
        "score",
        "rank",
    }
    assert result_fields.isdisjoint(forbidden_fields)


def test_r4_does_not_reinterpret_or_requery_upstream_signals() -> None:
    contract = _contract()
    boundary = contract.GovernedEpistemicPathSelectionMaterialization()

    forbidden_flags = (
        "inspects_preferences",
        "interprets_preference_orientation",
        "interprets_comparative_effects",
        "inspects_evidence_content",
        "interprets_suitability",
        "queries_capability_registry",
        "queries_official_runtime",
        "reconstructs_eligibility",
        "ranks_paths",
        "scores_paths",
        "filters_paths",
        "aggregates_preferences",
        "breaks_ties",
        "resolves_conflicts",
        "infers_winner",
        "confirms_winner",
        "overrides_determinacy",
    )
    for flag in forbidden_flags:
        assert getattr(boundary, flag) is False


def test_r5_preserves_exact_upstream_and_determinacy_lineage() -> None:
    contract = _contract()
    determinacy_basis = _determinacy_basis()

    result = _select(contract, determinacy_basis)

    assert result is not None
    assert result.determinacy_basis is determinacy_basis
    assert result.selected_path_eligibility is (
        determinacy_basis.determined_path_eligibility
    )
    assert result.preference_set is determinacy_basis.preference_set
    assert result.requirement is determinacy_basis.requirement
    assert result.path_a_eligibility is determinacy_basis.path_a_eligibility
    assert result.path_b_eligibility is determinacy_basis.path_b_eligibility
    assert result.preferences is determinacy_basis.preferences
    assert result.epistemic_need_identity == determinacy_basis.epistemic_need_identity
    assert result.epistemic_need_source_reference == (
        determinacy_basis.epistemic_need_source_reference
    )
    assert result.epistemic_need_lineage_kind == (
        determinacy_basis.epistemic_need_lineage_kind
    )
    assert result.requirement_identity == determinacy_basis.requirement_identity
    assert result.determinacy_provenance_authority == (
        determinacy_basis.provenance_authority
    )
    assert result.determinacy_evidence_codes is determinacy_basis.evidence_codes


def test_r6_exposes_no_negative_selection_taxonomy_or_fallback() -> None:
    contract = _contract()
    result_fields = {
        item.name for item in fields(contract.GovernedEpistemicPathSelection)
    }
    forbidden = {
        "tied",
        "no_winner",
        "indeterminate",
        "conflicted",
        "consensus",
        "majority",
        "fallback_winner",
        "ranking",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r7_selection_is_not_authorization_acquisition_or_execution() -> None:
    contract = _contract()
    boundary = contract.GovernedEpistemicPathSelectionMaterialization()
    result = _select(contract, _determinacy_basis())

    assert result is not None
    result_fields = {
        item.name for item in fields(contract.GovernedEpistemicPathSelection)
    }
    forbidden_fields = {
        "authorized",
        "authorized_for_acquisition",
        "authorized_for_execution",
        "acquired",
        "executed",
        "acquisition_plan",
    }
    assert result_fields.isdisjoint(forbidden_fields)
    for flag in (
        "plans_acquisition",
        "authorizes_acquisition",
        "authorizes_execution",
        "acquires_evidence",
        "invokes_selected_capability",
        "queries_selected_source",
        "asks_human",
        "executes_actions",
    ):
        assert getattr(boundary, flag) is False


def test_r8_boundary_is_read_only_derivational_and_inert() -> None:
    contract = _contract()
    boundary = contract.GovernedEpistemicPathSelectionMaterialization()

    assert boundary.read_only is True
    assert boundary.derivational is True
    inert_flags = (
        "mutates_determinacy_basis",
        "mutates_preference_set",
        "mutates_requirement",
        "mutates_preferences",
        "creates_evidence",
        "acquires_evidence",
        "inspects_evidence_content",
        "aggregates_preferences",
        "weights_preferences",
        "scores_preferences",
        "ranks_paths",
        "filters_paths",
        "resolves_conflicts",
        "creates_determinacy",
        "queries_capability_registry",
        "queries_official_runtime",
        "reconstructs_eligibility",
        "plans_acquisition",
        "authorizes_acquisition",
        "authorizes_execution",
        "creates_questions",
        "assigns_question_worthiness",
        "assigns_relevance",
        "invokes_curiosity",
        "creates_goals",
        "invokes_initiative",
        "invokes_conversation",
        "persists_results",
        "modifies_memory",
        "creates_learning_candidate",
        "creates_cognitive_authority",
        "executes_actions",
        "claims_subjective_experience",
        "claims_consciousness",
    )
    for flag in inert_flags:
        assert getattr(boundary, flag) is False
