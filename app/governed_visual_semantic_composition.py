from __future__ import annotations

from core.object_detection import ObjectDetection
from core.object_knowledge import (
    ObjectEvidence,
    ObjectKind,
    ObjectKnowledgeEngine,
    ObjectKnowledgeRequest,
)
from core.scene_understanding import (
    SceneEvidence,
    SceneUnderstandingEngine,
    SceneUnderstandingRequest,
)
from core.visual_attention import (
    VisualAttentionEngine,
    VisualAttentionEvidence,
    VisualAttentionRequest,
)
from core.visual_context_integration import (
    IntegratedVisualContext,
    VisualContextIntegrationEngine,
    VisualContextIntegrationRequest,
)
from core.visual_observation_resolution import (
    VisualObservationCandidate,
    VisualObservationPurpose,
    VisualObservationResolutionEngine,
    VisualObservationResolutionRequest,
)
from core.visual_understanding_foundation import (
    VisualObservationSignal,
    VisualUnderstandingFoundationEngine,
    VisualUnderstandingFoundationRequest,
)


class GovernedVisualSemanticComposition:
    """Composes the existing governed M128-M133 visual semantic authorities."""

    def __init__(
        self,
        *,
        foundation: VisualUnderstandingFoundationEngine,
        resolution: VisualObservationResolutionEngine,
        scene: SceneUnderstandingEngine,
        objects: ObjectKnowledgeEngine,
        attention: VisualAttentionEngine,
        integration: VisualContextIntegrationEngine,
    ) -> None:
        self._foundation = foundation
        self._resolution = resolution
        self._scene = scene
        self._objects = objects
        self._attention = attention
        self._integration = integration

    def compose(
        self,
        *,
        owner: str,
        observation: VisualObservationSignal,
        explicit_user_consent: bool,
        candidates: tuple[VisualObservationCandidate, ...] = (),
        purpose: VisualObservationPurpose = VisualObservationPurpose.GENERAL_CONTEXT,
        scene_evidence: tuple[SceneEvidence, ...] = (),
        object_evidence: tuple[ObjectEvidence, ...] = (),
        object_detection: ObjectDetection | None = None,
        attention_evidence: tuple[VisualAttentionEvidence, ...] = (),
        now=None,
    ) -> IntegratedVisualContext:
        visual_context = self._foundation.establish(
            VisualUnderstandingFoundationRequest(
                owner=owner,
                observation=observation,
                explicit_user_consent=explicit_user_consent,
            ),
            now=now,
        )
        resolved = self._resolution.resolve(
            VisualObservationResolutionRequest(
                owner=owner,
                visual_context=visual_context,
                purpose=purpose,
                candidates=candidates,
            ),
            now=now,
        )
        scene = self._scene.understand(
            SceneUnderstandingRequest(
                owner=owner,
                resolved_observation=resolved,
                evidence=scene_evidence,
            ),
            now=now,
        )
        projected_object_evidence = tuple(
            ObjectEvidence(
                evidence_ref=(
                    f"{observation.observation_ref}:"
                    f"{object_detection.detector_name}:{index}:evidence"
                ),
                observation_ref=observation.observation_ref,
                object_ref=(
                    f"{observation.observation_ref}:"
                    f"{object_detection.detector_name}:{index}:object"
                ),
                object_kind=ObjectKind.UNKNOWN,
                label=region.label,
                confidence=region.confidence,
            )
            for index, region in enumerate(
                object_detection.regions if object_detection is not None else ()
            )
        )
        objects = self._objects.build(
            ObjectKnowledgeRequest(
                owner=owner,
                scene_understanding=scene,
                evidence=object_evidence + projected_object_evidence,
            ),
            now=now,
        )
        attention = self._attention.prioritize(
            VisualAttentionRequest(
                owner=owner,
                scene_understanding=scene,
                object_knowledge=objects,
                evidence=attention_evidence,
            ),
            now=now,
        )
        return self._integration.integrate(
            VisualContextIntegrationRequest(
                owner=owner,
                visual_context=visual_context,
                resolved_observation=resolved,
                scene_understanding=scene,
                object_knowledge=objects,
                attention_plan=attention,
            ),
            now=now,
        )
