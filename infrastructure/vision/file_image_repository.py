from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from core.governed_image_repository import (
    ImageCategory,
    ImageStoreRequest,
    StoredImage,
    StoredImageAsset,
)

_ALLOWED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class FileImageRepository:
    """Private local image store with explicit metadata and no biometrics."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.assets = root / "assets"
        self.metadata = root / "metadata"

    def store(
        self,
        request: ImageStoreRequest,
        *,
        image_bytes: bytes,
        mime_type: str,
    ) -> StoredImage:
        if not request.user_requested:
            raise PermissionError("image storage must be explicitly requested")
        if not request.explicit_user_consent:
            raise PermissionError("image storage requires explicit user consent")
        if not image_bytes:
            raise ValueError("image bytes must not be empty")
        extension = _ALLOWED_MIME_TYPES.get(mime_type)
        if extension is None:
            raise ValueError("unsupported image mime type")

        image_id = uuid4().hex
        digest = sha256(image_bytes).hexdigest()
        stored = StoredImage(
            image_id=image_id,
            owner=request.owner,
            label=request.label,
            category=request.category,
            tags=request.tags,
            mime_type=mime_type,
            size_bytes=len(image_bytes),
            sha256=digest,
            stored_at=datetime.now(timezone.utc),
        )
        self.assets.mkdir(parents=True, exist_ok=True)
        self.metadata.mkdir(parents=True, exist_ok=True)
        (self.assets / f"{image_id}{extension}").write_bytes(image_bytes)
        payload = asdict(stored)
        payload["category"] = stored.category.value
        payload["stored_at"] = stored.stored_at.isoformat()
        (self.metadata / f"{image_id}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return stored

    def get(self, image_id: str) -> StoredImage | None:
        path = self.metadata / f"{self._safe_id(image_id)}.json"
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return StoredImage(
            image_id=data["image_id"],
            owner=data["owner"],
            label=data["label"],
            category=ImageCategory(data["category"]),
            tags=tuple(data["tags"]),
            mime_type=data["mime_type"],
            size_bytes=int(data["size_bytes"]),
            sha256=data["sha256"],
            stored_at=datetime.fromisoformat(data["stored_at"]),
        )

    def read_asset(self, image_id: str, *, owner: str) -> StoredImageAsset:
        """Read one explicitly selected private asset with owner/integrity checks."""

        record = self.get(image_id)
        if record is None:
            raise FileNotFoundError("stored image was not found")
        if record.owner != owner.strip():
            raise PermissionError("stored image owner does not match request owner")
        extension = _ALLOWED_MIME_TYPES[record.mime_type]
        asset_path = self.assets / f"{self._safe_id(image_id)}{extension}"
        if not asset_path.is_file():
            raise FileNotFoundError("stored image asset was not found")
        image_bytes = asset_path.read_bytes()
        digest = sha256(image_bytes).hexdigest()
        if digest != record.sha256:
            raise ValueError("stored image sha256 integrity check failed")
        return StoredImageAsset(stored_image=record, image_bytes=image_bytes)

    def list(self, *, owner: str | None = None) -> tuple[StoredImage, ...]:
        if not self.metadata.exists():
            return ()
        records = tuple(
            record
            for path in sorted(self.metadata.glob("*.json"))
            if (record := self.get(path.stem)) is not None
            and (owner is None or record.owner == owner)
        )
        return records

    def delete(self, image_id: str) -> bool:
        safe_id = self._safe_id(image_id)
        metadata_path = self.metadata / f"{safe_id}.json"
        record = self.get(safe_id)
        if record is None:
            return False
        extension = _ALLOWED_MIME_TYPES[record.mime_type]
        asset_path = self.assets / f"{safe_id}{extension}"
        metadata_path.unlink(missing_ok=True)
        asset_path.unlink(missing_ok=True)
        return True

    @staticmethod
    def _safe_id(image_id: str) -> str:
        value = image_id.strip()
        if not value or not value.isalnum():
            raise ValueError("invalid image id")
        return value
