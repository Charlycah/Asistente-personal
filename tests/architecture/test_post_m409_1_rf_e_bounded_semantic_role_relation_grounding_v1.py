from __future__ import annotations

import ast
import inspect
from dataclasses import FrozenInstanceError

import pytest

from core.governed_reasoning import (
    ContextualSemanticGroundingStatus,
    ContextualSemanticRelation,
    ContextualSemanticRole,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedContextualSemanticGroundingCandidate,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)

SCOPE = "session:grounding-v1"
SOURCE = "conversation:session:grounding-v1/turn-1"
PRODUCER = GovernedContextualRuleInterpretationProducer()
GROUNDER = GovernedBoundedSemanticRoleRelationGrounder()


def _candidate(text: str):
    return PRODUCER.produce(
        text,
        source_reference=SOURCE,
        scope_reference=SCOPE,
    )


def _supported_rule() -> str:
    return (
        "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
        "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
        "ese sistema pierde esa capacidad."
    )


def test_foundation_grounds_one_bounded_dependency_loss_family() -> None:
    result = GROUNDER.ground(_candidate(_supported_rule()), scope_reference=SCOPE)

    assert result.normalized_status is ContextualSemanticGroundingStatus.GROUNDED
    assert tuple(item.role_id for item in result.role_mentions) == (
        ContextualSemanticRole.DEPENDENT,
        ContextualSemanticRole.RESOURCE,
        ContextualSemanticRole.CAPABILITY,
    )
    assert tuple(item.relation for item in result.semantic_slots) == (
        ContextualSemanticRelation.DEPENDENCY,
        ContextualSemanticRelation.AVAILABILITY,
        ContextualSemanticRelation.ALTERNATIVE,
        ContextualSemanticRelation.CAPABILITY,
    )
    assert tuple(item.value for item in result.semantic_slots) == (
        "exclusive",
        "unavailable",
        "absent",
        "unavailable",
    )


def test_role_and_slot_spans_are_exact_source_spans() -> None:
    candidate = _candidate(_supported_rule())
    result = GROUNDER.ground(candidate, scope_reference=SCOPE)

    for item in (*result.role_mentions, *result.semantic_slots):
        assert (
            candidate.source_text[item.start_offset : item.end_offset]
            == item.source_text
        )


def test_grounding_is_domain_neutral_within_the_certified_family() -> None:
    text = (
        "Regla temporal: si una aplicación depende exclusivamente de un servicio para "
        "una función y ese recurso queda indisponible y no hay alternativa, entonces "
        "ese sistema pierde esa capacidad."
    )
    result = GROUNDER.ground(_candidate(text), scope_reference=SCOPE)

    assert result.normalized_status is ContextualSemanticGroundingStatus.GROUNDED
    assert result.role_mentions[0].source_text == "una aplicación"
    assert result.role_mentions[1].source_text == "un servicio"
    assert result.role_mentions[2].source_text == "una función"


def test_non_candidate_or_wrong_shape_abstains_without_partial_grounding() -> None:
    ordinary = _candidate("Si llueve, entonces Juan lleva paraguas.")
    result = GROUNDER.ground(ordinary, scope_reference=SCOPE)
    assert result.normalized_status is ContextualSemanticGroundingStatus.UNSUPPORTED
    assert result.role_mentions == ()
    assert result.semantic_slots == ()

    wrong_shape = _candidate(
        "Usá esta regla: si A depende exclusivamente de B para C, entonces D ocurre."
    )
    result = GROUNDER.ground(wrong_shape, scope_reference=SCOPE)
    assert result.normalized_status is ContextualSemanticGroundingStatus.UNSUPPORTED
    assert result.role_mentions == ()
    assert result.semantic_slots == ()


def test_implicit_role_reference_in_declaration_fails_closed() -> None:
    text = (
        "Usá esta regla: si él depende exclusivamente de un recurso para una capacidad "
        "y ese recurso está indisponible y no existe alternativa, entonces ese sistema "
        "pierde esa capacidad."
    )
    result = GROUNDER.ground(_candidate(text), scope_reference=SCOPE)
    assert result.normalized_status is ContextualSemanticGroundingStatus.AMBIGUOUS
    assert result.role_mentions == ()
    assert result.semantic_slots == ()


def test_unsupported_semantic_variant_is_not_guessed() -> None:
    text = (
        "Usá esta regla: si un sistema depende parcialmente de un recurso para una "
        "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
        "ese sistema pierde esa capacidad."
    )
    result = GROUNDER.ground(_candidate(text), scope_reference=SCOPE)
    assert result.normalized_status is ContextualSemanticGroundingStatus.UNSUPPORTED
    assert result.role_mentions == ()
    assert result.semantic_slots == ()


def test_scope_mismatch_fails_closed() -> None:
    with pytest.raises(ValueError, match="scope mismatch"):
        GROUNDER.ground(_candidate(_supported_rule()), scope_reference="session:other")


def test_grounding_contract_is_frozen_and_non_authoritative() -> None:
    result = GROUNDER.ground(_candidate(_supported_rule()), scope_reference=SCOPE)

    with pytest.raises(FrozenInstanceError):
        result.family_id = "other"  # type: ignore[misc]
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


def test_grounder_has_no_forbidden_productive_dependencies() -> None:
    module = inspect.getmodule(GovernedBoundedSemanticRoleRelationGrounder)
    assert module is not None
    tree = ast.parse(inspect.getsource(module))
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    forbidden = {
        "core.llm_provider",
        "core.memory_foundation",
        "core.learning_foundation",
        "core.governed_reasoning.inference",
        "app.official_conversation_gateway",
        "app.governed_reasoning_runtime",
    }
    assert imports.isdisjoint(forbidden)
    assert "register" not in GovernedBoundedSemanticRoleRelationGrounder.__dict__
    assert "execute" not in GovernedBoundedSemanticRoleRelationGrounder.__dict__
    assert "save" not in GovernedBoundedSemanticRoleRelationGrounder.__dict__


def test_candidate_requires_governed_reasoning_authority() -> None:
    result = GROUNDER.ground(_candidate(_supported_rule()), scope_reference=SCOPE)
    payload = result.__dict__ | {"canonical_authority": "other"}
    with pytest.raises(ValueError, match="preserve governed reasoning authority"):
        GovernedContextualSemanticGroundingCandidate(**payload)
