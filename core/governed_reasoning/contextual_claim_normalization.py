from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.contextual_predicate_vocabulary import (
    TemporaryContextualPredicateVocabulary,
)

_SCHEMA_VERSION = "post-m409.1-contextual-claim-normalization-v1"
_EPISTEMIC_UNCERTAINTY_MARKERS = (
    "no sabemos",
    "no se sabe",
    "se desconoce",
    "desconocemos",
    "sin evidencia",
    "no tenemos evidencia",
    "no hay evidencia",
    "quizás",
    "quiza",
    "quizá",
    "posiblemente",
    "tal vez",
    "creo que",
)


class ContextualClaimNormalizationStatus(StrEnum):
    CANDIDATE = "candidate"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class GovernedContextualClaimCandidate:
    status: ContextualClaimNormalizationStatus
    subject: str | None
    predicate_id: str | None
    object_value: str | None
    source_text: str
    predicate_phrase: str
    source_reference: str
    scope_reference: str
    vocabulary_id: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    authorizes_inference: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.source_text.strip() or not self.predicate_phrase.strip():
            raise ValueError("contextual claim candidate requires explicit source text")
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError("contextual claim candidate requires scope and provenance")
        if not self.vocabulary_id.startswith("ctx-vocabulary-"):
            raise ValueError("contextual claim candidate vocabulary is invalid")
        if not self.source_fingerprint.strip():
            raise ValueError("contextual claim candidate requires fingerprint")
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError("contextual claim normalization schema is invalid")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "contextual claim candidate must preserve reasoning authority"
            )
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists_results,
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.establishes_truth,
                self.establishes_falsity,
                self.authorizes_inference,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("contextual claim candidate violates governed limits")
        if self.status is ContextualClaimNormalizationStatus.CANDIDATE:
            if not self.subject or not self.subject.strip():
                raise ValueError("factual claim candidate requires explicit subject")
            if self.predicate_id is None or self.object_value is None:
                raise ValueError("factual claim candidate requires predicate and value")
        elif self.predicate_id is not None or self.object_value is not None:
            raise ValueError(
                "non-candidate normalization cannot expose factual mapping"
            )


class GovernedContextualClaimNormalizer:
    """Normalize an explicitly delimited proposition through a closed vocabulary."""

    def normalize(
        self,
        *,
        source_text: str,
        subject: str | None,
        predicate_phrase: str,
        vocabulary: TemporaryContextualPredicateVocabulary,
        source_reference: str,
        scope_reference: str,
    ) -> GovernedContextualClaimCandidate:
        self._validate_inputs(
            source_text=source_text,
            predicate_phrase=predicate_phrase,
            source_reference=source_reference,
            scope_reference=scope_reference,
            vocabulary=vocabulary,
        )
        normalized_source = source_text.strip().casefold()
        normalized_phrase = predicate_phrase.strip().casefold()
        if any(
            marker in normalized_source
            for marker in _EPISTEMIC_UNCERTAINTY_MARKERS
        ):
            return self._result(
                status=ContextualClaimNormalizationStatus.UNSUPPORTED,
                subject=None,
                predicate_id=None,
                object_value=None,
                source_text=source_text,
                predicate_phrase=predicate_phrase,
                source_reference=source_reference,
                scope_reference=scope_reference,
                vocabulary=vocabulary,
                rationale_codes=("claim_normalization:epistemic_uncertainty_not_fact",),
            )
        if subject is None or not subject.strip():
            return self._result(
                status=ContextualClaimNormalizationStatus.AMBIGUOUS,
                subject=None,
                predicate_id=None,
                object_value=None,
                source_text=source_text,
                predicate_phrase=predicate_phrase,
                source_reference=source_reference,
                scope_reference=scope_reference,
                vocabulary=vocabulary,
                rationale_codes=("claim_normalization:explicit_subject_required",),
            )

        matches: list[tuple[str, str]] = []
        for entry in vocabulary.entries:
            value = entry.resolve_alias(normalized_phrase)
            if value is not None:
                matches.append((entry.predicate_id, value))
        if not matches:
            return self._result(
                status=ContextualClaimNormalizationStatus.UNSUPPORTED,
                subject=None,
                predicate_id=None,
                object_value=None,
                source_text=source_text,
                predicate_phrase=predicate_phrase,
                source_reference=source_reference,
                scope_reference=scope_reference,
                vocabulary=vocabulary,
                rationale_codes=("claim_normalization:predicate_phrase_not_certified",),
            )
        if len(matches) != 1:
            return self._result(
                status=ContextualClaimNormalizationStatus.AMBIGUOUS,
                subject=None,
                predicate_id=None,
                object_value=None,
                source_text=source_text,
                predicate_phrase=predicate_phrase,
                source_reference=source_reference,
                scope_reference=scope_reference,
                vocabulary=vocabulary,
                rationale_codes=("claim_normalization:multiple_predicate_matches",),
            )
        predicate_id, object_value = matches[0]
        return self._result(
            status=ContextualClaimNormalizationStatus.CANDIDATE,
            subject=subject.strip(),
            predicate_id=predicate_id,
            object_value=object_value,
            source_text=source_text,
            predicate_phrase=predicate_phrase,
            source_reference=source_reference,
            scope_reference=scope_reference,
            vocabulary=vocabulary,
            rationale_codes=("claim_normalization:certified_contextual_alias",),
        )

    @staticmethod
    def _validate_inputs(
        *,
        source_text: str,
        predicate_phrase: str,
        source_reference: str,
        scope_reference: str,
        vocabulary: TemporaryContextualPredicateVocabulary,
    ) -> None:
        if not source_text.strip() or not predicate_phrase.strip():
            raise ValueError(
                "contextual claim normalization requires explicit proposition"
            )
        if not source_reference.strip() or not scope_reference.strip():
            raise ValueError(
                "contextual claim normalization requires scope and provenance"
            )
        if vocabulary.scope_reference != scope_reference:
            raise ValueError("contextual claim normalization scope mismatch")

    @staticmethod
    def _result(
        *,
        status: ContextualClaimNormalizationStatus,
        subject: str | None,
        predicate_id: str | None,
        object_value: str | None,
        source_text: str,
        predicate_phrase: str,
        source_reference: str,
        scope_reference: str,
        vocabulary: TemporaryContextualPredicateVocabulary,
        rationale_codes: tuple[str, ...],
    ) -> GovernedContextualClaimCandidate:
        payload = (
            _SCHEMA_VERSION,
            status.value,
            subject,
            predicate_id,
            object_value,
            source_text,
            predicate_phrase,
            source_reference,
            scope_reference,
            vocabulary.vocabulary_id,
            rationale_codes,
        )
        fingerprint = sha256(repr(payload).encode("utf-8")).hexdigest()
        return GovernedContextualClaimCandidate(
            status=status,
            subject=subject,
            predicate_id=predicate_id,
            object_value=object_value,
            source_text=source_text,
            predicate_phrase=predicate_phrase,
            source_reference=source_reference,
            scope_reference=scope_reference,
            vocabulary_id=vocabulary.vocabulary_id,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
