from __future__ import annotations

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

SCOPE = "post-hcpdq-strong-generalization-multi-family"


def _dependency(
    fingerprint: str,
    dependent: str,
    resource: str,
    capability: str,
    *,
    scope: str = SCOPE,
) -> GovernedContextualSemanticGroundingCandidate:
    return GovernedContextualSemanticGroundingCandidate(
        status=ContextualSemanticGroundingStatus.GROUNDED,
        source_reference=f"challenge:{fingerprint}",
        scope_reference=scope,
        source_candidate_fingerprint=f"candidate:{fingerprint}",
        family_id="exclusive_dependency_capability_loss_v1",
        role_mentions=(
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
        ),
        semantic_slots=(
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
        ),
        rationale_codes=("challenge:dependency",),
        source_fingerprint=fingerprint,
    )


def _prerequisite(
    fingerprint: str,
    prerequisite: str,
    dependent: str,
    *,
    scope: str = SCOPE,
) -> GovernedContextualSemanticGroundingCandidate:
    return GovernedContextualSemanticGroundingCandidate(
        status=ContextualSemanticGroundingStatus.GROUNDED,
        source_reference=f"challenge:{fingerprint}",
        scope_reference=scope,
        source_candidate_fingerprint=f"candidate:{fingerprint}",
        family_id="relational_prerequisite_capability_block_v1",
        role_mentions=(
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
        ),
        semantic_slots=(
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
        ),
        rationale_codes=("challenge:prerequisite",),
        source_fingerprint=fingerprint,
    )


def _match(target, *known):
    return GovernedStructuralKnowledgeTransferMatcher().match(
        target=target, known=tuple(known), scope_reference=SCOPE
    )


def _assert_transfer(result):
    assert (
        result.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )
    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.session_local is True
    assert result.establishes_truth is False
    assert result.authorizes_inference is False
    assert result.creates_learning_candidate is False
    assert result.persists_results is False


# Family A: exclusive dependency / capability loss.


def test_mf_a1_dependency_cross_domain_transfer():
    result = _match(
        _dependency("a-target", "cirugía", "robot", "operar"),
        _dependency("a-source", "observatorio", "telescopio", "observar"),
    )
    _assert_transfer(result)


def test_mf_a2_dependency_lexical_entity_shift_transfer():
    result = _match(
        _dependency("a2-target", "archivo", "servidor", "consultar"),
        _dependency("a2-source", "expedición", "puente", "cruzar"),
    )
    _assert_transfer(result)


def test_mf_a3_dependency_rejects_prerequisite_lookalike():
    result = _match(
        _dependency("a3-target", "laboratorio", "reactivo", "medir"),
        _prerequisite("a3-source", "firma", "publicación"),
    )
    assert result.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER


def test_mf_a4_dependency_multiple_sources_are_ambiguous():
    result = _match(
        _dependency("a4-target", "misión", "ventana", "maniobrar"),
        _dependency("a4-source-1", "archivo", "servidor", "consultar"),
        _dependency("a4-source-2", "hospital", "equipo", "diagnosticar"),
    )
    assert result.normalized_status is StructuralKnowledgeTransferStatus.AMBIGUOUS


# Family B: prerequisite / dependent capability block.


def test_mf_b1_prerequisite_cross_domain_transfer():
    result = _match(
        _prerequisite("b-target", "autorización", "despliegue"),
        _prerequisite("b-source", "calibración", "medición"),
    )
    _assert_transfer(result)


def test_mf_b2_prerequisite_lexical_entity_shift_transfer():
    result = _match(
        _prerequisite("b2-target", "oxígeno", "supervivencia"),
        _prerequisite("b2-source", "credencial", "acceso"),
    )
    _assert_transfer(result)


def test_mf_b3_prerequisite_rejects_dependency_lookalike():
    result = _match(
        _prerequisite("b3-target", "firma", "publicación"),
        _dependency("b3-source", "archivo", "servidor", "consultar"),
    )
    assert result.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER


def test_mf_b4_prerequisite_multiple_sources_are_ambiguous():
    result = _match(
        _prerequisite("b4-target", "permiso", "ejecución"),
        _prerequisite("b4-source-1", "energía", "arranque"),
        _prerequisite("b4-source-2", "clave", "descifrado"),
    )
    assert result.normalized_status is StructuralKnowledgeTransferStatus.AMBIGUOUS


# Family C: cross-family discrimination and governance boundaries.


def test_mf_c1_same_terms_different_family_do_not_transfer():
    result = _match(
        _dependency("c1-target", "sistema", "recurso", "capacidad"),
        _prerequisite("c1-source", "recurso", "capacidad"),
    )
    assert result.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER


def test_mf_c2_cross_scope_structure_does_not_transfer():
    result = _match(
        _dependency("c2-target", "misión", "ventana", "maniobra"),
        _dependency(
            "c2-source",
            "archivo",
            "servidor",
            "consulta",
            scope="another-scope",
        ),
    )
    assert result.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER


def test_mf_c3_same_instance_is_not_generalization():
    target = _prerequisite("c3-same", "calibración", "medición")
    result = _match(target, target)
    assert result.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER


def test_mf_c4_family_specific_transfer_preserves_role_correspondence():
    result = _match(
        _prerequisite("c4-target", "licencia", "operación"),
        _prerequisite("c4-source", "certificado", "auditoría"),
    )
    _assert_transfer(result)
    assert tuple(item.normalized_role for item in result.correspondences) == (
        ContextualSemanticRole.PREREQUISITE,
        ContextualSemanticRole.DEPENDENT,
    )
