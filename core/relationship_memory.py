from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.presence import PresenceSnapshot


class RelationshipMemoryKind(str, Enum):
    """Tipos de memoria de convivencia que ROBY puede conservar."""

    INTERACTION_PATTERN = "interaction_pattern"
    USER_PREFERENCE = "user_preference"
    PROJECT_RHYTHM = "project_rhythm"
    TRUST_SIGNAL = "trust_signal"
    BOUNDARY = "boundary"
    TRANSIENT = "transient"


class RelationshipMemoryAction(str, Enum):
    """Acción recomendada para un candidato de memoria relacional."""

    REMEMBER = "remember"
    REVIEW = "review"
    IGNORE = "ignore"


class RelationshipEvidenceKind(str, Enum):
    """Clase explícita de evidencia que puede respaldar una memoria relacional."""

    DECLARATION = "declaration"
    INTERACTION = "interaction"
    CORRECTION = "correction"
    BOUNDARY = "boundary"


class RelationshipConsolidationStatus(str, Enum):
    """Estado diagnóstico M393.3 de consolidación relacional."""

    CONSOLIDATED = "consolidated"
    REVIEW_REQUIRED = "review_required"
    CONFLICTED = "conflicted"
    UNSUPPORTED = "unsupported"


class RelationshipConsistencyIssueKind(str, Enum):
    """Clase explícita M393.4 de inconsistencia relacional."""

    EXACT_DUPLICATE = "exact_duplicate"
    EXPLICIT_CONTRADICTION = "explicit_contradiction"
    EXPLICIT_INCOMPATIBILITY = "explicit_incompatibility"


class RelationshipEvolutionStatus(str, Enum):
    """Estado diagnóstico M393.5 de evolución entre dos vistas relacionales."""

    ADDED = "added"
    REMOVED = "removed"
    UNCHANGED = "unchanged"
    CHANGED = "changed"


