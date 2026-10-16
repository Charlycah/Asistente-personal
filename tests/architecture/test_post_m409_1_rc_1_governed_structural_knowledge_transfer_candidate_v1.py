from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.governed_reasoning import (
    ContextualSemanticGroundingStatus,
    ContextualSemanticRelation,
    ContextualSemanticRole,
    ContextualSemanticRoleMention,
    ContextualSemanticSlot,
    GovernedContextualSemanticGroundingCandidate,
    GovernedStructuralKnowledgeTransferMatcher,
    StructuralKnowledgeTransferStatus,
)

SCOPE = "rc-1-structural-transfer"


def _dependency_grounding(
    *,
    fingerprint: str,
    dependent: str,
    resource: str,
    capability: str,
    scope: str = SCOPE,
) -> GovernedContextualSemanticGroundingCandidate:
    roles = (
        ContextualSemanticRoleMention(
            ContextualSemanticRole.DEPENDENT, dependent, 0, len(dependent)
        ),
        ContextualSemanticRoleMention(
            ContextualSemanticRole.RESOURCE, resource, 20, 20 + len(resource)
        ),
        ContextualSemanticRoleMention(
            ContextualSemanticRole.CAPABILITY,
            capability,
            40,
            40 + len(capability),
        ),
    )
    slots = (
        ContextualSemanticSlot(
            ContextualSemanticRole.DEPENDENT,
            ContextualSemanticRelation.DEPENDENCY,
            "exclusive",
            "exclusive dependency",
            60,
            80,
        ),
        ContextualSemanticSlot(
            ContextualSemanticRole.RESOURCE,
            ContextualSemanticRelation.AVAILABILITY,
            "unavailable",
            "resource unavailable",
            81,
            101,
        ),
        ContextualSemanticSlot(
            ContextualSemanticRole.DEPENDENT,
            ContextualSemanticRelation.ALTERNATIVE,
            "absent",
            "no alternative",
            102,
            116,
        ),
        ContextualSemanticSlot(
            ContextualSemanticRole.DEPENDENT,
            ContextualSemanticRelation.CAPABILITY,
            "unavailable",
            "capability unavailable",
            117,
            139,
        ),
    )
    return GovernedContextualSemanticGroundingCandidate(
        status=ContextualSemanticGroundingStatus.GROUNDED,
        source_reference=f"conversation:{fingerprint}",
        scope_reference=scope,
        source_candidate_fingerprint=f"candidate:{fingerprint}",
        family_id="exclusive_dependency_capability_loss_v1",
        role_mentions=roles,
        semantic_slots=slots,
        rationale_codes=("test:grounded_dependency_structure",),
        source_fingerprint=fingerprint,
    )


def _relational_grounding(
    *,
    fingerprint: str,
    prerequisite: str,
    dependent: str,
) -> GovernedContextualSemanticGroundingCandidate:
    roles = (
        ContextualSemanticRoleMention(
            ContextualSemanticRole.PREREQUISITE,
            prerequisite,
            0,
            len(prerequisite),
        ),
        ContextualSemanticRoleMention(
            ContextualSemanticRole.DEPENDENT,
            dependent,
            20,
            20 + len(dependent),
        ),
    )
    slots = (
        ContextualSemanticSlot(
            ContextualSemanticRole.PREREQUISITE,
            ContextualSemanticRelation.REQUIRED_FOR,
            ContextualSemanticRole.DEPENDENT.value,
            "required for",
            40,
            52,
        ),
        ContextualSemanticSlot(
            ContextualSemanticRole.PREREQUISITE,
            ContextualSemanticRelation.AVAILABILITY,
            "unavailable",
            "prerequisite unavailable",
            53,
            77,
        ),
        ContextualSemanticSlot(
            ContextualSemanticRole.DEPENDENT,
            ContextualSemanticRelation.CAPABILITY,
            "unavailable",
            "dependent unavailable",
            78,
            99,
        ),
    )
    return GovernedContextualSemanticGroundingCandidate(
        status=ContextualSemanticGroundingStatus.GROUNDED,
        source_reference=f"conversation:{fingerprint}",
        scope_reference=SCOPE,
        source_candidate_fingerprint=f"candidate:{fingerprint}",
        family_id="relational_prerequisite_capability_block_v1",
        role_mentions=roles,
        semantic_slots=slots,
        rationale_codes=("test:grounded_relational_structure",),
        source_fingerprint=fingerprint,
    )


def test_cross_domain_structure_matches_without_shared_entity_words() -> None:
    known = _dependency_grounding(
        fingerprint="source-a",
        dependent="estación meteorológica",
        resource="sensor térmico",
        capability="medir temperatura",
    )
    target = _dependency_grounding(
        fingerprint="target-b",
        dependent="misión orbital",
        resource="ventana de lanzamiento",
        capability="ejecutar maniobra",
    )

    result = GovernedStructuralKnowledgeTransferMatcher().match(
        target=target,
        known=(known,),
        scope_reference=SCOPE,
    )

    assert (
        result.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )
    assert result.matched_source_fingerprints == ("source-a",)
    assert tuple(
        (item.normalized_role, item.source_text, item.target_text)
        for item in result.correspondences
    ) == (
        (
            ContextualSemanticRole.DEPENDENT,
            "estación meteorológica",
            "misión orbital",
        ),
        (
            ContextualSemanticRole.RESOURCE,
            "sensor térmico",
            "ventana de lanzamiento",
        ),
        (
            ContextualSemanticRole.CAPABILITY,
            "medir temperatura",
            "ejecutar maniobra",
        ),
    )


