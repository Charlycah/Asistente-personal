from __future__ import annotations

from dataclasses import fields
from importlib import import_module

from core.capability_registry import CapabilityDescriptor, CapabilityRegistryManager
from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
    EpistemicNeedIdentityReference,
)

MODULE = "core.cognitive_maturity.epistemic_resolution_binding"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY
CAPABILITY_NAME = "fixture.explicit_inner_continuity_evidence"
EVIDENCE_OUTPUT = "fixture.explicit_inner_continuity_evidence_output"
PROVENANCE = "governed_explicit_epistemic_resolution_declaration"


def _contract():
    return import_module(MODULE)


def _registry(
    *,
    capability_name: str = CAPABILITY_NAME,
    evidence_outputs: tuple[str, ...] = (EVIDENCE_OUTPUT,),
    enabled: bool = True,
) -> CapabilityRegistryManager:
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name=capability_name,
            description="Contract-only governed evidence capability fixture.",
            enabled=enabled,
            evidence_outputs=evidence_outputs,
        )
    )
    return registry


def _identity(
    *, identity: str | None = IDENTITY,
) -> EpistemicNeedIdentityReference:
    return EpistemicNeedIdentityReference(
        identity=identity,
        source_reference="inner-continuity-report-123",
        lineage_kind="explicit_inner_continuity_gap",
    )


def _declaration(
    contract,
    *,
    capability_name: str = CAPABILITY_NAME,
    declared_evidence_output: str = EVIDENCE_OUTPUT,
    identity: str | None = IDENTITY,
    provenance_authority: str = PROVENANCE,
):
    return contract.ExplicitEpistemicResolutionDeclaration(
        capability_name=capability_name,
        declared_evidence_output=declared_evidence_output,
        epistemic_need=_identity(identity=identity),
        provenance_authority=provenance_authority,
        evidence_codes=("explicit_epistemic_resolution_binding",),
    )


def _admit(contract, *, registry=None, declaration=None):
    registry = registry or _registry()
    declaration = declaration or _declaration(contract)
    return contract.EpistemicResolutionBindingAdmission().admit(
        registry,
        declaration,
    )


def test_r1_exact_explicit_resolution_binding_is_admitted() -> None:
    contract = _contract()

    result = _admit(contract)

    assert result.capability_name == CAPABILITY_NAME
    assert result.declared_evidence_output == EVIDENCE_OUTPUT
    assert result.epistemic_need_identity == IDENTITY
    assert result.epistemic_need_source_reference == "inner-continuity-report-123"
    assert result.epistemic_need_lineage_kind == "explicit_inner_continuity_gap"
    assert result.provenance_authority == PROVENANCE
    assert result.read_only is True


def test_r2_unregistered_capability_fails_closed() -> None:
    contract = _contract()
    declaration = _declaration(
        contract,
        capability_name="fixture.unregistered_capability",
    )

    assert _admit(contract, declaration=declaration) is None


def test_r3_exact_declared_evidence_output_membership_is_mandatory() -> None:
    contract = _contract()
    registry = _registry(evidence_outputs=("different.output",))
    declaration = _declaration(contract)

    assert _admit(contract, registry=registry, declaration=declaration) is None


def test_r4_explicit_supported_epistemic_identity_is_mandatory() -> None:
    contract = _contract()
    absent = _declaration(contract, identity=None)
    unsupported = _declaration(contract, identity="roby.self.creator_intention")

    assert _admit(contract, declaration=absent) is None
    assert _admit(contract, declaration=unsupported) is None


def test_r5_text_or_metadata_cannot_synthesize_resolution_binding() -> None:
    contract = _contract()
    registry = CapabilityRegistryManager()
    registry.register(
        CapabilityDescriptor(
            name=CAPABILITY_NAME,
            description="roby.self.explicit_inner_continuity",
            evidence_outputs=("different.output",),
            metadata={
                "epistemic_need_identity": IDENTITY,
                "declared_evidence_output": EVIDENCE_OUTPUT,
            },
        )
    )
    declaration = _declaration(contract)

    assert _admit(contract, registry=registry, declaration=declaration) is None
    declaration_defaults = {
        field.name: field.default
        for field in fields(contract.ExplicitEpistemicResolutionDeclaration)
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


def test_r6_authorized_provenance_and_independent_lineage_are_preserved() -> None:
    contract = _contract()
    registry = _registry(enabled=False)
    identity = _identity()
    declaration = contract.ExplicitEpistemicResolutionDeclaration(
        capability_name=CAPABILITY_NAME,
        declared_evidence_output=EVIDENCE_OUTPUT,
        epistemic_need=identity,
        provenance_authority=PROVENANCE,
        evidence_codes=("explicit_epistemic_resolution_binding",),
    )
    before = (registry.get(CAPABILITY_NAME), identity, declaration)

    result = _admit(contract, registry=registry, declaration=declaration)

    assert (registry.get(CAPABILITY_NAME), identity, declaration) == before
    assert result.capability_name == CAPABILITY_NAME
    assert result.declared_evidence_output == EVIDENCE_OUTPUT
    assert result.epistemic_need_source_reference == identity.source_reference
    assert result.epistemic_need_lineage_kind == identity.lineage_kind
    assert result.provenance_authority == PROVENANCE
    unauthorized = _declaration(
        contract,
        provenance_authority="arbitrary_resolution_authority",
    )
    assert _admit(contract, registry=registry, declaration=unauthorized) is None


def test_r7_resolution_binding_seam_is_inert_and_subordinate() -> None:
    contract = _contract()
    defaults = {
        field.name: field.default
        for field in fields(contract.EpistemicResolutionBindingAdmission)
    }

    assert defaults["read_only"] is True
    assert defaults["derivational"] is True
    for field_name in (
        "selects_sources",
        "selects_capabilities",
        "plans_acquisition",
        "authorizes_acquisition",
        "acquires_evidence",
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
    ):
        assert defaults[field_name] is False
