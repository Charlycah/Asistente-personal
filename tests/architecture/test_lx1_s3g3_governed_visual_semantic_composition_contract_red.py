from __future__ import annotations

import importlib
import inspect

MODULE = "app.governed_visual_semantic_composition"
CLASS = "GovernedVisualSemanticComposition"


def _module():
    return importlib.import_module(MODULE)


def _source() -> str:
    return inspect.getsource(_module())


def test_lx1_s3g3_exposes_one_subordinate_visual_semantic_composition_seam():
    module = _module()

    assert hasattr(module, CLASS)


def test_lx1_s3g3_composition_reuses_existing_m128_through_m133_engines():
    source = _source()

    required = (
        "VisualUnderstandingFoundationEngine",
        "VisualObservationResolutionEngine",
        "SceneUnderstandingEngine",
        "ObjectKnowledgeEngine",
        "VisualAttentionEngine",
        "VisualContextIntegrationEngine",
    )
    assert all(name in source for name in required)


def test_lx1_s3g3_m133_remains_the_only_integrated_context_authority():
    source = _source()

    assert ".integrate(" in source
    assert "IntegratedVisualContext(" not in source


def test_lx1_s3g3_composition_preserves_governed_evidence_and_lineage():
    source = _source()

    required = (
        "SceneEvidence",
        "ObjectEvidence",
        "VisualAttentionEvidence",
        "VisualContextIntegrationRequest",
        "owner=",
    )
    assert all(name in source for name in required)


def test_lx1_s3g3_composition_does_not_own_perception_or_cognition():
    source = _source()

    forbidden = (
        "OfficialVisionCore",
        "GovernedReasoning",
        "CognitiveRuntimeOrchestrator",
        "FileImageRepository",
        "SQLiteDocumentRepository",
    )
    assert all(name not in source for name in forbidden)
