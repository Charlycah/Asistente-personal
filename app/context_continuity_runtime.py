from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from core.conversation_context_curation import curate_recent_conversation_context
from core.conversation_history_sanitization import sanitize_conversation_history
from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.living_conversation.continuity import ConversationEpisode
from core.llm_provider import LLMRequest


@dataclass(frozen=True)
class ContextContinuityRuntimeSnapshot:
    owner: str
    session_id: str
    input_turns: int
    sanitized_turns: int
    selected_turns: int
    removed_turns: int
    context_applied: bool


class OfficialContextContinuityRuntimeGateway:
    """Official facade over ROBY's bounded, session-scoped context continuity."""

    _EVALUATION_TRIGGERS = (
        "evaluá continuidad contextual",
        "evalua continuidad contextual",
        "auditá continuidad contextual",
        "audita continuidad contextual",
    )
    _STATUS_TRIGGERS = (
        "estado de continuidad contextual",
        "estado del contexto conversacional",
        "estado del runtime de continuidad",
    )

    def __init__(self) -> None:
        self.cognitive_planner_shadow = None
        self._last_snapshot: ContextContinuityRuntimeSnapshot | None = None

    def set_cognitive_planner_shadow(self, planner_shadow: object) -> None:
        self.cognitive_planner_shadow = planner_shadow

    @property
    def snapshot(self) -> ContextContinuityRuntimeSnapshot | None:
        return self._last_snapshot

    def enrich(
        self,
        *,
        conversation: GovernedConversationPipelineRequest,
        inference_request: LLMRequest,
    ) -> LLMRequest:
        request = enrich_with_recent_conversation_context(
            conversation=conversation,
            inference_request=inference_request,
        )
        snapshot = self._snapshot_for(conversation)
        self._last_snapshot = snapshot
        if self.cognitive_planner_shadow is not None:
            self.cognitive_planner_shadow.observe_context_selection(
                conversation,
                available_conversation_turns=snapshot.sanitized_turns,
                selected_conversation_turns=snapshot.selected_turns,
                now=None,
            )
        return request

    def enrich_with_longitudinal_history(
        self,
        *,
        inference_request: LLMRequest,
        episodes: tuple[ConversationEpisode, ...],
    ) -> LLMRequest:
        if not episodes:
            return inference_request
        lines = ["[Contexto longitudinal previo]"]
        lines.extend(f"- {episode.summary}" for episode in episodes)
        prompt = f"{inference_request.prompt}\n\n" + "\n".join(lines)
        return replace(inference_request, prompt=prompt)

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
                rationale="official_context_continuity_status_completed",
            )
        if not any(trigger in normalized for trigger in self._EVALUATION_TRIGGERS):
            return None
        snapshot = self._snapshot_for(request)
        self._last_snapshot = snapshot
        return GovernedOperationalInterception(
            response_text="\n".join(
                (
                    "Evaluación de continuidad contextual:",
                    f"- Sesión: {snapshot.session_id}",
                    f"- Turnos recibidos: {snapshot.input_turns}",
                    f"- Turnos sanitizados: {snapshot.sanitized_turns}",
                    f"- Turnos seleccionados: {snapshot.selected_turns}",
                    f"- Turnos descartados: {snapshot.removed_turns}",
                    "- Alcance: propietario y sesión actuales.",
                    "- Proveedores, red y mutaciones: no ejecutados.",
                )
            ),
            rationale="official_context_continuity_evaluation_completed",
        )

    def _snapshot_for(
        self, request: GovernedConversationPipelineRequest
    ) -> ContextContinuityRuntimeSnapshot:
        sanitized = sanitize_conversation_history(request.recent_context)
        selected = curate_recent_conversation_context(
            current_text=request.text,
            recent_context=sanitized.context,
        )
        return ContextContinuityRuntimeSnapshot(
            owner=request.owner,
            session_id=request.session_id,
            input_turns=len(request.recent_context),
            sanitized_turns=len(sanitized.context),
            selected_turns=len(selected),
            removed_turns=len(request.recent_context) - len(selected),
            context_applied=bool(selected),
        )

    def _status_response(self) -> str:
        snapshot = self.snapshot
        if snapshot is None:
            return (
                "Runtime de continuidad contextual disponible, sin evaluaciones "
                "previas. Opera únicamente con historial explícito de la misma "
                "sesión."
            )
        return "\n".join(
            (
                "Estado del runtime de continuidad contextual:",
                f"- Propietario: {snapshot.owner}",
                f"- Sesión: {snapshot.session_id}",
                f"- Últimos turnos seleccionados: {snapshot.selected_turns}",
                f"- Contexto aplicado: {'sí' if snapshot.context_applied else 'no'}",
                "- Alcance aislado por propietario y sesión.",
            )
        )
