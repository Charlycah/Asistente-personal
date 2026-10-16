from dataclasses import FrozenInstanceError

import pytest

from core.governed_reasoning.contextual_rule_instantiation import (
    ContextualRuleConclusionTemplate,
    ContextualRuleConditionTemplate,
    ContextualRuleInstantiationSpec,
    ContextualRuleInstantiationStatus,
    ContextualRuleRoleBinding,
    GovernedContextualRuleInstantiator,
)

SCOPE = "session:rf-h-relational-role-binding-v1"
SOURCE = "conversation:rf-h-relational-role-binding-v1/rule-1"
VOCAB = "ctx-vocabulary-velar00000001"
P_REQUIRED = "ctx-predicate-required-for"
P_AVAILABLE = "ctx-predicate-availability"
P_BLOCKED = "ctx-predicate-blocked"


def _relational_spec() -> ContextualRuleInstantiationSpec:
    return ContextualRuleInstantiationSpec(
        rule_candidate_id="rule:velar-representability",
        scope_reference=SCOPE,
        vocabulary_id=VOCAB,
        source_reference=SOURCE,
        roles=("prerequisite", "dependent"),
        conditions=(
            ContextualRuleConditionTemplate(
                role_id="prerequisite",
                predicate_id=P_REQUIRED,
                object_role_id="dependent",
            ),
            ContextualRuleConditionTemplate(
                role_id="prerequisite",
                predicate_id=P_AVAILABLE,
                object_value="unavailable",
            ),
        ),
        conclusion=ContextualRuleConclusionTemplate(
            role_id="dependent",
            predicate_id=P_BLOCKED,
            object_value="true",
        ),
    )


def _bindings() -> tuple[ContextualRuleRoleBinding, ...]:
    return (
        ContextualRuleRoleBinding(
            "prerequisite",
            "reconstruct_experiment",
            "case:1",
            "reconstruir el experimento",
        ),
        ContextualRuleRoleBinding(
            "dependent",
            "reproduce_experiment",
            "case:2",
            "reproducir el experimento",
        ),
    )


def _instantiate(bindings=None):
    return GovernedContextualRuleInstantiator().instantiate(
        spec=_relational_spec(),
        bindings=_bindings() if bindings is None else bindings,
        scope_reference=SCOPE,
    )


def test_role_bound_relational_object_resolves_to_bound_entity() -> None:
    result = _instantiate()

    assert result.status is ContextualRuleInstantiationStatus.INSTANTIATED
    relation = result.concrete_conditions[0]
    assert relation.subject == "reconstruct_experiment"
    assert relation.predicate_id == P_REQUIRED
    assert relation.object_value == "reproduce_experiment"


def test_literal_object_semantics_remain_unchanged() -> None:
    result = _instantiate()

    literal = result.concrete_conditions[1]
    assert literal.subject == "reconstruct_experiment"
    assert literal.predicate_id == P_AVAILABLE
    assert literal.object_value == "unavailable"


def test_conclusion_can_resolve_role_bound_relational_object() -> None:
    spec = ContextualRuleInstantiationSpec(
        rule_candidate_id="rule:relational-conclusion",
        scope_reference=SCOPE,
        vocabulary_id=VOCAB,
        source_reference=SOURCE,
        roles=("prerequisite", "dependent"),
        conditions=(
            ContextualRuleConditionTemplate(
                role_id="prerequisite",
                predicate_id=P_AVAILABLE,
                object_value="unavailable",
            ),
        ),
        conclusion=ContextualRuleConclusionTemplate(
            role_id="prerequisite",
            predicate_id=P_REQUIRED,
            object_role_id="dependent",
        ),
    )

    result = GovernedContextualRuleInstantiator().instantiate(
        spec=spec,
        bindings=_bindings(),
        scope_reference=SCOPE,
    )

    assert result.concrete_conclusion is not None
    assert result.concrete_conclusion.subject == "reconstruct_experiment"
    assert result.concrete_conclusion.object_value == "reproduce_experiment"


def test_missing_object_role_binding_fails_closed_without_partial_rule() -> None:
    result = _instantiate(_bindings()[:1])

    assert result.status is ContextualRuleInstantiationStatus.INSUFFICIENT_BINDINGS
    assert result.concrete_conditions == ()
    assert result.concrete_conclusion is None


def test_unknown_object_role_is_rejected_by_spec() -> None:
    with pytest.raises(ValueError, match="undeclared role"):
        ContextualRuleInstantiationSpec(
            rule_candidate_id="rule:invalid-object-role",
            scope_reference=SCOPE,
            vocabulary_id=VOCAB,
            source_reference=SOURCE,
            roles=("prerequisite", "dependent"),
            conditions=(
                ContextualRuleConditionTemplate(
                    role_id="prerequisite",
                    predicate_id=P_REQUIRED,
                    object_role_id="unknown",
                ),
            ),
            conclusion=ContextualRuleConclusionTemplate(
                role_id="dependent",
                predicate_id=P_BLOCKED,
                object_value="true",
            ),
        )


def test_template_rejects_literal_and_role_object_together() -> None:
    with pytest.raises(ValueError, match="exactly one object source"):
        ContextualRuleConditionTemplate(
            role_id="prerequisite",
            predicate_id=P_REQUIRED,
            object_value="dependent",
            object_role_id="dependent",
        )


def test_template_rejects_missing_object_source() -> None:
    with pytest.raises(ValueError, match="exactly one object source"):
        ContextualRuleConditionTemplate(
            role_id="prerequisite",
            predicate_id=P_REQUIRED,
        )


def test_duplicate_object_role_binding_remains_ambiguous() -> None:
    duplicate = ContextualRuleRoleBinding(
        "dependent",
        "publish_experiment",
        "case:3",
        "publicar el experimento",
    )
    result = _instantiate((*_bindings(), duplicate))

    assert result.status is ContextualRuleInstantiationStatus.AMBIGUOUS_BINDINGS
    assert result.concrete_conditions == ()
    assert result.concrete_conclusion is None


def test_role_bound_object_change_changes_fingerprint_and_object() -> None:
    changed = (
        _bindings()[0],
        ContextualRuleRoleBinding(
            "dependent",
            "publish_experiment",
            "case:2",
            "publicar el experimento",
        ),
    )

    first = _instantiate()
    second = _instantiate(changed)

    assert first.source_fingerprint != second.source_fingerprint
    assert second.concrete_conditions[0].object_value == "publish_experiment"


def test_relational_instantiation_is_deterministic() -> None:
    assert _instantiate().source_fingerprint == _instantiate().source_fingerprint


def test_relational_instantiation_preserves_governed_limits() -> None:
    result = _instantiate()

    assert result.read_only is True
    assert result.session_local is True
    for name in (
        "persists_results",
        "creates_memory",
        "modifies_memory",
        "creates_learning_candidate",
        "modifies_learning",
        "establishes_truth",
        "establishes_falsity",
        "authorizes_inference",
        "registers_rule",
        "executes_actions",
        "grants_authority",
    ):
        assert getattr(result, name) is False
    with pytest.raises(FrozenInstanceError):
        result.scope_reference = "changed"  # type: ignore[misc]


def test_relational_binding_does_not_mutate_abstract_spec() -> None:
    spec = _relational_spec()
    before = repr(spec)

    GovernedContextualRuleInstantiator().instantiate(
        spec=spec,
        bindings=_bindings(),
        scope_reference=SCOPE,
    )

    assert repr(spec) == before
