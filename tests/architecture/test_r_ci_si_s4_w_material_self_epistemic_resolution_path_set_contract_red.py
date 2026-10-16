from __future__ import annotations

from dataclasses import fields
from importlib import import_module

from core.cognitive_maturity.epistemic_resolution_binding import (
    EpistemicResolutionBinding,
)
from core.cognitive_maturity.self_epistemic_material_dependency import (
    SelfEpistemicMaterialDependency,
)
from core.cognitive_maturity.self_epistemic_need_identity import (
    EXPLICIT_INNER_CONTINUITY_IDENTITY,
)

MODULE = "core.cognitive_maturity.material_self_epistemic_resolution_path_set"
IDENTITY = EXPLICIT_INNER_CONTINUITY_IDENTITY


def _contract():
    return import_module(MODULE)


def _material_dependency(
    *,
    identity: str = IDENTITY,
    self_gap_source_reference: str = "inner-continuity-report-123",
    self_gap_lineage_kind: str = "explicit_inner_continuity_gap",
) -> SelfEpistemicMaterialDependency:
    return SelfEpistemicMaterialDependency(
        assessment_id="epistemic-sufficiency-1234567890abcdef",
        requirement_id="discrimination-requirement-1234567890abcdef",
        epistemic_need_identity=identity,
        reasoning_source_reference="scenario-123",
        world_snapshot_id="world-1",
        self_gap_source_reference=self_gap_source_reference,
        self_gap_lineage_kind=self_gap_lineage_kind,
    )


def _binding(
    *,
    capability_name: str = "fixture.explicit_inner_continuity_evidence",
    declared_evidence_output: str = "fixture.inner_continuity_output",
    identity: str = IDENTITY,
    source_reference: str = "inner-continuity-report-123",
    lineage_kind: str = "explicit_inner_continuity_gap",
) -> EpistemicResolutionBinding:
    return EpistemicResolutionBinding(
        capability_name=capability_name,
        declared_evidence_output=declared_evidence_output,
        epistemic_need_identity=identity,
        epistemic_need_source_reference=source_reference,
        epistemic_need_lineage_kind=lineage_kind,
        provenance_authority=(
            "governed_explicit_epistemic_resolution_declaration"
        ),
        evidence_codes=("explicit_epistemic_resolution_binding",),
    )


def _compose(contract, dependency=None, bindings=None):
    dependency = dependency or _material_dependency()
    bindings = (_binding(),) if bindings is None else bindings
    return contract.MaterialSelfEpistemicResolutionPathSetComposition().compose(
        dependency,
        bindings,
    )


def test_r1_exact_material_need_resolution_path_is_composed() -> None:
    contract = _contract()
    dependency = _material_dependency()
    binding = _binding()

    result = _compose(contract, dependency, (binding,))

    assert result.assessment_id == dependency.assessment_id
    assert result.requirement_id == dependency.requirement_id
    assert result.epistemic_need_identity == dependency.epistemic_need_identity
    assert result.resolution_bindings == (binding,)
    assert result.read_only is True
    assert result.derivational is True


def test_r2_identity_mismatch_is_excluded() -> None:
    contract = _contract()
    mismatch = _binding(identity="roby.self.creator_intention")

    result = _compose(contract, bindings=(mismatch,))

    assert result.resolution_bindings == ()


def test_r3_source_reference_mismatch_is_excluded() -> None:
    contract = _contract()
    mismatch = _binding(source_reference="inner-continuity-report-other")

    result = _compose(contract, bindings=(mismatch,))

    assert result.resolution_bindings == ()


def test_r4_lineage_kind_mismatch_is_excluded() -> None:
    contract = _contract()
    mismatch = _binding(lineage_kind="different_self_gap_lineage")

    result = _compose(contract, bindings=(mismatch,))

    assert result.resolution_bindings == ()


def test_r5_zero_one_many_are_legitimate_without_selection() -> None:
    contract = _contract()
    first = _binding(capability_name="fixture.alpha")
    second = _binding(
        capability_name="fixture.beta",
        declared_evidence_output="fixture.beta_output",
    )

    zero = _compose(contract, bindings=())
    one = _compose(contract, bindings=(first,))
    many = _compose(contract, bindings=(first, second))

    assert zero.resolution_bindings == ()
    assert one.resolution_bindings == (first,)
    assert set(many.resolution_bindings) == {first, second}
    for result in (zero, one, many):
        assert not hasattr(result, "selected_path")
        assert not hasattr(result, "preferred_path")
        assert not hasattr(result, "best_path")


def test_r6_representation_is_deterministic_and_exactly_deduplicated() -> None:
    contract = _contract()
    alpha = _binding(capability_name="fixture.alpha")
    beta = _binding(
        capability_name="fixture.beta",
        declared_evidence_output="fixture.beta_output",
    )

    forward = _compose(contract, bindings=(beta, alpha, alpha))
    reverse = _compose(contract, bindings=(alpha, beta, alpha))

    assert forward.resolution_bindings == reverse.resolution_bindings
    assert forward.resolution_bindings == (alpha, beta)


def test_r7_material_anchor_and_binding_lineages_are_preserved() -> None:
    contract = _contract()
    dependency = _material_dependency()
    binding = _binding()
    before = (dependency, binding)

    result = _compose(contract, dependency, (binding,))

    assert (dependency, binding) == before
    assert result.assessment_id == dependency.assessment_id
    assert result.requirement_id == dependency.requirement_id
    assert result.reasoning_source_reference == dependency.reasoning_source_reference
    assert result.world_snapshot_id == dependency.world_snapshot_id
    assert result.self_gap_source_reference == dependency.self_gap_source_reference
    assert result.self_gap_lineage_kind == dependency.self_gap_lineage_kind
    assert result.resolution_bindings == (binding,)


def test_r8_resolution_path_set_seam_is_inert_and_subordinate() -> None:
    contract = _contract()
    defaults = {
        field.name: field.default
        for field in fields(
            contract.MaterialSelfEpistemicResolutionPathSetComposition
        )
    }

    assert defaults["read_only"] is True
    assert defaults["derivational"] is True
    for field_name in (
        "discovers_resolution_paths",
        "validates_capabilities_again",
        "consults_capability_registry",
        "checks_availability",
        "filters_by_enabled",
        "ranks_sources",
        "ranks_capabilities",
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
