from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.document_intelligence import DeterministicDocumentIntelligenceAnalyzer
from core.intelligent_vision import VisionCapability
from core.text_extraction import TextExtraction, TextRegion
from infrastructure.camera.camera_client import CameraFrame


class FakeCamera:
    def __init__(self) -> None:
        self.calls = 0

    def capture(self, camera_index: int) -> CameraFrame:
        self.calls += 1
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"private-document",
            captured_at=datetime.now(timezone.utc),
            frame_id="document-intelligence-frame",
        )


class InvoiceText:
    def extract(self, frame: CameraFrame) -> TextExtraction:
        return TextExtraction(
            (
                TextRegion("Empresa Electrica SA", 0.98),
                TextRegion("FACTURA", 0.98),
                TextRegion("Nro: A-12345", 0.98),
                TextRegion("Fecha: 20/07/2026", 0.96),
                TextRegion("Total: $ 1000", 0.95),
            ),
            "fake-ocr",
            "spa",
        )


def request(**overrides: object) -> VisionCaptureRequest:
    values = {
        "capabilities": (VisionCapability.DOCUMENT_UNDERSTANDING,),
        "camera_permission": True,
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(overrides)
    return VisionCaptureRequest(**values)


def build_core() -> OfficialVisionCore:
    return OfficialVisionCore(
        camera_provider=FakeCamera(),
        text_extractor=InvoiceText(),
    )


def test_document_intelligence_uses_one_authorized_frame():
    core = build_core()
    result = core.understand_document(request())
    assert result.intelligence.document_type == "invoice"
    assert result.intelligence.completeness == 1.0
    assert core.camera_provider.calls == 1
    assert not hasattr(result, "image_bytes")


@pytest.mark.parametrize(
    "field", ["camera_permission", "explicit_user_consent", "user_requested"]
)
def test_document_intelligence_requires_authorization(field: str):
    core = build_core()
    with pytest.raises(PermissionError):
        core.understand_document(request(**{field: False}))
    assert core.camera_provider.calls == 0


def test_document_intelligence_requires_capability_and_ocr():
    with pytest.raises(ValueError, match="document_understanding"):
        build_core().understand_document(
            request(capabilities=(VisionCapability.TEXT_EXTRACTION,))
        )
    with pytest.raises(RuntimeError, match="text extractor"):
        OfficialVisionCore(camera_provider=FakeCamera()).understand_document(request())


def test_missing_fields_are_reported_without_invention():
    class SparseText:
        def extract(self, frame: CameraFrame) -> TextExtraction:
            return TextExtraction((TextRegion("FACTURA", 0.9),), "ocr", "spa")

    core = OfficialVisionCore(
        camera_provider=FakeCamera(),
        text_extractor=SparseText(),
    )
    result = core.understand_document(request())
    assert "total_amount" in result.intelligence.missing_fields
    assert result.document.get("total_amount") is None


def test_conflicting_totals_generate_explainable_warning():
    from core.document_classification import DeterministicDocumentClassifier
    from core.document_extraction import DeterministicStructuredDocumentExtractor

    text = TextExtraction(
        (TextRegion("FACTURA\nTotal: $100\nTotal a pagar: $200", 0.9),),
        "ocr",
        "spa",
    )
    classification = DeterministicDocumentClassifier().classify(text=text)
    document = DeterministicStructuredDocumentExtractor().extract(
        text=text, classification=classification
    )
    intelligence = DeterministicDocumentIntelligenceAnalyzer().analyze(
        document=document, text=text
    )
    assert any(issue.code == "conflicting_totals" for issue in intelligence.issues)
    assert intelligence.consistency < 1.0


def test_snapshot_contains_only_safe_intelligence_metadata():
    core = build_core()
    core.understand_document(request())
    assert core.snapshot.document_intelligence_attempts == 1
    assert core.snapshot.documents_understood == 1
    assert "private-document" not in str(core.snapshot)
