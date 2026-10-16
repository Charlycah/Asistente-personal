from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.governed_reasoning import (
    ContextualSemanticGroundingStatus,
    ContextualSemanticRelation,
    ContextualSemanticRole,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedStructuralKnowledgeTransferMatcher,
    GovernedTargetProblemStructuralProjector,
    StructuralKnowledgeTransferStatus,
    TargetProblemStructuralProjectionStatus,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)

SCOPE = "rc-1-2-target-problem"
RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)
TARGET = (
    "La misión orbital depende exclusivamente de la ventana de lanzamiento para "
    "ejecutar una maniobra. La ventana de lanzamiento queda indisponible y no "
    "existe alternativa."
)
TARGET_WITH_CONCLUSION_WORDS = TARGET + " La maniobra queda indisponible."
NO_EXCLUSIVITY = (
    "La misión orbital depende de la ventana de lanzamiento para ejecutar una "
    "maniobra. La ventana de lanzamiento queda indisponible y no existe alternativa."
)
UNKNOWN_ALTERNATIVE = (
    "La misión orbital depende exclusivamente de la ventana de lanzamiento para "
    "ejecutar una maniobra. La ventana de lanzamiento queda indisponible."
)
POSITIVE_ALTERNATIVE = (
    "La misión orbital depende exclusivamente de la ventana de lanzamiento para "
    "ejecutar una maniobra. La ventana de lanzamiento queda indisponible y existe "
    "una alternativa."
)
MULTIPLE = TARGET + (
    " La nave depende exclusivamente del canal de control para mantener telemetría. "
    "El canal de control queda indisponible y no existe alternativa."
)


def _source_grounding():
    candidate = GovernedContextualRuleInterpretationProducer().produce(
        RULE,
        source_reference="memory:rc-1-2-source",
        scope_reference=SCOPE,
    )
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=SCOPE,
    )
    assert grounding.normalized_status is ContextualSemanticGroundingStatus.GROUNDED
    return grounding


def test_ordinary_problem_projects_explicit_antecedent_structure_only() -> None:
    result = GovernedTargetProblemStructuralProjector().project(
        text=TARGET,
        source_reference="conversation:target-1",
        scope_reference=SCOPE,
    )

    assert result.normalized_status is TargetProblemStructuralProjectionStatus.PROJECTED
    assert result.family_id == "exclusive_dependency_capability_loss_v1"
    assert tuple(item.normalized_role for item in result.role_bindings) == (
        ContextualSemanticRole.DEPENDENT,
        ContextualSemanticRole.RESOURCE,
        ContextualSemanticRole.CAPABILITY,
    )
    assert tuple(
        (item.role_id, item.relation, item.value) for item in result.observed_slots
    ) == (
        (
            ContextualSemanticRole.DEPENDENT,
            ContextualSemanticRelation.DEPENDENCY,
            "exclusive",
        ),
        (
            ContextualSemanticRole.RESOURCE,
            ContextualSemanticRelation.AVAILABILITY,
            "unavailable",
        ),
        (
            ContextualSemanticRole.DEPENDENT,
            ContextualSemanticRelation.ALTERNATIVE,
            "absent",
        ),
    )


def test_target_projection_does_not_project_rule_conclusion() -> None:
    result = GovernedTargetProblemStructuralProjector().project(
        text=TARGET_WITH_CONCLUSION_WORDS,
        source_reference="conversation:target-2",
        scope_reference=SCOPE,
    )

    assert result.normalized_status is TargetProblemStructuralProjectionStatus.PROJECTED
    assert all(
        item.relation is not ContextualSemanticRelation.CAPABILITY
        for item in result.observed_slots
    )
    assert "target_projection:conclusion_not_projected" in result.rationale_codes


def test_target_problem_can_match_recalled_rule_antecedent_without_conclusion() -> None:
    target = GovernedTargetProblemStructuralProjector().project(
        text=TARGET,
        source_reference="conversation:target-3",
        scope_reference=SCOPE,
    )
    transfer = GovernedStructuralKnowledgeTransferMatcher().match_target_problem(
        target=target,
        known=(_source_grounding(),),
        scope_reference=SCOPE,
    )

    assert (
        transfer.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )
    assert tuple(item.target_text for item in transfer.correspondences) == (
        "La misión orbital",
        "ventana de lanzamiento",
        "ejecutar una maniobra",
    )
    assert "structural_transfer:target_conclusion_not_assumed" in (
        transfer.rationale_codes
    )


def test_missing_explicit_exclusivity_is_insufficient() -> None:
    result = GovernedTargetProblemStructuralProjector().project(
        text=NO_EXCLUSIVITY,
        source_reference="conversation:target-4",
        scope_reference=SCOPE,
    )
    assert (
        result.normalized_status is TargetProblemStructuralProjectionStatus.INSUFFICIENT
    )
    assert result.role_bindings == ()
    assert result.observed_slots == ()


def test_unknown_alternative_is_insufficient() -> None:
    result = GovernedTargetProblemStructuralProjector().project(
        text=UNKNOWN_ALTERNATIVE,
        source_reference="conversation:target-5",
        scope_reference=SCOPE,
    )
    assert (
        result.normalized_status is TargetProblemStructuralProjectionStatus.INSUFFICIENT
    )


def test_positive_alternative_is_unsupported() -> None:
    result = GovernedTargetProblemStructuralProjector().project(
        text=POSITIVE_ALTERNATIVE,
        source_reference="conversation:target-6",
        scope_reference=SCOPE,
    )
    assert (
        result.normalized_status is TargetProblemStructuralProjectionStatus.UNSUPPORTED
    )


def test_multiple_dependency_candidates_are_ambiguous() -> None:
    result = GovernedTargetProblemStructuralProjector().project(
        text=MULTIPLE,
        source_reference="conversation:target-7",
        scope_reference=SCOPE,
    )
    assert result.normalized_status is TargetProblemStructuralProjectionStatus.AMBIGUOUS
    assert result.role_bindings == ()
    assert result.observed_slots == ()


def test_non_projected_target_cannot_transfer() -> None:
    target = GovernedTargetProblemStructuralProjector().project(
        text=UNKNOWN_ALTERNATIVE,
        source_reference="conversation:target-8",
        scope_reference=SCOPE,
    )
    transfer = GovernedStructuralKnowledgeTransferMatcher().match_target_problem(
        target=target,
        known=(_source_grounding(),),
        scope_reference=SCOPE,
    )
    assert transfer.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER


def test_cross_scope_target_fails_closed() -> None:
    target = GovernedTargetProblemStructuralProjector().project(
        text=TARGET,
        source_reference="conversation:target-9",
        scope_reference="another-scope",
    )
    transfer = GovernedStructuralKnowledgeTransferMatcher().match_target_problem(
        target=target,
        known=(_source_grounding(),),
        scope_reference=SCOPE,
    )
    assert transfer.normalized_status is StructuralKnowledgeTransferStatus.NO_TRANSFER


def test_projection_is_immutable_and_non_authoritative() -> None:
    result = GovernedTargetProblemStructuralProjector().project(
        text=TARGET,
        source_reference="conversation:target-10",
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
    with pytest.raises(FrozenInstanceError):
        result.scope_reference = "changed"  # type: ignore[misc]


def test_projection_is_deterministic() -> None:
    projector = GovernedTargetProblemStructuralProjector()
    first = projector.project(
        text=TARGET,
        source_reference="conversation:target-11",
        scope_reference=SCOPE,
    )
    second = projector.project(
        text=TARGET,
        source_reference="conversation:target-11",
        scope_reference=SCOPE,
    )
    assert first == second
