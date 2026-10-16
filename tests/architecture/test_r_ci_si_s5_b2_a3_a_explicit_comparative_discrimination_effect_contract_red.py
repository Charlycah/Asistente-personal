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
from core.cognitive_maturity.explicit_requirement_satisfaction import (
    ExplicitRequirementSatisfaction,
    ExplicitRequirementSatisfactionAdmission,
    ExplicitRequirementSatisfactionDeclaration,
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

MODULE = "core.cognitive_maturity.explicit_comparative_discrimination_effect"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY
AUTHORIZED_PROVENANCE = (
    "governed_explicit_comparative_discrimination_effect_declaration"
)


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


def _satisfaction() -> ExplicitRequirementSatisfaction:
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
    materialization_declaration = (
        ExplicitDiscriminatingEvidenceMaterializationDeclaration(
            requirement_identity=requirement.requirement_identity,
            evidence_id=evidence.evidence_id,
            provenance_authority=(
                "governed_explicit_discriminating_evidence_"
                "materialization_declaration"
            ),
            evidence_codes=("explicit_r_e_materialization_binding",),
        )
    )
    materialization = ExplicitDiscriminatingEvidenceMaterializationAdmission().admit(
        requirement,
        evidence,
        materialization_declaration,
    )
    assert materialization is not None
    satisfaction_declaration = ExplicitRequirementSatisfactionDeclaration(
        requirement_identity=materialization.requirement_identity,
        evidence_id=materialization.evidence_id,
        provenance_authority=(
            "governed_explicit_requirement_satisfaction_declaration"
        ),
        evidence_codes=("explicit_requirement_satisfaction",),
    )
    satisfaction = ExplicitRequirementSatisfactionAdmission().admit(
        materialization,
        satisfaction_declaration,
    )
    assert satisfaction is not None
    return satisfaction


def _path_identity(eligibility: GovernedSelectionEligibility) -> tuple[str, str]:
    return (
        eligibility.suitability.capability_name,
        eligibility.suitability.declared_evidence_output,
    )


def _declaration(contract, satisfaction, **overrides):
    path_a = satisfaction.requirement.path_a_eligibility
    path_b = satisfaction.requirement.path_b_eligibility
    values = {
        "requirement_identity": satisfaction.requirement_identity,
        "evidence_id": satisfaction.evidence_id,
        "path_a_capability_name": path_a.suitability.capability_name,
        "path_a_declared_evidence_output": (
            path_a.suitability.declared_evidence_output
        ),
        "path_b_capability_name": path_b.suitability.capability_name,
        "path_b_declared_evidence_output": (
            path_b.suitability.declared_evidence_output
        ),
        "path_a_effect": "fixture.explicit.effect.alpha",
        "path_b_effect": "fixture.explicit.effect.beta",
        "provenance_authority": AUTHORIZED_PROVENANCE,
        "evidence_codes": ("explicit_comparative_discrimination_effect",),
    }
    values.update(overrides)
    return contract.ExplicitComparativeDiscriminationEffectDeclaration(**values)


def _admit(contract, satisfaction, declaration):
    return contract.ExplicitComparativeDiscriminationEffectAdmission().admit(
        satisfaction,
        declaration,
    )


def test_r1_requires_exact_existing_satisfaction_anchor() -> None:
    contract = _contract()
    satisfaction = _satisfaction()
    declaration = _declaration(contract, satisfaction)

    result = _admit(contract, satisfaction, declaration)

    assert result is not None
    assert result.satisfaction == satisfaction
    with pytest.raises(TypeError):
        _admit(contract, satisfaction.materialization, declaration)
    with pytest.raises(TypeError):
        _admit(contract, satisfaction.requirement, declaration)
    with pytest.raises(TypeError):
        _admit(contract, satisfaction.evidence, declaration)


def test_r2_requires_exact_requirement_and_evidence_correspondence() -> None:
    contract = _contract()
    satisfaction = _satisfaction()
    wrong_requirement = _declaration(
        contract,
        satisfaction,
        requirement_identity="fixture.other.requirement",
    )
    wrong_evidence = _declaration(
        contract,
        satisfaction,
        evidence_id="fixture.other.evidence",
    )

    assert _admit(contract, satisfaction, wrong_requirement) is None
    assert _admit(contract, satisfaction, wrong_evidence) is None


def test_r3_requires_exact_inherited_path_correspondence() -> None:
    contract = _contract()
    satisfaction = _satisfaction()
    wrong_a = _declaration(
        contract,
        satisfaction,
        path_a_capability_name="fixture.other.alpha",
    )
    wrong_b = _declaration(
        contract,
        satisfaction,
        path_b_declared_evidence_output="fixture.other.beta_output",
    )

    assert _admit(contract, satisfaction, wrong_a) is None
    assert _admit(contract, satisfaction, wrong_b) is None


def test_r4_preserves_explicit_opaque_effect_values_without_taxonomy() -> None:
    contract = _contract()
    satisfaction = _satisfaction()
    result = _admit(
        contract,
        satisfaction,
        _declaration(contract, satisfaction),
    )

    assert result is not None
    assert result.path_a_effect == "fixture.explicit.effect.alpha"
    assert result.path_b_effect == "fixture.explicit.effect.beta"
    with pytest.raises(ValueError):
        _declaration(contract, satisfaction, path_a_effect=" ")
    with pytest.raises(ValueError):
        _declaration(contract, satisfaction, path_b_effect="")
    assert not hasattr(contract, "ComparativeDiscriminationEffectType")


def test_r5_requires_dedicated_provenance_and_explicit_lineage() -> None:
    contract = _contract()
    satisfaction = _satisfaction()
    unauthorized = _declaration(
        contract,
        satisfaction,
        provenance_authority=satisfaction.provenance_authority,
    )

    assert _admit(contract, satisfaction, unauthorized) is None
    with pytest.raises(ValueError):
        _declaration(contract, satisfaction, evidence_codes=())
    with pytest.raises(ValueError):
        _declaration(contract, satisfaction, inferred_from_metadata=True)


def test_r6_preserves_upstream_anchors_and_lineage_exactly() -> None:
    contract = _contract()
    satisfaction = _satisfaction()
    result = _admit(
        contract,
        satisfaction,
        _declaration(contract, satisfaction),
    )

    assert result is not None
    assert result.satisfaction == satisfaction
    assert result.materialization == satisfaction.materialization
    assert result.requirement == satisfaction.requirement
    assert result.evidence == satisfaction.evidence
    assert result.epistemic_need_identity == satisfaction.epistemic_need_identity
    assert result.epistemic_need_source_reference == (
        satisfaction.epistemic_need_source_reference
    )
    assert result.epistemic_need_lineage_kind == (
        satisfaction.epistemic_need_lineage_kind
    )
    assert result.requirement_identity == satisfaction.requirement_identity
    assert result.evidence_id == satisfaction.evidence_id
    assert result.path_a_eligibility == satisfaction.requirement.path_a_eligibility
    assert result.path_b_eligibility == satisfaction.requirement.path_b_eligibility
    assert _path_identity(result.path_a_eligibility) == _path_identity(
        satisfaction.requirement.path_a_eligibility
    )
    assert _path_identity(result.path_b_eligibility) == _path_identity(
        satisfaction.requirement.path_b_eligibility
    )


def test_r7_rejection_is_neutral_and_effect_is_not_preference_or_truth() -> None:
    contract = _contract()
    satisfaction = _satisfaction()
    mismatch = _declaration(
        contract,
        satisfaction,
        evidence_id="fixture.other.evidence",
    )

    assert _admit(contract, satisfaction, mismatch) is None
    result_fields = {
        item.name
        for item in fields(contract.ExplicitComparativeDiscriminationEffect)
    }
    forbidden = {
        "neutral_effect",
        "indistinguishable",
        "paths_equal",
        "does_not_discriminate",
        "certified_true",
        "preferred_path",
        "winner",
        "rank",
        "score",
        "selected_path",
        "authorized",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r8_boundary_is_read_only_derivational_and_inert() -> None:
    contract = _contract()
    boundary = contract.ExplicitComparativeDiscriminationEffectAdmission()

    assert boundary.read_only is True
    assert boundary.derivational is True
    inert_flags = (
        "mutates_satisfaction",
        "mutates_materialization",
        "mutates_requirement",
        "mutates_evidence",
        "creates_evidence",
        "normalizes_evidence",
        "acquires_evidence",
        "persists_evidence",
        "inspects_evidence_content",
        "evaluates_evidence_quality",
        "evaluates_freshness",
        "queries_evidence_registry",
        "queries_capability_registry",
        "queries_official_runtime",
        "uses_fuzzy_matching",
        "uses_semantic_matching",
        "uses_embeddings",
        "uses_llm",
        "uses_retrieval",
        "creates_effect_taxonomy",
        "aggregates_effects",
        "reconciles_effects",
        "scores_sources",
        "compares_sources",
        "ranks_sources",
        "prefers_sources",
        "filters_sources",
        "selects_sources",
        "selects_capabilities",
        "plans_acquisition",
        "authorizes_acquisition",
        "authorizes_execution",
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
