from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .relevance_evaluator import (
    RelevanceCandidate,
    RelevanceEvaluator,
    RelevanceRecipient,
)


class InitiativeDisposition(StrEnum):
    DISCARD = "discard"
    DEFER = "defer"
    INITIATE = "initiate"
    INTERRUPT = "interrupt"


@dataclass(frozen=True)
class InitiativeContext:
    conversation_active: bool = False
    quiet_hours: bool = False
    recently_intervened: bool = False


@dataclass(frozen=True)
class InitiativeProposal:
    title: str
    recipient: RelevanceRecipient
    disposition: InitiativeDisposition
    priority: int
    reasons: tuple[str, ...]

    @property
    def should_speak(self) -> bool:
        return self.disposition in {
            InitiativeDisposition.INITIATE,
            InitiativeDisposition.INTERRUPT,
        }


@dataclass(frozen=True)
class InitiativeEngineSnapshot:
    schema_version: str
    authority: str
    relevance_authority: str
    execution_enabled: bool


class PersonalInitiativeEngine:
    """Canonical pure planner for justified household initiatives."""

    SCHEMA_VERSION = "m343.4"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"

    def __init__(self, relevance_evaluator: RelevanceEvaluator) -> None:
        self._relevance_evaluator = relevance_evaluator

    @property
    def snapshot(self) -> InitiativeEngineSnapshot:
        return InitiativeEngineSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            relevance_authority=self._relevance_evaluator.snapshot.authority,
            execution_enabled=False,
        )

    def propose(
        self,
        candidate: RelevanceCandidate,
        *,
        context: InitiativeContext | None = None,
    ) -> InitiativeProposal:
        effective_context = context or InitiativeContext()
        relevance = self._relevance_evaluator.evaluate(candidate)
        priority = max(relevance.scores.values(), default=0)
        disposition, initiative_reason = self._disposition(
            relevance.should_share,
            relevance.should_interrupt,
            effective_context,
        )
        return InitiativeProposal(
            title=candidate.title,
            recipient=relevance.recipient,
            disposition=disposition,
            priority=priority,
            reasons=(*relevance.reasons, initiative_reason),
        )

    @staticmethod
    def _disposition(
        should_share: bool,
        should_interrupt: bool,
        context: InitiativeContext,
    ) -> tuple[InitiativeDisposition, str]:
        if not should_share:
            return InitiativeDisposition.DISCARD, "not_relevant_enough"
        if context.quiet_hours:
            return InitiativeDisposition.DEFER, "quiet_hours"
        if context.recently_intervened:
            return InitiativeDisposition.DEFER, "recent_intervention"
        if should_interrupt:
            return InitiativeDisposition.INTERRUPT, "interrupt_threshold_met"
        if context.conversation_active:
            return InitiativeDisposition.DEFER, "conversation_active"
        return InitiativeDisposition.INITIATE, "initiative_justified"
