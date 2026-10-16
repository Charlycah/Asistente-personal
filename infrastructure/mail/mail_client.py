from __future__ import annotations

import email
import imaplib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.message import Message
from typing import Protocol


@dataclass(frozen=True)
class MailMessage:
    """Mensaje de correo normalizado para ROBY en modo solo lectura."""

    message_id: str
    sender: str
    subject: str
    snippet: str
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    recipients: tuple[str, ...] = ()
    labels: tuple[str, ...] = ()
    unread: bool = False
    has_attachments: bool = False
    body: str | None = None

    def __post_init__(self) -> None:
        if not self.message_id.strip():
            raise ValueError("mail message id must not be empty")
        if not self.sender.strip():
            raise ValueError("mail sender must not be empty")
        if not self.subject.strip():
            raise ValueError("mail subject must not be empty")
        if not self.snippet.strip():
            raise ValueError("mail snippet must not be empty")
        if self.received_at.tzinfo is None:
            raise ValueError("mail timestamp must be timezone-aware")
        if any(not item.strip() for item in self.recipients):
            raise ValueError("mail recipients must not be blank")
        if any(not item.strip() for item in self.labels):
            raise ValueError("mail labels must not be blank")
        if self.body is not None and not self.body.strip():
            raise ValueError("mail body must not be blank")

    def to_dict(self) -> dict[str, object]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "subject": self.subject,
            "snippet": self.snippet,
            "received_at": self.received_at.isoformat(),
            "recipients": list(self.recipients),
            "labels": list(self.labels),
            "unread": self.unread,
            "has_attachments": self.has_attachments,
            "body": self.body,
        }


@dataclass(frozen=True)
class MailSearchResult:
    """Resultado normalizado de búsqueda o listado de correos."""

    messages: tuple[MailMessage, ...]
    query: str | None = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.query is not None and not self.query.strip():
            raise ValueError("mail query must not be blank")
        if self.generated_at.tzinfo is None:
            raise ValueError("mail search timestamp must be timezone-aware")

    @property
    def unread_count(self) -> int:
        return sum(1 for message in self.messages if message.unread)

    def to_dict(self) -> dict[str, object]:
        return {
            "query": self.query,
            "messages": [message.to_dict() for message in self.messages],
            "unread_count": self.unread_count,
            "generated_at": self.generated_at.isoformat(),
        }


class MailProviderError(RuntimeError):
    """Error normalizado del proveedor de correo."""


class MailReadProvider(Protocol):
    """Contrato mínimo para providers de correo de solo lectura."""

    def list_recent(
        self,
        *,
        limit: int = 10,
        unread_only: bool = False,
    ) -> MailSearchResult:
        """Lista correos recientes sin modificar la casilla."""

    def search(self, query: str, *, limit: int = 10) -> MailSearchResult:
        """Busca correos sin modificar la casilla."""

    def read(self, message_id: str) -> MailMessage:
        """Lee un correo por ID sin responder, borrar ni marcar acciones externas."""


ImapFactory = Callable[[str], imaplib.IMAP4_SSL]


