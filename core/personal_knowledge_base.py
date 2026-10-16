from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol
from uuid import uuid4

from core.document_inbox import DocumentInboxManager, DocumentRecord
from core.scope_guard import ScopeDomain, ScopeGuardManager, ScopeGuardStatus


class KnowledgeKind(str, Enum):
    """Tipos normalizados de conocimiento personal."""

    FACT = "fact"
    CONCEPT = "concept"
    IDEA = "idea"
    NOTE = "note"
    SUMMARY = "summary"
    REFERENCE = "reference"
    PREFERENCE = "preference"
    PROCEDURE = "procedure"
    QUESTION = "question"
    CONCLUSION = "conclusion"


class KnowledgeOwner(str, Enum):
    """Propietario lógico del conocimiento."""

    CARLOS = "carlos"
    PARTNER = "partner"
    SHARED = "shared"


class KnowledgeSource(str, Enum):
    """Procedencia auditable de un elemento de conocimiento."""

    CONVERSATION = "conversation"
    DOCUMENT = "document"
    MANUAL_ENTRY = "manual_entry"
    HOUSEHOLD_MEMORY = "household_memory"
    SYSTEM_GENERATED = "system_generated"


class KnowledgeStatus(str, Enum):
    """Estados del ciclo de vida del conocimiento."""

    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class KnowledgeRelationType(str, Enum):
    """Relaciones semánticas explícitas entre elementos."""

    RELATED_TO = "related_to"
    DERIVED_FROM = "derived_from"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXPANDS = "expands"
    REPLACES = "replaces"


class KnowledgeSignal(str, Enum):
    """Señales auditables emitidas por M74."""

    CANDIDATE_CREATED = "candidate_created"
    KNOWLEDGE_STORED = "knowledge_stored"
    KNOWLEDGE_RECALLED = "knowledge_recalled"
    KNOWLEDGE_RELATED = "knowledge_related"
    KNOWLEDGE_SUPERSEDED = "knowledge_superseded"
    KNOWLEDGE_ARCHIVED = "knowledge_archived"
    DUPLICATE_REUSED = "duplicate_reused"
    SCOPE_PRESERVED = "scope_preserved"


