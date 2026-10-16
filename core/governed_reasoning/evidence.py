from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.daily_briefing import DailyBriefing
from core.document_inbox import DocumentRecord, DocumentStatus
from core.household_memory import HouseholdMemoryEntry, HouseholdMemoryStatus
from core.personal_knowledge_base import KnowledgeItem, KnowledgeStatus
from core.scope_guard import ScopeDomain, ScopeGuardManager, ScopeGuardStatus
from core.task_intelligence import Task, TaskStatus


class EvidenceSourceType(str, Enum):
    """Subsistema original que conserva el registro citado."""

    HOUSEHOLD_MEMORY = "household_memory"
    DOCUMENT = "document"
    KNOWLEDGE = "knowledge"
    TASK = "task"
    DAILY_BRIEFING = "daily_briefing"
    LEVEL2_ACQUIRED = "level2_acquired"


class EvidenceKind(str, Enum):
    """Naturaleza observable de una referencia de evidencia."""

    RECORD = "record"
    DOCUMENT = "document"
    KNOWLEDGE_ITEM = "knowledge_item"
    TASK_STATE = "task_state"
    SUMMARY = "summary"
    OBSERVATION = "observation"


class EvidenceStatus(str, Enum):
    """Estado normalizado sin alterar el ciclo de vida de la fuente."""

    ACTIVE = "active"
    REVIEW_REQUIRED = "review_required"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    CANCELLED = "cancelled"


class EvidenceSensitivity(str, Enum):
    """Clasificación conservadora para controlar exposición posterior."""

    PERSONAL = "personal"
    HOUSEHOLD = "household"
    SENSITIVE = "sensitive"


@dataclass(frozen=True)
class EvidenceReference:
    """Referencia inmutable y verificable a un registro fuente de M72–M76."""

    source_type: EvidenceSourceType | str
    source_id: str
    kind: EvidenceKind | str
    owner: str
    status: EvidenceStatus | str
    sensitivity: EvidenceSensitivity | str
    observed_at: datetime
    fingerprint: str
    summary: str
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    metadata: tuple[tuple[str, str], ...] = ()
    evidence_id: str = ""

    def __post_init__(self) -> None:
        source_type = EvidenceSourceType(self.source_type)
        EvidenceKind(self.kind)
        EvidenceStatus(self.status)
        EvidenceSensitivity(self.sensitivity)
        if not self.source_id.strip():
            raise ValueError("evidence source id must not be empty")
        if not self.owner.strip():
            raise ValueError("evidence owner must not be empty")
        if not self.summary.strip():
            raise ValueError("evidence summary must not be empty")
        if self.observed_at.tzinfo is None:
            raise ValueError("evidence observed timestamp must be timezone-aware")
        for timestamp in (self.valid_from, self.valid_until):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError("evidence validity timestamps must be timezone-aware")
        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValueError("evidence validity end cannot precede start")
        if len(self.fingerprint) != 64:
            raise ValueError("evidence fingerprint must be SHA-256")
        if any(not key.strip() or not value.strip() for key, value in self.metadata):
            raise ValueError("evidence metadata keys and values must not be blank")
        expected_id = self.build_id(source_type, self.source_id, self.fingerprint)
        if self.evidence_id and self.evidence_id != expected_id:
            raise ValueError("evidence id must match source and fingerprint")
        object.__setattr__(self, "evidence_id", expected_id)

    @staticmethod
    def build_id(
        source_type: EvidenceSourceType | str,
        source_id: str,
        fingerprint: str,
    ) -> str:
        payload = f"{EvidenceSourceType(source_type).value}|{source_id}|{fingerprint}"
        return sha256(payload.encode("utf-8")).hexdigest()

    @property
    def normalized_source_type(self) -> EvidenceSourceType:
        return EvidenceSourceType(self.source_type)

    @property
    def normalized_kind(self) -> EvidenceKind:
        return EvidenceKind(self.kind)

    @property
    def normalized_status(self) -> EvidenceStatus:
        return EvidenceStatus(self.status)

    @property
    def normalized_sensitivity(self) -> EvidenceSensitivity:
        return EvidenceSensitivity(self.sensitivity)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.evidence_id,
            "source_type": self.normalized_source_type.value,
            "source_id": self.source_id,
            "kind": self.normalized_kind.value,
            "owner": self.owner,
            "status": self.normalized_status.value,
            "sensitivity": self.normalized_sensitivity.value,
            "observed_at": self.observed_at.isoformat(),
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "fingerprint": self.fingerprint,
            "summary": self.summary,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class EvidenceBundle:
    """Colección ordenada y deduplicada de referencias normalizadas."""

    references: tuple[EvidenceReference, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    bundle_id: str = ""

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise ValueError("evidence bundle timestamp must be timezone-aware")
        ids = [reference.evidence_id for reference in self.references]
        if len(ids) != len(set(ids)):
            raise ValueError("evidence bundle must not contain duplicates")
        ordered = tuple(sorted(self.references, key=_reference_sort_key))
        object.__setattr__(self, "references", ordered)
        evidence_ids = "|".join(item.evidence_id for item in ordered)
        fingerprint = sha256(evidence_ids.encode()).hexdigest()
        expected_id = sha256(
            f"{self.created_at.isoformat()}|{fingerprint}".encode()
        ).hexdigest()
        if self.bundle_id and self.bundle_id != expected_id:
            raise ValueError("evidence bundle id is inconsistent")
        object.__setattr__(self, "bundle_id", expected_id)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.bundle_id,
            "created_at": self.created_at.isoformat(),
            "references": [reference.to_dict() for reference in self.references],
        }


