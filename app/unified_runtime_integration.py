from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from infrastructure.camera.camera_adapter import CameraAdapter
from infrastructure.mail.mail_adapter import MailReaderAdapter

from .voice_input import VoiceRequestTranscriber
from .voice_output import VoiceResponseReader


@dataclass(frozen=True)
class UnifiedRuntimeIntegrationSnapshot:
    evaluations: int
    handled_turns: int
    last_capability: str | None


class MailReaderConversationInterceptionPort:
    """Expose the existing read-only mail adapter to natural conversation."""

    _TRIGGERS = (
        "correo",
        "correos",
        "mail",
        "emails",
        "e-mails",
        "mostramelos",
        "mostrámelos",
    )

    def __init__(self, adapter: MailReaderAdapter) -> None:
        self.adapter = adapter
        self._last_mail_request = False

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        normalized = request.text.strip().casefold()
        follow_up = normalized in {"mostramelos", "mostrámelos", "mostrame", "mostráme"}
        if not any(trigger in normalized for trigger in self._TRIGGERS) and not (
            follow_up and self._last_mail_request
        ):
            return None
        self._last_mail_request = True
        unread_only = "nuevo" in normalized or "sin leer" in normalized
        result = self.adapter.read_mail(
            {
                "action": "summary",
                "unread_only": unread_only,
            }
        )
        return GovernedOperationalInterception(
            response_text=str(result["natural_summary"]),
            rationale="unified_runtime_mail_read_completed",
        )


class MailUnavailableConversationInterceptionPort:
    """Reserve mail requests when Gmail/IMAP is not configured."""

    _TRIGGERS = ("correo", "correos", "mail", "email", "mostramelos", "mostrámelos")

    def __init__(self, reason: str = "not_configured") -> None:
        self.reason = reason

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        normalized = request.text.strip().casefold()
        if not any(trigger in normalized for trigger in self._TRIGGERS):
            return None
        return GovernedOperationalInterception(
            response_text=(
                "No tengo acceso real a tu correo en este momento. "
                "Configurá Gmail o IMAP en las credenciales y recién ahí "
                "puedo mostrarte mensajes reales."
            ),
            rationale=f"mail_unavailable_{self.reason}",
        )


class CameraConversationInterceptionPort:
    """Expose camera capture only after the governed consent route allows it."""

    _TRIGGERS = (
        "captura una imagen",
        "saca una foto",
        "sacá una foto",
        "usar la camara",
        "usar la cámara",
        "activa la camara",
        "activá la cámara",
    )

    def __init__(self, adapter: CameraAdapter) -> None:
        self.adapter = adapter

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        normalized = request.text.strip().casefold()
        if not any(trigger in normalized for trigger in self._TRIGGERS):
            return None
        result = self.adapter.capture({})
        return GovernedOperationalInterception(
            response_text=str(result["natural_summary"]),
            rationale="unified_runtime_camera_capture_completed",
        )


class VoiceRuntimeConversationInterceptionPort:
    """Connect existing voice input/output boundaries to the official registry."""

    def __init__(
        self,
        *,
        transcriber: VoiceRequestTranscriber,
        response_reader: VoiceResponseReader,
        response_factory: Callable[[str], object] | None = None,
    ) -> None:
        self.transcriber = transcriber
        self.response_reader = response_reader
        self.response_factory = response_factory

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        normalized = request.text.strip().casefold()
        if normalized in {"escuchar", "escuchame", "escuchá", "entrada por voz"}:
            transcription = self.transcriber.transcribe()
            text = transcription or "No recibi una entrada de voz util."
            return GovernedOperationalInterception(
                response_text=text,
                rationale="unified_runtime_voice_input_completed",
            )
        prefix = next(
            (
                item
                for item in ("leer en voz alta:", "lee en voz alta:")
                if normalized.startswith(item)
            ),
            None,
        )
        if prefix is None:
            return None
        spoken_text = request.text[len(prefix) :].strip()
        if not spoken_text:
            return GovernedOperationalInterception(
                response_text="Decime que texto queres que lea.",
                rationale="unified_runtime_voice_output_missing_text",
            )
        if self.response_factory is not None:
            self.response_reader.read(self.response_factory(spoken_text))
        return GovernedOperationalInterception(
            response_text="Listo. Lei el texto mediante la salida de voz configurada.",
            rationale="unified_runtime_voice_output_completed",
        )


class UnifiedRuntimeIntegrationGateway:
    """Observability facade for formerly isolated operational adapters."""

    _TRIGGERS = (
        "estado de integracion",
        "estado de integración",
        "modulos integrados",
        "módulos integrados",
        "runtime unificado",
    )

    def __init__(self, connected_names: tuple[str, ...]) -> None:
        self.connected_names = connected_names
        self._evaluations = 0
        self._handled_turns = 0
        self._last_capability: str | None = None

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        self._evaluations += 1
        normalized = request.text.strip().casefold()
        if not any(trigger in normalized for trigger in self._TRIGGERS):
            return None
        self._handled_turns += 1
        self._last_capability = "runtime.integration"
        lines = [
            "Runtime unificado operativo.",
            "Capacidades conectadas por X.6:",
            *(f"- {name}" for name in self.connected_names),
        ]
        return GovernedOperationalInterception(
            response_text="\n".join(lines),
            rationale="unified_runtime_integration_inspection_completed",
        )

    def snapshot(self) -> UnifiedRuntimeIntegrationSnapshot:
        return UnifiedRuntimeIntegrationSnapshot(
            evaluations=self._evaluations,
            handled_turns=self._handled_turns,
            last_capability=self._last_capability,
        )
