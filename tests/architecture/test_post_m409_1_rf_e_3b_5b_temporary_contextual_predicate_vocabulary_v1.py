from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.governed_reasoning import (
    ContextualPredicateAlias,
    TemporaryContextualPredicateEntrySpec,
    TemporaryContextualPredicateVocabularyFactory,
)


def test_builds_closed_session_local_vocabulary() -> None:
    vocabulary = _build()
    assert vocabulary.canonical_authority == "governed_reasoning"
    assert vocabulary.read_only is True
    assert vocabulary.contextual is True
    assert vocabulary.temporary is True
    assert vocabulary.session_local is True
    assert vocabulary.persists_results is False
    assert vocabulary.creates_memory is False
    assert vocabulary.creates_learning_candidate is False
    assert vocabulary.modifies_world_model is False
    assert vocabulary.modifies_global_vocabulary is False
    assert vocabulary.executes_actions is False
    assert vocabulary.grants_authority is False


def test_vocabulary_and_entries_are_immutable() -> None:
    vocabulary = _build()
    with pytest.raises(FrozenInstanceError):
        vocabulary.scope_reference = "session:B"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        vocabulary.entries[0].label = "changed"  # type: ignore[misc]


def test_same_input_produces_same_ids_and_fingerprint() -> None:
    assert _build() == _build()


def test_different_scope_does_not_gain_cross_session_semantic_identity() -> None:
    left = _build(scope="session:A")
    right = _build(scope="session:B")
    assert left.vocabulary_id != right.vocabulary_id
    assert left.entries[0].predicate_id != right.entries[0].predicate_id


def test_same_predicate_entry_resolves_only_certified_aliases() -> None:
    entry = _build().entry_by_label("resource_availability")
    assert entry is not None
    assert entry.resolve_alias("está indisponible") == "unavailable"
    assert entry.resolve_alias("ESTÁ DISPONIBLE") == "available"
    assert entry.resolve_alias("dejó de responder") is None


def test_unknown_relation_does_not_expand_vocabulary() -> None:
    vocabulary = _build()
    before = vocabulary.entries
    assert vocabulary.entry_by_label("new_relation") is None
    assert vocabulary.entries == before


def test_unknown_cannot_be_an_ordinary_predicate_value() -> None:
    with pytest.raises(ValueError, match="unknown cannot be an ordinary"):
        _spec(values=("true", "unknown"))


def test_indeterminate_cannot_be_an_ordinary_predicate_value() -> None:
    with pytest.raises(ValueError, match="unknown cannot be an ordinary"):
        _spec(values=("true", "indeterminate"))


def test_epistemically_uncertain_phrase_cannot_be_factual_alias() -> None:
    with pytest.raises(ValueError, match="epistemic uncertainty"):
        _spec(
            aliases=(
                ContextualPredicateAlias(
                    "no sabemos si existe alternativa",
                    "false",
                ),
            ),
            values=("true", "false"),
        )


def test_alias_value_must_belong_to_declared_domain() -> None:
    with pytest.raises(ValueError, match="outside its domain"):
        _spec(
            aliases=(ContextualPredicateAlias("está roto", "broken"),),
        )


def test_duplicate_alias_terms_fail_closed() -> None:
    with pytest.raises(ValueError, match="aliases must be unambiguous"):
        _spec(
            aliases=(
                ContextualPredicateAlias("Disponible", "available"),
                ContextualPredicateAlias("disponible", "unavailable"),
            ),
        )


def test_duplicate_predicate_labels_fail_closed() -> None:
    spec = _spec()
    with pytest.raises(ValueError, match="labels must be unique"):
        TemporaryContextualPredicateVocabularyFactory().build(
            scope_reference="session:A",
            source_reference="turn:1",
            entries=(spec, spec),
        )


def test_predicate_supports_at_most_four_values() -> None:
    with pytest.raises(ValueError, match="one and four values"):
        _spec(values=("a", "b", "c", "d", "e"))


def test_vocabulary_supports_at_most_eight_entries() -> None:
    entries = tuple(
        _spec(label=f"predicate_{index}", source=f"turn:{index}")
        for index in range(9)
    )
    with pytest.raises(ValueError, match="one and eight entries"):
        TemporaryContextualPredicateVocabularyFactory().build(
            scope_reference="session:A",
            source_reference="turn:root",
            entries=entries,
        )


def test_blank_scope_or_provenance_is_rejected() -> None:
    factory = TemporaryContextualPredicateVocabularyFactory()
    with pytest.raises(ValueError, match="scope and provenance"):
        factory.build(
            scope_reference=" ",
            source_reference="turn:1",
            entries=(_spec(),),
        )


def test_predicate_identity_is_not_subject_identity() -> None:
    vocabulary = _build()
    entry = vocabulary.entry_by_label("resource_availability")
    assert entry is not None
    assert "sensor" not in entry.predicate_id
    assert "T" not in entry.predicate_id
    assert "U" not in entry.predicate_id


def _build(*, scope: str = "session:A"):
    return TemporaryContextualPredicateVocabularyFactory().build(
        scope_reference=scope,
        source_reference="turn:rule",
        entries=(
            _spec(),
            _spec(
                label="alternative_exists",
                values=("true", "false"),
                aliases=(
                    ContextualPredicateAlias("existe alternativa", "true"),
                    ContextualPredicateAlias("no existe alternativa", "false"),
                ),
                source="turn:rule:alternative",
            ),
        ),
    )


def _spec(
    *,
    label: str = "resource_availability",
    values: tuple[str, ...] = ("available", "unavailable"),
    aliases: tuple[ContextualPredicateAlias, ...] | None = None,
    source: str = "turn:rule:availability",
) -> TemporaryContextualPredicateEntrySpec:
    if aliases is None:
        aliases = (
            ContextualPredicateAlias("está disponible", "available"),
            ContextualPredicateAlias("está indisponible", "unavailable"),
        )
    return TemporaryContextualPredicateEntrySpec(
        label=label,
        allowed_values=values,
        aliases=aliases,
        source_reference=source,
    )
