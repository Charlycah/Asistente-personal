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

A3_MODULE = "core.cognitive_maturity.explicit_comparative_discrimination_effect"
MODULE = "core.cognitive_maturity.explicit_epistemic_path_preference"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY
A3_AUTHORIZED_PROVENANCE = (
    "governed_explicit_comparative_discrimination_effect_declaration"
)
AUTHORIZED_PROVENANCE = (
    "governed_explicit_epistemic_path_preference_declaration"
)


def _contract():
    return import_module(MODULE)


def _a3_contract():
    return import_module(A3_MODULE)


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


def _a3_declaration(contract, satisfaction, **overrides):
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
        "provenance_authority": A3_AUTHORIZED_PROVENANCE,
        "evidence_codes": ("explicit_comparative_discrimination_effect",),
    }
    values.update(overrides)
    return contract.ExplicitComparativeDiscriminationEffectDeclaration(**values)


def _a3_admit(contract, satisfaction, declaration):
    return contract.ExplicitComparativeDiscriminationEffectAdmission().admit(
        satisfaction,
        declaration,
    )




def _comparative_effect():
    contract = _a3_contract()
    satisfaction = _satisfaction()
    declaration = _a3_declaration(contract, satisfaction)
    result = _a3_admit(contract, satisfaction, declaration)
    assert result is not None
    return result


def _preference_declaration(contract, effect, **overrides):
    preferred = effect.path_a_eligibility
    relative = effect.path_b_eligibility
    values = {
        "requirement_identity": effect.requirement_identity,
        "evidence_id": effect.evidence_id,
        "preferred_capability_name": preferred.suitability.capability_name,
        "preferred_declared_evidence_output": (
            preferred.suitability.declared_evidence_output
        ),
        "relative_capability_name": relative.suitability.capability_name,
        "relative_declared_evidence_output": (
            relative.suitability.declared_evidence_output
        ),
        "provenance_authority": AUTHORIZED_PROVENANCE,
        "evidence_codes": ("explicit_epistemic_path_preference",),
    }
    values.update(overrides)
    return contract.ExplicitEpistemicPathPreferenceDeclaration(**values)


def _preference_admit(contract, effect, declaration):
    return contract.ExplicitEpistemicPathPreferenceAdmission().admit(
        effect,
        declaration,
    )


def test_r1_requires_actual_comparative_effect_anchor() -> None:
    contract = _contract()
    effect = _comparative_effect()
    declaration = _preference_declaration(contract, effect)

    result = _preference_admit(contract, effect, declaration)

    assert result is not None
    assert result.comparative_effect is effect
    with pytest.raises(TypeError):
        _preference_admit(contract, effect.satisfaction, declaration)
    with pytest.raises(TypeError):
        _preference_admit(contract, effect.requirement, declaration)
    with pytest.raises(TypeError):
        _preference_admit(contract, effect.evidence, declaration)


def test_r2_requires_exact_requirement_and_evidence_correspondence() -> None:
    contract = _contract()
    effect = _comparative_effect()
    wrong_requirement = _preference_declaration(
        contract,
        effect,
        requirement_identity="fixture.other.requirement",
    )
    wrong_evidence = _preference_declaration(
        contract,
        effect,
        evidence_id="fixture.other.evidence",
    )

    assert _preference_admit(contract, effect, wrong_requirement) is None
    assert _preference_admit(contract, effect, wrong_evidence) is None


def test_r3_requires_exact_orientation_over_inherited_paths() -> None:
    contract = _contract()
    effect = _comparative_effect()
    path_a = effect.path_a_eligibility
    path_b = effect.path_b_eligibility

    a_over_b = _preference_admit(
        contract,
        effect,
        _preference_declaration(contract, effect),
    )
    b_over_a = _preference_admit(
        contract,
        effect,
        _preference_declaration(
            contract,
            effect,
            preferred_capability_name=path_b.suitability.capability_name,
            preferred_declared_evidence_output=(
                path_b.suitability.declared_evidence_output
            ),
            relative_capability_name=path_a.suitability.capability_name,
            relative_declared_evidence_output=(
                path_a.suitability.declared_evidence_output
            ),
        ),
    )
    self_preference = _preference_declaration(
        contract,
        effect,
        relative_capability_name=path_a.suitability.capability_name,
        relative_declared_evidence_output=(
            path_a.suitability.declared_evidence_output
        ),
    )
    unknown = _preference_declaration(
        contract,
        effect,
        preferred_capability_name="fixture.unknown",
    )

    assert a_over_b is not None
    assert b_over_a is not None
    assert _path_identity(a_over_b.preferred_path_eligibility) == (
        _path_identity(path_a)
    )
    assert _path_identity(b_over_a.preferred_path_eligibility) == (
        _path_identity(path_b)
    )
    assert effect.path_a_eligibility is path_a
    assert effect.path_b_eligibility is path_b
    assert _preference_admit(contract, effect, self_preference) is None
    assert _preference_admit(contract, effect, unknown) is None


