from __future__ import annotations

from dataclasses import dataclass, fields
from importlib import import_module

import pytest

from core.cognitive_maturity.canonical_runtime_readiness_projection import (
    CanonicalRuntimeReadinessProjectionObservation,
    CanonicalRuntimeReadinessProjectionStatus,
)
from core.cognitive_maturity.current_registry_resolution_path_availability import (
    CurrentRegistryResolutionPathAvailabilityObservation,
    CurrentRegistryResolutionPathAvailabilityStatus,
)
from core.cognitive_maturity.epistemic_resolution_binding import (
    EpistemicResolutionBinding,
)
from core.cognitive_maturity.explicit_epistemic_suitability import (
    ExplicitEpistemicSuitability,
)
from core.cognitive_maturity.governed_selection_eligibility import (
    GovernedSelectionEligibility,
)
from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
)

MODULE = "core.cognitive_maturity.explicit_path_discrimination_requirement"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY
AUTHORIZED_PROVENANCE = (
    "governed_explicit_path_discrimination_requirement_declaration"
)


def _contract():
    return import_module(MODULE)


@dataclass(frozen=True)
class _CanonicalReadiness:
    capability_id: str
    ready: bool = True
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def _eligibility(
    name: str,
    output: str,
    *,
    identity: str = IDENTITY,
    source_reference: str = "inner-continuity-report-123",
    lineage_kind: str = "explicit_inner_continuity_gap",
    eligible: bool = True,
) -> GovernedSelectionEligibility:
    binding = EpistemicResolutionBinding(
        capability_name=name,
        declared_evidence_output=output,
        epistemic_need_identity=identity,
        epistemic_need_source_reference=source_reference,
        epistemic_need_lineage_kind=lineage_kind,
        provenance_authority=(
            "governed_explicit_epistemic_resolution_declaration"
        ),
        evidence_codes=("explicit_epistemic_resolution_binding",),
    )
    suitability = ExplicitEpistemicSuitability(
        capability_name=name,
        declared_evidence_output=output,
        epistemic_need_identity=identity,
        epistemic_need_source_reference=source_reference,
        epistemic_need_lineage_kind=lineage_kind,
        provenance_authority="governed_explicit_epistemic_suitability_declaration",
        evidence_codes=("explicit_epistemic_suitability",),
    )
    registry_observation = CurrentRegistryResolutionPathAvailabilityObservation(
        binding=binding,
        status=(
            CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE
        ),
    )
    runtime_observation = CanonicalRuntimeReadinessProjectionObservation(
        registry_observation=registry_observation,
        status=CanonicalRuntimeReadinessProjectionStatus.AVAILABLE,
        runtime_readiness=_CanonicalReadiness(capability_id=name),
    )
    return GovernedSelectionEligibility(
        suitability=suitability,
        runtime_observation=runtime_observation,
        eligible_for_selection=eligible,
    )


def _pair() -> tuple[GovernedSelectionEligibility, GovernedSelectionEligibility]:
    return (
        _eligibility("fixture.alpha", "fixture.alpha_output"),
        _eligibility("fixture.beta", "fixture.beta_output"),
    )


def _declaration(contract, *, a=None, b=None, **overrides):
    if a is None or b is None:
        a, b = _pair()
    values = {
        "epistemic_need_identity": a.suitability.epistemic_need_identity,
        "path_a_capability_name": a.suitability.capability_name,
        "path_a_declared_evidence_output": (
            a.suitability.declared_evidence_output
        ),
        "path_b_capability_name": b.suitability.capability_name,
        "path_b_declared_evidence_output": (
            b.suitability.declared_evidence_output
        ),
        "requirement_identity": "fixture.discrimination.requirement",
        "provenance_authority": AUTHORIZED_PROVENANCE,
        "evidence_codes": ("explicit_path_discrimination_requirement",),
    }
    values.update(overrides)
    return contract.ExplicitPathDiscriminationRequirementDeclaration(**values)


def _admit(contract, a, b, declaration):
    return contract.ExplicitPathDiscriminationRequirementAdmission().admit(
        a,
        b,
        declaration,
    )


def test_r1_requires_two_exact_positive_b1_b_eligibility_anchors() -> None:
    contract = _contract()
    a, b = _pair()
    declaration = _declaration(contract, a=a, b=b)

    result = _admit(contract, a, b, declaration)

    assert result is not None
    assert result.path_a_eligibility == a
    assert result.path_b_eligibility == b
    with pytest.raises(TypeError):
        _admit(contract, a.suitability, b, declaration)
    with pytest.raises(TypeError):
        _admit(contract, a, b.suitability, declaration)
    blocked = _eligibility("fixture.beta", "fixture.beta_output", eligible=False)
    assert _admit(contract, a, blocked, declaration) is None


def test_r2_requires_exact_same_x_lineage_and_declaration_identity() -> None:
    contract = _contract()
    a, b = _pair()
    mismatches = (
        _eligibility("fixture.beta", "fixture.beta_output", identity="roby.self.other"),
        _eligibility(
            "fixture.beta",
            "fixture.beta_output",
            source_reference="inner-continuity-report-other",
        ),
        _eligibility(
            "fixture.beta",
            "fixture.beta_output",
            lineage_kind="other_lineage",
        ),
    )

    for mismatch in mismatches:
        declaration = _declaration(contract, a=a, b=mismatch)
        assert _admit(contract, a, mismatch, declaration) is None

    wrong_x = _declaration(contract, a=a, b=b, epistemic_need_identity="other")
    assert _admit(contract, a, b, wrong_x) is None


