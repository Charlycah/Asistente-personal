from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol


class ImageCategory(str, Enum):
    PERSON_REFERENCE = "person_reference"
    PET = "pet"
    DOCUMENT = "document"
    OBJECT = "object"
    GENERAL = "general"


@dataclass(frozen=True)
class ImageStoreRequest:
    owner: str
    label: str
    category: ImageCategory | str = ImageCategory.GENERAL
    tags: tuple[str, ...] = ()
    explicit_user_consent: bool = False
    user_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        label = self.label.strip()
        category = ImageCategory(self.category)
        tags = tuple(tag.strip() for tag in self.tags if tag.strip())
        if not owner:
            raise ValueError("image owner must not be blank")
        if not label:
            raise ValueError("image label must not be blank")
        if len(tags) != len(set(tags)):
            raise ValueError("image tags must be unique")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "tags", tags)


@dataclass(frozen=True)
class StoredImageAsset:
    """Transient selected asset; never exposes repository filesystem details."""

    stored_image: "StoredImage"
    image_bytes: bytes

    def __post_init__(self) -> None:
        if not self.image_bytes:
            raise ValueError("stored image asset bytes must not be empty")


@dataclass(frozen=True)
class StoredImage:
    image_id: str
    owner: str
    label: str
    category: ImageCategory | str
    tags: tuple[str, ...]
    mime_type: str
    size_bytes: int
    sha256: str
    stored_at: datetime

    def __post_init__(self) -> None:
        category = ImageCategory(self.category)
        if self.stored_at.tzinfo is None:
            raise ValueError("stored image timestamp must be timezone-aware")
        if self.size_bytes <= 0:
            raise ValueError("stored image size must be positive")
        object.__setattr__(self, "category", category)


class ImageRepository(Protocol):
    def store(
        self,
        request: ImageStoreRequest,
        *,
        image_bytes: bytes,
        mime_type: str,
    ) -> StoredImage: ...

    def get(self, image_id: str) -> StoredImage | None: ...

    def read_asset(self, image_id: str, *, owner: str) -> StoredImageAsset: ...

    def list(self, *, owner: str | None = None) -> tuple[StoredImage, ...]: ...

    def delete(self, image_id: str) -> bool: ...