class RelationshipEvidenceValidation(str, Enum):
    """Estado declarado de validación de una evidencia relacional."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    REJECTED = "rejected"


@dataclass(frozen=True)
class RelationshipEvidenceReference:
    """Referencia explícita y auditable a evidencia relacional ya gobernada."""

    record_id: str
    evidence_ref: str
    kind: RelationshipEvidenceKind | str
    source_authority: str
    epistemic_level: str = "unknown"
    validation: RelationshipEvidenceValidation | str = (
        RelationshipEvidenceValidation.UNVERIFIED
    )
    observed_at: datetime | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        RelationshipEvidenceKind(self.kind)
        from core.cognitive_maturity.epistemic import EpistemicLevel

        EpistemicLevel(self.epistemic_level)
        RelationshipEvidenceValidation(self.validation)
        if not self.record_id.strip():
            raise ValueError("relationship evidence record_id must not be empty")
        if not self.evidence_ref.strip():
            raise ValueError("relationship evidence ref must not be empty")
        if not self.source_authority.strip():
            raise ValueError("relationship evidence source authority must not be empty")
        if self.observed_at is not None and self.observed_at.tzinfo is None:
            raise ValueError("relationship evidence timestamp must be timezone-aware")
        if any(not note.strip() for note in self.notes):
            raise ValueError("relationship evidence notes must not contain blanks")

    @property
    def normalized_kind(self) -> RelationshipEvidenceKind:
        return RelationshipEvidenceKind(self.kind)

    @property
    def normalized_epistemic_level(self):
        from core.cognitive_maturity.epistemic import EpistemicLevel

        return EpistemicLevel(self.epistemic_level)

    @property
    def normalized_validation(self) -> RelationshipEvidenceValidation:
        return RelationshipEvidenceValidation(self.validation)

    @property
    def support_weight(self) -> float:
        """Peso explicable del respaldo; no altera la confianza del registro fuente."""

        from core.cognitive_maturity.epistemic import EpistemicLevel

        if self.normalized_validation in {
            RelationshipEvidenceValidation.REJECTED,
            RelationshipEvidenceValidation.DISPUTED,
        }:
            return 0.0
        epistemic_weight = {
            EpistemicLevel.FACT: 1.0,
            EpistemicLevel.INFERENCE: 0.65,
            EpistemicLevel.HYPOTHESIS: 0.35,
            EpistemicLevel.UNKNOWN: 0.0,
        }[self.normalized_epistemic_level]
        validation_factor = (
            1.0
            if self.normalized_validation is RelationshipEvidenceValidation.VERIFIED
            else 0.5
        )
        return epistemic_weight * validation_factor


@dataclass(frozen=True)
class EnrichedRelationshipMemoryEntry:
    """Memoria relacional existente acompañada por evidencia explícita."""

    record: "RelationshipMemoryRecord"
    evidence: tuple[RelationshipEvidenceReference, ...] = ()

    @property
    def is_evidenced(self) -> bool:
        return bool(self.evidence)

    @property
    def evidence_support_score(self) -> float:
        """Respaldo agregado derivado sólo de evidencia explícitamente recibida."""

        if not self.evidence:
            return 0.0
        return sum(item.support_weight for item in self.evidence) / len(self.evidence)

    @property
    def has_verified_support(self) -> bool:
        return any(
            item.normalized_validation is RelationshipEvidenceValidation.VERIFIED
            and item.support_weight > 0.0
            for item in self.evidence
        )

    @property
    def has_conflicting_evidence(self) -> bool:
        return any(
            item.normalized_validation
            in {
                RelationshipEvidenceValidation.DISPUTED,
                RelationshipEvidenceValidation.REJECTED,
            }
            for item in self.evidence
        )


@dataclass(frozen=True)
class EnrichedRelationshipMemoryView:
    """Vista M393.1 de sólo lectura bajo la autoridad relationship_memory."""

    entries: tuple[EnrichedRelationshipMemoryEntry, ...]
    source_snapshot_id: str | None
    authority_id: str = "relationship_memory"

    @property
    def evidenced_entries(self) -> tuple[EnrichedRelationshipMemoryEntry, ...]:
        return tuple(entry for entry in self.entries if entry.is_evidenced)

    @property
    def review_required_record_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.record.record_id for entry in self.entries if not entry.is_evidenced
        )

    @property
    def verified_record_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.record.record_id
            for entry in self.entries
            if entry.has_verified_support
        )

    @property
    def conflicted_record_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.record.record_id
            for entry in self.entries
            if entry.has_conflicting_evidence
        )


@dataclass(frozen=True)
class ConsolidatedRelationshipEntry:
    """Diagnóstico inmutable de consolidación sobre una entrada M393.2."""

    source: EnrichedRelationshipMemoryEntry
    status: RelationshipConsolidationStatus
    rationale: str

    @property
    def record(self) -> "RelationshipMemoryRecord":
        return self.source.record

    @property
    def evidence_support_score(self) -> float:
        return self.source.evidence_support_score


@dataclass(frozen=True)
class RelationshipConsolidationView:
    """Vista diagnóstica M393.3 bajo la autoridad relationship_memory."""

    entries: tuple[ConsolidatedRelationshipEntry, ...]
    source_snapshot_id: str | None
    authority_id: str = "relationship_memory"

    @property
    def consolidated_record_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.record.record_id
            for entry in self.entries
            if entry.status is RelationshipConsolidationStatus.CONSOLIDATED
        )

    @property
    def review_required_record_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.record.record_id
            for entry in self.entries
            if entry.status is RelationshipConsolidationStatus.REVIEW_REQUIRED
        )

    @property
    def conflicted_record_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.record.record_id
            for entry in self.entries
            if entry.status is RelationshipConsolidationStatus.CONFLICTED
        )

    @property
    def unsupported_record_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.record.record_id
            for entry in self.entries
            if entry.status is RelationshipConsolidationStatus.UNSUPPORTED
        )


@dataclass(frozen=True)
class RelationshipConsistencyRelation:
    """Relación explícita entre registros para diagnóstico de consistencia."""

    source_record_id: str
    target_record_id: str
    kind: RelationshipConsistencyIssueKind | str
    evidence_ref: str

    def __post_init__(self) -> None:
        normalized = RelationshipConsistencyIssueKind(self.kind)
        if normalized is RelationshipConsistencyIssueKind.EXACT_DUPLICATE:
            raise ValueError("exact duplicates are detected from record content")
        if not self.source_record_id.strip() or not self.target_record_id.strip():
            raise ValueError("relationship consistency record ids must not be empty")
        if self.source_record_id == self.target_record_id:
            raise ValueError("relationship consistency relation requires two records")
        if not self.evidence_ref.strip():
            raise ValueError("relationship consistency evidence ref must not be empty")

    @property
    def normalized_kind(self) -> RelationshipConsistencyIssueKind:
        return RelationshipConsistencyIssueKind(self.kind)


@dataclass(frozen=True)
class RelationshipConsistencyIssue:
    """Inconsistencia observable sin resolución o reescritura automática."""

    kind: RelationshipConsistencyIssueKind
    record_ids: tuple[str, str]
    rationale: str
    evidence_ref: str | None = None


@dataclass(frozen=True)
class RelationshipConsistencyView:
    """Vista diagnóstica M393.4 bajo la autoridad relationship_memory."""

    consolidation: RelationshipConsolidationView
    issues: tuple[RelationshipConsistencyIssue, ...]
    authority_id: str = "relationship_memory"

    @property
    def source_snapshot_id(self) -> str | None:
        return self.consolidation.source_snapshot_id

    @property
    def is_consistent(self) -> bool:
        return not self.issues

    @property
    def inconsistent_record_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    record_id
                    for issue in self.issues
                    for record_id in issue.record_ids
                }
            )
        )

    @property
    def duplicate_record_ids(self) -> tuple[str, ...]:
        return self._record_ids_for(RelationshipConsistencyIssueKind.EXACT_DUPLICATE)

    @property
    def contradicted_record_ids(self) -> tuple[str, ...]:
        return self._record_ids_for(
            RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION
        )

    @property
    def incompatible_record_ids(self) -> tuple[str, ...]:
        return self._record_ids_for(
            RelationshipConsistencyIssueKind.EXPLICIT_INCOMPATIBILITY
        )

    def _record_ids_for(
        self, kind: RelationshipConsistencyIssueKind
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    record_id
                    for issue in self.issues
                    if issue.kind is kind
                    for record_id in issue.record_ids
                }
            )
        )


@dataclass(frozen=True)
class RelationshipEvolutionEntry:
    """Comparación inmutable de un registro entre dos estados relacionales."""

    record_id: str
    status: RelationshipEvolutionStatus
    previous: ConsolidatedRelationshipEntry | None
    current: ConsolidatedRelationshipEntry | None
    previous_issues: tuple[RelationshipConsistencyIssueKind, ...] = ()
    current_issues: tuple[RelationshipConsistencyIssueKind, ...] = ()

    @property
    def previous_record(self) -> "RelationshipMemoryRecord | None":
        return self.previous.record if self.previous is not None else None

    @property
    def current_record(self) -> "RelationshipMemoryRecord | None":
        return self.current.record if self.current is not None else None


@dataclass(frozen=True)
class RelationshipEvolutionView:
    """Vista M393.5 de evolución explícita bajo relationship_memory."""

    entries: tuple[RelationshipEvolutionEntry, ...]
    previous_snapshot_id: str | None
    current_snapshot_id: str | None
    authority_id: str = "relationship_memory"

    def record_ids_for(
        self, status: RelationshipEvolutionStatus
    ) -> tuple[str, ...]:
        return tuple(
            entry.record_id for entry in self.entries if entry.status is status
        )

    @property
    def added_record_ids(self) -> tuple[str, ...]:
        return self.record_ids_for(RelationshipEvolutionStatus.ADDED)

    @property
    def removed_record_ids(self) -> tuple[str, ...]:
        return self.record_ids_for(RelationshipEvolutionStatus.REMOVED)

    @property
    def unchanged_record_ids(self) -> tuple[str, ...]:
        return self.record_ids_for(RelationshipEvolutionStatus.UNCHANGED)

    @property
    def changed_record_ids(self) -> tuple[str, ...]:
        return self.record_ids_for(RelationshipEvolutionStatus.CHANGED)


@dataclass(frozen=True)
class RelationshipTraceEntry:
    """Trazabilidad inmutable M393.6 de un registro relacional gobernado."""

    record_id: str
    record: "RelationshipMemoryRecord"
    evidence_refs: tuple[str, ...]
    consolidation_status: RelationshipConsolidationStatus
    consistency_issues: tuple[RelationshipConsistencyIssueKind, ...]
    evolution_status: RelationshipEvolutionStatus | None = None


@dataclass(frozen=True)
class RelationshipTraceabilityView:
    """Vista M393.6 de linaje relacional bajo relationship_memory."""

    entries: tuple[RelationshipTraceEntry, ...]
    source_snapshot_id: str | None
    evolution_previous_snapshot_id: str | None = None
    authority_id: str = "relationship_memory"

    @property
    def record_ids(self) -> tuple[str, ...]:
        return tuple(entry.record_id for entry in self.entries)

    @property
    def traced_evidence_refs(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    evidence_ref
                    for entry in self.entries
                    for evidence_ref in entry.evidence_refs
                }
            )
        )


class RelationshipAuditStatus(str, Enum):
    """Estado diagnóstico M393.7 derivado sólo de trazabilidad explícita."""

    CLEAR = "clear"
    REVIEW_REQUIRED = "review_required"
    CONFLICTED = "conflicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class RelationshipAuditEntry:
    """Resultado inmutable de auditoría para un registro relacional trazado."""

    trace: RelationshipTraceEntry
    status: RelationshipAuditStatus
    rationale: str

    @property
    def record_id(self) -> str:
        return self.trace.record_id


@dataclass(frozen=True)
class RelationshipAuditView:
    """Vista M393.7 de auditoría final bajo relationship_memory."""

    entries: tuple[RelationshipAuditEntry, ...]
    source_snapshot_id: str | None
    evolution_previous_snapshot_id: str | None = None
    authority_id: str = "relationship_memory"

    def record_ids_for(
        self, status: RelationshipAuditStatus
    ) -> tuple[str, ...]:
        return tuple(
            entry.record_id for entry in self.entries if entry.status is status
        )

    @property
    def clear_record_ids(self) -> tuple[str, ...]:
        return self.record_ids_for(RelationshipAuditStatus.CLEAR)

    @property
    def review_required_record_ids(self) -> tuple[str, ...]:
        return self.record_ids_for(RelationshipAuditStatus.REVIEW_REQUIRED)

    @property
    def conflicted_record_ids(self) -> tuple[str, ...]:
        return self.record_ids_for(RelationshipAuditStatus.CONFLICTED)

    @property
    def insufficient_evidence_record_ids(self) -> tuple[str, ...]:
        return self.record_ids_for(RelationshipAuditStatus.INSUFFICIENT_EVIDENCE)

    @property
    def is_clear(self) -> bool:
        return all(
            entry.status is RelationshipAuditStatus.CLEAR for entry in self.entries
        )


@dataclass(frozen=True)
class RelationshipMemoryRecord:
    """Entrada auditable de memoria de convivencia.

    M52 conserva señales relacionales, no hechos arbitrarios. Cada entrada
    incluye categoría, confianza, origen y fecha para permitir revisión futura.
    """

    content: str
    kind: RelationshipMemoryKind | str
    confidence: float
    reason: str
    tags: tuple[str, ...] = ()
    source: str = "relationship_memory"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    record_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        RelationshipMemoryKind(self.kind)
        if not self.content.strip():
            raise ValueError("relationship memory content must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("relationship memory confidence must be between 0 and 1")
        if not self.reason.strip():
            raise ValueError("relationship memory reason must not be empty")
        if not self.source.strip():
            raise ValueError("relationship memory source must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("relationship memory timestamp must be timezone-aware")
        if not self.record_id.strip():
            raise ValueError("relationship memory id must not be empty")

    @property
    def normalized_kind(self) -> RelationshipMemoryKind:
        return RelationshipMemoryKind(self.kind)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.record_id,
            "content": self.content,
            "kind": self.normalized_kind.value,
            "confidence": self.confidence,
            "reason": self.reason,
            "tags": list(self.tags),
            "source": self.source,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class RelationshipMemoryCandidate:
    """Candidato producido por la política antes de almacenarse."""

    content: str
    kind: RelationshipMemoryKind | str
    action: RelationshipMemoryAction | str
    confidence: float
    reason: str
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        RelationshipMemoryKind(self.kind)
        RelationshipMemoryAction(self.action)
        if not self.content.strip():
            raise ValueError("relationship memory candidate must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "relationship candidate confidence must be between 0 and 1"
            )
        if not self.reason.strip():
            raise ValueError("relationship candidate reason must not be empty")

    @property
    def normalized_kind(self) -> RelationshipMemoryKind:
        return RelationshipMemoryKind(self.kind)

    @property
    def normalized_action(self) -> RelationshipMemoryAction:
        return RelationshipMemoryAction(self.action)

    def to_record(
        self,
        *,
        source: str = "relationship_memory",
        created_at: datetime | None = None,
    ) -> RelationshipMemoryRecord:
        return RelationshipMemoryRecord(
            content=self.content,
            kind=self.normalized_kind,
            confidence=self.confidence,
            reason=self.reason,
            tags=self.tags,
            source=source,
            created_at=created_at or datetime.now(timezone.utc),
        )


@dataclass(frozen=True)
class RelationshipMemorySnapshot:
    """Vista estable de la relación usuario-ROBY en el turno actual."""

    familiarity_score: float
    trust_score: float
    continuity_score: float
    records: tuple[RelationshipMemoryRecord, ...] = ()
    reviewed_candidates: tuple[RelationshipMemoryCandidate, ...] = ()
    ignored_candidates: tuple[RelationshipMemoryCandidate, ...] = ()
    presence_snapshot_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        for score in (
            self.familiarity_score,
            self.trust_score,
            self.continuity_score,
        ):
            if not 0.0 <= score <= 1.0:
                raise ValueError("relationship memory scores must be between 0 and 1")
        if self.created_at.tzinfo is None:
            raise ValueError("relationship memory snapshot timestamp must be aware")
        if not self.snapshot_id.strip():
            raise ValueError("relationship memory snapshot id must not be empty")

    @property
    def has_context(self) -> bool:
        return bool(self.records)

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Memoria de convivencia M52:",
            f"- Familiaridad: {self.familiarity_score:.2f}",
            f"- Confianza relacional: {self.trust_score:.2f}",
            f"- Continuidad relacional: {self.continuity_score:.2f}",
        ]
        if self.presence_snapshot_id is not None:
            lines.append(f"- Presencia asociada: {self.presence_snapshot_id}")
        if self.records:
            lines.append("- Señales recordadas:")
            for record in self.records[-3:]:
                lines.append(f"  - {record.normalized_kind.value}: {record.content}")
        else:
            lines.append("- Sin señales relacionales persistentes aún.")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "familiarity_score": self.familiarity_score,
            "trust_score": self.trust_score,
            "continuity_score": self.continuity_score,
            "has_context": self.has_context,
            "presence_snapshot_id": self.presence_snapshot_id,
            "records": [record.to_dict() for record in self.records],
            "reviewed_candidates": [
                candidate.content for candidate in self.reviewed_candidates
            ],
            "ignored_candidates": [
                candidate.content for candidate in self.ignored_candidates
            ],
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class RelationshipMemoryPolicy:
    """Política determinística para decidir qué recordar de la convivencia."""

    remember_threshold: float = 0.72
    review_threshold: float = 0.45
    max_records: int = 50

    def __post_init__(self) -> None:
        if not 0.0 <= self.review_threshold < self.remember_threshold <= 1.0:
            raise ValueError("relationship memory thresholds must be ordered")
        if self.max_records <= 0:
            raise ValueError("relationship memory max_records must be positive")

    def action_for(self, confidence: float) -> RelationshipMemoryAction:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("relationship memory confidence must be between 0 and 1")
        if confidence >= self.remember_threshold:
            return RelationshipMemoryAction.REMEMBER
        if confidence >= self.review_threshold:
            return RelationshipMemoryAction.REVIEW
        return RelationshipMemoryAction.IGNORE


class RelationshipMemoryEngine:
    """Motor puro de M52 — Memoria de Convivencia."""

    _PREFERENCE_PATTERNS = (
        "prefiero",
        "me gusta",
        "quiero que",
        "desde ahora",
        "de ahora en adelante",
        "mismo método",
        "mismo metodo",
    )
    _PROJECT_RHYTHM_PATTERNS = (
        "commit",
        "ruff",
        "pytest",
        "zip",
        "milestone",
        "fase",
        "mismo metodo",
        "mismo método",
    )
    _TRUST_PATTERNS = (
        "seguimos",
        "continuamos",
        "perfecto",
        "excelente",
        "confi",
        "bien",
    )
    _BOUNDARY_PATTERNS = (
        "no hagas",
        "no quiero",
        "sin romper",
        "no reemplaza",
        "no toques",
    )
    _TRANSIENT_PATTERNS = (
        "hoy",
        "mañana",
        "manana",
        "ayer",
        "ahora",
        "después",
        "despues",
    )

    def __init__(self, policy: RelationshipMemoryPolicy | None = None) -> None:
        self.policy = policy or RelationshipMemoryPolicy()

    def evaluate_turn(
        self,
        text: str,
        *,
        existing_records: tuple[RelationshipMemoryRecord, ...] = (),
        presence: PresenceSnapshot | None = None,
        now: datetime | None = None,
    ) -> RelationshipMemorySnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("relationship memory timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("relationship memory text must not be empty")

        candidates = self._candidates_for(text)
        records = list(existing_records)
        reviewed: list[RelationshipMemoryCandidate] = []
        ignored: list[RelationshipMemoryCandidate] = []

        for candidate in candidates:
            action = candidate.normalized_action
            if action is RelationshipMemoryAction.REMEMBER:
                records.append(
                    candidate.to_record(
                        source="relationship_memory_turn",
                        created_at=timestamp,
                    )
                )
            elif action is RelationshipMemoryAction.REVIEW:
                reviewed.append(candidate)
            else:
                ignored.append(candidate)

        records = records[-self.policy.max_records :]
        continuity = presence.continuity_score if presence is not None else 0.0
        familiarity = self._score_familiarity(tuple(records), continuity)
        trust = self._score_trust(tuple(records), continuity)

        return RelationshipMemorySnapshot(
            familiarity_score=familiarity,
            trust_score=trust,
            continuity_score=continuity,
            records=tuple(records),
            reviewed_candidates=tuple(reviewed),
            ignored_candidates=tuple(ignored),
            presence_snapshot_id=presence.snapshot_id if presence is not None else None,
            created_at=timestamp,
        )

    def _candidates_for(self, text: str) -> tuple[RelationshipMemoryCandidate, ...]:
        normalized = " ".join(text.strip().lower().split())
        if not normalized:
            return ()

        kind = self._kind_for(normalized)
        confidence = self._confidence_for(normalized, kind)
        action = self.policy.action_for(confidence)

        return (
            RelationshipMemoryCandidate(
                content=normalized,
                kind=kind,
                action=action,
                confidence=confidence,
                reason=self._reason_for(kind, action),
                tags=(kind.value, "m52"),
            ),
        )

    def _kind_for(self, text: str) -> RelationshipMemoryKind:
        if self._contains_any(text, self._BOUNDARY_PATTERNS):
            return RelationshipMemoryKind.BOUNDARY
        if self._contains_any(text, self._PREFERENCE_PATTERNS):
            return RelationshipMemoryKind.USER_PREFERENCE
        if self._contains_any(text, self._PROJECT_RHYTHM_PATTERNS):
            return RelationshipMemoryKind.PROJECT_RHYTHM
        if self._contains_any(text, self._TRUST_PATTERNS):
            return RelationshipMemoryKind.TRUST_SIGNAL
        if self._contains_any(text, self._TRANSIENT_PATTERNS):
            return RelationshipMemoryKind.TRANSIENT
        return RelationshipMemoryKind.INTERACTION_PATTERN

    def _confidence_for(
        self,
        text: str,
        kind: RelationshipMemoryKind,
    ) -> float:
        if kind is RelationshipMemoryKind.BOUNDARY:
            return 0.86
        if kind is RelationshipMemoryKind.USER_PREFERENCE:
            return 0.82
        if kind is RelationshipMemoryKind.PROJECT_RHYTHM:
            return 0.78
        if kind is RelationshipMemoryKind.TRUST_SIGNAL:
            return 0.66
        if kind is RelationshipMemoryKind.TRANSIENT:
            return 0.35
        if len(text) >= 24:
            return 0.50
        return 0.20

    @staticmethod
    def _reason_for(
        kind: RelationshipMemoryKind,
        action: RelationshipMemoryAction,
    ) -> str:
        if action is RelationshipMemoryAction.REMEMBER:
            return f"{kind.value}_supports_continuity"
        if action is RelationshipMemoryAction.REVIEW:
            return f"{kind.value}_needs_more_context"
        return f"{kind.value}_is_not_stable_enough"

    @staticmethod
    def _score_familiarity(
        records: tuple[RelationshipMemoryRecord, ...],
        continuity: float,
    ) -> float:
        base = min(0.70, len(records) * 0.08)
        preference_bonus = sum(
            0.04
            for record in records
            if record.normalized_kind
            in {
                RelationshipMemoryKind.USER_PREFERENCE,
                RelationshipMemoryKind.PROJECT_RHYTHM,
            }
        )
        return min(1.0, base + preference_bonus + continuity * 0.20)

    @staticmethod
    def _score_trust(
        records: tuple[RelationshipMemoryRecord, ...],
        continuity: float,
    ) -> float:
        trust = 0.20 + continuity * 0.25
        for record in records:
            if record.normalized_kind is RelationshipMemoryKind.TRUST_SIGNAL:
                trust += 0.08
            elif record.normalized_kind is RelationshipMemoryKind.BOUNDARY:
                trust += 0.10
            elif record.normalized_kind is RelationshipMemoryKind.USER_PREFERENCE:
                trust += 0.04
        return min(1.0, trust)

    @staticmethod
    def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
        return any(pattern in text for pattern in patterns)


class RelationshipMemoryManager:
    """Fachada estable para M52.

    Conserva snapshots en memoria del proceso. No reemplaza M18-M21 ni la
    memoria cognitiva M36-M39: prepara una capa relacional auditable que podrá
    conectarse luego a persistencia concreta sin cambiar contratos.
    """

    def __init__(self, engine: RelationshipMemoryEngine | None = None) -> None:
        self.engine = engine or RelationshipMemoryEngine()
        self._snapshots: list[RelationshipMemorySnapshot] = []

    @property
    def history(self) -> tuple[RelationshipMemorySnapshot, ...]:
        return tuple(self._snapshots)

    @property
    def last_snapshot(self) -> RelationshipMemorySnapshot | None:
        if not self._snapshots:
            return None
        return self._snapshots[-1]

    @property
    def records(self) -> tuple[RelationshipMemoryRecord, ...]:
        if self.last_snapshot is None:
            return ()
        return self.last_snapshot.records

    def observe_turn(
        self,
        text: str,
        *,
        presence: PresenceSnapshot | None = None,
        now: datetime | None = None,
    ) -> RelationshipMemorySnapshot:
        snapshot = self.engine.evaluate_turn(
            text,
            existing_records=self.records,
            presence=presence,
            now=now,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def enriched_view(
        self,
        evidence: tuple[RelationshipEvidenceReference, ...] = (),
    ) -> EnrichedRelationshipMemoryView:
        """Construye una vista enriquecida sin inferir ni modificar registros."""

        records_by_id = {record.record_id: record for record in self.records}
        evidence_by_record: dict[str, list[RelationshipEvidenceReference]] = {
            record_id: [] for record_id in records_by_id
        }
        seen_refs: set[tuple[str, str]] = set()
        for reference in evidence:
            if reference.record_id not in records_by_id:
                raise ValueError("relationship evidence references unknown record")
            identity = (reference.record_id, reference.evidence_ref)
            if identity in seen_refs:
                raise ValueError("relationship evidence reference must be unique")
            seen_refs.add(identity)
            evidence_by_record[reference.record_id].append(reference)

        entries = tuple(
            EnrichedRelationshipMemoryEntry(
                record=record,
                evidence=tuple(
                    sorted(
                        evidence_by_record[record.record_id],
                        key=lambda item: (
                            item.evidence_ref,
                            item.normalized_kind.value,
                            item.source_authority,
                            item.normalized_epistemic_level.value,
                            item.normalized_validation.value,
                        ),
                    )
                ),
            )
            for record in self.records
        )
        return EnrichedRelationshipMemoryView(
            entries=entries,
            source_snapshot_id=(
                self.last_snapshot.snapshot_id
                if self.last_snapshot is not None
                else None
            ),
        )

    def consolidation_view(
        self,
        evidence: tuple[RelationshipEvidenceReference, ...] = (),
    ) -> RelationshipConsolidationView:
        """Clasifica respaldo relacional sin reescribir ni persistir memoria."""

        enriched = self.enriched_view(evidence)
        entries: list[ConsolidatedRelationshipEntry] = []
        for source in enriched.entries:
            if source.has_conflicting_evidence:
                status = RelationshipConsolidationStatus.CONFLICTED
                rationale = "explicit_conflicting_evidence"
            elif not source.is_evidenced:
                status = RelationshipConsolidationStatus.UNSUPPORTED
                rationale = "no_explicit_evidence"
            elif (
                source.has_verified_support
                and source.evidence_support_score >= 0.75
            ):
                status = RelationshipConsolidationStatus.CONSOLIDATED
                rationale = "verified_explicit_support"
            else:
                status = RelationshipConsolidationStatus.REVIEW_REQUIRED
                rationale = "evidence_requires_review"
            entries.append(
                ConsolidatedRelationshipEntry(
                    source=source,
                    status=status,
                    rationale=rationale,
                )
            )
        return RelationshipConsolidationView(
            entries=tuple(entries),
            source_snapshot_id=enriched.source_snapshot_id,
        )

    def consistency_view(
        self,
        evidence: tuple[RelationshipEvidenceReference, ...] = (),
        relations: tuple[RelationshipConsistencyRelation, ...] = (),
    ) -> RelationshipConsistencyView:
        """Diagnostica consistencia sin inferir contradicciones desde texto libre."""

        consolidation = self.consolidation_view(evidence)
        records = tuple(entry.record for entry in consolidation.entries)
        records_by_id = {record.record_id: record for record in records}
        issues: list[RelationshipConsistencyIssue] = []

        duplicate_groups: dict[tuple[str, str], list[str]] = {}
        for record in records:
            normalized_content = " ".join(record.content.strip().lower().split())
            key = (record.normalized_kind.value, normalized_content)
            duplicate_groups.setdefault(key, []).append(record.record_id)
        for record_ids in duplicate_groups.values():
            ordered_ids = sorted(record_ids)
            for index, source_id in enumerate(ordered_ids):
                for target_id in ordered_ids[index + 1 :]:
                    issues.append(
                        RelationshipConsistencyIssue(
                            kind=RelationshipConsistencyIssueKind.EXACT_DUPLICATE,
                            record_ids=(source_id, target_id),
                            rationale="same_kind_and_normalized_content",
                        )
                    )

        seen_relations: set[tuple[str, str, str, str]] = set()
        for relation in relations:
            if relation.source_record_id not in records_by_id:
                raise ValueError("relationship consistency references unknown record")
            if relation.target_record_id not in records_by_id:
                raise ValueError("relationship consistency references unknown record")
            record_ids = tuple(
                sorted((relation.source_record_id, relation.target_record_id))
            )
            identity = (
                record_ids[0],
                record_ids[1],
                relation.normalized_kind.value,
                relation.evidence_ref,
            )
            if identity in seen_relations:
                raise ValueError("relationship consistency relation must be unique")
            seen_relations.add(identity)
            rationale = {
                RelationshipConsistencyIssueKind.EXPLICIT_CONTRADICTION:
                    "explicit_contradiction_relation",
                RelationshipConsistencyIssueKind.EXPLICIT_INCOMPATIBILITY:
                    "explicit_incompatibility_relation",
            }[relation.normalized_kind]
            issues.append(
                RelationshipConsistencyIssue(
                    kind=relation.normalized_kind,
                    record_ids=record_ids,
                    rationale=rationale,
                    evidence_ref=relation.evidence_ref,
                )
            )

        ordered_issues = tuple(
            sorted(
                issues,
                key=lambda issue: (
                    issue.kind.value,
                    issue.record_ids,
                    issue.evidence_ref or "",
                    issue.rationale,
                ),
            )
        )
        return RelationshipConsistencyView(
            consolidation=consolidation,
            issues=ordered_issues,
        )

    def evolution_view(
        self,
        previous: RelationshipConsistencyView,
        current: RelationshipConsistencyView,
    ) -> RelationshipEvolutionView:
        """Compara dos vistas explícitas sin inferir causas ni reescribir memoria."""

        if previous.authority_id != "relationship_memory":
            raise ValueError("previous relationship view has unexpected authority")
        if current.authority_id != "relationship_memory":
            raise ValueError("current relationship view has unexpected authority")

        previous_entries = {
            entry.record.record_id: entry
            for entry in previous.consolidation.entries
        }
        current_entries = {
            entry.record.record_id: entry
            for entry in current.consolidation.entries
        }

        def issue_map(
            view: RelationshipConsistencyView,
        ) -> dict[str, tuple[RelationshipConsistencyIssueKind, ...]]:
            result: dict[str, set[RelationshipConsistencyIssueKind]] = {}
            for issue in view.issues:
                for record_id in issue.record_ids:
                    result.setdefault(record_id, set()).add(issue.kind)
            return {
                record_id: tuple(sorted(kinds, key=lambda kind: kind.value))
                for record_id, kinds in result.items()
            }

        previous_issue_map = issue_map(previous)
        current_issue_map = issue_map(current)
        entries: list[RelationshipEvolutionEntry] = []
        all_ids = sorted(set(previous_entries) | set(current_entries))
        for record_id in all_ids:
            before = previous_entries.get(record_id)
            after = current_entries.get(record_id)
            before_issues = previous_issue_map.get(record_id, ())
            after_issues = current_issue_map.get(record_id, ())
            if before is None:
                status = RelationshipEvolutionStatus.ADDED
            elif after is None:
                status = RelationshipEvolutionStatus.REMOVED
            else:
                before_signature = (
                    before.record.normalized_kind.value,
                    before.record.content,
                    before.record.confidence,
                    before.status.value,
                    before_issues,
                )
                after_signature = (
                    after.record.normalized_kind.value,
                    after.record.content,
                    after.record.confidence,
                    after.status.value,
                    after_issues,
                )
                status = (
                    RelationshipEvolutionStatus.UNCHANGED
                    if before_signature == after_signature
                    else RelationshipEvolutionStatus.CHANGED
                )
            entries.append(
                RelationshipEvolutionEntry(
                    record_id=record_id,
                    status=status,
                    previous=before,
                    current=after,
                    previous_issues=before_issues,
                    current_issues=after_issues,
                )
            )

        return RelationshipEvolutionView(
            entries=tuple(entries),
            previous_snapshot_id=previous.source_snapshot_id,
            current_snapshot_id=current.source_snapshot_id,
        )

    def traceability_view(
        self,
        consistency: RelationshipConsistencyView,
        evolution: RelationshipEvolutionView | None = None,
    ) -> RelationshipTraceabilityView:
        """Expone linaje explícito sin inferir, resolver ni reescribir memoria."""

        if consistency.authority_id != "relationship_memory":
            raise ValueError("relationship consistency view has unexpected authority")
        if evolution is not None and evolution.authority_id != "relationship_memory":
            raise ValueError("relationship evolution view has unexpected authority")
        if (
            evolution is not None
            and evolution.current_snapshot_id is not None
            and consistency.source_snapshot_id is not None
            and evolution.current_snapshot_id != consistency.source_snapshot_id
        ):
            raise ValueError("relationship traceability snapshot lineage mismatch")

        current_entries = {
            entry.record.record_id: entry
            for entry in consistency.consolidation.entries
        }
        current_issues: dict[str, set[RelationshipConsistencyIssueKind]] = {}
        for issue in consistency.issues:
            for record_id in issue.record_ids:
                current_issues.setdefault(record_id, set()).add(issue.kind)

        evolution_entries = (
            {entry.record_id: entry for entry in evolution.entries}
            if evolution is not None
            else {}
        )
        all_ids = sorted(set(current_entries) | set(evolution_entries))
        traced: list[RelationshipTraceEntry] = []
        for record_id in all_ids:
            current_entry = current_entries.get(record_id)
            evolution_entry = evolution_entries.get(record_id)
            source_entry = current_entry
            issues = tuple(
                sorted(
                    current_issues.get(record_id, set()),
                    key=lambda kind: kind.value,
                )
            )
            if source_entry is None and evolution_entry is not None:
                source_entry = evolution_entry.previous
                issues = evolution_entry.previous_issues
            if source_entry is None:
                raise ValueError("relationship traceability lacks source record")

            evidence_refs = tuple(
                sorted(
                    evidence.evidence_ref
                    for evidence in source_entry.source.evidence
                )
            )
            traced.append(
                RelationshipTraceEntry(
                    record_id=record_id,
                    record=source_entry.record,
                    evidence_refs=evidence_refs,
                    consolidation_status=source_entry.status,
                    consistency_issues=issues,
                    evolution_status=(
                        evolution_entry.status
                        if evolution_entry is not None
                        else None
                    ),
                )
            )

        return RelationshipTraceabilityView(
            entries=tuple(traced),
            source_snapshot_id=consistency.source_snapshot_id,
            evolution_previous_snapshot_id=(
                evolution.previous_snapshot_id if evolution is not None else None
            ),
        )

    def audit_view(
        self, traceability: RelationshipTraceabilityView
    ) -> RelationshipAuditView:
        """Resume trazabilidad explícita sin resolver ni modificar memoria."""

        if traceability.authority_id != "relationship_memory":
            raise ValueError("relationship traceability view has unexpected authority")

        audited: list[RelationshipAuditEntry] = []
        for trace in traceability.entries:
            if trace.consistency_issues or (
                trace.consolidation_status
                is RelationshipConsolidationStatus.CONFLICTED
            ):
                status = RelationshipAuditStatus.CONFLICTED
                rationale = "explicit_consistency_or_consolidation_conflict"
            elif not trace.evidence_refs or (
                trace.consolidation_status
                is RelationshipConsolidationStatus.UNSUPPORTED
            ):
                status = RelationshipAuditStatus.INSUFFICIENT_EVIDENCE
                rationale = "explicit_evidence_is_absent_or_unsupported"
            elif (
                trace.consolidation_status
                is RelationshipConsolidationStatus.REVIEW_REQUIRED
                or trace.evolution_status
                is RelationshipEvolutionStatus.CHANGED
            ):
                status = RelationshipAuditStatus.REVIEW_REQUIRED
                rationale = "explicit_review_or_change_requires_attention"
            else:
                status = RelationshipAuditStatus.CLEAR
                rationale = "explicit_lineage_has_no_audit_findings"

            audited.append(
                RelationshipAuditEntry(
                    trace=trace,
                    status=status,
                    rationale=rationale,
                )
            )

        return RelationshipAuditView(
            entries=tuple(audited),
            source_snapshot_id=traceability.source_snapshot_id,
            evolution_previous_snapshot_id=(
                traceability.evolution_previous_snapshot_id
            ),
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return ("Memoria de convivencia M52: sin contexto relacional aún.",)
        return self.last_snapshot.system_prompt_lines()
