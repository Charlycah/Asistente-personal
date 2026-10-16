from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

from app.cognitive_agenda_manager import (
    CognitiveAgendaItem,
    CognitiveAgendaSnapshot,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_reasoning import (
    CognitiveAgendaDeliberation,
    CognitiveAgendaReasoningDisposition,
)


class CognitiveReflectionOutcome(str, Enum):
    NO_REFLECTION = "no_reflection"
    AFFIRM_FOCUS = "affirm_focus"
    REASSESS_PRIORITY = "reassess_priority"
    SEEK_MORE_EVIDENCE = "seek_more_evidence"
    WAIT_FOR_CHANGE = "wait_for_change"
    RELEASE_STALE_FOCUS = "release_stale_focus"


@dataclass(frozen=True)
class CognitiveReflectionPolicy:
    stale_after: timedelta = timedelta(minutes=30)
    persistence_cycles: int = 3
    low_confidence_threshold: float = 0.62
    competing_focus_margin: float = 0.08

    def __post_init__(self) -> None:
        if self.stale_after.total_seconds() < 0:
            raise ValueError("reflection stale interval must not be negative")
        if self.persistence_cycles <= 0:
            raise ValueError("reflection persistence cycles must be positive")
        if not 0.0 <= self.low_confidence_threshold <= 1.0:
            raise ValueError("reflection confidence threshold must be between 0 and 1")
        if not 0.0 <= self.competing_focus_margin <= 1.0:
            raise ValueError("reflection focus margin must be between 0 and 1")


@dataclass(frozen=True)
class CognitiveReflection:
    generated_at: datetime
    agenda_key: str | None
    outcome: CognitiveReflectionOutcome
    summary: str
    rationale: str
    confidence: float
    recommends_agenda_reassessment: bool
    requires_user_authorization: bool = False


class CognitiveReflectionEngine:
    """Question resident deliberation without mutating authoritative state."""

    def __init__(
        self,
        *,
        policy: CognitiveReflectionPolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveReflectionPolicy()
        self._last_focus_key: str | None = None
        self._focus_cycles = 0

    def reflect(
        self,
        snapshot: CognitiveAgendaSnapshot | None,
        deliberation: CognitiveAgendaDeliberation | None,
        *,
        now: datetime | None = None,
    ) -> CognitiveReflection:
        timestamp = now or datetime.now(timezone.utc)
        item = snapshot.primary_focus if snapshot is not None else None
        self._observe_focus(item)
        outcome = self._select_outcome(snapshot, item, deliberation, timestamp)
        return CognitiveReflection(
            generated_at=timestamp,
            agenda_key=item.key if item is not None else None,
            outcome=outcome,
            summary=self._build_summary(item, outcome),
            rationale=self._build_rationale(item, deliberation, outcome),
            confidence=self._confidence(item, deliberation, outcome),
            recommends_agenda_reassessment=outcome
            in {
                CognitiveReflectionOutcome.REASSESS_PRIORITY,
                CognitiveReflectionOutcome.RELEASE_STALE_FOCUS,
            },
        )

    def _observe_focus(self, item: CognitiveAgendaItem | None) -> None:
        key = item.key if item is not None else None
        if key is None:
            self._last_focus_key = None
            self._focus_cycles = 0
        elif key == self._last_focus_key:
            self._focus_cycles += 1
        else:
            self._last_focus_key = key
            self._focus_cycles = 1

    def _select_outcome(
        self,
        snapshot: CognitiveAgendaSnapshot | None,
        item: CognitiveAgendaItem | None,
        deliberation: CognitiveAgendaDeliberation | None,
        now: datetime,
    ) -> CognitiveReflectionOutcome:
        if item is None or deliberation is None:
            return CognitiveReflectionOutcome.NO_REFLECTION
        if item.status is CognitiveAgendaStatus.BLOCKED:
            return CognitiveReflectionOutcome.WAIT_FOR_CHANGE
        if now - item.last_seen_at > self.policy.stale_after:
            return CognitiveReflectionOutcome.RELEASE_STALE_FOCUS
        if deliberation.confidence < self.policy.low_confidence_threshold:
            return CognitiveReflectionOutcome.SEEK_MORE_EVIDENCE
        if self._has_close_competitor(snapshot):
            return CognitiveReflectionOutcome.REASSESS_PRIORITY
        if (
            self._focus_cycles >= self.policy.persistence_cycles
            and deliberation.disposition is CognitiveAgendaReasoningDisposition.CONTINUE
        ):
            return CognitiveReflectionOutcome.REASSESS_PRIORITY
        return CognitiveReflectionOutcome.AFFIRM_FOCUS

    def _has_close_competitor(
        self,
        snapshot: CognitiveAgendaSnapshot | None,
    ) -> bool:
        if snapshot is None or len(snapshot.items) < 2:
            return False
        first, second = snapshot.items[:2]
        return first.score - second.score <= self.policy.competing_focus_margin

    @staticmethod
    def _build_summary(
        item: CognitiveAgendaItem | None,
        outcome: CognitiveReflectionOutcome,
    ) -> str:
        if item is None:
            return "No hay un foco de agenda que revisar"
        actions = {
            CognitiveReflectionOutcome.NO_REFLECTION: "Sin reflexión",
            CognitiveReflectionOutcome.AFFIRM_FOCUS: "Sostener el foco",
            CognitiveReflectionOutcome.REASSESS_PRIORITY: "Reevaluar prioridad",
            CognitiveReflectionOutcome.SEEK_MORE_EVIDENCE: "Buscar más evidencia",
            CognitiveReflectionOutcome.WAIT_FOR_CHANGE: "Esperar un cambio",
            CognitiveReflectionOutcome.RELEASE_STALE_FOCUS: "Liberar foco obsoleto",
        }
        return f"{actions[outcome]}: {item.title}"

    def _build_rationale(
        self,
        item: CognitiveAgendaItem | None,
        deliberation: CognitiveAgendaDeliberation | None,
        outcome: CognitiveReflectionOutcome,
    ) -> str:
        key = item.key if item is not None else "none"
        confidence = deliberation.confidence if deliberation is not None else 0.0
        return (
            f"cognitive_reflection:{outcome.value}:{key}:"
            f"cycles={self._focus_cycles}:confidence={confidence:.3f}"
        )

    @staticmethod
    def _confidence(
        item: CognitiveAgendaItem | None,
        deliberation: CognitiveAgendaDeliberation | None,
        outcome: CognitiveReflectionOutcome,
    ) -> float:
        if item is None or deliberation is None:
            return 1.0
        base = deliberation.confidence
        if outcome is CognitiveReflectionOutcome.AFFIRM_FOCUS:
            base += 0.08
        elif outcome is CognitiveReflectionOutcome.SEEK_MORE_EVIDENCE:
            base = 1.0 - base
        return round(min(1.0, max(0.0, base)), 6)
