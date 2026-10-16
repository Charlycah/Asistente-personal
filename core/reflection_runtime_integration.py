from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from core.adaptive_cognition import ReflectionOutcome, ReflectionRecord
from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.llm_provider import LLMRequest

AdaptiveReflectionSource = Callable[..., ReflectionRecord | None]


@dataclass(frozen=True)
class ReflectionRuntimeContributor:
    """Project governed adaptive reflection into the current turn."""

    source: AdaptiveReflectionSource
    name: str = "reflection"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del request
        record = self.source(
            owner=owner,
            session_id=session_id,
            text=text,
            now=now,
        )
        if record is None:
            return self._skipped("adaptive_reflection_unavailable")

        outcome = record.normalized_outcome
        references = (
            record.record_id,
            *record.assessment_ids,
            *(item.observation_id for item in record.observations),
            *record.episode_ids,
            *record.mental_model_ids,
        )
        if record.requires_review:
            return self._skipped(
                f"adaptive_reflection_{outcome.value}_requires_review",
                references,
            )
        if outcome is ReflectionOutcome.INSUFFICIENT:
            return CognitiveRuntimeContribution(
                stage=self.name,
                status=CognitiveRuntimeStageStatus.APPLIED,
                prompt_lines=(
                    "La reflexión adaptativa considera insuficiente el historial; "
                    "no inferir patrones estables y responder con cautela.",
                ),
                reference_ids=references,
                rationale=("adaptive_reflection_insufficient_applied",),
            )

        lines = [
            f"Reflexión adaptativa: {record.summary}",
            f"Resultado de la reflexión: {outcome.value}.",
            "Usar la reflexión solo para revisar la respuesta; no reescribir "
            "decisiones ni ejecutar recomendaciones.",
        ]
        for observation in record.observations[:4]:
            lines.append(
                "Observación reflexiva "
                f"({observation.normalized_importance.value}): "
                f"{observation.description}"
            )
        for recommendation in record.recommendations[:3]:
            lines.append(f"Recomendación consultiva: {recommendation}")

        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=tuple(lines),
            reference_ids=references,
            rationale=("adaptive_reflection_context_applied",),
        )

    def _skipped(
        self,
        rationale: str,
        reference_ids: tuple[str, ...] = (),
    ) -> CognitiveRuntimeContribution:
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.SKIPPED,
            reference_ids=reference_ids,
            rationale=(rationale,),
        )
