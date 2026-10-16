from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

_RESERVED_EPISTEMIC_VALUES = frozenset(
    {
        "unknown",
        "indeterminate",
        "insufficient",
        "insufficient_information",
    }
)
_SCHEMA_VERSION = "post-m409.1-contextual-predicate-vocabulary-v1"
_EPISTEMIC_UNCERTAINTY_MARKERS = (
    "no sabemos",
    "no se sabe",
    "se desconoce",
    "desconocemos",
    "sin evidencia",
    "no tenemos evidencia",
    "no hay evidencia",
)


@dataclass(frozen=True)
class ContextualPredicateAlias:
    term: str
    value: str

    def __post_init__(self) -> None:
        if not self.term.strip() or not self.value.strip():
            raise ValueError("contextual predicate alias must not be blank")


@dataclass(frozen=True)
class TemporaryContextualPredicateEntrySpec:
    label: str
    allowed_values: tuple[str, ...]
    aliases: tuple[ContextualPredicateAlias, ...]
    source_reference: str

    def __post_init__(self) -> None:
        if not self.label.strip() or not self.source_reference.strip():
            raise ValueError("contextual predicate entry requires label and provenance")
        _validate_values(self.allowed_values)
        if not self.aliases:
            raise ValueError("contextual predicate entry requires certified aliases")
        seen_terms: set[str] = set()
        for alias in self.aliases:
            if alias.value not in self.allowed_values:
                raise ValueError(
                    "contextual predicate alias value is outside its domain"
                )
            identity = alias.term.strip().casefold()
            if any(marker in identity for marker in _EPISTEMIC_UNCERTAINTY_MARKERS):
                raise ValueError(
                    "epistemic uncertainty cannot become a factual predicate alias"
                )
            if identity in seen_terms:
                raise ValueError("contextual predicate aliases must be unambiguous")
            seen_terms.add(identity)


@dataclass(frozen=True)
class TemporaryContextualPredicateEntry:
    predicate_id: str
    label: str
    allowed_values: tuple[str, ...]
    aliases: tuple[ContextualPredicateAlias, ...]
    source_reference: str
    source_fingerprint: str

    def __post_init__(self) -> None:
        if not self.predicate_id.startswith("ctx-predicate-"):
            raise ValueError("contextual predicate identifier is invalid")
        if not self.source_fingerprint.strip():
            raise ValueError("contextual predicate entry requires fingerprint")
        TemporaryContextualPredicateEntrySpec(
            label=self.label,
            allowed_values=self.allowed_values,
            aliases=self.aliases,
            source_reference=self.source_reference,
        )

    def resolve_alias(self, term: str) -> str | None:
        identity = term.strip().casefold()
        for alias in self.aliases:
            if alias.term.strip().casefold() == identity:
                return alias.value
        return None


@dataclass(frozen=True)
class TemporaryContextualPredicateVocabulary:
    vocabulary_id: str
    scope_reference: str
    source_reference: str
    entries: tuple[TemporaryContextualPredicateEntry, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    contextual: bool = True
    temporary: bool = True
    session_local: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    modifies_global_vocabulary: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.vocabulary_id.startswith("ctx-vocabulary-"):
            raise ValueError("contextual vocabulary identifier is invalid")
        if not self.scope_reference.strip() or not self.source_reference.strip():
            raise ValueError("contextual vocabulary requires scope and provenance")
        if not 1 <= len(self.entries) <= 8:
            raise ValueError(
                "contextual vocabulary supports between one and eight entries"
            )
        if not self.source_fingerprint.strip():
            raise ValueError("contextual vocabulary requires fingerprint")
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError("contextual vocabulary schema version is invalid")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("contextual vocabulary must preserve reasoning authority")
        if any(
            (
                not self.read_only,
                not self.contextual,
                not self.temporary,
                not self.session_local,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.modifies_global_vocabulary,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("contextual vocabulary violates governed limits")
        predicate_ids = tuple(entry.predicate_id for entry in self.entries)
        labels = tuple(entry.label.strip().casefold() for entry in self.entries)
        if len(set(labels)) != len(labels):
            raise ValueError("contextual predicate labels must be unique")
        if len(set(predicate_ids)) != len(predicate_ids):
            raise ValueError("contextual predicate identifiers must be unique")

    def entry_by_label(self, label: str) -> TemporaryContextualPredicateEntry | None:
        identity = label.strip().casefold()
        for entry in self.entries:
            if entry.label.strip().casefold() == identity:
                return entry
        return None


class TemporaryContextualPredicateVocabularyFactory:
    """Build a closed, deterministic, session-local predicate vocabulary only."""

    def build(
        self,
        *,
        scope_reference: str,
        source_reference: str,
        entries: tuple[TemporaryContextualPredicateEntrySpec, ...],
    ) -> TemporaryContextualPredicateVocabulary:
        if not scope_reference.strip() or not source_reference.strip():
            raise ValueError("contextual vocabulary requires scope and provenance")
        if not 1 <= len(entries) <= 8:
            raise ValueError(
                "contextual vocabulary supports between one and eight entries"
            )

        built = tuple(
            self._build_entry(
                scope_reference=scope_reference,
                vocabulary_source_reference=source_reference,
                spec=spec,
            )
            for spec in entries
        )
        identity_payload = (
            _SCHEMA_VERSION,
            scope_reference,
            source_reference,
            tuple(
                (
                    item.predicate_id,
                    item.label,
                    item.allowed_values,
                    tuple((alias.term, alias.value) for alias in item.aliases),
                    item.source_reference,
                    item.source_fingerprint,
                )
                for item in built
            ),
        )
        fingerprint = sha256(repr(identity_payload).encode("utf-8")).hexdigest()
        return TemporaryContextualPredicateVocabulary(
            vocabulary_id=f"ctx-vocabulary-{fingerprint[:16]}",
            scope_reference=scope_reference,
            source_reference=source_reference,
            entries=built,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _build_entry(
        *,
        scope_reference: str,
        vocabulary_source_reference: str,
        spec: TemporaryContextualPredicateEntrySpec,
    ) -> TemporaryContextualPredicateEntry:
        predicate_identity = (
            _SCHEMA_VERSION,
            scope_reference,
            spec.label.strip().casefold(),
        )
        predicate_fingerprint = sha256(
            repr(predicate_identity).encode("utf-8")
        ).hexdigest()
        identity_payload = (
            _SCHEMA_VERSION,
            scope_reference,
            vocabulary_source_reference,
            spec.label,
            spec.allowed_values,
            tuple((alias.term, alias.value) for alias in spec.aliases),
            spec.source_reference,
        )
        fingerprint = sha256(repr(identity_payload).encode("utf-8")).hexdigest()
        return TemporaryContextualPredicateEntry(
            predicate_id=f"ctx-predicate-{predicate_fingerprint[:16]}",
            label=spec.label,
            allowed_values=spec.allowed_values,
            aliases=spec.aliases,
            source_reference=spec.source_reference,
            source_fingerprint=fingerprint,
        )


def _validate_values(values: tuple[str, ...]) -> None:
    if not 1 <= len(values) <= 4:
        raise ValueError("contextual predicate supports between one and four values")
    if any(not value.strip() for value in values):
        raise ValueError("contextual predicate values must not be blank")
    normalized = tuple(value.strip().casefold() for value in values)
    if len(set(normalized)) != len(normalized):
        raise ValueError("contextual predicate values must be unique")
    if any(value in _RESERVED_EPISTEMIC_VALUES for value in normalized):
        raise ValueError("epistemic unknown cannot be an ordinary predicate value")
