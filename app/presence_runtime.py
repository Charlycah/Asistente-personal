from __future__ import annotations

from datetime import datetime

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.presence import PresenceManager, PresenceSnapshot


class OfficialPresenceRuntimeGateway:
    """Explicit, non-autonomous access to ROBY's official presence state."""

    _STATUS_TRIGGERS = (
        "estado de presencia",
        "estado de tu presencia",
        "cómo está tu presencia",
        "como esta tu presencia",
        "presencia actual",
    )
    _OBSERVE_TRIGGERS = (
        "registrá mi presencia",
        "registra mi presencia",
        "registrá esta interacción",
        "registra esta interacción",
    )
    _SILENCE_TRIGGERS = (
        "registrá silencio",
        "registra silencio",
        "marcá silencio",
        "marca silencio",
    )
    _RESET_TRIGGERS = (
        "reiniciá la presencia",
        "reinicia la presencia",
        "reseteá la presencia",
        "resetea la presencia",
    )

    def __init__(self, manager: PresenceManager | None = None) -> None:
        self.manager = manager or PresenceManager()

    @property
    def snapshot(self) -> PresenceSnapshot | None:
        return self.manager.last_snapshot

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return self._result(
                self.snapshot,
                rationale="official_presence_status_completed",
            )
        if any(trigger in normalized for trigger in self._RESET_TRIGGERS):
            return self._result(
                self.manager.reset(now=now),
                rationale="official_presence_reset_completed",
            )
        if any(trigger in normalized for trigger in self._SILENCE_TRIGGERS):
            return self._result(
                self.manager.observe_silence(now=now),
                rationale="official_presence_silence_completed",
            )
        if any(trigger in normalized for trigger in self._OBSERVE_TRIGGERS):
            return self._result(
                self.manager.observe_user_turn(request.text, now=now),
                rationale="official_presence_observation_completed",
            )
        return None

    @staticmethod
    def _result(
        snapshot: PresenceSnapshot | None,
        *,
        rationale: str,
    ) -> GovernedOperationalInterception:
        if snapshot is None:
            text = (
                "Presencia continua: sin señales registradas. "
                "ROBY no infiere actividad ni inicia acciones autónomas."
            )
        else:
            last_seen = (
                snapshot.last_user_seen_at.isoformat()
                if snapshot.last_user_seen_at is not None
                else "sin interacción reciente"
            )
            text = "\n".join(
                (
                    "Estado oficial de presencia:",
                    f"- Modo: {snapshot.normalized_mode.value}",
                    f"- Continuidad: {snapshot.continuity_score:.2f}",
                    f"- Última interacción: {last_seen}",
                    "- Autonomía: deshabilitada; solo observación explícita.",
                )
            )
        return GovernedOperationalInterception(
            response_text=text,
            rationale=rationale,
        )
