from dataclasses import FrozenInstanceError, fields

import pytest

from core.governed_reasoning import (
    ContextualClaimNormalizationStatus,
    ContextualPredicateAlias,
    GovernedContextualClaimNormalizer,
    TemporaryContextualPredicateEntrySpec,
    TemporaryContextualPredicateVocabularyFactory,
)

NORMALIZER = GovernedContextualClaimNormalizer()
SCOPE = "session:A"
SOURCE = "turn:case"


def test_certified_alias_produces_semantic_claim_candidate() -> None:
    vocabulary = _vocabulary()
    result = _normalize(
        vocabulary,
        source_text="El sensor T está indisponible.",
        subject="sensor:T",
        phrase="está indisponible",
    )
    entry = vocabulary.entry_by_label("resource_availability")
    assert entry is not None
    assert result.status is ContextualClaimNormalizationStatus.CANDIDATE
    assert result.subject == "sensor:T"
    assert result.predicate_id == entry.predicate_id
    assert result.object_value == "unavailable"


def test_available_alias_maps_to_other_allowed_value() -> None:
    result = _normalize(
        _vocabulary(),
        source_text="El sensor T está disponible.",
        subject="sensor:T",
        phrase="está disponible",
    )
    assert result.object_value == "available"


def test_explicit_negative_alternative_can_be_factual_candidate() -> None:
    result = _normalize(
        _vocabulary(),
        source_text="La estación no tiene alternativa.",
        subject="station:1:temperature",
        phrase="no existe alternativa",
    )
    assert result.status is ContextualClaimNormalizationStatus.CANDIDATE
    assert result.object_value == "false"


def test_unknown_alternative_is_never_promoted_to_negative_fact() -> None:
    result = _normalize(
        _vocabulary(),
        source_text="No sabemos si existe alternativa.",
        subject="station:1:temperature",
        phrase="no existe alternativa",
    )
    assert result.status is ContextualClaimNormalizationStatus.UNSUPPORTED
    assert result.predicate_id is None
    assert result.object_value is None
    assert "epistemic_uncertainty_not_fact" in result.rationale_codes[0]


@pytest.mark.parametrize(
    "text",
    (
        "Se desconoce si existe alternativa.",
        "No tenemos evidencia de una alternativa.",
        "Quizás exista alternativa.",
        "Creo que T está disponible.",
    ),
)
def test_epistemically_qualified_statement_does_not_become_fact(text: str) -> None:
    result = _normalize(
        _vocabulary(),
        source_text=text,
        subject="station:1",
        phrase="existe alternativa",
    )
    assert result.status is ContextualClaimNormalizationStatus.UNSUPPORTED
    assert result.predicate_id is None


def test_missing_explicit_subject_is_ambiguous() -> None:
    result = _normalize(
        _vocabulary(),
        source_text="Está disponible.",
        subject=None,
        phrase="está disponible",
    )
    assert result.status is ContextualClaimNormalizationStatus.AMBIGUOUS
    assert result.predicate_id is None


def test_uncertified_phrase_is_unsupported_without_vocabulary_expansion() -> None:
    vocabulary = _vocabulary()
    before = vocabulary.entries
    result = _normalize(
        vocabulary,
        source_text="El sensor T dejó de responder.",
        subject="sensor:T",
        phrase="dejó de responder",
    )
    assert result.status is ContextualClaimNormalizationStatus.UNSUPPORTED
    assert vocabulary.entries == before


def test_scope_mismatch_fails_closed() -> None:
    with pytest.raises(ValueError, match="scope mismatch"):
        NORMALIZER.normalize(
            source_text="T está disponible.",
            subject="sensor:T",
            predicate_phrase="está disponible",
            vocabulary=_vocabulary(),
            source_reference=SOURCE,
            scope_reference="session:B",
        )


