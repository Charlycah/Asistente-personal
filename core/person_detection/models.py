from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from domain.vision.camera_frame import CameraFrame


@dataclass(frozen=True)
class PersonRegion:
    """Non-biometric region where a detector observed a possible person."""

    x: int
    y: int
    width: int
    height: int
    confidence: float

    def __post_init__(self) -> None:
        if self.x < 0 or self.y < 0:
            raise ValueError("person region coordinates must not be negative")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("person region dimensions must be positive")
        if not 0 <= self.confidence <= 1:
            raise ValueError("person confidence must be between zero and one")


@dataclass(frozen=True)
class PersonDetection:
    """Safe detector output; it never contains source image bytes."""

    regions: tuple[PersonRegion, ...] = ()
    detector_name: str = "unknown"

    def __post_init__(self) -> None:
        name = self.detector_name.strip()
        if not name:
            raise ValueError("person detector name must not be blank")
        object.__setattr__(self, "detector_name", name)

    @property
    def person_count(self) -> int:
        return len(self.regions)

    @property
    def person_present(self) -> bool:
        return bool(self.regions)


class PersonDetector(Protocol):
    """Boundary for local, non-biometric person detection."""

    def detect(self, frame: CameraFrame) -> PersonDetection:
        """Detect possible people in one already-authorized camera frame."""
