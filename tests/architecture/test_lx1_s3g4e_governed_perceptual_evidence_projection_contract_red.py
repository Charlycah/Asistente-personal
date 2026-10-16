from __future__ import annotations

import inspect

from app.governed_visual_semantic_composition import GovernedVisualSemanticComposition
from core.object_detection import ObjectDetection, ObjectRegion
from core.object_knowledge import ObjectKind
from core.visual_understanding_foundation import (
    VisualMediaType,
    VisualObservationSignal,
    VisualObservationSource,
    VisualPrivacyLevel,
)

SOURCE_REF = "stored_image:" + "a" * 32


class _Stage:
    def __init__(self, method_name: str, result: object) -> None:
        self.method_name = method_name
        self.result = result
        self.requests: list[object] = []

    def __getattr__(self, name: str):
        if name != self.method_name:
            raise AttributeError(name)

        def call(request: object, *, now=None) -> object:
            self.requests.append(request)
            return self.result

        return call


def _observation() -> VisualObservationSignal:
    return VisualObservationSignal(
        observation_ref=SOURCE_REF,
        source=VisualObservationSource.IMAGE_FILE,
        media_type=VisualMediaType.PHOTO,
        privacy_level=VisualPrivacyLevel.PERSONAL,
        confidence=1.0,
    )


def _composition():
    foundation = _Stage("establish", object())
    resolution = _Stage("resolve", object())
    scene = _Stage("understand", object())
    objects = _Stage("build", object())
    attention = _Stage("prioritize", object())
    integration = _Stage("integrate", object())
    composition = GovernedVisualSemanticComposition(
        foundation=foundation,
        resolution=resolution,
        scene=scene,
        objects=objects,
        attention=attention,
        integration=integration,
    )
    return composition, scene, objects, attention


def test_g4e_composition_accepts_preserved_object_detection():
    parameters = inspect.signature(GovernedVisualSemanticComposition.compose).parameters

    assert "object_detection" in parameters


def test_g4e_projects_real_object_regions_without_semantic_reclassification():
    composition, _scene, objects, _attention = _composition()
    detection = ObjectDetection(
        regions=(ObjectRegion("book", 0.83, 5, 6, 20, 22),),
        detector_name="object-detector",
    )

    composition.compose(
        owner="Carlos",
        observation=_observation(),
        explicit_user_consent=True,
        object_detection=detection,
    )

    evidence = objects.requests[0].evidence
    assert len(evidence) == 1
    assert evidence[0].observation_ref == SOURCE_REF
    assert evidence[0].label == "book"
    assert evidence[0].confidence == 0.83
    assert evidence[0].object_kind is ObjectKind.UNKNOWN
    assert evidence[0].object_ref.startswith(SOURCE_REF)
    assert evidence[0].evidence_ref.startswith(SOURCE_REF)


def test_g4e_absent_object_detection_adds_no_object_evidence():
    composition, _scene, objects, _attention = _composition()

    composition.compose(
        owner="Carlos",
        observation=_observation(),
        explicit_user_consent=True,
        object_detection=None,
    )

    assert objects.requests[0].evidence == ()


def test_g4e_projection_does_not_fabricate_scene_or_attention_evidence():
    composition, scene, _objects, attention = _composition()
    detection = ObjectDetection(
        regions=(ObjectRegion("book", 0.83, 5, 6, 20, 22),),
        detector_name="object-detector",
    )

    composition.compose(
        owner="Carlos",
        observation=_observation(),
        explicit_user_consent=True,
        object_detection=detection,
    )

    assert scene.requests[0].evidence == ()
    assert attention.requests[0].evidence == ()


def test_g4e_projection_keeps_existing_semantic_authorities_subordinate():
    source = inspect.getsource(GovernedVisualSemanticComposition)

    assert "ObjectDetection" in source
    assert "ObjectEvidence(" in source
    assert "ObjectKind.UNKNOWN" in source
    assert "SceneEvidence(" not in source
    assert "VisualAttentionEvidence(" not in source
    assert "IntegratedVisualContext(" not in source
    assert "GovernedReasoning" not in source
    assert "CognitiveRuntimeOrchestrator" not in source
