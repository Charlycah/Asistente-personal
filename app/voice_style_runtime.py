from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.natural_greeting_response import NaturalGreetingStatus
from core.roby_voice_style_policy import (
    ROBYVoiceStylePolicy,
    ROBYVoiceStyleRequest,
    VoicePolicyStatus,
)


@dataclass(frozen=True)
class VoiceStyleRuntimeSnapshot:
    status: str
    original_text: str
    response_text: str
    normalized: bool
    bureaucratic_phrase_detected: bool
    policy_id: str


class OfficialVoiceStyleRuntimeGateway:
    """Explicit operational facade over ROBY's deterministic voice policy."""

    _EVALUATION_PREFIXES = (
        "evaluá el estilo de voz:",
        "evalua el estilo de voz:",
        "revisá el estilo de voz:",
        "revisa el estilo de voz:",
        "aplicá el estilo de roby:",
        "aplica el estilo de roby:",
    )
    _STATUS_TRIGGERS = (
        "estado del estilo de voz",
        "estado de tu estilo de voz",
        "cómo está tu estilo de voz",
        "como esta tu estilo de voz",
    )

    def __init__(self, policy: ROBYVoiceStylePolicy | None = None) -> None:
        self.policy = policy or ROBYVoiceStylePolicy()
        self._last_snapshot: VoiceStyleRuntimeSnapshot | None = None

    @property
    def snapshot(self) -> VoiceStyleRuntimeSnapshot | None:
        return self._last_snapshot

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._status_response(),
                rationale="official_voice_style_runtime_status_completed",
            )
        text = self._extract_text(request.text)
        if text is None:
            return None
        if not text:
            return GovernedOperationalInterception(
                response_text="Indicá el texto después de los dos puntos.",
                rationale="official_voice_style_runtime_text_required",
            )
        result = self.policy.apply(
            ROBYVoiceStyleRequest(
                owner=request.owner,
                greeting_result=self._synthetic_greeting(request.owner, text),
            ),
            now=now,
        )
        self._last_snapshot = VoiceStyleRuntimeSnapshot(
            status=result.status.value,
            original_text=result.original_text,
            response_text=result.response_text,
            normalized=result.normalized,
            bureaucratic_phrase_detected=result.bureaucratic_phrase_detected,
            policy_id=result.policy_id,
        )
        if result.status is VoicePolicyStatus.APPLIED:
            response = "\n".join(
                (
                    "Evaluación del estilo de voz oficial:",
                    f"- Resultado: {result.response_text}",
                    f"- Normalizado: {'sí' if result.normalized else 'no'}",
                    "- Efectos externos: ninguno.",
                )
            )
        else:
            response = "\n".join(
                (
                    "Evaluación del estilo de voz oficial:",
                    "- Resultado: retenido por la política de voz.",
                    "- Motivo: lenguaje burocrático o no natural detectado.",
                    "- Efectos externos: ninguno.",
                )
            )
        return GovernedOperationalInterception(
            response_text=response,
            rationale="official_voice_style_runtime_evaluation_completed",
        )

    def _status_response(self) -> str:
        if self.snapshot is None:
            return (
                "Runtime de estilo de voz oficial: disponible, sin evaluaciones "
                "registradas. Solo se aplica por solicitud explícita."
            )
        return "\n".join(
            (
                "Estado del runtime de estilo de voz:",
                f"- Último estado: {self.snapshot.status}",
                f"- Normalizado: {'sí' if self.snapshot.normalized else 'no'}",
                "- Activación: únicamente por solicitud explícita.",
            )
        )

    def _extract_text(self, text: str) -> str | None:
        normalized = text.strip().casefold()
        for prefix in self._EVALUATION_PREFIXES:
            if normalized.startswith(prefix):
                return text.strip()[len(prefix) :].strip()
        return None

    @staticmethod
    def _synthetic_greeting(owner: str, text: str):
        return SimpleNamespace(
            request=SimpleNamespace(owner=owner),
            status=NaturalGreetingStatus.GENERATED,
            response_text=text,
            natural=True,
            greeting_id=f"voice-style:{owner.casefold()}:{text}",
        )
