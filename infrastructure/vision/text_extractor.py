from __future__ import annotations

from dataclasses import dataclass

from core.text_extraction import TextExtraction, TextRegion
from infrastructure.camera.camera_client import CameraFrame


class TextExtractorError(RuntimeError):
    """Normalized error raised by optional local OCR providers."""


@dataclass(frozen=True)
class TesseractTextExtractorConfig:
    language: str = "spa"
    page_segmentation_mode: int = 6
    minimum_confidence: float = 0.5

    def __post_init__(self) -> None:
        if not self.language.strip():
            raise ValueError("OCR language must not be blank")
        if self.page_segmentation_mode < 0:
            raise ValueError("OCR page segmentation mode must not be negative")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("OCR minimum confidence must be between zero and one")


class TesseractTextExtractor:
    """Optional local OCR adapter using OpenCV decoding and Tesseract."""

    def __init__(self, config: TesseractTextExtractorConfig | None = None) -> None:
        self.config = config or TesseractTextExtractorConfig()

    def extract(self, frame: CameraFrame) -> TextExtraction:
        try:
            import cv2  # type: ignore[import-not-found]
            import numpy as np  # type: ignore[import-not-found]
            import pytesseract  # type: ignore[import-not-found]
            from pytesseract import Output  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover
            raise TextExtractorError(
                "local OCR dependencies are not available"
            ) from exc

        encoded = np.frombuffer(frame.image_bytes, dtype=np.uint8)
        image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if image is None:
            raise TextExtractorError("camera frame could not be decoded")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        data = pytesseract.image_to_data(
            gray,
            lang=self.config.language,
            config=f"--psm {self.config.page_segmentation_mode}",
            output_type=Output.DICT,
        )
        regions: list[TextRegion] = []
        for index, raw_text in enumerate(data.get("text", [])):
            text = str(raw_text).strip()
            if not text:
                continue
            try:
                raw_confidence = float(data["conf"][index])
            except (KeyError, TypeError, ValueError, IndexError):
                continue
            confidence = max(0.0, min(raw_confidence / 100.0, 1.0))
            if confidence < self.config.minimum_confidence:
                continue
            regions.append(
                TextRegion(
                    text=text,
                    confidence=confidence,
                    x=int(data["left"][index]),
                    y=int(data["top"][index]),
                    width=int(data["width"][index]),
                    height=int(data["height"][index]),
                )
            )
        return TextExtraction(
            regions=tuple(regions),
            extractor_name="tesseract_local_ocr",
            language=self.config.language,
        )
