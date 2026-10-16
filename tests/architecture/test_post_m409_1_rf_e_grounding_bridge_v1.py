from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from core.governed_reasoning import (
    ContextualRuleGroundingCompilationStatus,
    ContextualRuleInstantiationStatus,
    ContextualSemanticGroundingStatus,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedContextualRuleGroundingCompiler,
    GovernedContextualRuleInstantiator,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)

SCOPE = "session:grounding-bridge-v1"
SOURCE = "conversation:grounding-bridge-v1/turn-1"
TEXT = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)


def test_supported_grounding_compiles_through_existing_contracts() -> None:
    compilation = _compile()

    assert (
        compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.COMPILED
    )
    assert compilation.vocabulary is not None
    assert compilation.instantiation_spec is not None
    assert len(compilation.normalized_conditions) == 3
    assert compilation.normalized_conclusion is not None
    assert compilation.instantiation_spec.roles == (
        "dependent",
        "resource",
        "capability",
    )


def test_compilation_uses_grounding_slots_as_only_certified_alias_source() -> None:
    grounding = _grounding()
    compilation = _compiler().compile(
        rule_candidate=_candidate(),
        semantic_grounding=grounding,
        scope_reference=SCOPE,
    )

    assert compilation.vocabulary is not None
    aliases = tuple(entry.aliases[0].term for entry in compilation.vocabulary.entries)
    assert aliases == tuple(slot.source_text for slot in grounding.semantic_slots)


def test_compilation_preserves_bounded_relation_values() -> None:
    compilation = _compile()
    assert compilation.vocabulary is not None

    values = {
        entry.label: entry.allowed_values for entry in compilation.vocabulary.entries
    }
    assert values == {
        "dependency": ("exclusive",),
        "availability": ("unavailable",),
        "alternative": ("false",),
        "capability": ("unavailable",),
    }


def test_compilation_builds_abstract_templates_not_case_bindings() -> None:
    compilation = _compile()
    spec = compilation.instantiation_spec
    assert spec is not None

    assert tuple(item.role_id for item in spec.conditions) == (
        "dependent",
        "resource",
        "dependent",
    )
    assert spec.conclusion.role_id == "dependent"
    assert "station" not in repr(spec).casefold()
    assert "sensor:t" not in repr(spec).casefold()


def test_3a4_still_requires_case_bindings_after_compilation() -> None:
    compilation = _compile()
    spec = compilation.instantiation_spec
    assert spec is not None

    result = GovernedContextualRuleInstantiator().instantiate(
        spec=spec,
        bindings=(),
        scope_reference=SCOPE,
    )
    assert result.status is ContextualRuleInstantiationStatus.INSUFFICIENT_BINDINGS
    assert result.concrete_conditions == ()
    assert result.concrete_conclusion is None


def test_scope_mismatch_fails_closed_without_partial_compilation() -> None:
    compilation = _compiler().compile(
        rule_candidate=_candidate(),
        semantic_grounding=_grounding(),
        scope_reference="session:other",
    )

    assert (
        compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.SCOPE_MISMATCH
    )
    _assert_no_partial(compilation)


def test_provenance_mismatch_fails_closed_without_partial_compilation() -> None:
    grounding = replace(
        _grounding(),
        source_candidate_fingerprint="different-candidate-fingerprint",
    )
    compilation = _compiler().compile(
        rule_candidate=_candidate(),
        semantic_grounding=grounding,
        scope_reference=SCOPE,
    )

    assert (
        compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.PROVENANCE_MISMATCH
    )
    _assert_no_partial(compilation)


def test_non_grounded_semantics_do_not_compile() -> None:
    grounding = replace(
        _grounding(),
        status=ContextualSemanticGroundingStatus.AMBIGUOUS,
        role_mentions=(),
        semantic_slots=(),
    )
    compilation = _compiler().compile(
        rule_candidate=_candidate(),
        semantic_grounding=grounding,
        scope_reference=SCOPE,
    )

    assert (
        compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.AMBIGUOUS
    )
    _assert_no_partial(compilation)


def test_claim_normalization_ambiguity_aborts_whole_compilation() -> None:
    grounding = _grounding()
    first = grounding.semantic_slots[0]
    second = replace(
        grounding.semantic_slots[1],
        source_text=first.source_text,
    )
    ambiguous = replace(
        grounding,
        semantic_slots=(
            first,
            second,
            grounding.semantic_slots[2],
            grounding.semantic_slots[3],
        ),
    )
    compilation = _compiler().compile(
        rule_candidate=_candidate(),
        semantic_grounding=ambiguous,
        scope_reference=SCOPE,
    )

    assert (
        compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.AMBIGUOUS
    )
    _assert_no_partial(compilation)


def test_compilation_is_deterministic_and_session_local() -> None:
    first = _compile()
    second = _compile()

    assert first.source_fingerprint == second.source_fingerprint
    assert first.vocabulary is not None
    assert second.vocabulary is not None
    assert first.vocabulary.vocabulary_id == second.vocabulary.vocabulary_id
    assert first.instantiation_spec == second.instantiation_spec
    assert first.session_local is True


def test_compilation_is_immutable_and_non_authoritative() -> None:
    compilation = _compile()

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
        assert getattr(compilation, name) is False
    with pytest.raises(FrozenInstanceError):
        compilation.scope_reference = "changed"  # type: ignore[misc]


def test_bridge_remains_inside_governed_reasoning_without_runtime_wiring() -> None:
    import core.governed_reasoning.contextual_rule_grounding_compilation as module

    source = module.__file__
    assert source is not None
    text = Path(source).read_text(encoding="utf-8")
    assert "OfficialConversationGateway" not in text
    assert "GovernedTemporaryConcreteRuleAdmissionBoundary" not in text
    assert "InMemoryInferenceRuleRegistry" not in text
    assert "llm" not in text.casefold()


def _candidate():
    return GovernedContextualRuleInterpretationProducer().produce(
        TEXT,
        source_reference=SOURCE,
        scope_reference=SCOPE,
    )


def _grounding():
    return GovernedBoundedSemanticRoleRelationGrounder().ground(
        _candidate(),
        scope_reference=SCOPE,
    )


def _compiler() -> GovernedContextualRuleGroundingCompiler:
    return GovernedContextualRuleGroundingCompiler()


def _compile():
    candidate = _candidate()
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=SCOPE,
    )
    return _compiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference=SCOPE,
    )


def _assert_no_partial(compilation) -> None:
    assert compilation.vocabulary is None
    assert compilation.normalized_conditions == ()
    assert compilation.normalized_conclusion is None
    assert compilation.instantiation_spec is None
