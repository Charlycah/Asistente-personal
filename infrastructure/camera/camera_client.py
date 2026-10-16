from __future__ import annotations

from typing import Protocol

from domain.vision.camera_frame import CameraFrame


class CameraProviderError(RuntimeError):
    """Error normalizado para proveedores de cámara de M68."""


class CameraProvider(Protocol):
    """Contrato mínimo para capturar imagen local detrás de M68."""

    def capture(self, camera_index: int) -> CameraFrame:
        """Captura un frame normalizado desde una cámara local."""


class OpenCVCameraClient:
    """Cliente OpenCV opcional; el core nunca debe invocarlo directamente."""

    def __init__(self, *, capture_backend: object | None = None) -> None:
        self.capture_backend = capture_backend

    def capture(self, camera_index: int) -> CameraFrame:
        if camera_index < 0:
            raise ValueError("camera index must not be negative")
        try:
            import cv2  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - optional dependency boundary
            raise CameraProviderError("opencv is not available") from exc

        capture = self.capture_backend or cv2.VideoCapture(camera_index)
        try:
            if not capture.isOpened():
                raise CameraProviderError("camera device is not available")
            ok, frame = capture.read()
            if not ok or frame is None:
                raise CameraProviderError("camera frame capture failed")
            ok, encoded = cv2.imencode(".jpg", frame)
            if not ok:
                raise CameraProviderError("camera frame encoding failed")
            height, width = frame.shape[:2]
            return CameraFrame(
                camera_index=camera_index,
                mime_type="image/jpeg",
                image_bytes=encoded.tobytes(),
                width=int(width),
                height=int(height),
            )
        finally:
            release = getattr(capture, "release", None)
            if callable(release):
                release()
