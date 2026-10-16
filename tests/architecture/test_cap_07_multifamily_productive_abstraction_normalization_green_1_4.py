from __future__ import annotations

from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticGroundingStatus,
    ContextualSemanticRelation,
    ContextualSemanticRole,
    ContextualSemanticRoleMention,
    ContextualSemanticSlot,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedContextualSemanticGroundingCandidate,
)
from core.governed_reasoning.productive_abstraction_admission import (
    GovernedProductiveAbstractionAdmission,
    ProductiveAbstractionAdmissionStatus,
)


def _grounding(
    *,
    family_id: str,
    source_fingerprint: str,
    role_mentions: tuple[ContextualSemanticRoleMention, ...],
    slots: tuple[ContextualSemanticSlot, ...],
) -> GovernedContextualSemanticGroundingCandidate:
    return GovernedContextualSemanticGroundingCandidate(
        status=ContextualSemanticGroundingStatus.GROUNDED,
        source_reference=f"source:{source_fingerprint}",
        scope_reference="scope:multifamily",
        source_candidate_fingerprint=f"candidate:{source_fingerprint}",
        family_id=family_id,
        role_mentions=role_mentions,
        semantic_slots=slots,
        rationale_codes=("grounding:test_fixture",),
        source_fingerprint=source_fingerprint,
    )


def _exclusive_dependency_grounding(
    source_fingerprint: str,
) -> GovernedContextualSemanticGroundingCandidate:
    return _grounding(
        family_id=GovernedBoundedSemanticRoleRelationGrounder.FAMILY_ID,
        source_fingerprint=source_fingerprint,
        role_mentions=(
            ContextualSemanticRoleMention(
                role_id=ContextualSemanticRole.DEPENDENT,
                source_text="sistema",
                start_offset=0,
                end_offset=7,
            ),
            ContextualSemanticRoleMention(
                role_id=ContextualSemanticRole.RESOURCE,
                source_text="recurso",
                start_offset=8,
                end_offset=15,
            ),
            ContextualSemanticRoleMention(
                role_id=ContextualSemanticRole.CAPABILITY,
                source_text="capacidad",
                start_offset=16,
                end_offset=25,
            ),
        ),
        slots=(
            ContextualSemanticSlot(
                role_id=ContextualSemanticRole.DEPENDENT,
                relation=ContextualSemanticRelation.DEPENDENCY,
                value="exclusive",
                source_text="dependencia exclusiva",
                start_offset=0,
                end_offset=20,
            ),
            ContextualSemanticSlot(
                role_id=ContextualSemanticRole.RESOURCE,
                relation=ContextualSemanticRelation.AVAILABILITY,
                value="unavailable",
                source_text="recurso no disponible",
                start_offset=21,
                end_offset=41,
            ),
            ContextualSemanticSlot(
                role_id=ContextualSemanticRole.DEPENDENT,
                relation=ContextualSemanticRelation.ALTERNATIVE,
                value="absent",
                source_text="sin alternativa",
                start_offset=42,
                end_offset=57,
            ),
            ContextualSemanticSlot(
                role_id=ContextualSemanticRole.DEPENDENT,
                relation=ContextualSemanticRelation.CAPABILITY,
                value="unavailable",
                source_text="capacidad no disponible",
                start_offset=58,
                end_offset=80,
            ),
        ),
    )


def _velar_grounding(
    source_fingerprint: str,
) -> GovernedContextualSemanticGroundingCandidate:
    return _grounding(
        family_id=GovernedBoundedSemanticRoleRelationGrounder.VELAR_FAMILY_ID,
        source_fingerprint=source_fingerprint,
        role_mentions=(
            ContextualSemanticRoleMention(
                role_id=ContextualSemanticRole.PREREQUISITE,
                source_text="prerequisito",
                start_offset=0,
                end_offset=12,
            ),
            ContextualSemanticRoleMention(
                role_id=ContextualSemanticRole.DEPENDENT,
                source_text="dependiente",
                start_offset=13,
                end_offset=23,
            ),
        ),
        slots=(
            ContextualSemanticSlot(
                role_id=ContextualSemanticRole.PREREQUISITE,
                relation=ContextualSemanticRelation.REQUIRED_FOR,
                value="dependent",
                source_text="prerequisito requerido",
                start_offset=0,
                end_offset=20,
            ),
            ContextualSemanticSlot(
                role_id=ContextualSemanticRole.PREREQUISITE,
                relation=ContextualSemanticRelation.AVAILABILITY,
                value="unavailable",
                source_text="prerequisito no disponible",
                start_offset=21,
                end_offset=47,
            ),
            ContextualSemanticSlot(
                role_id=ContextualSemanticRole.DEPENDENT,
                relation=ContextualSemanticRelation.CAPABILITY,
                value="unavailable",
                source_text="dependiente bloqueado",
                start_offset=48,
                end_offset=68,
            ),
        ),
    )


def test_green_1_r1_mapping_remains_unchanged() -> None:
    evidence = GovernedProductiveAbstractionAdmission.normalize_grounding(
        _exclusive_dependency_grounding("fp:r1"),
        scope_reference="scope:multifamily",
    )
    assert evidence is not None
    assert evidence.example.relation == "required_for"
    assert evidence.example.outcome == "blocked_when_unavailable"
    assert evidence.normalization_family_id == (
        "productive_abstraction:r1_required_for_blocked"
    )


