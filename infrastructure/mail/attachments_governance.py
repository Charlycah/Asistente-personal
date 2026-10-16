from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any


class AttachmentDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class AttachmentDisposition(str, Enum):
    ALLOWED = "allowed"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"


@dataclass(frozen=True, slots=True)
class AttachmentPolicy:
    max_attachment_bytes: int = 10 * 1024 * 1024
    max_total_bytes: int = 20 * 1024 * 1024
    max_attachment_count: int = 10
    allowed_content_types: frozenset[str] = frozenset(
        {
            "application/pdf",
            "application/zip",
            "image/jpeg",
            "image/png",
            "text/csv",
            "text/plain",
        }
    )
    blocked_extensions: frozenset[str] = frozenset(
        {".bat", ".cmd", ".com", ".exe", ".js", ".msi", ".ps1", ".scr", ".vbs"}
    )
    quarantine_unknown_inbound_types: bool = True

    def __post_init__(self) -> None:
        if self.max_attachment_bytes <= 0:
            raise ValueError("attachment size limit must be positive")
        if self.max_total_bytes < self.max_attachment_bytes:
            raise ValueError("total attachment limit cannot be smaller than item limit")
        if self.max_attachment_count <= 0:
            raise ValueError("attachment count limit must be positive")


@dataclass(frozen=True, slots=True)
class AttachmentDecision:
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    disposition: AttachmentDisposition
    reason: str | None = None


class AttachmentGovernanceError(ValueError):
    """Raised when outbound attachments violate governed policy."""


class GmailAttachmentsGovernance:
    """M227.4 deterministic, secret-free attachment policy authority."""

    def __init__(self, policy: AttachmentPolicy | None = None) -> None:
        self._policy = policy or AttachmentPolicy()
        self._evaluated = 0
        self._rejected = 0
        self._quarantined = 0

    def govern_outbound(
        self, attachments: Iterable[Mapping[str, Any]]
    ) -> tuple[Mapping[str, Any], ...]:
        normalized = tuple(self._normalize_attachment(item) for item in attachments)
        self._validate_collection(normalized)
        for item in normalized:
            decision = self._evaluate(item, AttachmentDirection.OUTBOUND)
            if decision.disposition is not AttachmentDisposition.ALLOWED:
                self._rejected += 1
                raise AttachmentGovernanceError(
                    decision.reason or "attachment rejected"
                )
        return tuple(MappingProxyType(item) for item in normalized)

    def inspect_inbound(
        self, attachments: Iterable[Mapping[str, Any]]
    ) -> tuple[AttachmentDecision, ...]:
        normalized = tuple(
            self._normalize_attachment(item, content_optional=True)
            for item in attachments
        )
        self._validate_collection(normalized)
        return tuple(
            self._evaluate(item, AttachmentDirection.INBOUND) for item in normalized
        )

    def status(self) -> dict[str, object]:
        return {
            "max_attachment_bytes": self._policy.max_attachment_bytes,
            "max_total_bytes": self._policy.max_total_bytes,
            "max_attachment_count": self._policy.max_attachment_count,
            "allowed_content_type_count": len(self._policy.allowed_content_types),
            "evaluated": self._evaluated,
            "rejected": self._rejected,
            "quarantined": self._quarantined,
        }

    def _validate_collection(self, attachments: tuple[dict[str, Any], ...]) -> None:
        if len(attachments) > self._policy.max_attachment_count:
            raise AttachmentGovernanceError("attachment count limit exceeded")
        if (
            sum(int(item["size_bytes"]) for item in attachments)
            > self._policy.max_total_bytes
        ):
            raise AttachmentGovernanceError("total attachment size limit exceeded")

    def _evaluate(
        self, item: Mapping[str, Any], direction: AttachmentDirection
    ) -> AttachmentDecision:
        self._evaluated += 1
        filename = str(item["filename"])
        content_type = str(item["content_type"])
        size_bytes = int(item["size_bytes"])
        digest = str(item["sha256"])
        reason: str | None = None
        disposition = AttachmentDisposition.ALLOWED
        extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if extension in self._policy.blocked_extensions:
            disposition = AttachmentDisposition.REJECTED
            reason = "attachment extension blocked"
        elif size_bytes > self._policy.max_attachment_bytes:
            disposition = AttachmentDisposition.REJECTED
            reason = "attachment size limit exceeded"
        elif content_type not in self._policy.allowed_content_types:
            if (
                direction is AttachmentDirection.INBOUND
                and self._policy.quarantine_unknown_inbound_types
            ):
                disposition = AttachmentDisposition.QUARANTINED
                reason = "attachment content type requires quarantine"
                self._quarantined += 1
            else:
                disposition = AttachmentDisposition.REJECTED
                reason = "attachment content type blocked"
        if (
            disposition is AttachmentDisposition.REJECTED
            and direction is AttachmentDirection.INBOUND
        ):
            self._rejected += 1
        return AttachmentDecision(
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            sha256=digest,
            disposition=disposition,
            reason=reason,
        )

    @staticmethod
    def _normalize_attachment(
        item: Mapping[str, Any], *, content_optional: bool = False
    ) -> dict[str, Any]:
        filename = _safe_filename(str(item.get("filename", "")))
        content_type = str(item.get("content_type", "")).strip().lower()
        if not filename:
            raise AttachmentGovernanceError("attachment filename required")
        if not content_type or "/" not in content_type:
            raise AttachmentGovernanceError("attachment content type required")
        content = item.get("content")
        if content is None and content_optional:
            size_bytes = int(item.get("size_bytes", 0))
            digest = str(item.get("sha256", ""))
            if size_bytes < 0 or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise AttachmentGovernanceError("attachment metadata invalid")
            return {
                "filename": filename,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "sha256": digest,
            }
        if not isinstance(content, bytes):
            raise AttachmentGovernanceError("attachment content must be bytes")
        return {
            "filename": filename,
            "content_type": content_type,
            "content": content,
            "size_bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }


def _safe_filename(value: str) -> str:
    candidate = value.replace("\\", "/").rsplit("/", 1)[-1].strip()
    candidate = re.sub(r"[\x00-\x1f\x7f]", "", candidate)
    return candidate[:255]
