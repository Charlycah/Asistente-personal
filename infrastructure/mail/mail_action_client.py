from __future__ import annotations

import smtplib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Protocol
from uuid import uuid4

from infrastructure.mail.mail_client import MailProviderError


@dataclass(frozen=True)
class MailDraft:
    """Borrador normalizado para acciones de correo de M67."""

    to: tuple[str, ...]
    subject: str
    body: str
    cc: tuple[str, ...] = ()
    bcc: tuple[str, ...] = ()
    reply_to_message_id: str | None = None
    draft_id: str = field(default_factory=lambda: uuid4().hex)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.to:
            raise ValueError("mail draft recipients must not be empty")
        if any(not recipient.strip() for recipient in self.to):
            raise ValueError("mail draft recipients must not be blank")
        if any(not recipient.strip() for recipient in self.cc):
            raise ValueError("mail draft cc recipients must not be blank")
        if any(not recipient.strip() for recipient in self.bcc):
            raise ValueError("mail draft bcc recipients must not be blank")
        if not self.subject.strip():
            raise ValueError("mail draft subject must not be empty")
        if not self.body.strip():
            raise ValueError("mail draft body must not be empty")
        if (
            self.reply_to_message_id is not None
            and not self.reply_to_message_id.strip()
        ):
            raise ValueError("mail draft reply id must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("mail draft timestamp must be timezone-aware")
        if not self.draft_id.strip():
            raise ValueError("mail draft id must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "draft_id": self.draft_id,
            "to": list(self.to),
            "cc": list(self.cc),
            "bcc": list(self.bcc),
            "subject": self.subject,
            "body": self.body,
            "reply_to_message_id": self.reply_to_message_id,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class MailSendReceipt:
    """Recibo auditable de una acción de envío de correo."""

    draft: MailDraft
    provider_message_id: str
    sent_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    receipt_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.provider_message_id.strip():
            raise ValueError("mail provider message id must not be empty")
        if self.sent_at.tzinfo is None:
            raise ValueError("mail send timestamp must be timezone-aware")
        if not self.receipt_id.strip():
            raise ValueError("mail send receipt id must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "receipt_id": self.receipt_id,
            "provider_message_id": self.provider_message_id,
            "draft": self.draft.to_dict(),
            "sent_at": self.sent_at.isoformat(),
        }


class MailActionProvider(Protocol):
    """Contrato mínimo para redactar y enviar correo detrás de M67."""

    def create_draft(self, draft: MailDraft) -> MailDraft:
        """Crea o conserva un borrador sin enviarlo."""

    def send(self, draft: MailDraft) -> MailSendReceipt:
        """Envía un borrador previamente autorizado."""


SmtpFactory = Callable[[str, int], smtplib.SMTP_SSL]


class SmtpMailActionClient:
    """Cliente SMTP mínimo; nunca debe ser invocado directamente por el core."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        *,
        smtp_factory: SmtpFactory = smtplib.SMTP_SSL,
    ) -> None:
        if not host.strip():
            raise ValueError("smtp host must not be empty")
        if port <= 0:
            raise ValueError("smtp port must be positive")
        if not username.strip():
            raise ValueError("smtp username must not be empty")
        if not password.strip():
            raise ValueError("smtp password must not be empty")
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.smtp_factory = smtp_factory

    def create_draft(self, draft: MailDraft) -> MailDraft:
        return draft

    def send(self, draft: MailDraft) -> MailSendReceipt:
        message = EmailMessage()
        message["From"] = self.username
        message["To"] = ", ".join(draft.to)
        if draft.cc:
            message["Cc"] = ", ".join(draft.cc)
        message["Subject"] = draft.subject
        message.set_content(draft.body)
        recipients = (*draft.to, *draft.cc, *draft.bcc)
        try:
            with self.smtp_factory(self.host, self.port) as connection:
                connection.login(self.username, self.password)
                response = connection.send_message(message, to_addrs=list(recipients))
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise MailProviderError("mail send failed") from exc
        provider_id = f"smtp:{draft.draft_id}:{len(response)}"
        return MailSendReceipt(draft=draft, provider_message_id=provider_id)