def test_r4_preference_is_explicit_and_effects_remain_opaque() -> None:
    contract = _contract()
    effect = _comparative_effect()
    result = _preference_admit(
        contract,
        effect,
        _preference_declaration(contract, effect),
    )

    assert result is not None
    assert result.path_a_effect == effect.path_a_effect
    assert result.path_b_effect == effect.path_b_effect
    assert result.path_a_effect != result.path_b_effect
    result_fields = {
        item.name for item in fields(contract.ExplicitEpistemicPathPreference)
    }
    forbidden = {
        "preference_score",
        "effect_score",
        "effect_classification",
        "winner",
        "rank",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r5_requires_dedicated_provenance_and_explicit_lineage() -> None:
    contract = _contract()
    effect = _comparative_effect()
    unauthorized = _preference_declaration(
        contract,
        effect,
        provenance_authority=effect.provenance_authority,
    )

    assert _preference_admit(contract, effect, unauthorized) is None
    with pytest.raises(ValueError):
        _preference_declaration(contract, effect, evidence_codes=())
    with pytest.raises(ValueError):
        _preference_declaration(
            contract,
            effect,
            evidence_codes=(" ",),
        )
    with pytest.raises(ValueError):
        _preference_declaration(
            contract,
            effect,
            inferred_from_metadata=True,
        )


def test_r6_preserves_upstream_anchors_and_orientation_exactly() -> None:
    contract = _contract()
    effect = _comparative_effect()
    result = _preference_admit(
        contract,
        effect,
        _preference_declaration(contract, effect),
    )

    assert result is not None
    assert result.comparative_effect is effect
    assert result.satisfaction is effect.satisfaction
    assert result.materialization is effect.materialization
    assert result.requirement is effect.requirement
    assert result.evidence is effect.evidence
    assert result.epistemic_need_identity == effect.epistemic_need_identity
    assert result.epistemic_need_source_reference == (
        effect.epistemic_need_source_reference
    )
    assert result.epistemic_need_lineage_kind == (
        effect.epistemic_need_lineage_kind
    )
    assert result.requirement_identity == effect.requirement_identity
    assert result.evidence_id == effect.evidence_id
    assert result.path_a_eligibility is effect.path_a_eligibility
    assert result.path_b_eligibility is effect.path_b_eligibility
    assert result.preferred_path_eligibility is effect.path_a_eligibility
    assert result.relative_path_eligibility is effect.path_b_eligibility
    assert result.path_a_effect == effect.path_a_effect
    assert result.path_b_effect == effect.path_b_effect


def test_r7_rejection_is_neutral_and_preference_is_not_selection() -> None:
    contract = _contract()
    effect = _comparative_effect()
    mismatch = _preference_declaration(
        contract,
        effect,
        evidence_id="fixture.other.evidence",
    )

    assert _preference_admit(contract, effect, mismatch) is None
    result_fields = {
        item.name for item in fields(contract.ExplicitEpistemicPathPreference)
    }
    forbidden = {
        "paths_equal",
        "indistinguishable",
        "opposite_preference",
        "certified_true",
        "global_rank",
        "rank",
        "score",
        "selected_path",
        "authorized",
    }
    assert result_fields.isdisjoint(forbidden)


def test_r8_boundary_is_read_only_derivational_and_inert() -> None:
    contract = _contract()
    boundary = contract.ExplicitEpistemicPathPreferenceAdmission()

    assert boundary.read_only is True
    assert boundary.derivational is True
    inert_flags = (
        "mutates_comparative_effect",
        "mutates_satisfaction",
        "mutates_materialization",
        "mutates_requirement",
        "mutates_evidence",
        "creates_evidence",
        "acquires_evidence",
        "inspects_evidence_content",
        "evaluates_evidence_quality",
        "queries_evidence_registry",
        "queries_capability_registry",
        "queries_official_runtime",
        "uses_fuzzy_matching",
        "uses_semantic_matching",
        "uses_embeddings",
        "uses_llm",
        "uses_retrieval",
        "interprets_effect_semantics",
        "creates_preference_taxonomy",
        "aggregates_preferences",
        "reconciles_preferences",
        "scores_sources",
        "ranks_sources",
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