def test_same_words_with_different_relational_structure_do_not_transfer() -> None:
    known = _dependency_grounding(
        fingerprint="source-a",
        dependent="estación",
        resource="sensor",
        capability="temperatura",
    )
    target = _relational_grounding(
        fingerprint="target-c",
        prerequisite="sensor",
        dependent="temperatura",
    )

    result = GovernedStructuralKnowledgeTransferMatcher().match(
        target=target,
        known=(known,),
        scope_reference=SCOPE,
    )

    assert result.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER
    assert result.correspondences == ()


def test_two_structurally_compatible_sources_require_review() -> None:
    first = _dependency_grounding(
        fingerprint="source-a",
        dependent="estación",
        resource="sensor",
        capability="temperatura",
    )
    second = _dependency_grounding(
        fingerprint="source-b",
        dependent="laboratorio",
        resource="reactivo",
        capability="medición",
    )
    target = _dependency_grounding(
        fingerprint="target-c",
        dependent="misión",
        resource="ventana",
        capability="maniobra",
    )

    result = GovernedStructuralKnowledgeTransferMatcher().match(
        target=target,
        known=(first, second),
        scope_reference=SCOPE,
    )

    assert result.normalized_status is StructuralKnowledgeTransferStatus.AMBIGUOUS
    assert result.matched_source_fingerprints == ("source-a", "source-b")
    assert result.correspondences == ()


def test_cross_scope_source_is_not_eligible() -> None:
    known = _dependency_grounding(
        fingerprint="source-other",
        dependent="estación",
        resource="sensor",
        capability="temperatura",
        scope="another-session",
    )
    target = _dependency_grounding(
        fingerprint="target",
        dependent="misión",
        resource="ventana",
        capability="maniobra",
    )

    result = GovernedStructuralKnowledgeTransferMatcher().match(
        target=target,
        known=(known,),
        scope_reference=SCOPE,
    )

    assert result.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER


def test_target_scope_mismatch_fails_closed() -> None:
    target = _dependency_grounding(
        fingerprint="target",
        dependent="misión",
        resource="ventana",
        capability="maniobra",
        scope="another-session",
    )

    result = GovernedStructuralKnowledgeTransferMatcher().match(
        target=target,
        known=(),
        scope_reference=SCOPE,
    )

    assert result.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER
    assert result.rationale_codes == ("structural_transfer:target_scope_mismatch",)


def test_same_grounding_is_not_treated_as_cross_context_transfer() -> None:
    target = _dependency_grounding(
        fingerprint="same",
        dependent="misión",
        resource="ventana",
        capability="maniobra",
    )

    result = GovernedStructuralKnowledgeTransferMatcher().match(
        target=target,
        known=(target,),
        scope_reference=SCOPE,
    )

    assert result.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER


def test_result_is_deterministic_and_immutable() -> None:
    known = _dependency_grounding(
        fingerprint="source",
        dependent="estación",
        resource="sensor",
        capability="temperatura",
    )
    target = _dependency_grounding(
        fingerprint="target",
        dependent="misión",
        resource="ventana",
        capability="maniobra",
    )
    matcher = GovernedStructuralKnowledgeTransferMatcher()

    first = matcher.match(target=target, known=(known,), scope_reference=SCOPE)
    second = matcher.match(target=target, known=(known,), scope_reference=SCOPE)

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.scope_reference = "changed"  # type: ignore[misc]


def test_transfer_candidate_has_no_inference_or_learning_authority() -> None:
    known = _dependency_grounding(
        fingerprint="source",
        dependent="estación",
        resource="sensor",
        capability="temperatura",
    )
    target = _dependency_grounding(
        fingerprint="target",
        dependent="misión",
        resource="ventana",
        capability="maniobra",
    )

    result = GovernedStructuralKnowledgeTransferMatcher().match(
        target=target,
        known=(known,),
        scope_reference=SCOPE,
    )

    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.session_local is True
    for name in (
        "persists_results",
        "creates_memory",
        "modifies_memory",
        "creates_learning_candidate",
        "modifies_learning",
        "modifies_world_model",
        "establishes_truth",
        "authorizes_inference",
        "registers_rule",
        "executes_actions",
        "grants_authority",
        "uses_provider",
        "uses_retrieval",
    ):
        assert getattr(result, name) is False


def test_matcher_does_not_mutate_known_or_target_groundings() -> None:
    known = _dependency_grounding(
        fingerprint="source",
        dependent="estación",
        resource="sensor",
        capability="temperatura",
    )
    target = _dependency_grounding(
        fingerprint="target",
        dependent="misión",
        resource="ventana",
        capability="maniobra",
    )
    before_known = known
    before_target = target

    GovernedStructuralKnowledgeTransferMatcher().match(
        target=target,
        known=(known,),
        scope_reference=SCOPE,
    )

    assert known == before_known
    assert target == before_target


def test_structural_matching_ignores_concrete_domain_terms() -> None:
    first = _dependency_grounding(
        fingerprint="source",
        dependent="sistema A",
        resource="recurso B",
        capability="capacidad C",
    )
    second = _dependency_grounding(
        fingerprint="target",
        dependent="persona",
        resource="documento",
        capability="verificar identidad",
    )

    result = GovernedStructuralKnowledgeTransferMatcher().match(
        target=second,
        known=(first,),
        scope_reference=SCOPE,
    )

    assert (
        result.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )
