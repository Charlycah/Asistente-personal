from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime

from app.cognitive_agenda_manager import (
    CognitiveAgendaSignal,
    CognitiveAgendaStatus,
)
from app.governed_long_horizon_investigation_continuity import (
    GovernedPassiveInvestigationCheckpoint,
)
from domain.cognitive_agenda import CognitiveAgendaKind


@dataclass(frozen=True)
class CallableCognitiveAgendaSource:
    """Small adapter for composing authoritative runtime read models."""

    name: str
    collector: Callable[[datetime], Sequence[CognitiveAgendaSignal]]
    absence_status: CognitiveAgendaStatus | None = None

    def collect(self, *, now: datetime) -> Sequence[CognitiveAgendaSignal]:
        return tuple(self.collector(now))


class GovernedPassiveInvestigationAgendaSignalAdapter:
    """Project passive investigation continuity into the existing agenda."""

    CANONICAL_AGENDA_AUTHORITY = "CognitiveAgendaManager"

    def adapt(
        self,
        checkpoint: GovernedPassiveInvestigationCheckpoint,
    ) -> CognitiveAgendaSignal:
        if not checkpoint.read_only or not checkpoint.passive:
            raise ValueError("investigation checkpoint must remain passive/read-only")
        if any(
            (
                checkpoint.starts_background_process,
                checkpoint.invokes_capabilities,
                checkpoint.executes_actions,
                checkpoint.modifies_memory,
                checkpoint.modifies_world_model,
                checkpoint.modifies_planning,
                checkpoint.performs_reasoning,
                checkpoint.grants_authority,
            )
        ):
            raise ValueError("investigation checkpoint must remain passive")

        context_tags = (
            checkpoint.checkpoint_id,
            checkpoint.thread_id,
            checkpoint.originating_reasoning_id,
            checkpoint.source_reference,
            *checkpoint.world_snapshot_ids,
            *checkpoint.requirement_ids,
        )
        return CognitiveAgendaSignal(
            key=checkpoint.checkpoint_id,
            kind=CognitiveAgendaKind.FOLLOW_UP,
            title=f"Paused investigation {checkpoint.thread_id}",
            source="governed_long_horizon_investigation",
            urgency=0.0,
            status=CognitiveAgendaStatus.WATCHING,
            rationale=checkpoint.pause_reason,
            resume_conditions=(checkpoint.pause_reason,),
            dependencies=checkpoint.requirement_ids,
            context_tags=context_tags,
        )
