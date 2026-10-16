from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from app.governed_stored_image_runtime_wiring import (
    GovernedStoredImageConversationInterceptionPort,
)
from app.governed_visual_semantic_composition import GovernedVisualSemanticComposition
from core.object_knowledge import ObjectKnowledgeEngine
from core.scene_understanding import SceneUnderstandingEngine
from core.visual_attention import VisualAttentionEngine
from core.visual_context_integration import (
    IntegratedVisualContext,
    VisualContextIntegrationEngine,
)
from core.visual_observation_resolution import VisualObservationResolutionEngine
from core.visual_understanding_foundation import (
    VisualMediaType,
    VisualObservationSignal,
    VisualObservationSource,
    VisualPrivacyLevel,
    VisualUnderstandingFoundationEngine,
)


class _GatewayStub:
    def analyze_stored_image(self, request):
        return SimpleNamespace(
            image_id=request.image_id,
            owner=request.owner,
            sha256="a" * 64,
            mime_type="image/png",
            source_ref=f"stored_image:{request.image_id}",
            analysis=SimpleNamespace(
                source_ref=f"stored_image:{request.image_id}",
                visual_observation=VisualObservationSignal(
                    observation_ref=f"stored_image:{request.image_id}",
                    source=VisualObservationSource.IMAGE_FILE,
                    media_type=VisualMediaType.PHOTO,
                    privacy_level=VisualPrivacyLevel.PERSONAL,
                    confidence=1.0,
                ),
                objects=None,
            ),
        )


def _semantic_composition() -> GovernedVisualSemanticComposition:
    return GovernedVisualSemanticComposition(
        foundation=VisualUnderstandingFoundationEngine(),
        resolution=VisualObservationResolutionEngine(),
        scene=SceneUnderstandingEngine(),
        objects=ObjectKnowledgeEngine(),
        attention=VisualAttentionEngine(),
        integration=VisualContextIntegrationEngine(),
    )


def _port() -> GovernedStoredImageConversationInterceptionPort:
    return GovernedStoredImageConversationInterceptionPort(
        _GatewayStub(),
        semantic_composition=_semantic_composition(),
    )


def test_lx1_s3d_existing_port_exposes_subordinate_cognitive_projection():
    port = _port()

    assert hasattr(port, "analyze_image_for_cognitive_convergence")


def test_lx1_s3d_projection_requires_fresh_explicit_consent():
    port = _port()

    with pytest.raises(PermissionError):
        port.analyze_image_for_cognitive_convergence(
            owner="Carlos",
            image_id="a" * 32,
            explicit_user_consent=False,
        )


def test_lx1_s3d_projection_returns_existing_integrated_visual_context():
    port = _port()

    result = port.analyze_image_for_cognitive_convergence(
        owner="Carlos",
        image_id="a" * 32,
        explicit_user_consent=True,
    )

    assert isinstance(result, IntegratedVisualContext)
    assert result.request.owner == "Carlos"


def test_lx1_s3d_projection_preserves_stored_image_source_lineage():
    port = _port()

    result = port.analyze_image_for_cognitive_convergence(
        owner="Carlos",
        image_id="a" * 32,
        explicit_user_consent=True,
    )

    observation = result.request.visual_context.request.observation
    assert observation.observation_ref == "stored_image:" + "a" * 32


def test_lx1_s3d_port_does_not_import_or_own_reasoning_authority():
    source = inspect.getsource(GovernedStoredImageConversationInterceptionPort)

    assert "Reasoning" not in source
    assert "reasoning" not in source
    assert "CognitiveRuntimeOrchestrator" not in source
