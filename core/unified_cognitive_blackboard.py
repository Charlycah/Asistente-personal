from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from threading import RLock
from typing import Iterable

from core.adaptive_conversation_operational_consolidation import (
    AdaptiveConversationOperationalConsolidation,
)
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest


class CognitiveBlackboardDomain(str, Enum):
    CONVERSATION = "conversation"
    MEMORY = "memory"
    REASONING = "reasoning"
    PLANNING = "planning"
    REFLECTION = "reflection"
    EXECUTIVE = "executive"
    TOOLING = "tooling"
    PROVIDER = "provider"
    PRESENCE = "presence"
    SYSTEM = "system"


class CognitiveBlackboardEntryKind(str, Enum):
    SIGNAL = "signal"
    CONTEXT = "context"
    CONSTRAINT = "constraint"
    CANDIDATE = "candidate"
    HEALTH = "health"


@dataclass(frozen=True)
class CognitiveBlackboardEntry:
    owner: str
    session_id: str
    domain: CognitiveBlackboardDomain | str
    kind: CognitiveBlackboardEntryKind | str
    key: str
    value: str
    confidence: float = 1.0
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    entry_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        domain = CognitiveBlackboardDomain(self.domain)
        kind = CognitiveBlackboardEntryKind(self.kind)
        key = self.key.strip()
        value = self.value.strip()
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("cognitive blackboard identity must be complete")
        if not key or not value:
            raise ValueError("cognitive blackboard entry must have key and value")
        if self.created_at.tzinfo is None:
            raise ValueError("cognitive blackboard time must be timezone-aware")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "cognitive blackboard confidence must be between zero and one"
            )
        if len(set(references)) != len(references):
            raise ValueError("cognitive blackboard references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    domain.value,
                    kind.value,
                    key,
                    value,
                    f"{self.confidence:.3f}",
                    ",".join(references),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.entry_id and self.entry_id != expected:
            raise ValueError("cognitive blackboard entry id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "entry_id", expected)


@dataclass(frozen=True)
class CognitiveBlackboardSnapshot:
    owner: str
    session_id: str
    entries: tuple[CognitiveBlackboardEntry, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        if not owner or not session_id:
            raise ValueError("cognitive blackboard snapshot identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError(
                "cognitive blackboard snapshot time must be timezone-aware"
            )
        if any(
            entry.owner != owner or entry.session_id != session_id
            for entry in self.entries
        ):
            raise ValueError("cognitive blackboard snapshot cannot cross identities")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    *(entry.entry_id for entry in self.entries),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.snapshot_id and self.snapshot_id != expected:
            raise ValueError("cognitive blackboard snapshot id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "snapshot_id", expected)

    def latest(self, key: str) -> CognitiveBlackboardEntry | None:
        normalized = key.strip().casefold()
        for entry in reversed(self.entries):
            if entry.key.casefold() == normalized:
                return entry
        return None


class UnifiedCognitiveBlackboard:
    """Provide an append-only, session-isolated exchange surface for cognition."""

    def __init__(self, *, maximum_entries_per_session: int = 256) -> None:
        if maximum_entries_per_session < 1:
            raise ValueError("blackboard maximum entries must be positive")
        self.maximum_entries_per_session = maximum_entries_per_session
        self._entries: dict[tuple[str, str], list[CognitiveBlackboardEntry]] = {}
        self._lock = RLock()
        self.last_snapshot: CognitiveBlackboardSnapshot | None = None

    def publish(self, entry: CognitiveBlackboardEntry) -> CognitiveBlackboardEntry:
        identity = (entry.owner.casefold(), entry.session_id)
        with self._lock:
            bucket = self._entries.setdefault(identity, [])
            if not any(current.entry_id == entry.entry_id for current in bucket):
                bucket.append(entry)
                overflow = len(bucket) - self.maximum_entries_per_session
                if overflow > 0:
                    del bucket[:overflow]
        return entry

    def publish_many(
        self, entries: Iterable[CognitiveBlackboardEntry]
    ) -> tuple[CognitiveBlackboardEntry, ...]:
        return tuple(self.publish(entry) for entry in entries)

    def snapshot(
        self,
        *,
        owner: str,
        session_id: str,
        domains: tuple[CognitiveBlackboardDomain | str, ...] = (),
        now: datetime | None = None,
    ) -> CognitiveBlackboardSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "cognitive blackboard snapshot time must be timezone-aware"
            )
        normalized_domains = {CognitiveBlackboardDomain(domain) for domain in domains}
        identity = (owner.strip().casefold(), session_id.strip())
        with self._lock:
            entries = tuple(self._entries.get(identity, ()))
        if normalized_domains:
            entries = tuple(
                entry for entry in entries if entry.domain in normalized_domains
            )
        snapshot = CognitiveBlackboardSnapshot(
            owner=owner,
            session_id=session_id,
            entries=entries,
            created_at=timestamp,
        )
        self.last_snapshot = snapshot
        return snapshot

    def clear_session(self, *, owner: str, session_id: str) -> int:
        identity = (owner.strip().casefold(), session_id.strip())
        with self._lock:
            entries = self._entries.pop(identity, [])
        return len(entries)


@dataclass(frozen=True)
class UnifiedCognitiveBlackboardRuntimeContributor:
    blackboard: UnifiedCognitiveBlackboard
    consolidation: AdaptiveConversationOperationalConsolidation | None = None
    name: str = "unified_cognitive_blackboard"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del request
        references: tuple[str, ...] = ()
        value = "available"
        confidence = 0.90
        rationale = ("blackboard_turn_surface_available",)
        if self.consolidation is not None:
            assessment = self.consolidation.last_assessment
            if (
                assessment is None
                or assessment.owner != owner.strip()
                or assessment.session_id != session_id.strip()
            ):
                assessment = self.consolidation.assess(
                    owner=owner,
                    session_id=session_id,
                    text=text,
                    now=now,
                )
            value = assessment.state.value
            confidence = assessment.confidence
            references = (
                assessment.assessment_id,
                *assessment.source_reference_ids,
            )
            rationale = (
                "m200_operational_state_published",
                "blackboard_turn_surface_available",
            )
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.CONVERSATION,
                kind=CognitiveBlackboardEntryKind.SIGNAL,
                key="adaptive_conversation_operational_state",
                value=value,
                confidence=confidence,
                source_reference_ids=references,
                created_at=now,
            )
        )
        snapshot = self.blackboard.snapshot(
            owner=owner,
            session_id=session_id,
            now=now,
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "Blackboard cognitivo unificado: "
                f"{len(snapshot.entries)} señal(es) gobernada(s) disponibles; "
                f"estado conversacional {value}.",
            ),
            reference_ids=(entry.entry_id, snapshot.snapshot_id, *references),
            rationale=rationale,
        )
