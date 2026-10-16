from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from domain.vision.camera_frame import CameraFrame


@dataclass(frozen=True)
class TextRegion:
    """One OCR text fragment and its optional geometric location."""

    text: str
    confidence: float
    x: int | None = None
    y: int | None = None
    width: int | None = None
    height: int | None = None

    def __post_init__(self) -> None:
        text = self.text.strip()
        if not text:
            raise ValueError("OCR text region must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("OCR confidence must be between zero and one")
        geometry = (self.x, self.y, self.width, self.height)
        if any(value is not None for value in geometry):
            if any(value is None for value in geometry):
                raise ValueError("OCR geometry must be complete or absent")
            assert self.x is not None
            assert self.y is not None
            assert self.width is not None
            assert self.height is not None
            if self.x < 0 or self.y < 0:
                raise ValueError("OCR coordinates must not be negative")
            if self.width <= 0 or self.height <= 0:
                raise ValueError("OCR dimensions must be positive")
        object.__setattr__(self, "text", text)


@dataclass(frozen=True)
class TextExtraction:
    """Safe OCR output containing text fragments and extractor provenance."""

    regions: tuple[TextRegion, ...] = ()
    extractor_name: str = "unknown"
    language: str = "und"

    def __post_init__(self) -> None:
        extractor_name = self.extractor_name.strip()
        language = self.language.strip()
        if not extractor_name:
            raise ValueError("OCR extractor name must not be blank")
        if not language:
            raise ValueError("OCR language must not be blank")
        object.__setattr__(self, "extractor_name", extractor_name)
        object.__setattr__(self, "language", language)

    @property
    def text_present(self) -> bool:
        return bool(self.regions)

    @property
    def full_text(self) -> str:
        return "\n".join(region.text for region in self.regions)


class TextExtractor(Protocol):
    def extract(self, frame: CameraFrame) -> TextExtraction:
        """Extract visible text from one transient frame without retaining it."""
