from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from core.governed_reasoning.contextual_rule_grounding_compilation import (
    ContextualRuleGroundingCompilationStatus,
    GovernedContextualRuleGroundingCompiler,
)
from core.governed_reasoning.contextual_rule_instantiation import (
    ContextualRuleInstantiationStatus,
    ContextualRuleRoleBinding,
    GovernedContextualRuleInstantiator,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticGroundingStatus,
    ContextualSemanticRelation,
    ContextualSemanticRole,
    GovernedBoundedSemanticRoleRelationGrounder,
)

TEXT = (
    "Regla temporal: si capacidad alfa es requisito indispensable para capacidad beta "
    "y la capacidad requisito queda indisponible, entonces la capacidad dependiente "
    "queda impedida."
)
SOURCE = "conversation:rf-h/velar-v1"
SCOPE = "session:rf-h-velar"


def _candidate(text: str = TEXT):
    return GovernedContextualRuleInterpretationProducer().produce(
        text,
        source_reference=SOURCE,
        scope_reference=SCOPE,
    )


def _ground(text: str = TEXT):
    return GovernedBoundedSemanticRoleRelationGrounder().ground(
        _candidate(text),
        scope_reference=SCOPE,
    )


def _compile():
    candidate = _candidate()
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=SCOPE,
    )
    return GovernedContextualRuleGroundingCompiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference=SCOPE,
    )


def test_velar_family_is_grounded_with_two_explicit_relational_roles() -> None:
    grounding = _ground()

    assert grounding.normalized_status is ContextualSemanticGroundingStatus.GROUNDED
    assert grounding.family_id == "relational_prerequisite_capability_block_v1"
    assert tuple(item.role_id for item in grounding.role_mentions) == (
        ContextualSemanticRole.PREREQUISITE,
        ContextualSemanticRole.DEPENDENT,
    )


def test_velar_grounding_preserves_required_for_relation_to_dependent_role() -> None:
    slots = _ground().semantic_slots

    assert slots[0].role_id is ContextualSemanticRole.PREREQUISITE
    assert slots[0].relation is ContextualSemanticRelation.REQUIRED_FOR
    assert slots[0].value == ContextualSemanticRole.DEPENDENT.value
    assert slots[1].relation is ContextualSemanticRelation.AVAILABILITY
    assert slots[2].role_id is ContextualSemanticRole.DEPENDENT


def test_compiler_emits_object_role_id_not_literal_dependent() -> None:
    compilation = _compile()

    assert (
        compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.COMPILED
    )
    assert compilation.instantiation_spec is not None
    relational = compilation.instantiation_spec.conditions[0]
    assert relational.object_role_id == "dependent"
    assert relational.object_value is None


def test_compiled_spec_contains_only_family_roles() -> None:
    spec = _compile().instantiation_spec

    assert spec is not None
    assert spec.roles == ("prerequisite", "dependent")


def test_instantiation_resolves_relational_object_from_existing_role_binding() -> None:
    spec = _compile().instantiation_spec
    assert spec is not None

    result = GovernedContextualRuleInstantiator().instantiate(
        spec=spec,
        bindings=(
            ContextualRuleRoleBinding(
                "prerequisite",
                "reconstruct_experiment",
                "case:velar:1",
                "capacidad alfa",
            ),
            ContextualRuleRoleBinding(
                "dependent",
                "reproduce_experiment",
                "case:velar:2",
                "capacidad beta",
            ),
        ),
        scope_reference=SCOPE,
    )

    assert result.status is ContextualRuleInstantiationStatus.INSTANTIATED
    assert result.concrete_conditions[0].subject == "reconstruct_experiment"
    assert result.concrete_conditions[0].object_value == "reproduce_experiment"
    assert result.concrete_conclusion is not None
    assert result.concrete_conclusion.subject == "reproduce_experiment"


def test_missing_relational_binding_fails_closed() -> None:
    spec = _compile().instantiation_spec
    assert spec is not None

    result = GovernedContextualRuleInstantiator().instantiate(
        spec=spec,
        bindings=(
            ContextualRuleRoleBinding(
                "prerequisite",
                "reconstruct_experiment",
                "case:velar:1",
                "capacidad alfa",
            ),
        ),
        scope_reference=SCOPE,
    )

    assert result.status is ContextualRuleInstantiationStatus.INSUFFICIENT_BINDINGS
    assert result.concrete_conditions == ()
    assert result.concrete_conclusion is None


def test_near_family_with_unsupported_relation_fails_closed_without_partial_grounding(
) -> None:
    text = (
        "Regla temporal: si capacidad alfa ayuda a capacidad beta "
        "y la capacidad requisito queda indisponible, entonces la capacidad "
        "dependiente "
        "queda impedida."
    )
    grounding = _ground(text)

    assert grounding.normalized_status is ContextualSemanticGroundingStatus.UNSUPPORTED
    assert grounding.role_mentions == ()
    assert grounding.semantic_slots == ()


def test_velar_grounding_is_immutable_session_local_and_non_authoritative() -> None:
    grounding = _ground()

    assert grounding.session_local is True
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
        assert getattr(grounding, name) is False
    with pytest.raises(FrozenInstanceError):
        grounding.scope_reference = "changed"  # type: ignore[misc]


def test_compilation_scope_mismatch_fails_closed() -> None:
    candidate = _candidate()
    grounding = _ground()

    result = GovernedContextualRuleGroundingCompiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference="session:other",
    )

    assert (
        result.normalized_status
        is ContextualRuleGroundingCompilationStatus.SCOPE_MISMATCH
    )
    assert result.instantiation_spec is None


def test_compilation_provenance_mismatch_fails_closed() -> None:
    candidate = _candidate()
    grounding = replace(_ground(), source_candidate_fingerprint="other")

    result = GovernedContextualRuleGroundingCompiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference=SCOPE,
    )

    assert (
        result.normalized_status
        is ContextualRuleGroundingCompilationStatus.PROVENANCE_MISMATCH
    )
    assert result.instantiation_spec is None


def test_velar_grounding_and_compilation_are_deterministic() -> None:
    first_grounding = _ground()
    second_grounding = _ground()
    first_compilation = _compile()
    second_compilation = _compile()

    assert first_grounding == second_grounding
    assert first_compilation == second_compilation
