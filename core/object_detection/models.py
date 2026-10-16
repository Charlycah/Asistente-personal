from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from domain.vision.camera_frame import CameraFrame


@dataclass(frozen=True)
class ObjectRegion:
    label: str
    confidence: float
    x: int | None = None
    y: int | None = None
    width: int | None = None
    height: int | None = None

    def __post_init__(self) -> None:
        label = self.label.strip()
        if not label:
            raise ValueError("object label must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("object confidence must be between zero and one")
        geometry = (self.x, self.y, self.width, self.height)
        if any(value is not None for value in geometry):
            if any(value is None for value in geometry):
                raise ValueError("object geometry must be complete")
            assert self.x is not None and self.y is not None
            assert self.width is not None and self.height is not None
            if self.x < 0 or self.y < 0:
                raise ValueError("object coordinates must not be negative")
            if self.width <= 0 or self.height <= 0:
                raise ValueError("object dimensions must be positive")
        object.__setattr__(self, "label", label)


@dataclass(frozen=True)
class ObjectDetection:
    regions: tuple[ObjectRegion, ...] = ()
    detector_name: str = "unknown_object_detector"

    def __post_init__(self) -> None:
        name = self.detector_name.strip()
        if not name:
            raise ValueError("object detector name must not be blank")
        object.__setattr__(self, "regions", tuple(self.regions))
        object.__setattr__(self, "detector_name", name)

    @property
    def object_present(self) -> bool:
        return bool(self.regions)

    @property
    def object_count(self) -> int:
        return len(self.regions)


class ObjectDetector(Protocol):
    def detect(self, frame: CameraFrame) -> ObjectDetection: ...
