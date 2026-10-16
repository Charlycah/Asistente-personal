from __future__ import annotations

from dataclasses import fields
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
from core.cognitive_maturity.explicit_discriminating_evidence_materialization import (
    ExplicitDiscriminatingEvidenceMaterialization,
    ExplicitDiscriminatingEvidenceMaterializationAdmission,
    ExplicitDiscriminatingEvidenceMaterializationDeclaration,
)
from core.cognitive_maturity.explicit_epistemic_suitability import (
    ExplicitEpistemicSuitability,
)
from core.cognitive_maturity.explicit_path_discrimination_requirement import (
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

MODULE = "core.cognitive_maturity.explicit_requirement_satisfaction"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY
AUTHORIZED_PROVENANCE = "governed_explicit_requirement_satisfaction_declaration"


def _contract():
    return import_module(MODULE)


class _CanonicalReadiness:
    def __init__(self, capability_id: str) -> None:
        self.capability_id = capability_id
        self.ready = True
        self.blockers: tuple[str, ...] = ()
        self.warnings: tuple[str, ...] = ()


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
        runtime_readiness=_CanonicalReadiness(name),
    )
    return GovernedSelectionEligibility(
        suitability=suitability,
        runtime_observation=runtime_observation,
        eligible_for_selection=True,
    )


