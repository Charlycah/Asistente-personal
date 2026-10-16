from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Protocol


class GmailMetadataRequest(Protocol):
    def execute(self) -> Mapping[str, Any]: ...


class GmailSubjectServiceFactory(Protocol):
    def __call__(self, *, timeout_seconds: float) -> Any: ...


class GmailUnreadSubjectProvider(Protocol):
    def list_unread_subjects(self, *, limit: int) -> tuple[str, ...]: ...


@dataclass(frozen=True)
class GmailSubjectAnnouncementPolicy:
    """Read-only startup policy: unread count and subjects, never message bodies."""

    enabled: bool = False
    max_subjects: int = 5
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        if self.max_subjects <= 0:
            raise ValueError("gmail subject announcement limit must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("gmail subject announcement timeout must be positive")


@dataclass(frozen=True)
class GmailSubjectAnnouncement:
    """Secret-minimal read-only result suitable for UI and voice output."""

    subjects: tuple[str, ...]
    text: str
    read_only: bool = True
    bodies_requested: bool = False

    @property
    def count(self) -> int:
        return len(self.subjects)

    def to_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "count": self.count,
                "subjects": self.subjects,
                "text": self.text,
                "read_only": self.read_only,
                "bodies_requested": self.bodies_requested,
            }
        )


class GoogleGmailUnreadSubjectProvider:
    """Fetches unread Gmail subjects using metadata-only API requests."""

    USER_ID = "me"

    def __init__(
        self,
        service_factory: GmailSubjectServiceFactory,
        *,
        timeout_seconds: float = 10.0,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("gmail subject provider timeout must be positive")
        self._service_factory = service_factory
        self._timeout_seconds = timeout_seconds
        self._requests = 0
        self._failures = 0

    def list_unread_subjects(self, *, limit: int) -> tuple[str, ...]:
        if limit <= 0:
            raise ValueError("gmail subject limit must be positive")
        try:
            service = self._service_factory(timeout_seconds=self._timeout_seconds)
            messages_resource = service.users().messages()
            listing = messages_resource.list(
                userId=self.USER_ID,
                q="is:unread",
                maxResults=limit,
            ).execute()
            self._requests += 1
            messages = (
                listing.get("messages", ()) if isinstance(listing, Mapping) else ()
            )
            subjects: list[str] = []
            for item in messages:
                if not isinstance(item, Mapping) or not item.get("id"):
                    continue
                metadata = messages_resource.get(
                    userId=self.USER_ID,
                    id=str(item["id"]),
                    format="metadata",
                    metadataHeaders=["Subject"],
                ).execute()
                self._requests += 1
                subjects.append(_subject_from_metadata(metadata))
            return tuple(subjects)
        except (ValueError, TypeError, AttributeError, OSError) as exc:
            self._failures += 1
            raise RuntimeError("gmail unread subject lookup failed") from exc

    def status(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "provider": "gmail",
                "mode": "metadata_only",
                "query": "is:unread",
                "requests": self._requests,
                "failures": self._failures,
                "message_bodies_requested": False,
                "mailbox_mutated": False,
            }
        )


class GmailStartupSubjectAnnouncer:
    """Produces the startup phrase without reading bodies or mutating Gmail."""

    def __init__(
        self,
        provider: GmailUnreadSubjectProvider,
        policy: GmailSubjectAnnouncementPolicy | None = None,
    ) -> None:
        self.provider = provider
        self.policy = policy or GmailSubjectAnnouncementPolicy()

    def announce(self) -> GmailSubjectAnnouncement:
        if not self.policy.enabled:
            return GmailSubjectAnnouncement(subjects=(), text="")
        subjects = self.provider.list_unread_subjects(limit=self.policy.max_subjects)
        return GmailSubjectAnnouncement(
            subjects=subjects,
            text=_announcement_text(subjects),
        )

    def __call__(self) -> str:
        return self.announce().text


def _subject_from_metadata(payload: object) -> str:
    if not isinstance(payload, Mapping):
        return "Sin asunto"
    message_payload = payload.get("payload")
    if not isinstance(message_payload, Mapping):
        return "Sin asunto"
    headers = message_payload.get("headers", ())
    if not isinstance(headers, (list, tuple)):
        return "Sin asunto"
    for header in headers:
        if not isinstance(header, Mapping):
            continue
        if str(header.get("name", "")).casefold() == "subject":
            subject = " ".join(str(header.get("value", "")).split()).strip()
            return subject or "Sin asunto"
    return "Sin asunto"


def _announcement_text(subjects: tuple[str, ...]) -> str:
    count = len(subjects)
    if count == 0:
        return "No tenés correos nuevos."
    prefix = (
        "Tenés un correo nuevo." if count == 1 else f"Tenés {count} correos nuevos."
    )
    rendered = "; ".join(
        f"{index}. {subject}" for index, subject in enumerate(subjects, 1)
    )
    return f"{prefix} Asuntos: {rendered}."