class ImapMailClient:
    """Cliente IMAP mínimo detrás del adapter; nunca lo usa el core."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        *,
        mailbox: str = "INBOX",
        imap_factory: ImapFactory = imaplib.IMAP4_SSL,
    ) -> None:
        if not host.strip():
            raise ValueError("imap host must not be empty")
        if not username.strip():
            raise ValueError("imap username must not be empty")
        if not password.strip():
            raise ValueError("imap password must not be empty")
        if not mailbox.strip():
            raise ValueError("imap mailbox must not be empty")
        self.host = host
        self.username = username
        self.password = password
        self.mailbox = mailbox
        self.imap_factory = imap_factory

    def list_recent(
        self,
        *,
        limit: int = 10,
        unread_only: bool = False,
    ) -> MailSearchResult:
        criterion = "UNSEEN" if unread_only else "ALL"
        return self._search_ids(criterion, limit=limit, query=None)

    def search(self, query: str, *, limit: int = 10) -> MailSearchResult:
        if not query.strip():
            raise ValueError("mail search query must not be empty")
        criterion = f'(TEXT "{query}")'
        return self._search_ids(criterion, limit=limit, query=query)

    def read(self, message_id: str) -> MailMessage:
        if not message_id.strip():
            raise ValueError("mail message id must not be empty")
        with self._connection() as connection:
            self._select(connection)
            return self._fetch_message(connection, message_id)

    def _search_ids(
        self,
        criterion: str,
        *,
        limit: int,
        query: str | None,
    ) -> MailSearchResult:
        if limit <= 0:
            raise ValueError("mail limit must be positive")
        with self._connection() as connection:
            self._select(connection)
            status, data = connection.search(None, criterion)
            if status != "OK" or not data:
                raise MailProviderError("mail search failed")
            ids = data[0].split()[-limit:]
            messages = tuple(
                self._fetch_message(connection, raw_id.decode("utf-8"))
                for raw_id in reversed(ids)
            )
            return MailSearchResult(messages=messages, query=query)

    def _connection(self) -> imaplib.IMAP4_SSL:
        connection = self.imap_factory(self.host)
        try:
            connection.login(self.username, self.password)
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise MailProviderError("mail login failed") from exc
        return connection

    def _select(self, connection: imaplib.IMAP4_SSL) -> None:
        status, _ = connection.select(self.mailbox, readonly=True)
        if status != "OK":
            raise MailProviderError("mailbox selection failed")

    def _fetch_message(
        self,
        connection: imaplib.IMAP4_SSL,
        message_id: str,
    ) -> MailMessage:
        status, data = connection.fetch(message_id, "(RFC822 FLAGS)")
        if status != "OK" or not data:
            raise MailProviderError("mail fetch failed")
        raw_message = self._raw_message_from(data)
        parsed = email.message_from_bytes(raw_message)
        return self._to_mail_message(message_id, parsed)

    @staticmethod
    def _raw_message_from(data: list[object]) -> bytes:
        for item in data:
            if (
                isinstance(item, tuple)
                and len(item) >= 2
                and isinstance(item[1], bytes)
            ):
                return item[1]
        raise MailProviderError("mail payload missing")

    def _to_mail_message(self, message_id: str, parsed: Message) -> MailMessage:
        subject = self._decoded_header(parsed.get("Subject", "Sin asunto"))
        sender = self._decoded_header(parsed.get("From", "remitente desconocido"))
        recipients = tuple(
            item.strip()
            for item in self._decoded_header(parsed.get("To", "")).split(",")
            if item.strip()
        )
        body = self._plain_text_body(parsed)
        snippet = self._snippet_from(body or subject)
        return MailMessage(
            message_id=message_id,
            sender=sender,
            subject=subject,
            snippet=snippet,
            recipients=recipients,
            unread=False,
            has_attachments=self._has_attachments(parsed),
            body=body,
        )

    @staticmethod
    def _decoded_header(value: str) -> str:
        try:
            return str(make_header(decode_header(value))).strip()
        except Exception:  # pragma: no cover - defensive fallback
            return value.strip()

    def _plain_text_body(self, parsed: Message) -> str | None:
        if parsed.is_multipart():
            for part in parsed.walk():
                if part.get_content_type() == "text/plain":
                    payload = self._decoded_payload(part)
                    if payload:
                        return payload
            return None
        return self._decoded_payload(parsed)

    @staticmethod
    def _decoded_payload(part: Message) -> str | None:
        payload = part.get_payload(decode=True)
        if payload is None:
            return None
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace").strip()

    @staticmethod
    def _snippet_from(text: str, *, max_length: int = 180) -> str:
        cleaned = " ".join(text.split())
        if len(cleaned) <= max_length:
            return cleaned
        return f"{cleaned[: max_length - 1]}…"

    @staticmethod
    def _has_attachments(parsed: Message) -> bool:
        if not parsed.is_multipart():
            return False
        return any(part.get_filename() for part in parsed.walk())
