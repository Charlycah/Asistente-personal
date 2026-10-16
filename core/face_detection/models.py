from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from domain.vision.camera_frame import CameraFrame


@dataclass(frozen=True)
class FaceRegion:
    """Geometric location of a possible face, without identity metadata."""

    x: int
    y: int
    width: int
    height: int
    confidence: float

    def __post_init__(self) -> None:
        if self.x < 0 or self.y < 0:
            raise ValueError("face region coordinates must not be negative")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("face region dimensions must be positive")
        if not 0 <= self.confidence <= 1:
            raise ValueError("face confidence must be between zero and one")


@dataclass(frozen=True)
class FaceDetection:
    """Safe output containing only face locations and detector provenance."""

    regions: tuple[FaceRegion, ...] = ()
    detector_name: str = "unknown"

    def __post_init__(self) -> None:
        name = self.detector_name.strip()
        if not name:
            raise ValueError("face detector name must not be blank")
        object.__setattr__(self, "detector_name", name)

    @property
    def face_present(self) -> bool:
        return bool(self.regions)

    @property
    def face_count(self) -> int:
        return len(self.regions)


class FaceDetector(Protocol):
    def detect(self, frame: CameraFrame) -> FaceDetection:
        """Locate faces in one transient frame without identifying them."""
