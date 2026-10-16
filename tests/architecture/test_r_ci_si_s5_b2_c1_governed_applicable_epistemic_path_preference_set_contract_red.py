from __future__ import annotations

from dataclasses import fields, replace
from importlib import import_module

import pytest

from core.cognitive_maturity.explicit_epistemic_path_preference import (
    ExplicitEpistemicPathPreference,
)

MODULE = (
    "core.cognitive_maturity."
    "governed_applicable_epistemic_path_preference_set"
)
B2_B1_MODULE = "core.cognitive_maturity.explicit_epistemic_path_preference"
B2_B1_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_b2_b1_explicit_epistemic_path_preference_contract_red"
)


def _contract():
    return import_module(MODULE)


def _b2_b1_contract():
    return import_module(B2_B1_MODULE)


def _fixtures():
    return import_module(B2_B1_TEST_MODULE)


def _preference(*, reverse: bool = False) -> ExplicitEpistemicPathPreference:
    fixtures = _fixtures()
    contract = _b2_b1_contract()
    effect = fixtures._comparative_effect()
    path_a = effect.path_a_eligibility
    path_b = effect.path_b_eligibility
    overrides = {}
    if reverse:
        overrides = {
            "preferred_capability_name": path_b.suitability.capability_name,
            "preferred_declared_evidence_output": (
                path_b.suitability.declared_evidence_output
            ),
            "relative_capability_name": path_a.suitability.capability_name,
            "relative_declared_evidence_output": (
                path_a.suitability.declared_evidence_output
            ),
        }
    declaration = fixtures._preference_declaration(
        contract,
        effect,
        **overrides,
    )
    preference = fixtures._preference_admit(contract, effect, declaration)
    assert preference is not None
    return preference


def _compose(contract, requirement, preferences):
    return contract.GovernedApplicableEpistemicPathPreferenceSetComposition().compose(
        requirement,
        preferences,
    )


def _path_identity(eligibility) -> tuple[str, str]:
    return (
        eligibility.suitability.capability_name,
        eligibility.suitability.declared_evidence_output,
    )


def test_r1_requires_actual_discrimination_requirement_anchor() -> None:
    contract = _contract()
    preference = _preference()
    requirement = preference.requirement

    result = _compose(contract, requirement, (preference,))

    assert result.requirement is requirement
    with pytest.raises(TypeError):
        _compose(contract, requirement.epistemic_need_identity, (preference,))
    with pytest.raises(TypeError):
        _compose(contract, requirement.path_a_eligibility, (preference,))
    with pytest.raises(TypeError):
        _compose(contract, object(), (preference,))


def test_r2_requires_exact_x_r_and_unordered_pair_applicability() -> None:
    contract = _contract()
    preference = _preference()
    requirement = preference.requirement
    reversed_anchor = replace(
        requirement,
        path_a_eligibility=requirement.path_b_eligibility,
        path_b_eligibility=requirement.path_a_eligibility,
    )
    same_x_wrong_requirement = replace(
        preference,
        requirement_identity="fixture.other.requirement",
    )
    same_requirement_wrong_x = replace(
        preference,
        epistemic_need_source_reference="fixture.other.source",
    )
    foreign_path = replace(
        preference,
        path_b_eligibility=preference.path_a_eligibility,
        relative_path_eligibility=preference.path_a_eligibility,
    )

    reversed_result = _compose(contract, reversed_anchor, (preference,))

    assert reversed_result.preferences == (preference,)
    assert _compose(contract, requirement, (same_x_wrong_requirement,)) is None
    assert _compose(contract, requirement, (same_requirement_wrong_x,)) is None
    assert _compose(contract, requirement, (foreign_path,)) is None


