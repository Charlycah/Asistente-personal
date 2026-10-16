from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.document_classification import (
    DeterministicDocumentClassifier,
    DocumentType,
)
from core.intelligent_vision import VisionCapability
from core.object_detection import ObjectDetection, ObjectRegion
from core.text_extraction import TextExtraction, TextRegion
from core.visual_code_detection import CodeRegion, VisualCodeDetection
from infrastructure.camera.camera_client import CameraFrame


class FakeCamera:
    def __init__(self) -> None:
        self.calls = 0

    def capture(self, camera_index: int) -> CameraFrame:
        self.calls += 1
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"transient-document-frame",
            captured_at=datetime.now(timezone.utc),
            frame_id="document-frame",
        )


class InvoiceText:
    def extract(self, frame: CameraFrame) -> TextExtraction:
        return TextExtraction(
            (
                TextRegion("FACTURA", 0.96),
                TextRegion("CUIT 30-12345678-9", 0.92),
                TextRegion("Importe total $ 42.850", 0.94),
                TextRegion("Vencimiento 15/08/2026", 0.91),
            ),
            "fake-ocr",
            "spa",
        )


class AmbiguousText:
    def extract(self, frame: CameraFrame) -> TextExtraction:
        return TextExtraction((TextRegion("Hola mundo", 0.9),), "fake-ocr", "spa")


class Objects:
    def detect(self, frame: CameraFrame) -> ObjectDetection:
        return ObjectDetection((ObjectRegion("document", 0.9),), "objects")


class Codes:
    def decode(self, frame: CameraFrame) -> VisualCodeDetection:
        return VisualCodeDetection((CodeRegion("123", "QR", 0.99),), "codes")


def request(**overrides: object) -> VisionCaptureRequest:
    values = {
        "capabilities": (VisionCapability.DOCUMENT_UNDERSTANDING,),
        "camera_permission": True,
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(overrides)
    return VisionCaptureRequest(**values)


def build_core(text_extractor: object | None = None) -> OfficialVisionCore:
    return OfficialVisionCore(
        camera_provider=FakeCamera(),
        text_extractor=text_extractor or InvoiceText(),
        object_detector=Objects(),
        visual_code_decoder=Codes(),
    )


def test_document_classification_identifies_invoice_from_one_frame():
    core = build_core()
    result = core.classify_document(request())

    assert result.classification.primary.document_type is DocumentType.INVOICE
    assert result.classification.primary.confidence > 0.8
    assert "factura" in result.classification.primary.matched_signals
    assert core.camera_provider.calls == 1
    assert not hasattr(result, "image_bytes")


@pytest.mark.parametrize(
    "field",
    ["camera_permission", "explicit_user_consent", "user_requested"],
)
def test_document_classification_requires_authorization(field: str):
    camera = FakeCamera()
    core = OfficialVisionCore(camera_provider=camera, text_extractor=InvoiceText())
    with pytest.raises(PermissionError):
        core.classify_document(request(**{field: False}))
    assert camera.calls == 0


def test_document_classification_requires_capability_and_ocr():
    with pytest.raises(ValueError, match="document_understanding"):
        build_core().classify_document(
            request(capabilities=(VisionCapability.TEXT_EXTRACTION,))
        )
    with pytest.raises(RuntimeError, match="text extractor"):
        OfficialVisionCore(camera_provider=FakeCamera()).classify_document(request())


def test_document_classifier_returns_unknown_for_ambiguous_text():
    result = build_core(AmbiguousText()).classify_document(request())
    assert result.classification.primary.document_type is DocumentType.UNKNOWN
    assert result.classification.primary.confidence == 0


def test_document_snapshot_contains_safe_classification_metadata():
    core = build_core()
    core.classify_document(request())

    assert core.snapshot.document_classification_attempts == 1
    assert core.snapshot.documents_classified == 1
    assert core.snapshot.last_document_type == "invoice"
    assert "transient-document-frame" not in str(core.snapshot)


def test_classifier_candidate_is_explainable_and_deterministic():
    classification = DeterministicDocumentClassifier().classify(
        text=InvoiceText().extract(FakeCamera().capture(0)),
        objects=None,
        codes=None,
    )
    assert classification.classifier_name
    assert classification.primary.matched_signals
    assert classification.primary.document_type is DocumentType.INVOICE
