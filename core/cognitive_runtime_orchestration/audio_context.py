from __future__ import annotations

from dataclasses import dataclass

from core.intelligent_audio import AudioEvent, AudioEventType
from core.llm_provider import LLMRequest

from .models import CognitiveRuntimeContribution, CognitiveRuntimeStageStatus

AUDIO_CONTEXT_STAGE = "audio_context"


@dataclass(frozen=True)
class GovernedAudioCognitiveContextBridge:
    """Project one governed ready utterance into transient cognition."""

    event: AudioEvent | None = None
    name: str = AUDIO_CONTEXT_STAGE

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now,
    ) -> CognitiveRuntimeContribution:
        del text, request, now
        return self.build(self.event, owner=owner, session_id=session_id)

    def build(
        self,
        event: AudioEvent | None,
        *,
        owner: str,
        session_id: str,
    ) -> CognitiveRuntimeContribution:
        owner = owner.strip()
        session_id = session_id.strip()
        if not owner or not session_id:
            raise ValueError("audio cognitive projection requires owner and session")
        if event is None:
            return self._skipped("audio_context:not_supplied")
        if event.event_type is not AudioEventType.UTTERANCE_READY:
            return self._skipped(
                f"audio_context:not_ready:{event.event_type.value}"
            )
        if not event.transcript:
            return self._skipped("audio_context:ready_utterance_blank")

        return CognitiveRuntimeContribution(
            stage=AUDIO_CONTEXT_STAGE,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                "Evidencia auditiva gobernada: úsala como contexto perceptivo "
                "subordinado; no certifica verdad.",
                f"transcripción_audio={event.transcript}",
            ),
            reference_ids=(event.event_id,),
            rationale=(
                "audio_utterance_ready_upstream",
                "audio_semantics_projected_for_transient_cognitive_use",
                "audio_evidence_remains_non_authoritative",
                "no_memory_learning_or_execution_authority",
            ),
        )

    @staticmethod
    def _skipped(reason: str) -> CognitiveRuntimeContribution:
        return CognitiveRuntimeContribution(
            stage=AUDIO_CONTEXT_STAGE,
            status=CognitiveRuntimeStageStatus.SKIPPED,
            rationale=(reason,),
        )
