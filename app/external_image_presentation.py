from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlparse


@dataclass(frozen=True)
class ExternalImageProvenance:
    source_id: str
    external_id: str
    verification: str | None = None


@dataclass(frozen=True)
class ExternalImagePresentationArtifact:
    source_id: str
    external_id: str
    title: str
    description: str
    published_at: str | None
    media_type: str
    preview_url: str
    verification: str | None
    provenance: ExternalImageProvenance

    @classmethod
    def from_raw(
        cls,
        raw: Mapping[str, object],
    ) -> ExternalImagePresentationArtifact:
        source_id = _required_text(raw.get("source_id"), "source_id")
        external_id = _required_text(raw.get("external_id"), "external_id")
        title = _required_text(raw.get("title"), "title")
        media_type = _required_text(raw.get("media_type"), "media_type")
        preview_url = _required_text(raw.get("preview_url"), "preview_url")
        verification = _optional_text(raw.get("verification"))
        return cls(
            source_id=source_id,
            external_id=external_id,
            title=title,
            description=_optional_text(raw.get("description")) or "",
            published_at=_optional_text(raw.get("published_at")),
            media_type=media_type,
            preview_url=preview_url,
            verification=verification,
            provenance=ExternalImageProvenance(
                source_id=source_id,
                external_id=external_id,
                verification=verification,
            ),
        )


def project_external_image(
    raw: Mapping[str, object],
) -> ExternalImagePresentationArtifact | None:
    if _optional_text(raw.get("media_type")) != "image":
        return None
    preview_url = _optional_text(raw.get("preview_url"))
    if preview_url is None or not _is_https_url(preview_url):
        return None
    try:
        return ExternalImagePresentationArtifact.from_raw(raw)
    except (TypeError, ValueError):
        return None


def _is_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme.casefold() == "https" and bool(parsed.netloc)


def _required_text(value: object, field: str) -> str:
    text = _optional_text(value)
    if text is None:
        raise ValueError(f"external image {field} cannot be empty")
    return text


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
