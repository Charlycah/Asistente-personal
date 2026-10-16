from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

from .ambient_context_runtime import OfficialAmbientContextRuntimeGateway
from .device_runtime import OfficialDeviceRuntimeGateway
from .presence_runtime import OfficialPresenceRuntimeGateway
from .voice_style_runtime import OfficialVoiceStyleRuntimeGateway


@dataclass(frozen=True)
class MultimodalConversationRequest:
    owner: str
    session_id: str
    text: str
    modalities: tuple[str, ...] = ("text",)
    explicit_consent: tuple[str, ...] = ()
    device_id: str | None = None

    def __post_init__(self) -> None:
        if (
            not self.owner.strip()
            or not self.session_id.strip()
            or not self.text.strip()
        ):
            raise ValueError("multimodal request identity and text must not be blank")
        normalized = tuple(
            dict.fromkeys(item.strip().casefold() for item in self.modalities)
        )
        if not normalized or any(not item for item in normalized):
            raise ValueError("multimodal request modalities must not be blank")
        object.__setattr__(self, "modalities", normalized)
        object.__setattr__(
            self,
            "explicit_consent",
            tuple(
                dict.fromkeys(item.strip().casefold() for item in self.explicit_consent)
            ),
        )


@dataclass(frozen=True)
class MultimodalConversationResult:
    request: MultimodalConversationRequest
    status: str
    active_modalities: tuple[str, ...]
    withheld_modalities: tuple[str, ...]
    presence_observed: bool
    ambient_context_available: bool
    voice_style_available: bool
    mobile_mode_declared: bool
    hardware_access_performed: bool
    automation_performed: bool
    created_at: datetime


@dataclass(frozen=True)
class MultimodalConversationSnapshot:
    evaluations: int
    last_status: str | None
    last_active_modalities: tuple[str, ...]
    last_withheld_modalities: tuple[str, ...]


class OfficialMultimodalConversationIntegrationGateway:
    """Coordinates declared modalities without implicit sensor or device access."""

    _SENSITIVE_MODALITIES = frozenset(
        {"voice", "ambient", "camera", "mobile", "device"}
    )
    _SUPPORTED_MODALITIES = frozenset(
        {"text", "voice", "ambient", "presence", "mobile", "device"}
    )

    def __init__(
        self,
        *,
        presence_runtime: OfficialPresenceRuntimeGateway,
        voice_style_runtime: OfficialVoiceStyleRuntimeGateway,
        ambient_context_runtime: OfficialAmbientContextRuntimeGateway,
        device_runtime: OfficialDeviceRuntimeGateway,
    ) -> None:
        self.presence_runtime = presence_runtime
        self.voice_style_runtime = voice_style_runtime
        self.ambient_context_runtime = ambient_context_runtime
        self.device_runtime = device_runtime
        self._evaluations = 0
        self._last_result: MultimodalConversationResult | None = None

    @property
    def snapshot(self) -> MultimodalConversationSnapshot:
        last = self._last_result
        return MultimodalConversationSnapshot(
            evaluations=self._evaluations,
            last_status=last.status if last is not None else None,
            last_active_modalities=last.active_modalities if last is not None else (),
            last_withheld_modalities=(
                last.withheld_modalities if last is not None else ()
            ),
        )

    def evaluate(
        self,
        request: MultimodalConversationRequest,
        *,
        now: datetime,
    ) -> MultimodalConversationResult:
        if now.tzinfo is None:
            raise ValueError("multimodal evaluation timestamp must be timezone-aware")
        unsupported = tuple(
            modality
            for modality in request.modalities
            if modality not in self._SUPPORTED_MODALITIES
        )
        consent = frozenset(request.explicit_consent)
        withheld = list(unsupported)
        active: list[str] = []
        for modality in request.modalities:
            if modality in unsupported:
                continue
            if modality in self._SENSITIVE_MODALITIES and modality not in consent:
                withheld.append(modality)
                continue
            active.append(modality)

        presence_observed = "presence" in active
        if presence_observed:
            self.presence_runtime.manager.observe_user_turn(request.text, now=now)

        result = MultimodalConversationResult(
            request=request,
            status="ready" if active else "withheld",
            active_modalities=tuple(active),
            withheld_modalities=tuple(withheld),
            presence_observed=presence_observed,
            ambient_context_available=(
                "ambient" in active
                and self.ambient_context_runtime.snapshot is not None
            ),
            voice_style_available="voice" in active,
            mobile_mode_declared="mobile" in active,
            hardware_access_performed=False,
            automation_performed=False,
            created_at=now,
        )
        self._evaluations += 1
        self._last_result = result
        return result

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        del now
        normalized = request.text.strip().casefold()
        if (
            "estado de integración multimodal" in normalized
            or "estado de integracion multimodal" in normalized
        ):
            snapshot = self.snapshot
            return GovernedOperationalInterception(
                response_text=(
                    "Estado de Multimodal Conversation Integration:\n"
                    f"- Evaluaciones: {snapshot.evaluations}\n"
                    f"- Último estado: {snapshot.last_status or 'ninguno'}\n"
                    "- Modalidades activas: "
                    f"{', '.join(snapshot.last_active_modalities) or 'ninguna'}\n"
                    "- Hardware y automatización: no ejecutados."
                ),
                rationale="multimodal_conversation_status_completed",
            )
        if (
            "audita integración multimodal" in normalized
            or "audita integracion multimodal" in normalized
        ):
            return GovernedOperationalInterception(
                response_text=(
                    "Auditoría de Multimodal Conversation Integration:\n"
                    "- Voz, ambiente, móvil y dispositivo requieren consentimiento.\n"
                    "- Presencia se registra solo por solicitud estructurada.\n"
                    "- Sensores, cámara, micrófono y automatización: cerrados."
                ),
                rationale="multimodal_conversation_audit_completed",
            )
        return None