@runtime_checkable
class EvidenceAdapter(Protocol):
    """Contrato para normalizar una entidad sin modificar su fuente."""

    source_type: EvidenceSourceType

    def supports(self, source: object) -> bool: ...

    def adapt(self, source: object) -> EvidenceReference: ...


class HouseholdMemoryEvidenceAdapter:
    source_type = EvidenceSourceType.HOUSEHOLD_MEMORY

    def supports(self, source: object) -> bool:
        return isinstance(source, HouseholdMemoryEntry)

    def adapt(self, source: object) -> EvidenceReference:
        if not isinstance(source, HouseholdMemoryEntry):
            raise TypeError("household memory adapter received an unsupported source")
        status = {
            HouseholdMemoryStatus.ACTIVE: EvidenceStatus.ACTIVE,
            HouseholdMemoryStatus.COMPLETED: EvidenceStatus.COMPLETED,
            HouseholdMemoryStatus.ARCHIVED: EvidenceStatus.ARCHIVED,
        }[source.normalized_status]
        fingerprint = _fingerprint(
            source.title,
            source.details,
            source.normalized_category.value,
            source.normalized_owner.value,
            source.normalized_status.value,
            source.updated_at.isoformat(),
        )
        return EvidenceReference(
            source_type=self.source_type,
            source_id=source.entry_id,
            kind=EvidenceKind.RECORD,
            owner=source.normalized_owner.value,
            status=status,
            sensitivity=EvidenceSensitivity.HOUSEHOLD,
            observed_at=source.updated_at,
            valid_from=source.created_at,
            valid_until=source.due_at,
            fingerprint=fingerprint,
            summary=f"{source.title}: {source.details}",
            metadata=(("category", source.normalized_category.value),),
        )


class DocumentEvidenceAdapter:
    source_type = EvidenceSourceType.DOCUMENT

    def supports(self, source: object) -> bool:
        return isinstance(source, DocumentRecord)

    def adapt(self, source: object) -> EvidenceReference:
        if not isinstance(source, DocumentRecord):
            raise TypeError("document adapter received an unsupported source")
        status = {
            DocumentStatus.INGESTED: EvidenceStatus.ACTIVE,
            DocumentStatus.REVIEW_REQUIRED: EvidenceStatus.REVIEW_REQUIRED,
            DocumentStatus.ARCHIVED: EvidenceStatus.ARCHIVED,
        }[source.normalized_status]
        sensitive_categories = {"medical", "insurance", "contract"}
        sensitivity = (
            EvidenceSensitivity.SENSITIVE
            if source.normalized_category.value in sensitive_categories
            else EvidenceSensitivity.PERSONAL
        )
        return EvidenceReference(
            source_type=self.source_type,
            source_id=source.document_id,
            kind=EvidenceKind.DOCUMENT,
            owner="shared",
            status=status,
            sensitivity=sensitivity,
            observed_at=source.updated_at,
            valid_from=source.metadata.issued_at or source.created_at,
            valid_until=source.metadata.expires_at,
            fingerprint=source.effective_hash,
            summary=f"{source.metadata.title} ({source.normalized_category.value})",
            metadata=(
                ("category", source.normalized_category.value),
                ("source_name", source.metadata.source_name),
                ("media_type", source.metadata.media_type),
            ),
        )


