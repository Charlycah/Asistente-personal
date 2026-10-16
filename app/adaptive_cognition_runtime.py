from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.adaptive_cognition import (
    AdaptiveCognitionCycle,
    AdaptiveCognitionManager,
    AdaptiveCognitionStageStatus,
    AdaptiveReflectionManager,
    EpisodicMemoryManager,
    MetaReasoningManager,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.scope_guard import ScopeDomain

from .governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway


@dataclass(frozen=True)
class AdaptiveCognitionRuntimeSnapshot:
    cycles: int
    last_owner: str | None
    last_cycle_id: str | None
    last_reasoning_status: str | None
    last_requires_review: bool
    completed_stages: int


def build_default_adaptive_cognition_manager() -> AdaptiveCognitionManager:
    """Build the safe official adaptive cognition chain."""
    return AdaptiveCognitionManager(
        episodic_memory=EpisodicMemoryManager(),
        meta_reasoning=MetaReasoningManager(),
        adaptive_reflection=AdaptiveReflectionManager(),
    )


class OfficialAdaptiveCognitionRuntimeGateway:
    """Observable facade over ROBY's advisory adaptive cognition pipeline."""

    _STATUS_TRIGGERS = (
        "estado del runtime de cognición adaptativa",
        "estado de cognición adaptativa",
        "estado del runtime de cognicion adaptativa",
        "estado de cognicion adaptativa",
    )
    _AUDIT_TRIGGERS = (
        "auditá runtime de cognición adaptativa",
        "audita runtime de cognición adaptativa",
        "auditá runtime de cognicion adaptativa",
        "audita runtime de cognicion adaptativa",
        "evaluá runtime de cognición adaptativa",
        "evalua runtime de cognición adaptativa",
    )

    def __init__(
        self,
        *,
        reasoning_runtime: OfficialGovernedReasoningRuntimeGateway | None = None,
        manager: AdaptiveCognitionManager | None = None,
    ) -> None:
        self.reasoning_runtime = (
            reasoning_runtime or OfficialGovernedReasoningRuntimeGateway()
        )
        self.manager = manager or build_default_adaptive_cognition_manager()
        self._cycles = 0
        self._last_owner: str | None = None
        self._last_reasoning_status: str | None = None
        self._last_cycle: AdaptiveCognitionCycle | None = None
        self._productive_cycles_by_reasoning_result_id: dict[
            str, AdaptiveCognitionCycle
        ] = {}

    @property
    def snapshot(self) -> AdaptiveCognitionRuntimeSnapshot:
        cycle = self._last_cycle
        completed = 0
        if cycle is not None:
            completed = sum(
                item.status is AdaptiveCognitionStageStatus.COMPLETED
                for item in cycle.stages
            )
        return AdaptiveCognitionRuntimeSnapshot(
            cycles=self._cycles,
            last_owner=self._last_owner,
            last_cycle_id=cycle.cycle_id if cycle is not None else None,
            last_reasoning_status=self._last_reasoning_status,
            last_requires_review=cycle.requires_review if cycle is not None else False,
            completed_stages=completed,
        )

    def evaluate_text(
        self,
        *,
        owner: str,
        text: str,
        now: datetime,
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
        scope_reference: str | None = None,
        observe_productive_intake: bool = True,
        productive_turn_id: str | None = None,
    ) -> AdaptiveCognitionCycle:
        if productive_turn_id is None:
            reasoning = self.reasoning_runtime.evaluate_text(
                owner=owner,
                text=text,
                now=now,
                domains=domains,
                scope_reference=scope_reference,
                observe_productive_intake=observe_productive_intake,
            )
        else:
            episode = self.reasoning_runtime.evaluate_productive_episode(
                owner=owner,
                session_id=scope_reference or "productive",
                text=text,
                now=now,
                turn_id=productive_turn_id,
                domains=domains,
                scope_reference=scope_reference,
                observe_productive_intake=observe_productive_intake,
            )
            reasoning = episode.result
        cycle = self.manager.process_reasoning(
            text,
            reasoning,
            owner=owner,
            domains=domains,
            now=now,
        )
        self._cycles += 1
        self._last_owner = owner
        self._last_reasoning_status = reasoning.status.value
        self._last_cycle = cycle
        return cycle

    def observe_productive_episode(
        self,
        *,
        owner: str,
        text: str,
        episode,
        now: datetime,
        domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,),
    ) -> AdaptiveCognitionCycle:
        """Observe one canonical reasoning episode at most once."""
        reasoning = episode.result
        existing = self._productive_cycles_by_reasoning_result_id.get(
            reasoning.result_id
        )
        if existing is not None:
            return existing
        cycle = self.manager.process_reasoning(
            text,
            reasoning,
            owner=owner,
            domains=domains,
            now=now,
        )
        self._productive_cycles_by_reasoning_result_id[reasoning.result_id] = cycle
        self._cycles += 1
        self._last_owner = owner
        self._last_reasoning_status = reasoning.status.value
        self._last_cycle = cycle
        return cycle

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        del now
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._status_response(),
                rationale="official_adaptive_cognition_runtime_status_completed",
            )
        if any(trigger in normalized for trigger in self._AUDIT_TRIGGERS):
            return GovernedOperationalInterception(
                response_text="\n".join(
                    (
                        "Auditoría del Adaptive Cognition Runtime:",
                        "- Experiencia y hechos: separados.",
                        "- Meta-razonamiento: evaluativo, no ejecutivo.",
                        "- Reflexión: consultiva y trazable.",
                        "- Evolución de conocimiento: no automática.",
                        (
                            "- Planificación y coordinación: requieren "
                            "invocación explícita."
                        ),
                        "- Acciones operacionales: no autorizadas por adaptación.",
                    )
                ),
                rationale="official_adaptive_cognition_runtime_audit_completed",
            )
        return None

    def _status_response(self) -> str:
        snapshot = self.snapshot
        return "\n".join(
            (
                "Estado del Adaptive Cognition Runtime:",
                f"- Ciclos adaptativos: {snapshot.cycles}",
                f"- Último razonamiento: {snapshot.last_reasoning_status or 'ninguno'}",
                f"- Etapas completadas: {snapshot.completed_stages}",
                (
                    "- Revisión humana pendiente: "
                    f"{'sí' if snapshot.last_requires_review else 'no'}"
                ),
                "- Modo: advisory, trazable y no ejecutivo.",
            )
        )
