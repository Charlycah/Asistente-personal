from __future__ import annotations

import inspect

from app import runtime_root_factory
from app.governed_stored_image_runtime_wiring import (
    GovernedStoredImageConversationInterceptionPort,
    build_governed_stored_image_runtime,
)


def test_g4g_stored_image_runtime_requires_existing_semantic_composition():
    parameters = inspect.signature(build_governed_stored_image_runtime).parameters

    assert "semantic_composition" in parameters


def test_g4g_port_receives_semantic_composition_by_injection():
    parameters = inspect.signature(
        GovernedStoredImageConversationInterceptionPort.__init__
    ).parameters

    assert "semantic_composition" in parameters


def test_g4g_port_exposes_s3d_subordinate_cognitive_reentry():
    source = inspect.getsource(GovernedStoredImageConversationInterceptionPort)

    assert "analyze_image_for_cognitive_convergence" in source
    assert "self.analyze_image(" in source
    assert ".visual_observation" in source
    assert ".objects" in source
    assert ".compose(" in source


def test_g4g_root_provisions_one_existing_m128_m133_composition():
    source = inspect.getsource(runtime_root_factory.build_runtime_root)

    assert source.count("GovernedVisualSemanticComposition(") == 1
    assert "VisualUnderstandingFoundationEngine(" in source
    assert "VisualObservationResolutionEngine(" in source
    assert "SceneUnderstandingEngine(" in source
    assert "ObjectKnowledgeEngine(" in source
    assert "VisualAttentionEngine(" in source
    assert "VisualContextIntegrationEngine(" in source
    assert "semantic_composition=" in source


def test_g4g_keeps_port_subordinate_to_existing_authorities():
    source = inspect.getsource(GovernedStoredImageConversationInterceptionPort)

    assert "GovernedVisualSemanticComposition(" not in source
    assert "VisualUnderstandingFoundationEngine(" not in source
    assert "VisualObservationResolutionEngine(" not in source
    assert "SceneUnderstandingEngine(" not in source
    assert "ObjectKnowledgeEngine(" not in source
    assert "VisualAttentionEngine(" not in source
    assert "VisualContextIntegrationEngine(" not in source
    assert "IntegratedVisualContext(" not in source
    assert "GovernedReasoning" not in source
    assert "CognitiveRuntimeOrchestrator" not in source
