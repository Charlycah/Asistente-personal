from __future__ import annotations

from dataclasses import fields, replace
from importlib import import_module

import pytest

C2_A_MODULE = (
    "core.cognitive_maturity.explicit_selection_determinacy_basis"
)
C1_MODULE = (
    "core.cognitive_maturity."
    "governed_applicable_epistemic_path_preference_set"
)
C1_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_b2_c1_governed_applicable_epistemic_path_preference_set_"
    "contract_red"
)
AUTHORIZED_PROVENANCE = (
    "governed_explicit_epistemic_selection_determinacy_declaration"
)


def _contract():
    return import_module(C2_A_MODULE)


def _c1_contract():
    return import_module(C1_MODULE)


def _fixtures():
    return import_module(C1_TEST_MODULE)


def _preference_set(*, empty: bool = False):
    c1 = _c1_contract()
    preference = _fixtures()._preference()
    preferences = () if empty else (preference,)
    result = c1.GovernedApplicableEpistemicPathPreferenceSetComposition().compose(
        preference.requirement,
        preferences,
    )
    assert result is not None
    return result


def _declaration(contract, preference_set, **overrides):
    determined = preference_set.path_a_eligibility
    values = {
        "preference_set": preference_set,
        "requirement_identity": preference_set.requirement_identity,
        "epistemic_need_identity": preference_set.epistemic_need_identity,
        "epistemic_need_source_reference": (
            preference_set.epistemic_need_source_reference
        ),
        "epistemic_need_lineage_kind": preference_set.epistemic_need_lineage_kind,
        "determined_capability_name": determined.suitability.capability_name,
        "determined_declared_evidence_output": (
            determined.suitability.declared_evidence_output
        ),
        "provenance_authority": AUTHORIZED_PROVENANCE,
        "evidence_codes": ("explicit_selection_determinacy_basis",),
    }
    values.update(overrides)
    return contract.ExplicitSelectionDeterminacyBasisDeclaration(**values)


def _admit(contract, preference_set, declaration):
    return contract.ExplicitSelectionDeterminacyBasisAdmission().admit(
        preference_set,
        declaration,
    )


def test_r1_requires_actual_c1_preference_set_anchor() -> None:
    contract = _contract()
    preference_set = _preference_set()
    declaration = _declaration(contract, preference_set)

    result = _admit(contract, preference_set, declaration)

    assert result is not None
    assert result.preference_set is preference_set
    with pytest.raises(TypeError):
        _admit(contract, preference_set.requirement, declaration)
    with pytest.raises(TypeError):
        _admit(contract, preference_set.preferences, declaration)
    with pytest.raises(TypeError):
        _admit(contract, object(), declaration)


def test_r2_requires_explicit_origin_without_structural_inference() -> None:
    contract = _contract()
    for preference_set in (_preference_set(empty=True), _preference_set()):
        declaration = _declaration(contract, preference_set)
        result = _admit(contract, preference_set, declaration)
        assert result is not None

    declaration_fields = {
        item.name
        for item in fields(contract.ExplicitSelectionDeterminacyBasisDeclaration)
    }
    forbidden = {
        "preference_count",
        "orientation_count",
        "unanimous",
        "conflict_state",
        "confidence",
        "score",
        "rank",
        "winner",
    }
    assert declaration_fields.isdisjoint(forbidden)


def test_r3_binds_declaration_to_exact_concrete_c1_composition() -> None:
    contract = _contract()
    first = _preference_set()
    second = replace(first)
    declaration = _declaration(contract, first)

    assert second == first
    assert second is not first
    assert _admit(contract, first, declaration) is not None
    assert _admit(contract, second, declaration) is None

    wrong_x = _declaration(
        contract,
        first,
        epistemic_need_source_reference="fixture.other.source",
    )
    wrong_requirement = _declaration(
        contract,
        first,
        requirement_identity="fixture.other.requirement",
    )
    assert _admit(contract, first, wrong_x) is None
    assert _admit(contract, first, wrong_requirement) is None


