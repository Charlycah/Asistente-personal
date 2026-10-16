from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.ambient_context_foundation import (
    AmbientContextFoundationEngine,
    AmbientContextFoundationRequest,
    AmbientFoundationStatus,
    AmbientObservationSignal,
    AmbientObservationSource,
    AmbientPrivacyLevel,
    AmbientScope,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class AmbientContextRuntimeSnapshot:
    status: str
    observation_ref: str
    context_resolution_required: bool
    automation_allowed: bool
    context_id: str


class OfficialAmbientContextRuntimeGateway:
    """Explicit facade over ROBY's governed ambient-context foundation."""

    _REGISTER_PREFIXES = (
        "registrá contexto ambiental:",
        "registra contexto ambiental:",
        "declará contexto ambiental:",
        "declara contexto ambiental:",
    )
    _STATUS_TRIGGERS = (
        "estado del contexto ambiental",
        "estado de tu contexto ambiental",
        "contexto ambiental actual",
    )

    def __init__(self, engine: AmbientContextFoundationEngine | None = None) -> None:
        self.engine = engine or AmbientContextFoundationEngine()
        self._last_snapshot: AmbientContextRuntimeSnapshot | None = None

    @property
    def snapshot(self) -> AmbientContextRuntimeSnapshot | None:
        return self._last_snapshot

    def intercept(self, request: GovernedConversationPipelineRequest, *, now: datetime):
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._status_response(),
                rationale="official_ambient_context_status_completed",
            )
        observation_ref = self._extract_observation(request.text)
        if observation_ref is None:
            return None
        if not observation_ref:
            return GovernedOperationalInterception(
                response_text="Indicá la observación después de los dos puntos.",
                rationale="official_ambient_context_observation_required",
            )
        context = self.engine.establish(
            AmbientContextFoundationRequest(
                owner=request.owner,
                observation=AmbientObservationSignal(
                    observation_ref=observation_ref,
                    source=AmbientObservationSource.DESKTOP_DEVICE,
                    scope=AmbientScope.PERSONAL,
                    privacy_level=AmbientPrivacyLevel.PERSONAL,
                    confidence=1.0,
                    observed_at=now,
                    externally_supplied=False,
                ),
                ambient_context_declared=True,
                explicit_user_consent=True,
            ),
            now=now,
        )
        self._last_snapshot = AmbientContextRuntimeSnapshot(
            status=context.status.value,
            observation_ref=observation_ref,
            context_resolution_required=context.context_resolution_required,
            automation_allowed=context.automation_allowed,
            context_id=context.context_id,
        )
        return GovernedOperationalInterception(
            response_text=self._context_response(context.status),
            rationale="official_ambient_context_registration_completed",
        )

    def _extract_observation(self, text: str) -> str | None:
        normalized = text.strip().casefold()
        for prefix in self._REGISTER_PREFIXES:
            if normalized.startswith(prefix):
                return text.strip()[len(prefix) :].strip()
        return None

    def _status_response(self) -> str:
        if self.snapshot is None:
            return (
                "Runtime de contexto ambiental: disponible, sin observaciones "
                "declaradas. No usa sensores ni inferencias silenciosas."
            )
        return "\n".join(
            (
                "Estado del contexto ambiental oficial:",
                f"- Estado: {self.snapshot.status}",
                f"- Observación: {self.snapshot.observation_ref}",
                "- Automatización: deshabilitada.",
                "- Activación: únicamente por declaración explícita.",
            )
        )

    @staticmethod
    def _context_response(status: AmbientFoundationStatus) -> str:
        if status is AmbientFoundationStatus.READY:
            return "\n".join(
                (
                    "Contexto ambiental declarado y gobernado:",
                    "- Observación disponible para resolución contextual.",
                    "- Inferencias de presencia o actividad: deshabilitadas.",
                    "- Automatización: deshabilitada.",
                )
            )
        return (
            "El contexto ambiental requiere revisión y no habilitó ninguna "
            "capacidad de interpretación o automatización."
        )
