from __future__ import annotations

import inspect
from datetime import datetime, timezone

from app.vision_core import OfficialVisionCore, StoredVisualInput
from core.face_detection import FaceDetection, FaceRegion
from core.object_detection import ObjectDetection, ObjectRegion
from core.person_detection import PersonDetection, PersonRegion
from core.text_extraction import TextExtraction, TextRegion
from core.visual_code_detection import CodeRegion, VisualCodeDetection

SOURCE_REF = "stored_image:" + "a" * 32
NOW = datetime(2026, 10, 2, tzinfo=timezone.utc)


class _Detector:
    def __init__(self, result: object) -> None:
        self.result = result

    def detect(self, frame: object) -> object:
        return self.result


class _Extractor:
    def __init__(self, result: TextExtraction) -> None:
        self.result = result

    def extract(self, frame: object) -> TextExtraction:
        return self.result


class _Decoder:
    def __init__(self, result: VisualCodeDetection) -> None:
        self.result = result

    def decode(self, frame: object) -> VisualCodeDetection:
        return self.result


def _input() -> StoredVisualInput:
    return StoredVisualInput(
        source_ref=SOURCE_REF,
        image_bytes=b"stored-visual-bytes",
        mime_type="image/png",
        observed_at=NOW,
        explicit_user_consent=True,
        user_requested=True,
    )


def _core() -> OfficialVisionCore:
    return OfficialVisionCore(
        camera_provider=None,
        person_detector=_Detector(
            PersonDetection(
                regions=(PersonRegion(1, 2, 30, 40, 0.91),),
                detector_name="person-detector",
            )
        ),
        face_detector=_Detector(
            FaceDetection(
                regions=(FaceRegion(3, 4, 10, 12, 0.87),),
                detector_name="face-detector",
            )
        ),
        object_detector=_Detector(
            ObjectDetection(
                regions=(ObjectRegion("book", 0.83, 5, 6, 20, 22),),
                detector_name="object-detector",
            )
        ),
        text_extractor=_Extractor(
            TextExtraction(
                regions=(TextRegion("evidence", 0.79, 7, 8, 14, 16),),
                extractor_name="ocr",
                language="eng",
            )
        ),
        visual_code_decoder=_Decoder(
            VisualCodeDetection(
                regions=(CodeRegion("abc", "qr", 0.95, 9, 10, 18, 19),),
                decoder_name="code-decoder",
            )
        ),
    )


def test_g4c_preserves_existing_perceptual_outputs_without_reinterpretation():
    result = _core().analyze_stored_image(object(), _input())

    assert result.people.regions[0].confidence == 0.91
    assert result.faces.regions[0].confidence == 0.87
    assert result.objects.regions[0].label == "book"
    assert result.objects.regions[0].width == 20
    assert result.text.regions[0].text == "evidence"
    assert result.codes.regions[0].code_type == "QR"


def test_g4c_preserves_stored_image_lineage_and_observation_time():
    result = _core().analyze_stored_image(object(), _input())

    assert result.source_ref == SOURCE_REF
    assert result.visual_observation.observation_ref == SOURCE_REF
    assert result.observed_at == NOW


def test_g4c_allows_empty_evidence_when_analyzers_are_not_configured():
    core = OfficialVisionCore(camera_provider=None)
    result = core.analyze_stored_image(object(), _input())

    assert result.people is None
    assert result.faces is None
    assert result.objects is None
    assert result.text is None
    assert result.codes is None


def test_g4c_result_exposes_no_raw_image_bytes():
    result = _core().analyze_stored_image(object(), _input())

    assert not hasattr(result, "image_bytes")
    assert b"stored-visual-bytes" not in repr(result).encode()


def test_g4c_preservation_does_not_claim_semantic_or_cognitive_authority():
    source = inspect.getsource(OfficialVisionCore.analyze_stored_image)

    assert "SceneEvidence(" not in source
    assert "ObjectEvidence(" not in source
    assert "VisualAttentionEvidence(" not in source
    assert "IntegratedVisualContext(" not in source
    assert "GovernedReasoning" not in source
    assert "CognitiveRuntimeOrchestrator" not in source
