from __future__ import annotations

from dataclasses import dataclass

from core.person_detection import PersonDetection, PersonRegion
from infrastructure.camera.camera_client import CameraFrame


class PersonDetectorError(RuntimeError):
    """Normalized error raised by optional person detector providers."""


@dataclass(frozen=True)
class OpenCVHOGPersonDetectorConfig:
    """Conservative local defaults for OpenCV's non-biometric HOG detector."""

    minimum_confidence: float = 0.5
    scale: float = 1.05

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("minimum person confidence must be between zero and one")
        if self.scale <= 1:
            raise ValueError("person detector scale must be greater than one")


class OpenCVHOGPersonDetector:
    """Optional CPU-only detector; no face or identity recognition is performed."""

    def __init__(self, config: OpenCVHOGPersonDetectorConfig | None = None) -> None:
        self.config = config or OpenCVHOGPersonDetectorConfig()

    def detect(self, frame: CameraFrame) -> PersonDetection:
        try:
            import cv2  # type: ignore[import-not-found]
            import numpy as np  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - optional dependency boundary
            raise PersonDetectorError(
                "opencv person detector is not available"
            ) from exc

        encoded = np.frombuffer(frame.image_bytes, dtype=np.uint8)
        image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if image is None:
            raise PersonDetectorError("camera frame could not be decoded")

        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        rectangles, weights = hog.detectMultiScale(
            image,
            winStride=(8, 8),
            padding=(8, 8),
            scale=self.config.scale,
        )
        regions: list[PersonRegion] = []
        for rectangle, raw_weight in zip(rectangles, weights, strict=True):
            confidence = max(0.0, min(1.0, float(raw_weight)))
            if confidence < self.config.minimum_confidence:
                continue
            x, y, width, height = (int(value) for value in rectangle)
            regions.append(
                PersonRegion(
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    confidence=confidence,
                )
            )
        return PersonDetection(
            regions=tuple(regions),
            detector_name="opencv_hog_people_detector",
        )
