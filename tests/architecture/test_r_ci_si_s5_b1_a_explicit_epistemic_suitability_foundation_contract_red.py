from __future__ import annotations

from dataclasses import fields
from importlib import import_module

from core.cognitive_maturity.epistemic_resolution_binding import (
    EpistemicResolutionBinding,
)

MODULE = "core.cognitive_maturity.explicit_epistemic_suitability"
IDENTITY = "roby.self.explicit_inner_continuity"
CAPABILITY_NAME = "fixture.explicit_inner_continuity_evidence"
EVIDENCE_OUTPUT = "fixture.explicit_inner_continuity_evidence_output"
PROVENANCE = "governed_explicit_epistemic_suitability_declaration"


def _contract():
    return import_module(MODULE)


def _binding(
    *,
    capability_name: str = CAPABILITY_NAME,
    declared_evidence_output: str = EVIDENCE_OUTPUT,
    identity: str = IDENTITY,
) -> EpistemicResolutionBinding:
    return EpistemicResolutionBinding(
        capability_name=capability_name,
        declared_evidence_output=declared_evidence_output,
        epistemic_need_identity=identity,
        epistemic_need_source_reference="inner-continuity-report-123",
        epistemic_need_lineage_kind="explicit_inner_continuity_gap",
        provenance_authority=(
            "governed_explicit_epistemic_resolution_declaration"
        ),
        evidence_codes=("explicit_epistemic_resolution_binding",),
    )


def _declaration(
    contract,
    *,
    capability_name: str = CAPABILITY_NAME,
    declared_evidence_output: str = EVIDENCE_OUTPUT,
    identity: str = IDENTITY,
    provenance_authority: str = PROVENANCE,
    evidence_codes: tuple[str, ...] = ("explicit_suitability_evidence",),
    **flags,
):
    return contract.ExplicitEpistemicSuitabilityDeclaration(
        epistemic_need_identity=identity,
        capability_name=capability_name,
        declared_evidence_output=declared_evidence_output,
        provenance_authority=provenance_authority,
        evidence_codes=evidence_codes,
        **flags,
    )


def _admit(contract, *, binding=None, declaration=None):
    binding = binding or _binding()
    declaration = declaration or _declaration(contract)
    return contract.ExplicitEpistemicSuitabilityAdmission().admit(
        binding,
        declaration,
    )


def test_r1_exact_existing_s4_t_binding_is_mandatory_and_preserved() -> None:
    contract = _contract()
    binding = _binding()

    result = _admit(contract, binding=binding)

    assert result.capability_name == binding.capability_name
    assert result.declared_evidence_output == binding.declared_evidence_output
    assert result.epistemic_need_identity == binding.epistemic_need_identity
    assert result.epistemic_need_source_reference == (
        binding.epistemic_need_source_reference
    )
    assert result.epistemic_need_lineage_kind == binding.epistemic_need_lineage_kind
    assert result.read_only is True


def test_r2_exact_x_c_d_correspondence_is_mandatory() -> None:
    contract = _contract()

    for declaration in (
        _declaration(contract, identity="roby.self.other_need"),
        _declaration(contract, capability_name="fixture.other_capability"),
        _declaration(contract, declared_evidence_output="fixture.other_output"),
    ):
        assert _admit(contract, declaration=declaration) is None


def test_r3_authorized_suitability_provenance_is_mandatory() -> None:
    contract = _contract()
    declaration = _declaration(
        contract,
        provenance_authority="arbitrary_suitability_authority",
    )

    assert _admit(contract, declaration=declaration) is None


def test_r4_explicit_independent_lineage_is_mandatory_and_preserved() -> None:
    contract = _contract()
    declaration = _declaration(
        contract,
        evidence_codes=("explicit_suitability_a", "explicit_suitability_b"),
    )

    result = _admit(contract, declaration=declaration)

    assert result.provenance_authority == PROVENANCE
    assert result.evidence_codes == declaration.evidence_codes
    declaration_defaults = {
        field.name: field.default
        for field in fields(contract.ExplicitEpistemicSuitabilityDeclaration)
    }
    for field_name in (
        "inferred_from_text",
        "inferred_from_metadata",
        "used_fuzzy_matching",
        "used_semantic_matching",
        "uses_llm",
        "uses_retrieval",
    ):
        assert declaration_defaults[field_name] is False


def test_r5_admission_does_not_require_registry_or_runtime_operability() -> None:
    contract = _contract()
    binding = _binding()
    declaration = _declaration(contract)
    before = (binding, declaration)

    result = contract.ExplicitEpistemicSuitabilityAdmission().admit(
        binding,
        declaration,
    )

    assert result is not None
    assert (binding, declaration) == before
    assert result.capability_name == CAPABILITY_NAME


def test_r6_rejection_does_not_create_negative_suitability() -> None:
    contract = _contract()
    rejected = _declaration(
        contract,
        declared_evidence_output="fixture.not_the_bound_output",
    )

    assert _admit(contract, declaration=rejected) is None
    assert not hasattr(contract, "UnsuitableEpistemicResolutionPath")


def test_r7_multiple_suitable_paths_remain_independent_and_unranked() -> None:
    contract = _contract()
    binding_a = _binding()
    binding_b = _binding(
        capability_name="fixture.second_evidence_capability",
        declared_evidence_output="fixture.second_evidence_output",
    )
    declaration_a = _declaration(contract)
    declaration_b = _declaration(
        contract,
        capability_name=binding_b.capability_name,
        declared_evidence_output=binding_b.declared_evidence_output,
    )
    admission = contract.ExplicitEpistemicSuitabilityAdmission()

    result_a = admission.admit(binding_a, declaration_a)
    result_b = admission.admit(binding_b, declaration_b)

    assert result_a.capability_name == binding_a.capability_name
    assert result_b.capability_name == binding_b.capability_name
    assert result_a != result_b


def test_r8_admission_is_read_only_derivational_and_non_selective() -> None:
    contract = _contract()
    defaults = {
        field.name: field.default
        for field in fields(contract.ExplicitEpistemicSuitabilityAdmission)
    }

    assert defaults["read_only"] is True
    assert defaults["derivational"] is True
    for field_name in (
        "mutates_resolution_binding",
        "queries_capability_registry",
        "mutates_capability_registry",
        "queries_official_runtime",
        "mutates_official_runtime",
        "creates_runtime_capability_graph",
        "creates_runtime_readiness_evidence",
        "creates_resolution_bindings",
        "infers_suitability",
        "scores_sources",
        "compares_sources",
        "ranks_sources",
        "prefers_sources",
        "filters_sources",
        "selects_sources",
        "selects_capabilities",
        "plans_acquisition",
        "authorizes_acquisition",
        "acquires_evidence",
        "certifies_truth",
        "grants_authority",
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
        "executes_actions",
        "claims_subjective_experience",
        "claims_consciousness",
    ):
        assert defaults[field_name] is False
