from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from domain.vision.camera_frame import CameraFrame


@dataclass(frozen=True)
class CodeRegion:
    """Decoded QR/barcode content and its optional geometric location."""

    content: str
    code_type: str
    confidence: float = 1.0
    x: int | None = None
    y: int | None = None
    width: int | None = None
    height: int | None = None

    def __post_init__(self) -> None:
        content = self.content.strip()
        code_type = self.code_type.strip().upper()
        if not content:
            raise ValueError("decoded code content must not be blank")
        if not code_type:
            raise ValueError("decoded code type must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("decoded code confidence must be between zero and one")
        geometry = (self.x, self.y, self.width, self.height)
        if any(value is not None for value in geometry):
            if any(value is None for value in geometry):
                raise ValueError("decoded code geometry must be complete or absent")
            assert self.x is not None and self.y is not None
            assert self.width is not None and self.height is not None
            if self.x < 0 or self.y < 0:
                raise ValueError("decoded code coordinates must not be negative")
            if self.width <= 0 or self.height <= 0:
                raise ValueError("decoded code dimensions must be positive")
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "code_type", code_type)


@dataclass(frozen=True)
class VisualCodeDetection:
    """Safe decoded-code output with no source image and no automatic action."""

    regions: tuple[CodeRegion, ...] = ()
    decoder_name: str = "unknown"

    def __post_init__(self) -> None:
        decoder_name = self.decoder_name.strip()
        if not decoder_name:
            raise ValueError("visual code decoder name must not be blank")
        object.__setattr__(self, "decoder_name", decoder_name)

    @property
    def code_present(self) -> bool:
        return bool(self.regions)


class VisualCodeDecoder(Protocol):
    def decode(self, frame: CameraFrame) -> VisualCodeDetection:
        """Decode QR/barcodes from one transient frame without retaining it."""