def test_r4_requires_exact_determined_path_and_preserves_actual_anchor() -> None:
    contract = _contract()
    preference_set = _preference_set()
    path_a = preference_set.path_a_eligibility
    path_b = preference_set.path_b_eligibility

    a_result = _admit(contract, preference_set, _declaration(contract, preference_set))
    b_declaration = _declaration(
        contract,
        preference_set,
        determined_capability_name=path_b.suitability.capability_name,
        determined_declared_evidence_output=(
            path_b.suitability.declared_evidence_output
        ),
    )
    b_result = _admit(contract, preference_set, b_declaration)

    assert a_result is not None
    assert b_result is not None
    assert a_result.determined_path_eligibility is path_a
    assert b_result.determined_path_eligibility is path_b

    third_path = _declaration(
        contract,
        preference_set,
        determined_capability_name="fixture.third.capability",
    )
    partial_mismatch = _declaration(
        contract,
        preference_set,
        determined_declared_evidence_output="fixture.third.output",
    )
    assert _admit(contract, preference_set, third_path) is None
    assert _admit(contract, preference_set, partial_mismatch) is None


def test_r5_requires_dedicated_provenance_and_explicit_lineage() -> None:
    contract = _contract()
    preference_set = _preference_set()

    valid = _declaration(contract, preference_set)
    assert _admit(contract, preference_set, valid) is not None

    wrong_provenance = _declaration(
        contract,
        preference_set,
        provenance_authority=(
            "governed_explicit_epistemic_path_preference_declaration"
        ),
    )
    assert _admit(contract, preference_set, wrong_provenance) is None
    assert contract.AUTHORIZED_PROVENANCE == AUTHORIZED_PROVENANCE

    with pytest.raises(ValueError):
        _declaration(contract, preference_set, evidence_codes=())
    with pytest.raises(ValueError):
        _declaration(contract, preference_set, evidence_codes=(" ",))


def test_r6_preserves_exact_upstream_without_requery_or_reconstruction() -> None:
    contract = _contract()
    preference_set = _preference_set()
    declaration = _declaration(contract, preference_set)

    result = _admit(contract, preference_set, declaration)

    assert result is not None
    assert result.preference_set is preference_set
    assert result.requirement is preference_set.requirement
    assert result.path_a_eligibility is preference_set.path_a_eligibility
    assert result.path_b_eligibility is preference_set.path_b_eligibility
    assert result.preferences is preference_set.preferences
    assert result.epistemic_need_identity == preference_set.epistemic_need_identity
    assert result.epistemic_need_source_reference == (
        preference_set.epistemic_need_source_reference
    )
    assert result.epistemic_need_lineage_kind == (
        preference_set.epistemic_need_lineage_kind
    )
    assert result.requirement_identity == preference_set.requirement_identity
    assert result.determined_path_eligibility is preference_set.path_a_eligibility


def test_r7_rejection_is_neutral_and_creates_no_determinacy_taxonomy() -> None:
    contract = _contract()
    preference_set = _preference_set()
    rejected = _declaration(
        contract,
        preference_set,
        provenance_authority="fixture.unauthorized",
    )

    assert _admit(contract, preference_set, rejected) is None

    result_fields = {
        item.name for item in fields(contract.ExplicitSelectionDeterminacyBasis)
    }
    forbidden = {
        "indeterminate",
        "equivalent",
        "tie",
        "consensus",
        "conflict_resolution",
        "unanimous",
        "majority",
        "dominant",
        "ranking",
        "selected_path",
        "authorized_path",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r8_boundary_is_read_only_derivational_and_inert() -> None:
    contract = _contract()
    boundary = contract.ExplicitSelectionDeterminacyBasisAdmission()

    assert boundary.read_only is True
    assert boundary.derivational is True
    inert_flags = (
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
        "infers_determinacy",
        "creates_determinacy_taxonomy",
        "queries_capability_registry",
        "queries_official_runtime",
        "reconstructs_eligibility",
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