@dataclass(frozen=True)
class KnowledgeCandidate:
    """Propuesta de conocimiento pendiente de validación o aprobación."""

    title: str
    content: str
    kind: KnowledgeKind | str
    source: KnowledgeSource | str
    owner: KnowledgeOwner | str = KnowledgeOwner.SHARED
    summary: str = ""
    tags: tuple[str, ...] = ()
    confidence: float = 1.0
    source_reference: str | None = None
    requires_review: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    candidate_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("knowledge candidate title must not be empty")
        if not self.content.strip():
            raise ValueError("knowledge candidate content must not be empty")
        KnowledgeKind(self.kind)
        KnowledgeSource(self.source)
        KnowledgeOwner(self.owner)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("knowledge confidence must be between zero and one")
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("knowledge tags must not be blank")
        if self.source_reference is not None and not self.source_reference.strip():
            raise ValueError("knowledge source reference must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("knowledge candidate timestamp must be timezone-aware")
        if not self.candidate_id.strip():
            raise ValueError("knowledge candidate id must not be empty")

    @property
    def normalized_kind(self) -> KnowledgeKind:
        return KnowledgeKind(self.kind)

    @property
    def normalized_source(self) -> KnowledgeSource:
        return KnowledgeSource(self.source)

    @property
    def normalized_owner(self) -> KnowledgeOwner:
        return KnowledgeOwner(self.owner)

    @property
    def normalized_tags(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(tag.strip().casefold() for tag in self.tags))


@dataclass(frozen=True)
class KnowledgeRelation:
    """Arista explícita y trazable del grafo personal de conocimiento."""

    source_item_id: str
    target_item_id: str
    relation_type: KnowledgeRelationType | str
    rationale: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    relation_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.source_item_id.strip() or not self.target_item_id.strip():
            raise ValueError("knowledge relation endpoints must not be empty")
        if self.source_item_id == self.target_item_id:
            raise ValueError("knowledge item cannot relate to itself")
        KnowledgeRelationType(self.relation_type)
        if self.created_at.tzinfo is None:
            raise ValueError("knowledge relation timestamp must be timezone-aware")
        if not self.relation_id.strip():
            raise ValueError("knowledge relation id must not be empty")

    @property
    def normalized_type(self) -> KnowledgeRelationType:
        return KnowledgeRelationType(self.relation_type)


@dataclass(frozen=True)
class KnowledgeItem:
    """Unidad inmutable, trazable y consultable de conocimiento personal."""

    title: str
    content: str
    kind: KnowledgeKind | str
    source: KnowledgeSource | str
    owner: KnowledgeOwner | str = KnowledgeOwner.SHARED
    summary: str = ""
    tags: tuple[str, ...] = ()
    confidence: float = 1.0
    status: KnowledgeStatus | str = KnowledgeStatus.ACTIVE
    source_reference: str | None = None
    superseded_by: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    item_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.content.strip():
            raise ValueError("knowledge title and content must not be empty")
        KnowledgeKind(self.kind)
        KnowledgeSource(self.source)
        KnowledgeOwner(self.owner)
        KnowledgeStatus(self.status)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("knowledge confidence must be between zero and one")
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("knowledge tags must not be blank")
        for reference in (self.source_reference, self.superseded_by):
            if reference is not None and not reference.strip():
                raise ValueError("knowledge references must not be blank")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("knowledge timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("knowledge update cannot precede creation")
        if not self.item_id.strip():
            raise ValueError("knowledge item id must not be empty")

    @property
    def normalized_kind(self) -> KnowledgeKind:
        return KnowledgeKind(self.kind)

    @property
    def normalized_source(self) -> KnowledgeSource:
        return KnowledgeSource(self.source)

    @property
    def normalized_owner(self) -> KnowledgeOwner:
        return KnowledgeOwner(self.owner)

    @property
    def normalized_status(self) -> KnowledgeStatus:
        return KnowledgeStatus(self.status)

    @property
    def normalized_tags(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(tag.strip().casefold() for tag in self.tags))

    @property
    def fingerprint(self) -> str:
        payload = f"{self.title.strip().casefold()}\n{self.content.strip()}"
        return sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.item_id,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "kind": self.normalized_kind.value,
            "source": self.normalized_source.value,
            "owner": self.normalized_owner.value,
            "tags": list(self.normalized_tags),
            "confidence": self.confidence,
            "status": self.normalized_status.value,
            "source_reference": self.source_reference,
            "superseded_by": self.superseded_by,
            "fingerprint": self.fingerprint,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class PersonalKnowledgeRepository(Protocol):
    """Contrato de persistencia desacoplado de infraestructura."""

    def save_item(self, item: KnowledgeItem) -> KnowledgeItem: ...

    def get_item(self, item_id: str) -> KnowledgeItem | None: ...

    def get_by_fingerprint(self, fingerprint: str) -> KnowledgeItem | None: ...

    def list_items(self) -> tuple[KnowledgeItem, ...]: ...

    def save_relation(self, relation: KnowledgeRelation) -> KnowledgeRelation: ...

    def list_relations(self) -> tuple[KnowledgeRelation, ...]: ...


class InMemoryPersonalKnowledgeRepository:
    """Repositorio determinista para M74 y pruebas unitarias."""

    def __init__(self) -> None:
        self._items: dict[str, KnowledgeItem] = {}
        self._relations: dict[str, KnowledgeRelation] = {}

    def save_item(self, item: KnowledgeItem) -> KnowledgeItem:
        self._items[item.item_id] = item
        return item

    def get_item(self, item_id: str) -> KnowledgeItem | None:
        return self._items.get(item_id)

    def get_by_fingerprint(self, fingerprint: str) -> KnowledgeItem | None:
        return next(
            (item for item in self._items.values() if item.fingerprint == fingerprint),
            None,
        )

    def list_items(self) -> tuple[KnowledgeItem, ...]:
        return tuple(
            sorted(
                self._items.values(),
                key=lambda item: (item.created_at, item.item_id),
            )
        )

    def save_relation(self, relation: KnowledgeRelation) -> KnowledgeRelation:
        self._relations[relation.relation_id] = relation
        return relation

    def list_relations(self) -> tuple[KnowledgeRelation, ...]:
        return tuple(
            sorted(
                self._relations.values(),
                key=lambda relation: (relation.created_at, relation.relation_id),
            )
        )


@dataclass(frozen=True)
class PersonalKnowledgeSnapshot:
    """Resumen estable para observabilidad y Cognitive Pipeline."""

    signals: tuple[KnowledgeSignal | str, ...]
    total_items: int
    active_items: int
    draft_items: int
    relation_count: int
    recent_items: tuple[KnowledgeItem, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("knowledge snapshot signals must not be empty")
        for signal in self.signals:
            KnowledgeSignal(signal)
        counters = (
            self.total_items,
            self.active_items,
            self.draft_items,
            self.relation_count,
        )
        if any(counter < 0 for counter in counters):
            raise ValueError("knowledge snapshot counters must not be negative")
        if self.active_items + self.draft_items > self.total_items:
            raise ValueError("knowledge status counters exceed total")
        if self.created_at.tzinfo is None:
            raise ValueError("knowledge snapshot timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("knowledge snapshot id must not be empty")

    def system_prompt_lines(self) -> tuple[str, ...]:
        lines = [
            "Personal Knowledge Base M74:",
            f"- Elementos registrados: {self.total_items}",
            f"- Elementos activos: {self.active_items}",
            f"- Borradores pendientes: {self.draft_items}",
            f"- Relaciones explícitas: {self.relation_count}",
            "- Regla: preservar fuente, confianza y estado del conocimiento.",
        ]
        for item in self.recent_items[:5]:
            lines.append(f"- Conocimiento: {item.title} ({item.normalized_kind.value})")
        return tuple(lines)


class PersonalKnowledgeBaseManager:
    """M74: conocimiento personal trazable, relacionado y gobernado."""

    def __init__(
        self,
        repository: PersonalKnowledgeRepository | None = None,
        *,
        scope_guard: ScopeGuardManager | None = None,
        document_inbox: DocumentInboxManager | None = None,
        recent_limit: int = 8,
        automatic_approval_threshold: float = 0.85,
    ) -> None:
        if recent_limit <= 0:
            raise ValueError("knowledge recent limit must be positive")
        if not 0.0 <= automatic_approval_threshold <= 1.0:
            raise ValueError("automatic approval threshold is invalid")
        self.repository = repository or InMemoryPersonalKnowledgeRepository()
        self.scope_guard = scope_guard or ScopeGuardManager()
        self.document_inbox = document_inbox
        self.recent_limit = recent_limit
        self.automatic_approval_threshold = automatic_approval_threshold
        self._signals: list[KnowledgeSignal] = []

    def create_candidate(
        self,
        *,
        title: str,
        content: str,
        kind: KnowledgeKind | str,
        source: KnowledgeSource | str = KnowledgeSource.MANUAL_ENTRY,
        owner: KnowledgeOwner | str = KnowledgeOwner.SHARED,
        summary: str = "",
        tags: tuple[str, ...] = (),
        confidence: float = 1.0,
        source_reference: str | None = None,
        now: datetime | None = None,
    ) -> KnowledgeCandidate:
        timestamp = self._timestamp(now)
        status = self._scope_status(title, content)
        candidate = KnowledgeCandidate(
            title=title,
            content=content,
            kind=kind,
            source=source,
            owner=owner,
            summary=summary,
            tags=tags,
            confidence=confidence,
            source_reference=source_reference,
            requires_review=(
                status is ScopeGuardStatus.REVIEW_REQUIRED
                or confidence < self.automatic_approval_threshold
                or KnowledgeSource(source) is KnowledgeSource.SYSTEM_GENERATED
            ),
            created_at=timestamp,
        )
        self._record(KnowledgeSignal.CANDIDATE_CREATED)
        self._record(KnowledgeSignal.SCOPE_PRESERVED)
        return candidate

    def candidate_from_document(
        self,
        document_id: str,
        *,
        kind: KnowledgeKind | str = KnowledgeKind.SUMMARY,
        owner: KnowledgeOwner | str = KnowledgeOwner.SHARED,
        confidence: float = 0.9,
        now: datetime | None = None,
    ) -> KnowledgeCandidate:
        if self.document_inbox is None:
            raise RuntimeError("document inbox integration is not configured")
        document = self.document_inbox.repository.get(document_id)
        if document is None:
            raise KeyError(f"unknown document: {document_id}")
        return self._candidate_for_document(
            document,
            kind=kind,
            owner=owner,
            confidence=confidence,
            now=now,
        )

    def approve(
        self,
        candidate: KnowledgeCandidate,
        *,
        reviewed: bool = False,
        now: datetime | None = None,
    ) -> KnowledgeItem:
        if candidate.requires_review and not reviewed:
            raise PermissionError("knowledge candidate requires human review")
        timestamp = self._timestamp(now)
        item = KnowledgeItem(
            title=candidate.title,
            content=candidate.content,
            kind=candidate.kind,
            source=candidate.source,
            owner=candidate.owner,
            summary=candidate.summary,
            tags=candidate.normalized_tags,
            confidence=candidate.confidence,
            status=KnowledgeStatus.ACTIVE,
            source_reference=candidate.source_reference,
            created_at=timestamp,
            updated_at=timestamp,
        )
        existing = self.repository.get_by_fingerprint(item.fingerprint)
        if existing is not None:
            self._record(KnowledgeSignal.DUPLICATE_REUSED)
            return existing
        stored = self.repository.save_item(item)
        self._record(KnowledgeSignal.KNOWLEDGE_STORED)
        return stored

    def remember(
        self,
        *,
        title: str,
        content: str,
        kind: KnowledgeKind | str,
        source: KnowledgeSource | str = KnowledgeSource.MANUAL_ENTRY,
        owner: KnowledgeOwner | str = KnowledgeOwner.SHARED,
        summary: str = "",
        tags: tuple[str, ...] = (),
        confidence: float = 1.0,
        source_reference: str | None = None,
        reviewed: bool = False,
        now: datetime | None = None,
    ) -> KnowledgeItem:
        candidate = self.create_candidate(
            title=title,
            content=content,
            kind=kind,
            source=source,
            owner=owner,
            summary=summary,
            tags=tags,
            confidence=confidence,
            source_reference=source_reference,
            now=now,
        )
        return self.approve(candidate, reviewed=reviewed, now=now)

    def recall(
        self,
        query: str = "",
        *,
        kind: KnowledgeKind | str | None = None,
        owner: KnowledgeOwner | str | None = None,
        status: KnowledgeStatus | str | None = KnowledgeStatus.ACTIVE,
        tags: tuple[str, ...] = (),
    ) -> tuple[KnowledgeItem, ...]:
        normalized_query = query.strip().casefold()
        kind_value = KnowledgeKind(kind) if kind is not None else None
        owner_value = KnowledgeOwner(owner) if owner is not None else None
        status_value = KnowledgeStatus(status) if status is not None else None
        requested_tags = {tag.strip().casefold() for tag in tags if tag.strip()}
        results = []
        for item in self.repository.list_items():
            searchable = " ".join(
                (
                    item.title,
                    item.summary,
                    item.content,
                    *item.normalized_tags,
                )
            ).casefold()
            if normalized_query and normalized_query not in searchable:
                continue
            if kind_value is not None and item.normalized_kind is not kind_value:
                continue
            if owner_value is not None and item.normalized_owner is not owner_value:
                continue
            if status_value is not None and item.normalized_status is not status_value:
                continue
            if requested_tags and not requested_tags.issubset(item.normalized_tags):
                continue
            results.append(item)
        self._record(KnowledgeSignal.KNOWLEDGE_RECALLED)
        return tuple(results)

    def relate(
        self,
        source_item_id: str,
        target_item_id: str,
        relation_type: KnowledgeRelationType | str,
        *,
        rationale: str = "",
        now: datetime | None = None,
    ) -> KnowledgeRelation:
        self._require(source_item_id)
        self._require(target_item_id)
        relation = KnowledgeRelation(
            source_item_id=source_item_id,
            target_item_id=target_item_id,
            relation_type=relation_type,
            rationale=rationale,
            created_at=self._timestamp(now),
        )
        stored = self.repository.save_relation(relation)
        self._record(KnowledgeSignal.KNOWLEDGE_RELATED)
        return stored

    def relations_for(self, item_id: str) -> tuple[KnowledgeRelation, ...]:
        self._require(item_id)
        return tuple(
            relation
            for relation in self.repository.list_relations()
            if item_id in (relation.source_item_id, relation.target_item_id)
        )

    def supersede(
        self,
        old_item_id: str,
        replacement_item_id: str,
        *,
        now: datetime | None = None,
    ) -> KnowledgeItem:
        old = self._require(old_item_id)
        self._require(replacement_item_id)
        timestamp = self._timestamp(now)
        superseded = replace(
            old,
            status=KnowledgeStatus.SUPERSEDED,
            superseded_by=replacement_item_id,
            updated_at=timestamp,
        )
        self.repository.save_item(superseded)
        self.relate(
            replacement_item_id,
            old_item_id,
            KnowledgeRelationType.REPLACES,
            rationale="El nuevo elemento reemplaza conocimiento anterior.",
            now=timestamp,
        )
        self._record(KnowledgeSignal.KNOWLEDGE_SUPERSEDED)
        return superseded

    def archive(
        self,
        item_id: str,
        *,
        now: datetime | None = None,
    ) -> KnowledgeItem:
        current = self._require(item_id)
        archived = replace(
            current,
            status=KnowledgeStatus.ARCHIVED,
            updated_at=self._timestamp(now),
        )
        self.repository.save_item(archived)
        self._record(KnowledgeSignal.KNOWLEDGE_ARCHIVED)
        return archived

    def list_items(self) -> tuple[KnowledgeItem, ...]:
        """Return the canonical read-only personal knowledge collection."""
        return self.repository.list_items()

    def snapshot(self, *, now: datetime | None = None) -> PersonalKnowledgeSnapshot:
        timestamp = self._timestamp(now)
        items = self.repository.list_items()
        signals = tuple(dict.fromkeys(self._signals)) or (
            KnowledgeSignal.SCOPE_PRESERVED,
        )
        return PersonalKnowledgeSnapshot(
            signals=signals,
            total_items=len(items),
            active_items=sum(
                item.normalized_status is KnowledgeStatus.ACTIVE for item in items
            ),
            draft_items=sum(
                item.normalized_status is KnowledgeStatus.DRAFT for item in items
            ),
            relation_count=len(self.repository.list_relations()),
            recent_items=items[-self.recent_limit :],
            created_at=timestamp,
        )

    def system_prompt_lines(self) -> tuple[str, ...]:
        return self.snapshot().system_prompt_lines()

    def _candidate_for_document(
        self,
        document: DocumentRecord,
        *,
        kind: KnowledgeKind | str,
        owner: KnowledgeOwner | str,
        confidence: float,
        now: datetime | None,
    ) -> KnowledgeCandidate:
        summary = document.content[:280].strip()
        if len(document.content) > 280:
            summary = f"{summary.rstrip()}…"
        return self.create_candidate(
            title=document.metadata.title,
            content=document.content,
            kind=kind,
            source=KnowledgeSource.DOCUMENT,
            owner=owner,
            summary=summary,
            tags=("documento", *document.metadata.normalized_tags),
            confidence=confidence,
            source_reference=f"document:{document.document_id}",
            now=now,
        )

    def _scope_status(self, title: str, content: str) -> ScopeGuardStatus:
        scope = self.scope_guard.observe_turn(
            f"conocimiento {title} {content}",
            proposed_domains=(ScopeDomain.KNOWLEDGE,),
        )
        if scope.normalized_status is ScopeGuardStatus.OUT_OF_SCOPE:
            raise PermissionError(scope.decision.rationale)
        return scope.normalized_status

    def _require(self, item_id: str) -> KnowledgeItem:
        if not item_id.strip():
            raise ValueError("knowledge item id must not be empty")
        item = self.repository.get_item(item_id)
        if item is None:
            raise KeyError(f"unknown knowledge item: {item_id}")
        return item

    @staticmethod
    def _timestamp(now: datetime | None) -> datetime:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("knowledge timestamp must be timezone-aware")
        return timestamp

    def _record(self, signal: KnowledgeSignal) -> None:
        self._signals.append(signal)
