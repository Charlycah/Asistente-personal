from __future__ import annotations

from dataclasses import dataclass

from core.llm_provider import LLMRequest
from core.visual_context_integration import (
    IntegratedVisualContext,
    VisualIntegrationStatus,
)

from .models import CognitiveRuntimeContribution, CognitiveRuntimeStageStatus

VISUAL_CONTEXT_STAGE = "visual_context"


@dataclass(frozen=True)
class GovernedVisualCognitiveContextBridge:
    """Project an already-integrated visual context into transient cognition."""

    context: IntegratedVisualContext | None = None
    name: str = VISUAL_CONTEXT_STAGE

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
        return self.build(self.context, owner=owner, session_id=session_id)

    def build(
        self,
        context: IntegratedVisualContext | None,
        *,
        owner: str,
        session_id: str,
    ) -> CognitiveRuntimeContribution:
        owner = owner.strip()
        session_id = session_id.strip()
        if not owner or not session_id:
            raise ValueError("visual cognitive projection requires owner and session")
        if context is None:
            return self._skipped("visual_context:not_supplied")
        if context.request.owner.casefold() != owner.casefold():
            return self._skipped("visual_context:owner_lineage_mismatch")
        if context.status is not VisualIntegrationStatus.READY:
            return self._skipped(
                f"visual_context:not_ready:{context.status.value}"
            )

        scene = context.request.scene_understanding
        objects = context.request.object_knowledge
        attention = context.request.attention_plan
        if scene is None or objects is None or attention is None:
            return self._skipped("visual_context:semantic_lineage_incomplete")

        scene_name = (
            scene.dominant_scene.value
            if scene.dominant_scene is not None
            else "unknown"
        )
        attributes = ",".join(scene.attributes) if scene.attributes else "none"
        object_items = tuple(
            f"{item.label} x{item.count} ({item.confidence:.2f})"
            for item in objects.objects
        )
        focus_items = tuple(
            f"{item.object_ref}:{item.priority.value}"
            for item in attention.focus_items
        )
        lines = (
            "Evidencia visual gobernada: úsala como contexto perceptivo "
            "subordinado; no certifica verdad.",
            f"escena={scene_name}; atributos={attributes}",
            "objetos=" + (", ".join(object_items) if object_items else "none"),
            "atención=" + (", ".join(focus_items) if focus_items else "none"),
        )
        references = tuple(
            dict.fromkeys(
                (
                    context.integration_id,
                    context.visual_context_id or "",
                    context.resolution_id or "",
                    context.scene_understanding_id or "",
                    context.object_knowledge_id or "",
                    context.attention_plan_id or "",
                )
            )
        )
        references = tuple(item for item in references if item)
        return CognitiveRuntimeContribution(
            stage=VISUAL_CONTEXT_STAGE,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=lines,
            reference_ids=references,
            rationale=(
                "visual_context_integrated_upstream",
                "visual_semantics_projected_for_transient_cognitive_use",
                "visual_evidence_remains_non_authoritative",
                "no_memory_learning_or_execution_authority",
            ),
        )

    @staticmethod
    def _skipped(reason: str) -> CognitiveRuntimeContribution:
        return CognitiveRuntimeContribution(
            stage=VISUAL_CONTEXT_STAGE,
            status=CognitiveRuntimeStageStatus.SKIPPED,
            rationale=(reason,),
        )
