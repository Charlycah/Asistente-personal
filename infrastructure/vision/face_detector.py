from __future__ import annotations

from dataclasses import dataclass

from core.face_detection import FaceDetection, FaceRegion
from infrastructure.camera.camera_client import CameraFrame


class FaceDetectorError(RuntimeError):
    """Normalized error raised by optional local face detector providers."""


@dataclass(frozen=True)
class OpenCVCascadeFaceDetectorConfig:
    scale_factor: float = 1.1
    minimum_neighbors: int = 5
    minimum_size: tuple[int, int] = (30, 30)

    def __post_init__(self) -> None:
        if self.scale_factor <= 1:
            raise ValueError("face detector scale factor must be greater than one")
        if self.minimum_neighbors < 0:
            raise ValueError("face detector minimum neighbors must not be negative")
        if any(value <= 0 for value in self.minimum_size):
            raise ValueError("face detector minimum size must be positive")


class OpenCVCascadeFaceDetector:
    """Optional local locator; it performs no recognition or attribute inference."""

    def __init__(self, config: OpenCVCascadeFaceDetectorConfig | None = None) -> None:
        self.config = config or OpenCVCascadeFaceDetectorConfig()

    def detect(self, frame: CameraFrame) -> FaceDetection:
        try:
            import cv2  # type: ignore[import-not-found]
            import numpy as np  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover
            raise FaceDetectorError("opencv face detector is not available") from exc

        encoded = np.frombuffer(frame.image_bytes, dtype=np.uint8)
        image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if image is None:
            raise FaceDetectorError("camera frame could not be decoded")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        classifier_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        classifier = cv2.CascadeClassifier(classifier_path)
        if classifier.empty():
            raise FaceDetectorError("opencv face cascade could not be loaded")
        rectangles = classifier.detectMultiScale(
            gray,
            scaleFactor=self.config.scale_factor,
            minNeighbors=self.config.minimum_neighbors,
            minSize=self.config.minimum_size,
        )
        regions = tuple(
            FaceRegion(
                x=int(x),
                y=int(y),
                width=int(width),
                height=int(height),
                confidence=1.0,
            )
            for x, y, width, height in rectangles
        )
        return FaceDetection(regions=regions, detector_name="opencv_haar_face_detector")