class KnowledgeEvidenceAdapter:
    source_type = EvidenceSourceType.KNOWLEDGE

    def supports(self, source: object) -> bool:
        return isinstance(source, KnowledgeItem)

    def adapt(self, source: object) -> EvidenceReference:
        if not isinstance(source, KnowledgeItem):
            raise TypeError("knowledge adapter received an unsupported source")
        status = {
            KnowledgeStatus.DRAFT: EvidenceStatus.REVIEW_REQUIRED,
            KnowledgeStatus.ACTIVE: EvidenceStatus.ACTIVE,
            KnowledgeStatus.SUPERSEDED: EvidenceStatus.SUPERSEDED,
            KnowledgeStatus.ARCHIVED: EvidenceStatus.ARCHIVED,
        }[source.normalized_status]
        return EvidenceReference(
            source_type=self.source_type,
            source_id=source.item_id,
            kind=EvidenceKind.KNOWLEDGE_ITEM,
            owner=source.normalized_owner.value,
            status=status,
            sensitivity=EvidenceSensitivity.PERSONAL,
            observed_at=source.updated_at,
            valid_from=source.created_at,
            fingerprint=source.fingerprint,
            summary=source.summary.strip() or source.title,
            metadata=(
                ("kind", source.normalized_kind.value),
                ("source", source.normalized_source.value),
                ("confidence", f"{source.confidence:.6f}"),
            ),
        )


class TaskEvidenceAdapter:
    source_type = EvidenceSourceType.TASK

    def supports(self, source: object) -> bool:
        return isinstance(source, Task)

    def adapt(self, source: object) -> EvidenceReference:
        if not isinstance(source, Task):
            raise TypeError("task adapter received an unsupported source")
        status = {
            TaskStatus.DRAFT: EvidenceStatus.REVIEW_REQUIRED,
            TaskStatus.PENDING: EvidenceStatus.ACTIVE,
            TaskStatus.IN_PROGRESS: EvidenceStatus.ACTIVE,
            TaskStatus.BLOCKED: EvidenceStatus.REVIEW_REQUIRED,
            TaskStatus.COMPLETED: EvidenceStatus.COMPLETED,
            TaskStatus.CANCELLED: EvidenceStatus.CANCELLED,
        }[source.normalized_status]
        fingerprint = _fingerprint(
            source.title,
            source.description,
            source.normalized_owner.value,
            source.normalized_status.value,
            source.updated_at.isoformat(),
        )
        return EvidenceReference(
            source_type=self.source_type,
            source_id=source.task_id,
            kind=EvidenceKind.TASK_STATE,
            owner=source.normalized_owner.value,
            status=status,
            sensitivity=EvidenceSensitivity.PERSONAL,
            observed_at=source.updated_at,
            valid_from=source.created_at,
            valid_until=source.deadline,
            fingerprint=fingerprint,
            summary=f"{source.title}: {source.description}",
            metadata=(
                ("origin", source.normalized_origin.value),
                ("importance", str(source.importance)),
                ("urgency", str(source.urgency)),
            ),
        )


class DailyBriefingEvidenceAdapter:
    source_type = EvidenceSourceType.DAILY_BRIEFING

    def supports(self, source: object) -> bool:
        return isinstance(source, DailyBriefing)

    def adapt(self, source: object) -> EvidenceReference:
        if not isinstance(source, DailyBriefing):
            raise TypeError("daily briefing adapter received an unsupported source")
        payload = source.to_dict()
        fingerprint = _fingerprint(str(payload))
        return EvidenceReference(
            source_type=self.source_type,
            source_id=source.briefing_id,
            kind=EvidenceKind.SUMMARY,
            owner=source.normalized_owner.value,
            status=EvidenceStatus.ACTIVE,
            sensitivity=EvidenceSensitivity.PERSONAL,
            observed_at=source.generated_at,
            valid_from=source.generated_at,
            fingerprint=fingerprint,
            summary=f"Daily briefing {source.normalized_period.value}",
            metadata=(
                ("period", source.normalized_period.value),
                ("item_count", str(len(source.items))),
                ("derived_summary", "true"),
            ),
        )


