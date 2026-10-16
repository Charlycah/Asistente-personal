from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.object_detection import ObjectDetection, ObjectRegion
from infrastructure.camera.camera_client import CameraFrame


class ObjectDetectorError(RuntimeError):
    pass


@dataclass(frozen=True)
class OpenCVDNNObjectDetectorConfig:
    model_path: str
    labels: tuple[str, ...]
    confidence_threshold: float = 0.5
    input_width: int = 640
    input_height: int = 640

    def __post_init__(self) -> None:
        if not self.model_path.strip():
            raise ValueError("object detector model path must not be blank")
        if not self.labels or any(not label.strip() for label in self.labels):
            raise ValueError("object detector labels must not be empty")
        if not 0 < self.confidence_threshold <= 1:
            raise ValueError("object confidence threshold must be in (0, 1]")
        if self.input_width <= 0 or self.input_height <= 0:
            raise ValueError("object detector input dimensions must be positive")


class OpenCVDNNObjectDetector:
    """Optional local ONNX detector. Model files are user-supplied and local."""

    def __init__(self, config: OpenCVDNNObjectDetectorConfig) -> None:
        self.config = config
        self._net = None

    def detect(self, frame: CameraFrame) -> ObjectDetection:
        try:
            import cv2  # type: ignore[import-not-found]
            import numpy as np  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover
            raise ObjectDetectorError(
                "local object detection dependencies are not available"
            ) from exc

        model_path = Path(self.config.model_path)
        if not model_path.is_file():
            raise ObjectDetectorError("local object detection model was not found")
        if self._net is None:
            self._net = cv2.dnn.readNetFromONNX(str(model_path))

        encoded = np.frombuffer(frame.image_bytes, dtype=np.uint8)
        image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if image is None:
            raise ObjectDetectorError("camera frame could not be decoded")
        blob = cv2.dnn.blobFromImage(
            image,
            scalefactor=1 / 255.0,
            size=(self.config.input_width, self.config.input_height),
            swapRB=True,
            crop=False,
        )
        self._net.setInput(blob)
        output = self._net.forward()
        rows = output[0] if getattr(output, "ndim", 0) == 3 else output
        image_height, image_width = image.shape[:2]
        regions: list[ObjectRegion] = []
        for row in rows:
            if len(row) < 6:
                continue
            scores = row[5:]
            class_id = int(np.argmax(scores))
            confidence = float(scores[class_id]) * float(row[4])
            if confidence < self.config.confidence_threshold:
                continue
            if class_id >= len(self.config.labels):
                continue
            center_x, center_y, width, height = map(float, row[:4])
            scale_x = image_width / self.config.input_width
            scale_y = image_height / self.config.input_height
            box_width = max(1, int(width * scale_x))
            box_height = max(1, int(height * scale_y))
            x = max(0, int(center_x * scale_x - box_width / 2))
            y = max(0, int(center_y * scale_y - box_height / 2))
            regions.append(
                ObjectRegion(
                    label=self.config.labels[class_id],
                    confidence=min(confidence, 1.0),
                    x=x,
                    y=y,
                    width=box_width,
                    height=box_height,
                )
            )
        return ObjectDetection(
            regions=tuple(regions),
            detector_name="opencv_dnn_onnx_object_detector",
        )
