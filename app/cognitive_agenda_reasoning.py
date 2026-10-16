from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from app.cognitive_agenda_manager import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaSnapshot,
    CognitiveAgendaStatus,
)


class CognitiveAgendaReasoningDisposition(str, Enum):
    OBSERVE = "observe"
    CONTINUE = "continue"
    PREPARE_FOLLOW_UP = "prepare_follow_up"
    PROPOSE_ACTION = "propose_action"
    WAIT_FOR_UNBLOCKING = "wait_for_unblocking"


@dataclass(frozen=True)
class CognitiveAgendaReasoningPolicy:
    propose_action_score: float = 0.82
    prepare_follow_up_score: float = 0.62
    urgent_threshold: float = 0.75

    def __post_init__(self) -> None:
        for name, value in (
            ("propose_action_score", self.propose_action_score),
            ("prepare_follow_up_score", self.prepare_follow_up_score),
            ("urgent_threshold", self.urgent_threshold),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"reasoning policy {name} must be between 0 and 1")
        if self.propose_action_score < self.prepare_follow_up_score:
            raise ValueError(
                "propose action score must not be lower than follow-up score"
            )


@dataclass(frozen=True)
class CognitiveAgendaDeliberation:
    generated_at: datetime
    agenda_key: str
    disposition: CognitiveAgendaReasoningDisposition
    summary: str
    rationale: str
    confidence: float
    requires_user_authorization: bool


class CognitiveAgendaReasoner:
    """Interpret the agenda without executing external or irreversible actions."""

    def __init__(
        self,
        *,
        policy: CognitiveAgendaReasoningPolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveAgendaReasoningPolicy()

    def deliberate(
        self,
        snapshot: CognitiveAgendaSnapshot,
        *,
        now: datetime | None = None,
    ) -> CognitiveAgendaDeliberation | None:
        item = snapshot.effective_focus
        if item is None:
            return None
        timestamp = now or datetime.now(timezone.utc)
        disposition = self._select_disposition(item)
        return CognitiveAgendaDeliberation(
            generated_at=timestamp,
            agenda_key=item.key,
            disposition=disposition,
            summary=self._build_summary(item, disposition),
            rationale=self._build_rationale(item, disposition),
            confidence=self._confidence(item),
            requires_user_authorization=(
                disposition is CognitiveAgendaReasoningDisposition.PROPOSE_ACTION
            ),
        )

    def _select_disposition(
        self,
        item: CognitiveAgendaItem,
    ) -> CognitiveAgendaReasoningDisposition:
        if item.status is CognitiveAgendaStatus.BLOCKED:
            return CognitiveAgendaReasoningDisposition.WAIT_FOR_UNBLOCKING
        if item.status is CognitiveAgendaStatus.WATCHING:
            return CognitiveAgendaReasoningDisposition.OBSERVE
        if (
            item.score >= self.policy.propose_action_score
            and item.urgency >= self.policy.urgent_threshold
            and item.kind
            in {
                CognitiveAgendaKind.COMMITMENT,
                CognitiveAgendaKind.FOLLOW_UP,
                CognitiveAgendaKind.CONVERSATION,
                CognitiveAgendaKind.OPPORTUNITY,
            }
        ):
            return CognitiveAgendaReasoningDisposition.PROPOSE_ACTION
        if item.score >= self.policy.prepare_follow_up_score:
            return CognitiveAgendaReasoningDisposition.PREPARE_FOLLOW_UP
        return CognitiveAgendaReasoningDisposition.CONTINUE

    @staticmethod
    def _build_summary(
        item: CognitiveAgendaItem,
        disposition: CognitiveAgendaReasoningDisposition,
    ) -> str:
        actions = {
            CognitiveAgendaReasoningDisposition.OBSERVE: "Observar",
            CognitiveAgendaReasoningDisposition.CONTINUE: "Mantener en foco",
            CognitiveAgendaReasoningDisposition.PREPARE_FOLLOW_UP: (
                "Preparar seguimiento"
            ),
            CognitiveAgendaReasoningDisposition.PROPOSE_ACTION: "Proponer acción",
            CognitiveAgendaReasoningDisposition.WAIT_FOR_UNBLOCKING: (
                "Esperar desbloqueo"
            ),
        }
        return f"{actions[disposition]}: {item.title}"

    @staticmethod
    def _build_rationale(
        item: CognitiveAgendaItem,
        disposition: CognitiveAgendaReasoningDisposition,
    ) -> str:
        return (
            f"agenda_reasoning:{disposition.value}:{item.kind.value}:"
            f"score={item.score:.3f}:urgency={item.urgency:.3f}"
        )

    @staticmethod
    def _confidence(item: CognitiveAgendaItem) -> float:
        evidence_bonus = min(0.1, max(0, len(item.sources) - 1) * 0.03)
        confidence = 0.45 + item.relevance * 0.35 + evidence_bonus
        return round(min(1.0, confidence), 6)