def test_r3_requires_structurally_distinct_resolution_paths() -> None:
    contract = _contract()
    a, _ = _pair()
    declaration = _declaration(contract, a=a, b=a)

    assert _admit(contract, a, a, declaration) is None


def test_r4_requires_exact_pair_and_order_is_preference_neutral() -> None:
    contract = _contract()
    a, b = _pair()
    declaration_ab = _declaration(contract, a=a, b=b)
    declaration_ba = _declaration(contract, a=b, b=a)

    admitted_ab = _admit(contract, a, b, declaration_ab)
    admitted_ba = _admit(contract, b, a, declaration_ba)

    assert admitted_ab is not None
    assert admitted_ba is not None
    assert admitted_ab.requirement_identity == admitted_ba.requirement_identity
    for result in (admitted_ab, admitted_ba):
        assert not hasattr(result, "winner")
        assert not hasattr(result, "loser")
        assert not hasattr(result, "preferred_path")
        assert not hasattr(result, "rank")
        assert not hasattr(result, "score")
        assert not hasattr(result, "selected_path")

    wrong_pair = _declaration(
        contract,
        a=a,
        b=b,
        path_b_declared_evidence_output="fixture.other_output",
    )
    assert _admit(contract, a, b, wrong_pair) is None


def test_r5_requires_authorized_provenance_and_explicit_lineage() -> None:
    contract = _contract()
    a, b = _pair()

    unauthorized = _declaration(
        contract,
        a=a,
        b=b,
        provenance_authority="unauthorized",
    )
    assert _admit(contract, a, b, unauthorized) is None

    declaration_fields = {field.name for field in fields(
        contract.ExplicitPathDiscriminationRequirementDeclaration
    )}
    inference_flags = {
        "inferred_from_text",
        "inferred_from_metadata",
        "used_fuzzy_matching",
        "used_semantic_matching",
        "uses_llm",
        "uses_retrieval",
    }
    assert inference_flags <= declaration_fields
    with pytest.raises(ValueError):
        _declaration(contract, a=a, b=b, evidence_codes=())
    for flag in inference_flags:
        with pytest.raises(ValueError):
            _declaration(contract, a=a, b=b, **{flag: True})


def test_r6_rejection_is_epistemically_neutral() -> None:
    contract = _contract()
    a, b = _pair()
    declaration = _declaration(
        contract,
        a=a,
        b=b,
        provenance_authority="unauthorized",
    )

    result = _admit(contract, a, b, declaration)

    assert result is None
    admission = contract.ExplicitPathDiscriminationRequirementAdmission()
    forbidden_states = {
        "paths_equivalent",
        "paths_indistinguishable",
        "no_discrimination_needed",
        "either_path_acceptable",
        "unsuitable",
        "negative_preference",
        "permission_to_select",
    }
    assert all(not hasattr(admission, name) for name in forbidden_states)


def test_r7_admitted_requirement_is_non_preferential_and_non_selective() -> None:
    contract = _contract()
    a, b = _pair()
    result = _admit(contract, a, b, _declaration(contract, a=a, b=b))

    assert result is not None
    assert result.epistemic_need_identity == IDENTITY
    assert result.epistemic_need_source_reference == (
        a.suitability.epistemic_need_source_reference
    )
    assert result.epistemic_need_lineage_kind == (
        a.suitability.epistemic_need_lineage_kind
    )
    assert result.requirement_identity == "fixture.discrimination.requirement"
    assert result.provenance_authority == AUTHORIZED_PROVENANCE
    assert result.evidence_codes == ("explicit_path_discrimination_requirement",)
    forbidden = {
        "winner",
        "loser",
        "preferred_path",
        "selected_path",
        "rank",
        "score",
        "weight",
        "priority",
        "recommendation",
        "discriminating_evidence",
        "comparative_result",
    }
    assert all(not hasattr(result, name) for name in forbidden)


def test_r8_boundary_is_read_only_derivational_and_inert() -> None:
    contract = _contract()
    admission = contract.ExplicitPathDiscriminationRequirementAdmission()

    assert admission.read_only is True
    assert admission.derivational is True
    forbidden_true = {
        "mutates_eligibility",
        "mutates_suitability",
        "mutates_resolution_binding",
        "queries_capability_registry",
        "mutates_capability_registry",
        "queries_official_runtime",
        "mutates_official_runtime",
        "creates_runtime_capability_graph",
        "creates_runtime_readiness_evidence",
        "creates_eligibility",
        "reconstructs_eligibility",
        "infers_discrimination_requirement",
        "uses_fuzzy_matching",
        "uses_semantic_matching",
        "uses_llm",
        "uses_retrieval",
        "acquires_discriminating_evidence",
        "evaluates_discriminating_evidence",
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
    }
    assert all(getattr(admission, name) is False for name in forbidden_true)
