from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from hashlib import sha256
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
from core.cognitive_maturity.explicit_path_discrimination_requirement import (
    ExplicitPathDiscriminationRequirement,
    ExplicitPathDiscriminationRequirementAdmission,
    ExplicitPathDiscriminationRequirementDeclaration,
)
from core.cognitive_maturity.governed_selection_eligibility import (
    GovernedSelectionEligibility,
)
from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
)
from core.governed_reasoning.evidence import (
    EvidenceKind,
    EvidenceReference,
    EvidenceSensitivity,
    EvidenceSourceType,
    EvidenceStatus,
)

MODULE = "core.cognitive_maturity.explicit_discriminating_evidence_materialization"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY
AUTHORIZED_PROVENANCE = (
    "governed_explicit_discriminating_evidence_materialization_declaration"
)


def _contract():
    return import_module(MODULE)


@dataclass(frozen=True)
class _CanonicalReadiness:
    capability_id: str
    ready: bool = True
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def _eligibility(name: str, output: str) -> GovernedSelectionEligibility:
    binding = EpistemicResolutionBinding(
        capability_name=name,
        declared_evidence_output=output,
        epistemic_need_identity=IDENTITY,
        epistemic_need_source_reference="inner-continuity-report-123",
        epistemic_need_lineage_kind="explicit_inner_continuity_gap",
        provenance_authority=(
            "governed_explicit_epistemic_resolution_declaration"
        ),
        evidence_codes=("explicit_epistemic_resolution_binding",),
    )
    suitability = ExplicitEpistemicSuitability(
        capability_name=name,
        declared_evidence_output=output,
        epistemic_need_identity=IDENTITY,
        epistemic_need_source_reference="inner-continuity-report-123",
        epistemic_need_lineage_kind="explicit_inner_continuity_gap",
        provenance_authority="governed_explicit_epistemic_suitability_declaration",
        evidence_codes=("explicit_epistemic_suitability",),
    )
    registry_observation = CurrentRegistryResolutionPathAvailabilityObservation(
        binding=binding,
        status=CurrentRegistryResolutionPathAvailabilityStatus.REGISTRY_AVAILABLE,
    )
    runtime_observation = CanonicalRuntimeReadinessProjectionObservation(
        registry_observation=registry_observation,
        status=CanonicalRuntimeReadinessProjectionStatus.AVAILABLE,
        runtime_readiness=_CanonicalReadiness(capability_id=name),
    )
    return GovernedSelectionEligibility(
        suitability=suitability,
        runtime_observation=runtime_observation,
        eligible_for_selection=True,
    )


def _requirement() -> ExplicitPathDiscriminationRequirement:
    a = _eligibility("fixture.alpha", "fixture.alpha_output")
    b = _eligibility("fixture.beta", "fixture.beta_output")
    declaration = ExplicitPathDiscriminationRequirementDeclaration(
        epistemic_need_identity=IDENTITY,
        path_a_capability_name=a.suitability.capability_name,
        path_a_declared_evidence_output=a.suitability.declared_evidence_output,
        path_b_capability_name=b.suitability.capability_name,
        path_b_declared_evidence_output=b.suitability.declared_evidence_output,
        requirement_identity="fixture.discrimination.requirement",
        provenance_authority=(
            "governed_explicit_path_discrimination_requirement_declaration"
        ),
        evidence_codes=("explicit_path_discrimination_requirement",),
    )
    result = ExplicitPathDiscriminationRequirementAdmission().admit(
        a,
        b,
        declaration,
    )
    assert result is not None
    return result


def _evidence(source_id: str = "fixture-evidence-1") -> EvidenceReference:
    return EvidenceReference(
        source_type=EvidenceSourceType.KNOWLEDGE,
        source_id=source_id,
        kind=EvidenceKind.KNOWLEDGE_ITEM,
        owner="fixture-owner",
        status=EvidenceStatus.ACTIVE,
        sensitivity=EvidenceSensitivity.PERSONAL,
        observed_at=datetime(2026, 9, 27, tzinfo=timezone.utc),
        fingerprint=sha256(f"fingerprint:{source_id}".encode()).hexdigest(),
        summary="Fixture governed evidence reference.",
    )


def _declaration(contract, requirement, evidence, **overrides):
    values = {
        "requirement_identity": requirement.requirement_identity,
        "evidence_id": evidence.evidence_id,
        "provenance_authority": AUTHORIZED_PROVENANCE,
        "evidence_codes": ("explicit_r_e_materialization_binding",),
    }
    values.update(overrides)
    return contract.ExplicitDiscriminatingEvidenceMaterializationDeclaration(
        **values
    )


def _admit(contract, requirement, evidence, declaration):
    return contract.ExplicitDiscriminatingEvidenceMaterializationAdmission().admit(
        requirement,
        evidence,
        declaration,
    )


