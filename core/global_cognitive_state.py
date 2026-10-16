from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    CognitiveBlackboardSnapshot,
    UnifiedCognitiveBlackboard,
)


class GlobalCognitiveReadiness(str, Enum):
    STABLE = "stable"
    LIMITED = "limited"
    BLOCKED = "blocked"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class GlobalCognitiveDimension:
    name: str
    value: str
    confidence: float
    source_reference_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        name = self.name.strip()
        value = self.value.strip()
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not name or not value:
            raise ValueError("global cognitive dimension must be complete")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "global cognitive dimension confidence must be between zero and one"
            )
        if len(set(references)) != len(references):
            raise ValueError("global cognitive dimension references must be unique")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "source_reference_ids", references)


@dataclass(frozen=True)
class GlobalCognitiveState:
    owner: str
    session_id: str
    readiness: GlobalCognitiveReadiness | str
    dimensions: tuple[GlobalCognitiveDimension, ...]
    active_domains: tuple[CognitiveBlackboardDomain | str, ...]
    signal_count: int
    average_confidence: float
    constraints: tuple[str, ...] = ()
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    state_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        readiness = GlobalCognitiveReadiness(self.readiness)
        domains = tuple(CognitiveBlackboardDomain(item) for item in self.active_domains)
        constraints = tuple(item.strip() for item in self.constraints if item.strip())
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("global cognitive state identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("global cognitive state time must be timezone-aware")
        if self.signal_count < 0:
            raise ValueError("global cognitive state signal count cannot be negative")
        if not 0.0 <= self.average_confidence <= 1.0:
            raise ValueError(
                "global cognitive state confidence must be between zero and one"
            )
        if len(set(domains)) != len(domains):
            raise ValueError("global cognitive state domains must be unique")
        if len(set(constraints)) != len(constraints):
            raise ValueError("global cognitive state constraints must be unique")
        if len(set(references)) != len(references):
            raise ValueError("global cognitive state references must be unique")
        dimension_names = tuple(item.name.casefold() for item in self.dimensions)
        if len(set(dimension_names)) != len(dimension_names):
            raise ValueError("global cognitive state dimensions must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    readiness.value,
                    *(
                        f"{item.name}:{item.value}:{item.confidence:.3f}"
                        for item in self.dimensions
                    ),
                    *(item.value for item in domains),
                    str(self.signal_count),
                    f"{self.average_confidence:.3f}",
                    *constraints,
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.state_id and self.state_id != expected:
            raise ValueError("global cognitive state id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "readiness", readiness)
        object.__setattr__(self, "active_domains", domains)
        object.__setattr__(self, "constraints", constraints)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "state_id", expected)

    def dimension(self, name: str) -> GlobalCognitiveDimension | None:
        normalized = name.strip().casefold()
        return next(
            (item for item in self.dimensions if item.name.casefold() == normalized),
            None,
        )


class GlobalCognitiveStateEngine:
    """Project a bounded blackboard snapshot into one advisory cognitive state."""

    def __init__(self, blackboard: UnifiedCognitiveBlackboard | None = None) -> None:
        self.blackboard = blackboard
        self.last_state: GlobalCognitiveState | None = None

    def bind_blackboard(self, blackboard: UnifiedCognitiveBlackboard) -> None:
        self.blackboard = blackboard

    def assess(
        self,
        *,
        owner: str,
        session_id: str,
        snapshot: CognitiveBlackboardSnapshot | None = None,
        now: datetime | None = None,
    ) -> GlobalCognitiveState:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("global cognitive state time must be timezone-aware")
        if snapshot is None:
            if self.blackboard is None:
                raise ValueError("global cognitive state requires a blackboard")
            snapshot = self.blackboard.snapshot(
                owner=owner,
                session_id=session_id,
                now=timestamp,
            )
        if snapshot.owner != owner.strip() or snapshot.session_id != session_id.strip():
            raise ValueError("global cognitive state snapshot identity mismatch")

        source_entries = tuple(
            entry for entry in snapshot.entries if entry.key != "global_cognitive_state"
        )
        active_domains = tuple(dict.fromkeys(entry.domain for entry in source_entries))
        average_confidence = (
            sum(entry.confidence for entry in source_entries) / len(source_entries)
            if source_entries
            else 0.0
        )
        conversation_entry = self._latest(
            source_entries, "adaptive_conversation_operational_state"
        )
        conversation_value = (
            conversation_entry.value
            if conversation_entry is not None
            else "unavailable"
        )
        readiness, constraints = self._resolve_readiness(
            conversation_value, source_entries
        )
        references = tuple(dict.fromkeys(entry.entry_id for entry in source_entries))
        dimensions = (
            GlobalCognitiveDimension(
                name="conversation_readiness",
                value=conversation_value,
                confidence=(
                    conversation_entry.confidence
                    if conversation_entry is not None
                    else 0.0
                ),
                source_reference_ids=(
                    (conversation_entry.entry_id,)
                    if conversation_entry is not None
                    else ()
                ),
            ),
            GlobalCognitiveDimension(
                name="cross_domain_visibility",
                value=("available" if active_domains else "empty"),
                confidence=(
                    min(1.0, len(active_domains) / 4) if active_domains else 0.0
                ),
                source_reference_ids=references,
            ),
            GlobalCognitiveDimension(
                name="signal_quality",
                value=self._quality_label(average_confidence),
                confidence=average_confidence,
                source_reference_ids=references,
            ),
        )
        state = GlobalCognitiveState(
            owner=owner,
            session_id=session_id,
            readiness=readiness,
            dimensions=dimensions,
            active_domains=active_domains,
            signal_count=len(source_entries),
            average_confidence=average_confidence,
            constraints=constraints,
            source_reference_ids=(snapshot.snapshot_id, *references),
            created_at=timestamp,
        )
        self.last_state = state
        return state

    @staticmethod
    def _latest(
        entries: tuple[CognitiveBlackboardEntry, ...], key: str
    ) -> CognitiveBlackboardEntry | None:
        normalized = key.casefold()
        for entry in reversed(entries):
            if entry.key.casefold() == normalized:
                return entry
        return None

    @staticmethod
    def _quality_label(confidence: float) -> str:
        if confidence >= 0.8:
            return "high"
        if confidence >= 0.5:
            return "moderate"
        if confidence > 0.0:
            return "low"
        return "unavailable"

    @staticmethod
    def _resolve_readiness(
        conversation_value: str,
        entries: tuple[CognitiveBlackboardEntry, ...],
    ) -> tuple[GlobalCognitiveReadiness, tuple[str, ...]]:
        constraints = tuple(
            dict.fromkeys(
                entry.value
                for entry in entries
                if entry.kind is CognitiveBlackboardEntryKind.CONSTRAINT
            )
        )
        if conversation_value == "repair_required":
            return GlobalCognitiveReadiness.BLOCKED, (
                "conversation_repair_required",
                *constraints,
            )
        if conversation_value in {
            "grounding_required",
            "expectation_calibration_required",
        }:
            return GlobalCognitiveReadiness.LIMITED, (
                f"conversation_{conversation_value}",
                *constraints,
            )
        if conversation_value == "ready":
            return (
                (
                    GlobalCognitiveReadiness.LIMITED
                    if constraints
                    else GlobalCognitiveReadiness.STABLE
                ),
                constraints,
            )
        return GlobalCognitiveReadiness.DEGRADED, (
            "insufficient_global_cognitive_signals",
            *constraints,
        )


@dataclass(frozen=True)
class GlobalCognitiveStateRuntimeContributor:
    engine: GlobalCognitiveStateEngine
    blackboard: UnifiedCognitiveBlackboard
    name: str = "global_cognitive_state"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del text, request
        self.engine.bind_blackboard(self.blackboard)
        state = self.engine.assess(
            owner=owner,
            session_id=session_id,
            now=now,
        )
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONTEXT,
                key="global_cognitive_state",
                value=state.readiness.value,
                confidence=state.average_confidence,
                source_reference_ids=(state.state_id, *state.source_reference_ids),
                created_at=now,
            )
        )
        constraints = ", ".join(state.constraints) if state.constraints else "none"
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "Estado cognitivo global: "
                f"{state.readiness.value}; dominios activos "
                f"{len(state.active_domains)}; señales {state.signal_count}; "
                f"restricciones {constraints}.",
            ),
            reference_ids=(entry.entry_id, state.state_id, *state.source_reference_ids),
            rationale=(
                "m201_blackboard_projected",
                "global_cognitive_state_published",
            ),
        )
