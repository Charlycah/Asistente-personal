from __future__ import annotations

from dataclasses import fields
from importlib import import_module

from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
    EpistemicNeedIdentityReference,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

MODULE = "core.cognitive_maturity.reasoning_epistemic_demand_binding"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY


def _contract():
    return import_module(MODULE)


def _requirement(
    *,
    requirement_id: str = "discrimination-requirement-1234567890abcdef",
    source_reference: str = "scenario-123",
    world_snapshot_id: str = "world-1",
    description: str = "ROBY explicit inner continuity",
) -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id=requirement_id,
        hypothesis_ids=("h1", "h2"),
        source_reference=source_reference,
        world_snapshot_id=world_snapshot_id,
        known_elements=("fact-shared",),
        missing_evidence_descriptions=(description,),
        evidence_codes=("comparison:indistinguishable",),
        source_report_id="multi-hypothesis-discrimination-source",
    )


def _declaration(
    contract,
    requirement: DiscriminatingEvidenceRequirement,
    *,
    identity: str | None = IDENTITY,
    requirement_id: str | None = None,
    source_reference: str | None = None,
    world_snapshot_id: str | None = None,
):
    identity_reference = EpistemicNeedIdentityReference(
        identity=identity,
        source_reference="explicit-authorized-epistemic-identity",
        lineage_kind="governed_explicit_epistemic_identity",
    )
    return contract.ExplicitReasoningEpistemicDemandDeclaration(
        requirement_id=requirement_id or requirement.requirement_id,
        source_reference=source_reference or requirement.source_reference,
        world_snapshot_id=world_snapshot_id or requirement.world_snapshot_id,
        epistemic_need=identity_reference,
        provenance_authority="governed_explicit_reasoning_need_declaration",
        evidence_codes=("explicit_reasoning_epistemic_need",),
    )


def test_r1_exact_explicit_reasoning_need_binding_is_admitted() -> None:
    contract = _contract()
    requirement = _requirement()
    declaration = _declaration(contract, requirement)

    result = contract.ReasoningEpistemicDemandBindingAdmission().admit(
        requirement,
        declaration,
    )

    assert result.requirement_id == requirement.requirement_id
    assert result.epistemic_need_identity == IDENTITY
    assert result.source_reference == requirement.source_reference
    assert result.world_snapshot_id == requirement.world_snapshot_id
    assert result.read_only is True


def test_r2_requirement_lineage_mismatch_fails_closed() -> None:
    contract = _contract()
    requirement = _requirement()
    admission = contract.ReasoningEpistemicDemandBindingAdmission()

    mismatches = (
        {"requirement_id": "discrimination-requirement-fedcba0987654321"},
        {"source_reference": "scenario-other"},
        {"world_snapshot_id": "world-other"},
    )
    for mismatch in mismatches:
        declaration = _declaration(contract, requirement, **mismatch)
        result = admission.admit(requirement, declaration)
        assert result is None


def test_r3_missing_explicit_identity_abstains_without_inference() -> None:
    contract = _contract()
    requirement = _requirement(description="ROBY explicit inner continuity")
    declaration = _declaration(contract, requirement, identity=None)

    result = contract.ReasoningEpistemicDemandBindingAdmission().admit(
        requirement,
        declaration,
    )

    assert result is None


def test_r4_unsupported_explicit_identity_is_rejected() -> None:
    contract = _contract()
    requirement = _requirement()
    declaration = _declaration(
        contract,
        requirement,
        identity="roby.self.creator_intention",
    )

    result = contract.ReasoningEpistemicDemandBindingAdmission().admit(
        requirement,
        declaration,
    )

    assert result is None


def test_r5_text_or_metadata_cannot_synthesize_binding() -> None:
    contract = _contract()
    requirement = _requirement(
        description="roby.self.explicit_inner_continuity",
    )
    declaration = _declaration(contract, requirement, identity=None)

    result = contract.ReasoningEpistemicDemandBindingAdmission().admit(
        requirement,
        declaration,
    )

    assert result is None
    assert declaration.inferred_from_text is False
    assert declaration.inferred_from_metadata is False
    assert declaration.used_fuzzy_matching is False
    assert declaration.used_semantic_matching is False


def test_r6_binding_preserves_requirement_and_independent_lineage() -> None:
    contract = _contract()
    requirement = _requirement()
    before = requirement
    declaration = _declaration(contract, requirement)

    result = contract.ReasoningEpistemicDemandBindingAdmission().admit(
        requirement,
        declaration,
    )

    assert requirement == before
    assert result.requirement_id == requirement.requirement_id
    assert result.source_reference == requirement.source_reference
    assert result.identity_source_reference != result.source_reference
    assert result.epistemic_need_identity == IDENTITY


def test_r7_binding_seam_is_inert_subordinate_and_non_subjective() -> None:
    contract = _contract()
    admission_defaults = {
        field.name: field.default
        for field in fields(contract.ReasoningEpistemicDemandBindingAdmission)
    }

    assert admission_defaults["read_only"] is True
    for field_name in (
        "assigns_materiality",
        "assigns_relevance",
        "creates_questions",
        "creates_goals",
        "creates_acquisition_plans",
        "acquires_evidence",
        "persists_results",
        "modifies_memory",
        "executes_actions",
        "grants_authority",
        "claims_subjective_experience",
    ):
        assert admission_defaults[field_name] is False
