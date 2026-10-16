from __future__ import annotations

from core.visual_code_detection import CodeRegion, VisualCodeDetection
from infrastructure.camera.camera_client import CameraFrame


class VisualCodeDecoderError(RuntimeError):
    """Normalized error raised by optional local QR/barcode providers."""


class PyzbarVisualCodeDecoder:
    """Optional local adapter for QR and common one-dimensional barcodes."""

    def decode(self, frame: CameraFrame) -> VisualCodeDetection:
        try:
            import cv2  # type: ignore[import-not-found]
            import numpy as np  # type: ignore[import-not-found]
            from pyzbar.pyzbar import decode  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover
            raise VisualCodeDecoderError(
                "local QR/barcode dependencies are not available"
            ) from exc

        encoded = np.frombuffer(frame.image_bytes, dtype=np.uint8)
        image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if image is None:
            raise VisualCodeDecoderError("camera frame could not be decoded")

        regions: list[CodeRegion] = []
        for item in decode(image):
            try:
                content = item.data.decode("utf-8")
            except UnicodeDecodeError:
                content = item.data.decode("utf-8", errors="replace")
            rectangle = item.rect
            regions.append(
                CodeRegion(
                    content=content,
                    code_type=str(item.type),
                    confidence=1.0,
                    x=int(rectangle.left),
                    y=int(rectangle.top),
                    width=int(rectangle.width),
                    height=int(rectangle.height),
                )
            )
        return VisualCodeDetection(
            regions=tuple(regions),
            decoder_name="pyzbar_local_decoder",
        )