def test_r1_requires_exact_existing_requirement_and_evidence_artifacts() -> None:
    contract = _contract()
    requirement = _requirement()
    evidence = _evidence()
    declaration = _declaration(contract, requirement, evidence)

    result = _admit(contract, requirement, evidence, declaration)

    assert result is not None
    assert result.requirement == requirement
    assert result.evidence == evidence
    with pytest.raises(TypeError):
        _admit(contract, requirement.requirement_identity, evidence, declaration)
    with pytest.raises(TypeError):
        _admit(contract, requirement, evidence.evidence_id, declaration)


def test_r2_requires_exact_declaration_to_requirement_correspondence() -> None:
    contract = _contract()
    requirement = _requirement()
    evidence = _evidence()
    declaration = _declaration(
        contract,
        requirement,
        evidence,
        requirement_identity="fixture.other.requirement",
    )

    assert _admit(contract, requirement, evidence, declaration) is None


def test_r3_requires_exact_declaration_to_evidence_correspondence() -> None:
    contract = _contract()
    requirement = _requirement()
    evidence = _evidence()
    other = _evidence("fixture-evidence-other")
    declaration = _declaration(contract, requirement, other)

    assert _admit(contract, requirement, evidence, declaration) is None


def test_r4_preserves_canonical_evidence_identity_and_provenance() -> None:
    contract = _contract()
    requirement = _requirement()
    evidence = _evidence()
    declaration = _declaration(contract, requirement, evidence)

    result = _admit(contract, requirement, evidence, declaration)

    assert result is not None
    assert result.evidence_id == evidence.evidence_id
    assert result.evidence_source_type == evidence.source_type
    assert result.evidence_source_id == evidence.source_id
    assert result.evidence_fingerprint == evidence.fingerprint
    assert result.evidence == evidence


def test_r5_requires_authorized_provenance_and_explicit_lineage() -> None:
    contract = _contract()
    requirement = _requirement()
    evidence = _evidence()
    unauthorized = _declaration(
        contract,
        requirement,
        evidence,
        provenance_authority="unauthorized",
    )

    assert _admit(contract, requirement, evidence, unauthorized) is None
    with pytest.raises(ValueError):
        _declaration(contract, requirement, evidence, evidence_codes=())
    with pytest.raises(ValueError):
        _declaration(contract, requirement, evidence, inferred_from_metadata=True)


def test_r6_rejection_is_epistemically_neutral() -> None:
    contract = _contract()
    requirement = _requirement()
    evidence = _evidence()
    mismatch = _declaration(
        contract,
        requirement,
        evidence,
        evidence_id=_evidence("fixture-other").evidence_id,
    )

    assert _admit(contract, requirement, evidence, mismatch) is None
    result_fields = {
        item.name
        for item in fields(
            contract.ExplicitDiscriminatingEvidenceMaterialization
        )
    }
    forbidden = {
        "does_not_satisfy_requirement",
        "irrelevant",
        "requirement_unsatisfiable",
        "paths_equivalent",
        "paths_indistinguishable",
        "preferred_path",
        "selected_path",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r7_binding_is_non_satisfying_and_non_comparative() -> None:
    contract = _contract()
    requirement = _requirement()
    evidence = _evidence()
    result = _admit(
        contract,
        requirement,
        evidence,
        _declaration(contract, requirement, evidence),
    )

    assert result is not None
    forbidden = {
        "satisfies_requirement",
        "partial_satisfaction",
        "satisfaction_score",
        "favors_path",
        "preferred_path",
        "winner",
        "rank",
        "score",
        "selected_path",
        "authorized",
    }
    assert {item.name for item in fields(result)}.isdisjoint(forbidden)


def test_r8_boundary_is_read_only_derivational_and_inert() -> None:
    contract = _contract()
    boundary = contract.ExplicitDiscriminatingEvidenceMaterializationAdmission()

    assert boundary.read_only is True
    assert boundary.derivational is True
    inert_flags = (
        "mutates_requirement",
        "mutates_evidence",
        "queries_capability_registry",
        "queries_official_runtime",
        "queries_evidence_registry",
        "creates_evidence",
        "creates_evidence_bundles",
        "uses_fuzzy_matching",
        "uses_semantic_matching",
        "uses_llm",
        "uses_retrieval",
        "acquires_evidence",
        "evaluates_requirement_satisfaction",
        "scores_sources",
        "compares_sources",
        "ranks_sources",
        "prefers_sources",
        "selects_sources",
        "selects_capabilities",
        "plans_acquisition",
        "authorizes_acquisition",
        "certifies_truth",
        "grants_authority",
        "creates_questions",
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
    )
    for flag in inert_flags:
        assert getattr(boundary, flag) is False
