from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.document_extraction import (
    DeterministicStructuredDocumentExtractor,
    ExtractedField,
    StructuredDocument,
)
from core.intelligent_vision import VisionCapability
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
            image_bytes=b"private-document-frame",
            captured_at=datetime.now(timezone.utc),
            frame_id="structured-document-frame",
        )


class InvoiceText:
    def extract(self, frame: CameraFrame) -> TextExtraction:
        return TextExtraction(
            (
                TextRegion("Empresa Electrica SA", 0.97),
                TextRegion("FACTURA", 0.98),
                TextRegion("CUIT: 30-12345678-9", 0.96),
                TextRegion("Fecha: 20/07/2026", 0.94),
                TextRegion("Vencimiento: 15/08/2026", 0.95),
                TextRegion("Total a pagar: $ 42.850,00", 0.96),
            ),
            "fake-ocr",
            "spa",
        )


class Codes:
    def decode(self, frame: CameraFrame) -> VisualCodeDetection:
        return VisualCodeDetection(
            (CodeRegion("PAY-123456", "QR", 0.99),),
            "fake-codes",
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
        visual_code_decoder=Codes(),
    )


def test_structured_extraction_uses_one_authorized_frame():
    core = build_core()
    result = core.extract_document_fields(request())

    assert result.document.document_type == "invoice"
    assert result.document.get("total_amount").value == "$ 42.850,00"
    assert result.document.get("due_date").value == "15/08/2026"
    assert result.document.get("currency").value == "ARS"
    assert core.camera_provider.calls == 1
    assert not hasattr(result, "image_bytes")


@pytest.mark.parametrize(
    "field",
    ["camera_permission", "explicit_user_consent", "user_requested"],
)
def test_structured_extraction_requires_authorization(field: str):
    core = build_core()
    with pytest.raises(PermissionError):
        core.extract_document_fields(request(**{field: False}))
    assert core.camera_provider.calls == 0


def test_structured_extraction_requires_capability_and_ocr():
    with pytest.raises(ValueError, match="document_understanding"):
        build_core().extract_document_fields(
            request(capabilities=(VisionCapability.TEXT_EXTRACTION,))
        )
    with pytest.raises(RuntimeError, match="text extractor"):
        OfficialVisionCore(camera_provider=FakeCamera()).extract_document_fields(
            request()
        )


def test_extracted_fields_are_traceable_and_unique():
    result = build_core().extract_document_fields(request())
    assert result.document.fields
    assert all(field.evidence for field in result.document.fields)
    assert len({field.name for field in result.document.fields}) == len(
        result.document.fields
    )


def test_visual_code_is_data_only_and_not_executed():
    result = build_core().extract_document_fields(request())
    field = result.document.get("payment_or_reference_code")
    assert field is not None
    assert field.value == "PAY-123456"
    assert "execute" not in str(result).lower()


def test_snapshot_contains_only_safe_extraction_metadata():
    core = build_core()
    core.extract_document_fields(request())
    assert core.snapshot.document_extraction_attempts == 1
    assert core.snapshot.documents_extracted == 1
    assert core.snapshot.last_extracted_field_count >= 5
    assert "private-document-frame" not in str(core.snapshot)


def test_structured_document_rejects_duplicate_fields():
    field = ExtractedField("total", "10", 0.9, "Total 10")
    with pytest.raises(ValueError, match="unique"):
        StructuredDocument("invoice", (field, field), "extractor")


def test_deterministic_extractor_does_not_invent_missing_fields():
    text = TextExtraction((TextRegion("FACTURA", 0.9),), "ocr", "spa")
    from core.document_classification import DeterministicDocumentClassifier

    classification = DeterministicDocumentClassifier().classify(text=text)
    document = DeterministicStructuredDocumentExtractor().extract(
        text=text,
        classification=classification,
    )
    assert document.get("total_amount") is None
    assert document.get("due_date") is None