def _materialization() -> ExplicitDiscriminatingEvidenceMaterialization:
    a = _eligibility("fixture.alpha", "fixture.alpha_output")
    b = _eligibility("fixture.beta", "fixture.beta_output")
    requirement_declaration = ExplicitPathDiscriminationRequirementDeclaration(
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
    requirement = ExplicitPathDiscriminationRequirementAdmission().admit(
        a,
        b,
        requirement_declaration,
    )
    assert requirement is not None
    source_id = "fixture-evidence-1"
    evidence = EvidenceReference(
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
    declaration = ExplicitDiscriminatingEvidenceMaterializationDeclaration(
        requirement_identity=requirement.requirement_identity,
        evidence_id=evidence.evidence_id,
        provenance_authority=(
            "governed_explicit_discriminating_evidence_materialization_declaration"
        ),
        evidence_codes=("explicit_r_e_materialization_binding",),
    )
    result = ExplicitDiscriminatingEvidenceMaterializationAdmission().admit(
        requirement,
        evidence,
        declaration,
    )
    assert result is not None
    return result


def _declaration(contract, materialization, **overrides):
    values = {
        "requirement_identity": materialization.requirement_identity,
        "evidence_id": materialization.evidence_id,
        "provenance_authority": AUTHORIZED_PROVENANCE,
        "evidence_codes": ("explicit_requirement_satisfaction",),
    }
    values.update(overrides)
    return contract.ExplicitRequirementSatisfactionDeclaration(**values)


def _admit(contract, materialization, declaration):
    return contract.ExplicitRequirementSatisfactionAdmission().admit(
        materialization,
        declaration,
    )


def test_r1_requires_exact_existing_materialization_anchor() -> None:
    contract = _contract()
    materialization = _materialization()
    declaration = _declaration(contract, materialization)

    result = _admit(contract, materialization, declaration)

    assert result is not None
    assert result.materialization == materialization
    with pytest.raises(TypeError):
        _admit(contract, materialization.requirement, declaration)
    with pytest.raises(TypeError):
        _admit(contract, materialization.evidence, declaration)


def test_r2_requires_exact_declaration_to_requirement_correspondence() -> None:
    contract = _contract()
    materialization = _materialization()
    declaration = _declaration(
        contract,
        materialization,
        requirement_identity="fixture.other.requirement",
    )

    assert _admit(contract, materialization, declaration) is None


def test_r3_requires_exact_declaration_to_evidence_correspondence() -> None:
    contract = _contract()
    materialization = _materialization()
    declaration = _declaration(
        contract,
        materialization,
        evidence_id="fixture.other.evidence",
    )

    assert _admit(contract, materialization, declaration) is None


def test_r4_preserves_upstream_anchors_and_lineage_exactly() -> None:
    contract = _contract()
    materialization = _materialization()
    result = _admit(
        contract,
        materialization,
        _declaration(contract, materialization),
    )

    assert result is not None
    assert result.materialization == materialization
    assert result.requirement == materialization.requirement
    assert result.evidence == materialization.evidence
    assert result.epistemic_need_identity == materialization.epistemic_need_identity
    assert result.epistemic_need_source_reference == (
        materialization.epistemic_need_source_reference
    )
    assert result.epistemic_need_lineage_kind == (
        materialization.epistemic_need_lineage_kind
    )
    assert result.requirement_identity == materialization.requirement_identity
    assert result.evidence_id == materialization.evidence_id
    assert result.evidence_source_type == materialization.evidence_source_type
    assert result.evidence_source_id == materialization.evidence_source_id
    assert result.evidence_fingerprint == materialization.evidence_fingerprint


def test_r5_requires_authorized_provenance_and_explicit_lineage() -> None:
    contract = _contract()
    materialization = _materialization()
    unauthorized = _declaration(
        contract,
        materialization,
        provenance_authority="unauthorized",
    )

    assert _admit(contract, materialization, unauthorized) is None
    with pytest.raises(ValueError):
        _declaration(contract, materialization, evidence_codes=())
    with pytest.raises(ValueError):
        _declaration(contract, materialization, inferred_from_metadata=True)


def test_r6_rejection_is_epistemically_neutral() -> None:
    contract = _contract()
    materialization = _materialization()
    mismatch = _declaration(
        contract,
        materialization,
        evidence_id="fixture.other.evidence",
    )

    assert _admit(contract, materialization, mismatch) is None
    result_fields = {
        item.name for item in fields(contract.ExplicitRequirementSatisfaction)
    }
    forbidden = {
        "does_not_satisfy_requirement",
        "partial_satisfaction",
        "irrelevant",
        "false",
        "requirement_unsatisfiable",
        "paths_equivalent",
        "paths_indistinguishable",
        "preferred_path",
        "selected_path",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r7_satisfaction_is_positive_non_comparative_and_non_selective() -> None:
    contract = _contract()
    materialization = _materialization()
    result = _admit(
        contract,
        materialization,
        _declaration(contract, materialization),
    )

    assert result is not None
    forbidden = {
        "partial_satisfaction",
        "satisfaction_score",
        "favors_path_a",
        "favors_path_b",
        "comparative_effect",
        "preferred_path",
        "winner",
        "rank",
        "score",
        "selected_path",
        "authorized",
        "certified_true",
    }
    assert {item.name for item in fields(result)}.isdisjoint(forbidden)


def test_r8_boundary_is_read_only_derivational_and_inert() -> None:
    contract = _contract()
    boundary = contract.ExplicitRequirementSatisfactionAdmission()

    assert boundary.read_only is True
    assert boundary.derivational is True
    inert_flags = (
        "mutates_materialization",
        "mutates_requirement",
        "mutates_evidence",
        "creates_evidence",
        "normalizes_evidence",
        "queries_evidence_registry",
        "queries_capability_registry",
        "queries_official_runtime",
        "resolves_sources",
        "acquires_evidence",
        "uses_fuzzy_matching",
        "uses_semantic_matching",
        "uses_llm",
        "uses_retrieval",
        "evaluates_evidence_quality",
        "evaluates_freshness",
        "inspects_evidence_content",
        "computes_partial_satisfaction",
        "scores_satisfaction",
        "computes_comparative_effect",
        "scores_sources",
        "compares_sources",
        "ranks_sources",
        "prefers_sources",
        "selects_sources",
        "selects_capabilities",
        "plans_acquisition",
        "authorizes_acquisition",
        "certifies_truth",
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
        "grants_authority",
        "claims_subjective_experience",
        "claims_consciousness",
    )
    for flag in inert_flags:
        assert getattr(boundary, flag) is False