class EvidenceRegistry:
    """Registro M77 de adaptadores y referencias, gobernado por Scope Guard."""

    def __init__(
        self,
        adapters: tuple[EvidenceAdapter, ...] | None = None,
        *,
        scope_guard: ScopeGuardManager | None = None,
    ) -> None:
        self.adapters = adapters or (
            HouseholdMemoryEvidenceAdapter(),
            DocumentEvidenceAdapter(),
            KnowledgeEvidenceAdapter(),
            TaskEvidenceAdapter(),
            DailyBriefingEvidenceAdapter(),
        )
        if not self.adapters:
            raise ValueError("evidence registry requires at least one adapter")
        source_types = [adapter.source_type for adapter in self.adapters]
        if len(source_types) != len(set(source_types)):
            raise ValueError("evidence adapters must have unique source types")
        self.scope_guard = scope_guard or ScopeGuardManager()
        self._references: dict[str, EvidenceReference] = {}
        self._sources: dict[tuple[EvidenceSourceType, str], object] = {}

    def register_reference(
        self,
        reference: EvidenceReference,
        *,
        source: object | None = None,
    ) -> EvidenceReference:
        """Register an already-normalized reference through the canonical registry."""
        self._assert_in_scope(reference.normalized_source_type)
        self._references[reference.evidence_id] = reference
        if source is not None:
            self._sources[
                (reference.normalized_source_type, reference.source_id)
            ] = source
        return reference

    def normalize(self, source: object) -> EvidenceReference:
        adapter = self._adapter_for(source)
        self._assert_in_scope(adapter.source_type)
        reference = adapter.adapt(source)
        self._references[reference.evidence_id] = reference
        self._sources[(reference.normalized_source_type, reference.source_id)] = source
        return reference

    def normalize_many(
        self,
        sources: tuple[object, ...],
        *,
        now: datetime | None = None,
    ) -> EvidenceBundle:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("evidence bundle timestamp must be timezone-aware")
        references = tuple(self.normalize(source) for source in sources)
        unique = {reference.evidence_id: reference for reference in references}
        return EvidenceBundle(tuple(unique.values()), created_at=timestamp)

    def get(self, evidence_id: str) -> EvidenceReference | None:
        return self._references.get(evidence_id)

    def resolve_source(self, reference: EvidenceReference) -> object | None:
        return self._sources.get(
            (reference.normalized_source_type, reference.source_id)
        )

    def list_all(self) -> tuple[EvidenceReference, ...]:
        return tuple(sorted(self._references.values(), key=_reference_sort_key))

    def _adapter_for(self, source: object) -> EvidenceAdapter:
        matches = [adapter for adapter in self.adapters if adapter.supports(source)]
        if not matches:
            raise TypeError(f"no evidence adapter for {type(source).__name__}")
        if len(matches) > 1:
            raise RuntimeError("multiple evidence adapters support the same source")
        return matches[0]

    def _assert_in_scope(self, source_type: EvidenceSourceType) -> None:
        domain = {
            EvidenceSourceType.HOUSEHOLD_MEMORY: ScopeDomain.HOUSEHOLD_MEMORY,
            EvidenceSourceType.DOCUMENT: ScopeDomain.DOCUMENTS,
            EvidenceSourceType.KNOWLEDGE: ScopeDomain.KNOWLEDGE,
            EvidenceSourceType.TASK: ScopeDomain.TASKS,
            EvidenceSourceType.DAILY_BRIEFING: ScopeDomain.TASKS,
            EvidenceSourceType.LEVEL2_ACQUIRED: ScopeDomain.PERSONAL_OPERATIONS,
        }[source_type]
        decision = self.scope_guard.observe_turn(
            f"normalizar evidencia de {source_type.value}",
            proposed_domains=(domain,),
        )
        if decision.status is ScopeGuardStatus.OUT_OF_SCOPE:
            raise PermissionError("evidence source is outside the configured scope")


def _fingerprint(*parts: str) -> str:
    payload = "\n".join(part.strip() for part in parts)
    return sha256(payload.encode("utf-8")).hexdigest()


def _reference_sort_key(reference: EvidenceReference) -> tuple[str, str, str]:
    return (
        reference.normalized_source_type.value,
        reference.source_id,
        reference.evidence_id,
    )