def test_same_input_is_deterministic() -> None:
    vocabulary = _vocabulary()
    first = _normalize(
        vocabulary,
        source_text="T está disponible.",
        subject="sensor:T",
        phrase="está disponible",
    )
    second = _normalize(
        vocabulary,
        source_text="T está disponible.",
        subject="sensor:T",
        phrase="está disponible",
    )
    assert first == second


def test_subject_identity_is_preserved_without_entering_predicate_id() -> None:
    vocabulary = _vocabulary()
    left = _normalize(
        vocabulary,
        source_text="T está indisponible.",
        subject="sensor:T",
        phrase="está indisponible",
    )
    right = _normalize(
        vocabulary,
        source_text="U está indisponible.",
        subject="sensor:U",
        phrase="está indisponible",
    )
    assert left.predicate_id == right.predicate_id
    assert left.subject != right.subject
    assert "sensor" not in (left.predicate_id or "")


def test_candidate_is_frozen_read_only_and_non_authoritative() -> None:
    result = _normalize(
        _vocabulary(),
        source_text="T está disponible.",
        subject="sensor:T",
        phrase="está disponible",
    )
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
        "executes_actions",
        "grants_authority",
    ):
        assert getattr(result, name) is False
    with pytest.raises(FrozenInstanceError):
        result.subject = "changed"  # type: ignore[misc]


def test_candidate_schema_contains_no_claim_registry_or_runtime_handles() -> None:
    result = _normalize(
        _vocabulary(),
        source_text="T está disponible.",
        subject="sensor:T",
        phrase="está disponible",
    )
    names = {field.name for field in fields(type(result))}
    assert "registry" not in names
    assert "repository" not in names
    assert "inference_engine" not in names
    assert "memory" not in names


def test_normalizer_does_not_create_governed_claim() -> None:
    result = _normalize(
        _vocabulary(),
        source_text="T está disponible.",
        subject="sensor:T",
        phrase="está disponible",
    )
    assert type(result).__name__ == "GovernedContextualClaimCandidate"
    assert not hasattr(result, "claim_id")


def test_same_alias_in_two_predicates_is_ambiguous() -> None:
    vocabulary = TemporaryContextualPredicateVocabularyFactory().build(
        scope_reference=SCOPE,
        source_reference="turn:rule",
        entries=(
            _spec("state_a", ("on",), "activo", "on"),
            _spec("state_b", ("yes",), "activo", "yes"),
        ),
    )
    result = _normalize(
        vocabulary,
        source_text="T está activo.",
        subject="sensor:T",
        phrase="activo",
    )
    assert result.status is ContextualClaimNormalizationStatus.AMBIGUOUS
    assert result.predicate_id is None


def _normalize(vocabulary, *, source_text: str, subject: str | None, phrase: str):
    return NORMALIZER.normalize(
        source_text=source_text,
        subject=subject,
        predicate_phrase=phrase,
        vocabulary=vocabulary,
        source_reference=SOURCE,
        scope_reference=SCOPE,
    )


def _vocabulary():
    return TemporaryContextualPredicateVocabularyFactory().build(
        scope_reference=SCOPE,
        source_reference="turn:rule",
        entries=(
            TemporaryContextualPredicateEntrySpec(
                label="resource_availability",
                allowed_values=("available", "unavailable"),
                aliases=(
                    ContextualPredicateAlias("está disponible", "available"),
                    ContextualPredicateAlias("está indisponible", "unavailable"),
                ),
                source_reference="turn:rule:availability",
            ),
            TemporaryContextualPredicateEntrySpec(
                label="alternative_exists",
                allowed_values=("true", "false"),
                aliases=(
                    ContextualPredicateAlias("existe alternativa", "true"),
                    ContextualPredicateAlias("no existe alternativa", "false"),
                ),
                source_reference="turn:rule:alternative",
            ),
        ),
    )


def _spec(label: str, values: tuple[str, ...], term: str, value: str):
    return TemporaryContextualPredicateEntrySpec(
        label=label,
        allowed_values=values,
        aliases=(ContextualPredicateAlias(term, value),),
        source_reference=f"turn:rule:{label}",
    )
