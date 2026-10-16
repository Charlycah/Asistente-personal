from dataclasses import FrozenInstanceError, fields

import pytest

from core.governed_reasoning.contextual_rule_instantiation import (
    ContextualRuleConclusionTemplate,
    ContextualRuleConditionTemplate,
    ContextualRuleInstantiationSpec,
    ContextualRuleInstantiationStatus,
    ContextualRuleRoleBinding,
    GovernedContextualRuleInstantiator,
)

P_AVAIL = "ctx-predicate-availability"
P_DEP = "ctx-predicate-dependency"
P_ALT = "ctx-predicate-alternative"
P_CAP = "ctx-predicate-capability"
VOCAB = "ctx-vocabulary-neral00000001"
SCOPE = "session-a"
SOURCE = "conversation:session-a/rule-1"


def spec() -> ContextualRuleInstantiationSpec:
    return ContextualRuleInstantiationSpec(
        rule_candidate_id="rule:neral",
        scope_reference=SCOPE,
        vocabulary_id=VOCAB,
        source_reference=SOURCE,
        roles=("system", "resource", "capability"),
        conditions=(
            ContextualRuleConditionTemplate("system", P_DEP, "exclusive"),
            ContextualRuleConditionTemplate("resource", P_AVAIL, "unavailable"),
            ContextualRuleConditionTemplate("system", P_ALT, "false"),
        ),
        conclusion=ContextualRuleConclusionTemplate("system", P_CAP, "unavailable"),
    )


def bindings() -> tuple[ContextualRuleRoleBinding, ...]:
    return (
        ContextualRuleRoleBinding("system", "station-1", "case:1", "la estación"),
        ContextualRuleRoleBinding("resource", "sensor:T", "case:2", "sensor T"),
        ContextualRuleRoleBinding("capability", "temperature", "case:3", "temperatura"),
    )


def instantiate(items=None):
    return GovernedContextualRuleInstantiator().instantiate(
        spec=spec(),
        bindings=bindings() if items is None else items,
        scope_reference=SCOPE,
    )


def test_complete_explicit_bindings_produce_concrete_candidate() -> None:
    result = instantiate()
    assert result.status is ContextualRuleInstantiationStatus.INSTANTIATED
    assert result.concrete_conditions[1].subject == "sensor:T"
    assert result.concrete_conclusion is not None
    assert result.concrete_conclusion.subject == "station-1"


def test_missing_role_fails_closed_without_partial_rule() -> None:
    result = instantiate(bindings()[:2])
    assert result.status is ContextualRuleInstantiationStatus.INSUFFICIENT_BINDINGS
    assert result.concrete_conditions == ()
    assert result.concrete_conclusion is None


def test_duplicate_role_is_ambiguous() -> None:
    duplicate = ContextualRuleRoleBinding("resource", "sensor:U", "case:4", "sensor U")
    result = instantiate((*bindings(), duplicate))
    assert result.status is ContextualRuleInstantiationStatus.AMBIGUOUS_BINDINGS
    assert result.concrete_conditions == ()


def test_undeclared_role_is_unsupported() -> None:
    extra = ContextualRuleRoleBinding("owner", "Carlos", "case:4", "Carlos")
    result = instantiate((*bindings(), extra))
    assert result.status is ContextualRuleInstantiationStatus.UNSUPPORTED


def test_binding_requires_provenance() -> None:
    with pytest.raises(ValueError):
        ContextualRuleRoleBinding("resource", "sensor:T", "", "sensor T")


def test_spec_rejects_undeclared_template_role() -> None:
    with pytest.raises(ValueError):
        ContextualRuleInstantiationSpec(
            rule_candidate_id="rule:x",
            scope_reference=SCOPE,
            vocabulary_id=VOCAB,
            source_reference=SOURCE,
            roles=("system",),
            conditions=(ContextualRuleConditionTemplate("resource", P_AVAIL, "x"),),
            conclusion=ContextualRuleConclusionTemplate("system", P_CAP, "x"),
        )


def test_scope_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError):
        GovernedContextualRuleInstantiator().instantiate(
            spec=spec(), bindings=bindings(), scope_reference="session-b"
        )


def test_same_input_has_same_fingerprint() -> None:
    assert instantiate().source_fingerprint == instantiate().source_fingerprint


def test_binding_change_changes_fingerprint_and_subject() -> None:
    changed = list(bindings())
    changed[1] = ContextualRuleRoleBinding("resource", "sensor:U", "case:2", "sensor U")
    first = instantiate()
    second = instantiate(tuple(changed))
    assert first.source_fingerprint != second.source_fingerprint
    assert second.concrete_conditions[1].subject == "sensor:U"


def test_abstract_spec_is_not_mutated() -> None:
    template = spec()
    before = repr(template)
    GovernedContextualRuleInstantiator().instantiate(
        spec=template, bindings=bindings(), scope_reference=SCOPE
    )
    assert repr(template) == before


def test_candidate_is_frozen_and_non_authoritative() -> None:
    result = instantiate()
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


def test_candidate_schema_has_no_runtime_or_registry_handles() -> None:
    names = {field.name for field in fields(type(instantiate()))}
    assert "registry" not in names
    assert "inference_engine" not in names
    assert "repository" not in names
    assert "memory" not in names


def test_instantiation_does_not_claim_condition_satisfaction() -> None:
    result = instantiate()
    assert result.establishes_truth is False
    assert result.authorizes_inference is False
    assert result.registers_rule is False


def test_subject_is_not_encoded_into_predicate_identity() -> None:
    first = instantiate()
    changed = list(bindings())
    changed[1] = ContextualRuleRoleBinding("resource", "sensor:U", "case:2", "sensor U")
    second = instantiate(tuple(changed))
    assert first.concrete_conditions[1].predicate_id == P_AVAIL
    assert second.concrete_conditions[1].predicate_id == P_AVAIL


def test_cross_domain_binding_preserves_structure() -> None:
    other = (
        ContextualRuleRoleBinding("system", "Lucia", "case:10", "Lucía"),
        ContextualRuleRoleBinding("resource", "notebook", "case:11", "cuaderno"),
        ContextualRuleRoleBinding(
            "capability", "combinations", "case:12", "combinaciones"
        ),
    )
    result = instantiate(other)
    assert result.status is ContextualRuleInstantiationStatus.INSTANTIATED
    assert result.concrete_conditions[1].subject == "notebook"
    assert result.concrete_conditions[1].predicate_id == P_AVAIL
    assert result.concrete_conclusion is not None
    assert result.concrete_conclusion.subject == "Lucia"


def test_role_count_is_bounded() -> None:
    with pytest.raises(ValueError):
        ContextualRuleInstantiationSpec(
            rule_candidate_id="rule:x",
            scope_reference=SCOPE,
            vocabulary_id=VOCAB,
            source_reference=SOURCE,
            roles=("a", "b", "c", "d", "e"),
            conditions=(ContextualRuleConditionTemplate("a", P_AVAIL, "x"),),
            conclusion=ContextualRuleConclusionTemplate("a", P_CAP, "x"),
        )