def test_r3_empty_composition_is_legitimate_and_neutral() -> None:
    contract = _contract()
    requirement = _preference().requirement

    result = _compose(contract, requirement, ())

    assert result is not None
    assert result.requirement is requirement
    assert result.preferences == ()
    result_fields = {
        item.name
        for item in fields(contract.GovernedApplicableEpistemicPathPreferenceSet)
    }
    forbidden = {
        "preference",
        "equivalent_paths",
        "indistinguishable_paths",
        "consensus",
        "rank",
        "ranking",
        "winner",
        "selected_path",
        "authorized",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r4_preserves_orientation_evidence_independence_and_lineage() -> None:
    contract = _contract()
    first = _preference()
    second = replace(
        first,
        evidence_id="fixture-independent-evidence-2",
        evidence_codes=("independent_preference_lineage",),
    )

    result = _compose(contract, first.requirement, (first, second))

    assert result is not None
    assert result.preferences == (first, second)
    assert result.preferences[0] is first
    assert result.preferences[1] is second
    assert first.evidence_id != second.evidence_id
    assert first.preferred_path_eligibility is first.path_a_eligibility
    assert second.preferred_path_eligibility is second.path_a_eligibility


def test_r5_multiplicity_is_not_voting_and_only_exact_duplicates_normalize() -> None:
    contract = _contract()
    first = _preference()
    independent = replace(
        first,
        evidence_id="fixture-independent-evidence-3",
        evidence_codes=("independent_preference_lineage",),
    )

    result = _compose(
        contract,
        first.requirement,
        (first, first, independent),
    )

    assert result is not None
    assert result.preferences == (first, independent)
    result_fields = {
        item.name
        for item in fields(contract.GovernedApplicableEpistemicPathPreferenceSet)
    }
    forbidden = {
        "vote_count",
        "votes",
        "weight",
        "confidence",
        "majority",
        "score",
        "rank",
        "ranking",
        "winner",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r6_contradictory_orientations_are_preserved_not_resolved() -> None:
    contract = _contract()
    a_over_b = _preference()
    path_a = a_over_b.path_a_eligibility
    path_b = a_over_b.path_b_eligibility
    b_over_a = replace(
        a_over_b,
        preferred_path_eligibility=path_b,
        relative_path_eligibility=path_a,
        evidence_id="fixture-opposite-evidence",
        evidence_codes=("opposite_preference_lineage",),
    )

    result = _compose(contract, a_over_b.requirement, (a_over_b, b_over_a))

    assert result is not None
    assert result.preferences == (a_over_b, b_over_a)
    assert _path_identity(result.preferences[0].preferred_path_eligibility) == (
        _path_identity(path_a)
    )
    assert _path_identity(result.preferences[1].preferred_path_eligibility) == (
        _path_identity(path_b)
    )
    result_fields = {
        item.name
        for item in fields(contract.GovernedApplicableEpistemicPathPreferenceSet)
    }
    forbidden = {
        "conflict_resolution",
        "tie",
        "consensus",
        "paths_equal",
        "winner",
        "selected_path",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r7_preserves_actual_upstream_without_reconstruction() -> None:
    contract = _contract()
    preference = _preference()
    requirement = preference.requirement

    result = _compose(contract, requirement, (preference,))

    assert result is not None
    assert result.requirement is requirement
    assert result.path_a_eligibility is requirement.path_a_eligibility
    assert result.path_b_eligibility is requirement.path_b_eligibility
    assert result.epistemic_need_identity == requirement.epistemic_need_identity
    assert result.epistemic_need_source_reference == (
        requirement.epistemic_need_source_reference
    )
    assert result.epistemic_need_lineage_kind == (
        requirement.epistemic_need_lineage_kind
    )
    assert result.requirement_identity == requirement.requirement_identity
    assert result.preferences == (preference,)
    assert result.preferences[0] is preference


def test_r8_boundary_is_read_only_derivational_and_inert() -> None:
    contract = _contract()
    boundary = contract.GovernedApplicableEpistemicPathPreferenceSetComposition()

    assert boundary.read_only is True
    assert boundary.derivational is True
    inert_flags = (
        "mutates_requirement",
        "mutates_preferences",
        "creates_preferences",
        "infers_preferences",
        "queries_capability_registry",
        "queries_official_runtime",
        "reconstructs_eligibility",
        "rematerializes_evidence",
        "reevaluates_satisfaction",
        "inspects_evidence_content",
        "interprets_effect_semantics",
        "aggregates_votes",
        "weights_preferences",
        "scores_preferences",
        "ranks_paths",
        "filters_paths",
        "chooses_winner",
        "resolves_conflicts",
        "creates_consensus_taxonomy",
        "selects_paths",
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
