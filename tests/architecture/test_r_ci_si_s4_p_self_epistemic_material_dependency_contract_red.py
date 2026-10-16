from __future__ import annotations

from dataclasses import fields
from importlib import import_module

from core.cognitive_maturity.reasoning_epistemic_demand_binding import (
    ReasoningEpistemicDemandBinding,
)
from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
    EpistemicNeedIdentityReference,
)
from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)

MODULE = "core.cognitive_maturity.self_epistemic_material_dependency"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY
MATERIAL = "epistemic_sufficiency:material_epistemic_impediment_present"
REQUIREMENTS = "epistemic_sufficiency:discrimination_requirements_present"
REQUIREMENT_ID = "discrimination-requirement-1234567890abcdef"


def _contract():
    return import_module(MODULE)


def _assessment(
    *,
    status: EpistemicSufficiencyStatus = EpistemicSufficiencyStatus.INSUFFICIENT,
    source_reference: str = "scenario-123",
    world_snapshot_id: str = "world-1",
    requirement_ids: tuple[str, ...] = (REQUIREMENT_ID,),
    rationale_codes: tuple[str, ...] = (MATERIAL, REQUIREMENTS),
) -> GovernedEpistemicSufficiencyAssessment:
    return GovernedEpistemicSufficiencyAssessment(
        assessment_id="epistemic-sufficiency-1234567890abcdef",
        status=status,
        source_hypothesis_deepening_report_id="deepening-123",
        source_multi_hypothesis_discrimination_report_id="discrimination-123",
        source_hypothesis_update_semantics_report_id=None,
        source_reference=source_reference,
        world_snapshot_id=world_snapshot_id,
        hypothesis_ids=("h1", "h2"),
        unresolved_hypothesis_ids=("h1", "h2"),
        epistemic_gap_ids=("gap-1",),
        discrimination_requirement_ids=requirement_ids,
        rationale_codes=rationale_codes,
        source_fingerprint="a" * 64,
    )


def _binding(
    *,
    source_reference: str = "scenario-123",
    world_snapshot_id: str = "world-1",
) -> ReasoningEpistemicDemandBinding:
    return ReasoningEpistemicDemandBinding(
        requirement_id=REQUIREMENT_ID,
        epistemic_need_identity=IDENTITY,
        source_reference=source_reference,
        world_snapshot_id=world_snapshot_id,
        identity_source_reference="reasoning-explicit-identity",
        identity_lineage_kind="governed_explicit_epistemic_identity",
        provenance_authority="governed_explicit_reasoning_need_declaration",
        evidence_codes=("explicit_reasoning_epistemic_need",),
    )


def _self_identity(
    *, identity: str | None = IDENTITY,
) -> EpistemicNeedIdentityReference:
    return EpistemicNeedIdentityReference(
        identity=identity,
        source_reference="inner-continuity-report-123",
        lineage_kind="explicit_inner_continuity_gap",
    )


def _derive(contract, assessment=None, binding=None, self_identity=None):
    return contract.SelfEpistemicMaterialDependencyDerivation().derive(
        assessment or _assessment(),
        binding or _binding(),
        self_identity or _self_identity(),
    )


def test_r1_exact_self_epistemic_material_dependency_is_derived() -> None:
    contract = _contract()

    result = _derive(contract)

    assert result.assessment_id == "epistemic-sufficiency-1234567890abcdef"
    assert result.requirement_id == REQUIREMENT_ID
    assert result.epistemic_need_identity == IDENTITY
    assert result.self_gap_source_reference == "inner-continuity-report-123"
    assert result.read_only is True


def test_r2_non_material_sufficiency_status_abstains() -> None:
    contract = _contract()
    for status in (
        EpistemicSufficiencyStatus.SUFFICIENT,
        EpistemicSufficiencyStatus.INDETERMINATE,
    ):
        assert _derive(contract, assessment=_assessment(status=status)) is None


def test_r3_missing_material_rationale_fails_closed() -> None:
    contract = _contract()
    assessment = _assessment(rationale_codes=(REQUIREMENTS,))

    assert _derive(contract, assessment=assessment) is None


def test_r4_exact_requirement_membership_is_mandatory() -> None:
    contract = _contract()
    assessment = _assessment(
        requirement_ids=("discrimination-requirement-other",),
    )

    assert _derive(contract, assessment=assessment) is None


def test_r5_reasoning_episode_lineage_mismatch_fails_closed() -> None:
    contract = _contract()
    mismatches = (
        _binding(source_reference="scenario-other"),
        _binding(world_snapshot_id="world-other"),
    )
    for binding in mismatches:
        assert _derive(contract, binding=binding) is None


def test_r6_exact_s4_i_identity_match_is_mandatory() -> None:
    contract = _contract()
    mismatch = _self_identity(identity="roby.self.creator_intention")
    abstain = _self_identity(identity=None)

    assert _derive(contract, self_identity=mismatch) is None
    assert _derive(contract, self_identity=abstain) is None
    assert _derive(contract, self_identity=_self_identity()) is not None


def test_r7_independent_provenance_is_preserved_without_mutation() -> None:
    contract = _contract()
    assessment = _assessment()
    binding = _binding()
    self_identity = _self_identity()
    before = (assessment, binding, self_identity)

    result = _derive(contract, assessment, binding, self_identity)

    assert (assessment, binding, self_identity) == before
    assert result.assessment_id == assessment.assessment_id
    assert result.requirement_id == binding.requirement_id
    assert result.reasoning_source_reference == binding.source_reference
    assert result.world_snapshot_id == binding.world_snapshot_id
    assert result.self_gap_source_reference == self_identity.source_reference
    assert result.self_gap_lineage_kind == self_identity.lineage_kind


def test_r8_material_dependency_seam_is_inert_and_subordinate() -> None:
    contract = _contract()
    defaults = {
        field.name: field.default
        for field in fields(contract.SelfEpistemicMaterialDependencyDerivation)
    }

    assert defaults["read_only"] is True
    assert defaults["derivational"] is True
    for field_name in (
        "assigns_question_worthiness",
        "assigns_relevance",
        "invokes_curiosity",
        "selects_sources",
        "creates_questions",
        "creates_goals",
        "creates_acquisition_plans",
        "acquires_evidence",
        "invokes_initiative",
        "invokes_conversation",
        "persists_results",
        "modifies_memory",
        "creates_learning_candidate",
        "executes_actions",
        "grants_authority",
        "claims_subjective_experience",
    ):
        assert defaults[field_name] is False
