from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class CameraFrame:
    """Neutral immutable representation of a captured camera frame."""

    camera_index: int
    mime_type: str
    image_bytes: bytes
    width: int | None = None
    height: int | None = None
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    frame_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if self.camera_index < 0:
            raise ValueError("camera index must not be negative")
        if not self.mime_type.strip():
            raise ValueError("camera mime type must not be empty")
        if not self.image_bytes:
            raise ValueError("camera image bytes must not be empty")
        if self.width is not None and self.width <= 0:
            raise ValueError("camera width must be positive")
        if self.height is not None and self.height <= 0:
            raise ValueError("camera height must be positive")
        if self.captured_at.tzinfo is None:
            raise ValueError("camera frame timestamp must be timezone-aware")
        if not self.frame_id.strip():
            raise ValueError("camera frame id must not be empty")

    def to_dict(self, *, include_bytes: bool = False) -> dict[str, object]:
        payload: dict[str, object] = {
            "frame_id": self.frame_id,
            "camera_index": self.camera_index,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "size_bytes": len(self.image_bytes),
            "captured_at": self.captured_at.isoformat(),
        }
        if include_bytes:
            payload["image_bytes"] = self.image_bytes
        return payload
