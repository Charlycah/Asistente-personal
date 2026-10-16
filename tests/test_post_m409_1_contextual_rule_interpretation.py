from dataclasses import FrozenInstanceError, fields

import pytest

from core.governed_reasoning.contextual_rule_interpretation import (
    ContextualRuleCandidateStatus,
    GovernedContextualRuleInterpretationProducer,
)

PRODUCER = GovernedContextualRuleInterpretationProducer()
SOURCE = "conversation:session-a/turn-1"
SCOPE = "session-a"


def produce(text: str):
    return PRODUCER.produce(
        text,
        source_reference=SOURCE,
        scope_reference=SCOPE,
    )


def test_simple_explicit_rule_produces_candidate() -> None:
    result = produce("Usá esta regla: si A ocurre, entonces B ocurre.")

    assert result.normalized_status is ContextualRuleCandidateStatus.CANDIDATE
    assert [item.normalized_text for item in result.conditions] == ["A ocurre"]
    assert result.conclusion is not None
    assert result.conclusion.normalized_text == "B ocurre"


def test_multiple_and_conditions_are_bounded_and_ordered() -> None:
    result = produce(
        "Regla temporal: si A ocurre y B está disponible, entonces C ocurre."
    )

    assert [item.normalized_text for item in result.conditions] == [
        "A ocurre",
        "B está disponible",
    ]


def test_rule_source_span_matches_original_text_exactly() -> None:
    text = "Prefacio. Usá esta regla:   si A ocurre, entonces B ocurre."
    result = produce(text)

    assert result.rule_source_text
    assert (
        text[result.rule_start_offset : result.rule_end_offset]
        == result.rule_source_text
    )


def test_ordinary_conditional_is_not_promoted_to_rule() -> None:
    result = produce("Si mañana llueve, entonces Juan lleva paraguas.")

    assert result.normalized_status is ContextualRuleCandidateStatus.NOT_RULE
    assert result.conditions == ()
    assert result.conclusion is None


def test_or_operator_is_unsupported_not_simplified() -> None:
    result = produce("Usá esta regla: si A o B, entonces C.")

    assert result.normalized_status is ContextualRuleCandidateStatus.UNSUPPORTED


@pytest.mark.parametrize("token", ["salvo", "excepto", "a menos que", "si y solo si"])
def test_exception_and_biconditional_operators_are_unsupported(token: str) -> None:
    result = produce(f"Usá esta regla: si A {token} B, entonces C.")

    assert result.normalized_status is ContextualRuleCandidateStatus.UNSUPPORTED


def test_missing_then_is_unsupported_in_v1() -> None:
    result = produce("Usá esta regla: si A ocurre, B ocurre.")

    assert result.normalized_status is ContextualRuleCandidateStatus.UNSUPPORTED


def test_compound_conclusion_is_ambiguous_in_v1() -> None:
    result = produce("Usá esta regla: si A ocurre, entonces B ocurre y C ocurre.")

    assert result.normalized_status is ContextualRuleCandidateStatus.AMBIGUOUS


def test_more_than_four_conditions_is_unsupported() -> None:
    result = produce("Usá esta regla: si A y B y C y D y E, entonces F.")

    assert result.normalized_status is ContextualRuleCandidateStatus.UNSUPPORTED


def test_explicit_negation_is_preserved_without_logical_rewrite() -> None:
    result = produce(
        "Regla temporal: si A no está disponible, entonces B no puede operar."
    )

    assert result.conditions[0].negated is True
    assert result.conclusion is not None
    assert result.conclusion.negated is True


def test_fingerprint_is_deterministic_and_scope_sensitive() -> None:
    text = "Usá esta regla: si A ocurre, entonces B ocurre."
    first = produce(text)
    second = produce(text)
    other_scope = PRODUCER.produce(
        text,
        source_reference=SOURCE,
        scope_reference="session-b",
    )

    assert first.source_fingerprint == second.source_fingerprint
    assert first.source_fingerprint != other_scope.source_fingerprint


def test_candidate_is_frozen_read_only_and_non_authoritative() -> None:
    result = produce("Usá esta regla: si A ocurre, entonces B ocurre.")

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
        "authorizes_action",
        "executes_actions",
        "grants_authority",
    ):
        assert getattr(result, name) is False
    with pytest.raises(FrozenInstanceError):
        result.scope_reference = "changed"  # type: ignore[misc]


def test_candidate_schema_contains_no_runtime_or_persistence_handles() -> None:
    result_type = type(produce("Usá esta regla: si A, entonces B."))
    names = {field.name for field in fields(result_type)}

    assert "repository" not in names
    assert "memory" not in names
    assert "registry" not in names
    assert "inference_engine" not in names


def test_actual_neral_wording_uses_bounded_compatibility_grammar() -> None:
    result = produce(
        "Para este diagnóstico aprende esta regla artificial llamada Principio "
        "Neral: si un sistema depende exclusivamente de un único recurso para "
        "una capacidad, y ese recurso queda indisponible, el sistema pierde esa "
        "capacidad mientras no exista una alternativa."
    )

    assert result.normalized_status is ContextualRuleCandidateStatus.CANDIDATE
    assert [item.normalized_text for item in result.conditions] == [
        "un sistema depende exclusivamente de un único recurso para una capacidad",
        "ese recurso queda indisponible",
        "no exista una alternativa",
    ]
    assert result.conclusion is not None
    assert result.conclusion.normalized_text == "el sistema pierde esa capacidad"
    assert "grammar:bounded_postcondition_v1" in result.rationale_codes


def test_prefix_named_principle_can_produce_bounded_candidate() -> None:
    result = produce("Principio Neral: si A ocurre y B ocurre, entonces C ocurre.")

    assert result.normalized_status is ContextualRuleCandidateStatus.CANDIDATE
    assert len(result.conditions) == 2


def test_bounded_compatibility_rule_span_excludes_trailing_comment() -> None:
    text = (
        "Para este diagnóstico aprende esta regla artificial llamada Principio "
        "Neral: si un sistema depende exclusivamente de un único recurso para "
        "una capacidad, y ese recurso queda indisponible, el sistema pierde esa "
        "capacidad mientras no exista una alternativa. No la trates como una "
        "regla sobre servidores: es una relación general de dependencia exclusiva."
    )
    result = produce(text)

    assert result.normalized_status is ContextualRuleCandidateStatus.CANDIDATE
    assert result.rule_source_text.endswith("no exista una alternativa.")
    assert "No la trates" not in result.rule_source_text
    assert (
        text[result.rule_start_offset : result.rule_end_offset]
        == result.rule_source_text
    )


@pytest.mark.parametrize(
    "text",
    [
        "Usá esta regla: si A ocurre, B ocurre.",
        "Usá esta regla: si A ocurre, probablemente B ocurre mientras no "
        "exista alternativa.",
        "Usá esta regla: si A ocurre, B ocurre salvo que C.",
        "Usá esta regla: si A ocurre o B ocurre, C ocurre mientras no "
        "exista alternativa.",
    ],
)
def test_bounded_compatibility_does_not_relax_general_grammar(text: str) -> None:
    assert produce(text).normalized_status is ContextualRuleCandidateStatus.UNSUPPORTED
