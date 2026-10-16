from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

from .models import (
    InMemoryROBYVoiceStyleRepository,
    ROBYVoiceStyleConfig,
    ROBYVoiceStyleRepository,
    ROBYVoiceStyleRequest,
    ROBYVoiceStyleResult,
    VoicePolicyAction,
    VoicePolicyStatus,
    greeting_allows_style,
)


class ROBYVoiceStylePolicy:
    """Applies ROBY's stable conversational voice to generated text."""

    _FORBIDDEN = (
        "recibido",
        "comando aceptado",
        "solicitud procesada",
        "puedo asistirle",
        "en que puedo asistirle",
    )

    def __init__(
        self,
        *,
        config: ROBYVoiceStyleConfig | None = None,
        repository: ROBYVoiceStyleRepository | None = None,
    ) -> None:
        self.config = config or ROBYVoiceStyleConfig()
        self.repository = repository or InMemoryROBYVoiceStyleRepository()

    @property
    def last_result(self) -> ROBYVoiceStyleResult | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def apply(
        self,
        request: ROBYVoiceStyleRequest,
        *,
        now: datetime | None = None,
    ) -> ROBYVoiceStyleResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("voice policy timestamp must be timezone-aware")
        result = self._apply(request, timestamp)
        self.repository.add(result)
        return result

    def _apply(
        self,
        request: ROBYVoiceStyleRequest,
        timestamp: datetime,
    ) -> ROBYVoiceStyleResult:
        if not request.style_requested:
            return self._inactive(
                request,
                timestamp,
                VoicePolicyStatus.NOT_APPLICABLE,
                VoicePolicyAction.NONE,
                "voice_style_not_requested",
            )
        if not greeting_allows_style(request.greeting_result):
            return self._inactive(
                request,
                timestamp,
                VoicePolicyStatus.WITHHELD,
                VoicePolicyAction.WITHHOLD,
                "greeting_result_not_deliverable",
            )

        original = request.greeting_result.response_text
        detected = self._contains_forbidden(original)
        if detected and self.config.forbid_bureaucratic_phrases:
            return self._inactive(
                request,
                timestamp,
                VoicePolicyStatus.WITHHELD,
                VoicePolicyAction.WITHHOLD,
                "bureaucratic_phrase_rejected",
                original_text=original,
                bureaucratic_phrase_detected=True,
            )

        response = self._normalize(original)
        if len(response) > self.config.max_response_length:
            raise ValueError("voice response exceeds configured maximum length")
        return ROBYVoiceStyleResult(
            request=request,
            status=VoicePolicyStatus.APPLIED,
            action=VoicePolicyAction.DELIVER,
            original_text=original,
            response_text=response,
            normalized=response != original,
            natural=True,
            bureaucratic_phrase_detected=detected,
            provider_call_allowed=False,
            network_access_allowed=False,
            platform_mutation_allowed=False,
            rationale=("roby_voice_style_applied",),
            created_at=timestamp,
        )

    def _normalize(self, text: str) -> str:
        response = re.sub(r"\s+", " ", text).strip()
        if self.config.strip_diacritics:
            response = "".join(
                char
                for char in unicodedata.normalize("NFD", response)
                if unicodedata.category(char) != "Mn"
            )
        return response

    def _contains_forbidden(self, text: str) -> bool:
        normalized = self._normalize(text).casefold()
        return any(phrase in normalized for phrase in self._FORBIDDEN)

    @staticmethod
    def _inactive(
        request: ROBYVoiceStyleRequest,
        timestamp: datetime,
        status: VoicePolicyStatus,
        action: VoicePolicyAction,
        rationale: str,
        *,
        original_text: str = "",
        bureaucratic_phrase_detected: bool = False,
    ) -> ROBYVoiceStyleResult:
        return ROBYVoiceStyleResult(
            request=request,
            status=status,
            action=action,
            original_text=original_text,
            response_text="",
            normalized=False,
            natural=False,
            bureaucratic_phrase_detected=bureaucratic_phrase_detected,
            provider_call_allowed=False,
            network_access_allowed=False,
            platform_mutation_allowed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )
