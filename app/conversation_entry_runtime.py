from __future__ import annotations

from dataclasses import dataclass

from core.conversation_entry_point import ConversationEntryPoint
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class ConversationEntryRuntimeSnapshot:
    kind: str
    action: str
    normalized_text: str
    addressed_to_roby: bool


class OfficialConversationEntryRuntimeGateway:
    """Explicit diagnostic facade over ROBY's deterministic entry classifier."""

    _CLASSIFY_PREFIXES = (
        "clasificá entrada conversacional:",
        "clasifica entrada conversacional:",
        "evaluá entrada conversacional:",
        "evalua entrada conversacional:",
    )
    _STATUS_TRIGGERS = (
        "estado del clasificador conversacional",
        "estado de entrada conversacional",
    )

    def __init__(self, classifier: ConversationEntryPoint | None = None) -> None:
        self.classifier = classifier or ConversationEntryPoint()
        self._last_snapshot: ConversationEntryRuntimeSnapshot | None = None

    @property
    def snapshot(self) -> ConversationEntryRuntimeSnapshot | None:
        return self._last_snapshot

    def evaluate_text(self, text: str) -> ConversationEntryRuntimeSnapshot:
        """Classify one conversational entry through the public runtime contract."""
        normalized_text = self.classifier._normalize(text)
        addressed = self.classifier._addressed_to_roby(normalized_text)
        semantic_text = self.classifier._remove_assistant_name(normalized_text)
        if not semantic_text:
            kind = "attention" if addressed else "incomplete"
            action = "route_to_attention" if addressed else "request_completion"
        else:
            kind_value, action_value, _ = self.classifier._intent(semantic_text)
            kind = kind_value.value
            action = action_value.value
        snapshot = ConversationEntryRuntimeSnapshot(
            kind=kind,
            action=action,
            normalized_text=normalized_text,
            addressed_to_roby=addressed,
        )
        self._last_snapshot = snapshot
        return snapshot

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._status_response(),
                rationale="official_conversation_entry_status_completed",
            )
        text = self._extract_text(request.text)
        if text is None:
            return None
        if not text:
            return GovernedOperationalInterception(
                response_text="Indicá el texto después de los dos puntos.",
                rationale="official_conversation_entry_text_required",
            )
        snapshot = self.evaluate_text(text)
        kind = snapshot.kind
        action = snapshot.action
        addressed = snapshot.addressed_to_roby
        return GovernedOperationalInterception(
            response_text="\n".join(
                (
                    "Clasificación de entrada conversacional:",
                    f"- Tipo: {kind}",
                    f"- Ruta sugerida: {action}",
                    f"- Dirigido a Roby: {'sí' if addressed else 'no'}",
                    "- Ejecución y llamadas externas: no autorizadas.",
                )
            ),
            rationale="official_conversation_entry_classification_completed",
        )

    def _extract_text(self, text: str) -> str | None:
        normalized = text.strip().casefold()
        for prefix in self._CLASSIFY_PREFIXES:
            if normalized.startswith(prefix):
                return text.strip()[len(prefix) :].strip()
        return None

    def _status_response(self) -> str:
        if self.snapshot is None:
            return (
                "Clasificador conversacional disponible, sin evaluaciones previas. "
                "No genera respuestas ni ejecuta acciones."
            )
        return "\n".join(
            (
                "Estado del clasificador conversacional:",
                f"- Último tipo: {self.snapshot.kind}",
                f"- Última ruta: {self.snapshot.action}",
                f"- Texto normalizado: {self.snapshot.normalized_text}",
            )
        )