def test_green_2_r2_maps_certified_exclusive_dependency_shape() -> None:
    evidence = GovernedProductiveAbstractionAdmission.normalize_grounding(
        _velar_grounding("fp:r2"),
        scope_reference="scope:multifamily",
    )
    assert evidence is not None
    assert evidence.example.relation == "required_for"
    assert evidence.example.outcome == (
        "blocked_when_prerequisite_unavailable"
    )
    assert evidence.normalization_family_id == (
        "productive_abstraction:r2_prerequisite_unavailable_block"
    )


def test_green_2_r2_incomplete_shape_fails_closed() -> None:
    grounding = _velar_grounding("fp:incomplete")
    object.__setattr__(
        grounding,
        "semantic_slots",
        grounding.semantic_slots[:-1],
    )
    evidence = GovernedProductiveAbstractionAdmission.normalize_grounding(
        grounding,
        scope_reference="scope:multifamily",
    )
    assert evidence is None


def test_green_2_unsupported_family_stays_not_applicable() -> None:
    grounding = _exclusive_dependency_grounding("fp:unsupported")
    object.__setattr__(grounding, "family_id", "unsupported_family_v1")
    evidence = GovernedProductiveAbstractionAdmission.normalize_grounding(
        grounding,
        scope_reference="scope:multifamily",
    )
    assert evidence is None


def test_green_3_r1_and_r2_accumulate_in_separate_family_buckets() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    first_r1 = admission.observe(
        _exclusive_dependency_grounding("fp:r1:1"),
        session_id="session:mix",
        turn_id="turn:r1:1",
        scope_reference="scope:multifamily",
    )
    first_r2 = admission.observe(
        _velar_grounding("fp:r2:1"),
        session_id="session:mix",
        turn_id="turn:r2:1",
        scope_reference="scope:multifamily",
    )
    assert first_r1.status is ProductiveAbstractionAdmissionStatus.INSUFFICIENT_EVIDENCE
    assert first_r2.status is ProductiveAbstractionAdmissionStatus.INSUFFICIENT_EVIDENCE


def test_green_4_two_r2_observations_induce_r2_with_existing_inducer() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    first = admission.observe(
        _velar_grounding("fp:r2:1"),
        session_id="session:r2",
        turn_id="turn:r2:1",
        scope_reference="scope:multifamily",
    )
    second = admission.observe(
        _velar_grounding("fp:r2:2"),
        session_id="session:r2",
        turn_id="turn:r2:2",
        scope_reference="scope:multifamily",
    )
    assert first.episode is None
    assert second.status is ProductiveAbstractionAdmissionStatus.ABSTRACTION_AVAILABLE
    assert second.episode is not None
    assert second.episode.abstraction_candidate.invariant_relation == "required_for"
    assert second.episode.abstraction_candidate.invariant_outcome == (
        "blocked_when_prerequisite_unavailable"
    )


def test_green_4_r1_and_r2_can_each_produce_distinct_abstraction_episode() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    r1 = None
    r2 = None
    for index in (1, 2):
        r1 = admission.observe(
            _exclusive_dependency_grounding(f"fp:r1:{index}"),
            session_id="session:both",
            turn_id=f"turn:r1:{index}",
            scope_reference="scope:multifamily",
        )
        r2 = admission.observe(
            _velar_grounding(f"fp:r2:{index}"),
            session_id="session:both",
            turn_id=f"turn:r2:{index}",
            scope_reference="scope:multifamily",
        )
    assert r1 is not None and r1.episode is not None
    assert r2 is not None and r2.episode is not None
    assert (
        r1.episode.abstraction_candidate.invariant_relation,
        r1.episode.abstraction_candidate.invariant_outcome,
    ) != (
        r2.episode.abstraction_candidate.invariant_relation,
        r2.episode.abstraction_candidate.invariant_outcome,
    )


def test_green_4_duplicate_r2_does_not_inflate_support() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    first = admission.observe(
        _velar_grounding("fp:r2:duplicate"),
        session_id="session:dup",
        turn_id="turn:1",
        scope_reference="scope:multifamily",
    )
    duplicate = admission.observe(
        _velar_grounding("fp:r2:duplicate"),
        session_id="session:dup",
        turn_id="turn:2",
        scope_reference="scope:multifamily",
    )
    assert first.admitted_support == 1
    assert duplicate.status is ProductiveAbstractionAdmissionStatus.DUPLICATE
    assert duplicate.admitted_support == 1


def test_green_4_global_scope_bound_remains_shared_across_families() -> None:
    admission = GovernedProductiveAbstractionAdmission()
    for index in range(4):
        admission.observe(
            _exclusive_dependency_grounding(f"fp:r1:{index}"),
            session_id="session:bound",
            turn_id=f"turn:r1:{index}",
            scope_reference="scope:multifamily",
        )
        admission.observe(
            _velar_grounding(f"fp:r2:{index}"),
            session_id="session:bound",
            turn_id=f"turn:r2:{index}",
            scope_reference="scope:multifamily",
        )
    result = admission.observe(
        _velar_grounding("fp:r2:overflow"),
        session_id="session:bound",
        turn_id="turn:overflow",
        scope_reference="scope:multifamily",
    )
    assert result.status is ProductiveAbstractionAdmissionStatus.ABSTAIN
    assert "abstraction_admission:scope_item_bound_reached" in result.rationale_codes
