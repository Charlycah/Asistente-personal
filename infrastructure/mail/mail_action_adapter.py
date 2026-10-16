from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from core.tool_gateway import ToolGatewayManager, ToolRequest, ToolResult
from infrastructure.config.config_schema import AppConfig
from infrastructure.mail.mail_action_client import (
    MailActionProvider,
    MailDraft,
    SmtpMailActionClient,
)


@dataclass(frozen=True)
class MailActionAdapterPolicy:
    """Política de M67 para acciones de correo con consentimiento explícito."""

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    allow_send_action: bool = True
    default_subject_prefix: str = ""

    def __post_init__(self) -> None:
        if not self.smtp_host.strip():
            raise ValueError("mail smtp host must not be empty")
        if self.smtp_port <= 0:
            raise ValueError("mail smtp port must be positive")


class MailActionAdapter:
    """Adapter M67: redactar, responder y enviar correo bajo permisos M63."""

    ACTION_CAPABILITY = "mail.send"

    def __init__(
        self,
        provider: MailActionProvider,
        policy: MailActionAdapterPolicy | None = None,
    ) -> None:
        self.provider = provider
        self.policy = policy or MailActionAdapterPolicy()

    def register_with_gateway(self, gateway: ToolGatewayManager) -> None:
        """Registra acciones de correo detrás del Tool Gateway."""

        gateway.register_capability(
            gateway.capabilities[self.ACTION_CAPABILITY],
            handler=self.handle_mail_action,
        )

    def handle_mail_action(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        action = str(payload.get("action") or "draft").casefold()
        if action in {"draft", "compose"}:
            draft = self.provider.create_draft(self._draft_from(payload))
            return self._draft_output(draft, action="draft")
        if action == "reply":
            draft = self.provider.create_draft(self._reply_draft_from(payload))
            return self._draft_output(draft, action="reply")
        if action == "send":
            if not self.policy.allow_send_action:
                raise ValueError("mail send action is disabled by policy")
            draft = self._draft_from(payload)
            receipt = self.provider.send(draft)
            return {
                "capability": self.ACTION_CAPABILITY,
                "kind": "mail_send_receipt",
                "action": "send",
                "receipt": receipt.to_dict(),
                "requires_consent": True,
                "mutates_external_state": True,
                "natural_summary": (
                    f"Envié el correo '{draft.subject}' a {', '.join(draft.to)}."
                ),
            }
        raise ValueError("unsupported mail action")

    def execute_draft(
        self,
        gateway: ToolGatewayManager,
        *,
        to: tuple[str, ...],
        subject: str,
        body: str,
        reason: str = "mail_draft_requested",
    ) -> ToolResult:
        return gateway.execute(
            ToolRequest(
                self.ACTION_CAPABILITY,
                payload={
                    "action": "draft",
                    "to": to,
                    "subject": subject,
                    "body": body,
                },
                reason=reason,
            )
        )

    def execute_reply(
        self,
        gateway: ToolGatewayManager,
        *,
        message_id: str,
        to: tuple[str, ...],
        subject: str,
        body: str,
        reason: str = "mail_reply_requested",
    ) -> ToolResult:
        return gateway.execute(
            ToolRequest(
                self.ACTION_CAPABILITY,
                payload={
                    "action": "reply",
                    "message_id": message_id,
                    "to": to,
                    "subject": subject,
                    "body": body,
                },
                reason=reason,
            )
        )

    def execute_send(
        self,
        gateway: ToolGatewayManager,
        *,
        to: tuple[str, ...],
        subject: str,
        body: str,
        reason: str = "mail_send_requested",
    ) -> ToolResult:
        return gateway.execute(
            ToolRequest(
                self.ACTION_CAPABILITY,
                payload={
                    "action": "send",
                    "to": to,
                    "subject": subject,
                    "body": body,
                },
                reason=reason,
            )
        )

    def _draft_from(self, payload: Mapping[str, Any]) -> MailDraft:
        return MailDraft(
            to=self._recipients_from(payload, "to"),
            cc=self._recipients_from(payload, "cc", required=False),
            bcc=self._recipients_from(payload, "bcc", required=False),
            subject=self._subject_from(payload),
            body=self._body_from(payload),
            reply_to_message_id=self._optional_text(payload, "reply_to_message_id"),
        )

    def _reply_draft_from(self, payload: Mapping[str, Any]) -> MailDraft:
        message_id = self._required_text(payload, "message_id")
        subject = self._subject_from(payload)
        if not subject.casefold().startswith("re:"):
            subject = f"Re: {subject}"
        return MailDraft(
            to=self._recipients_from(payload, "to"),
            cc=self._recipients_from(payload, "cc", required=False),
            bcc=self._recipients_from(payload, "bcc", required=False),
            subject=subject,
            body=self._body_from(payload),
            reply_to_message_id=message_id,
        )

    def _subject_from(self, payload: Mapping[str, Any]) -> str:
        subject = self._required_text(payload, "subject")
        return f"{self.policy.default_subject_prefix}{subject}"

    @staticmethod
    def _body_from(payload: Mapping[str, Any]) -> str:
        return MailActionAdapter._required_text(payload, "body")

    @staticmethod
    def _required_text(payload: Mapping[str, Any], key: str) -> str:
        value = str(payload.get(key) or "")
        if not value.strip():
            raise ValueError(f"mail {key} must not be empty")
        return value.strip()

    @staticmethod
    def _optional_text(payload: Mapping[str, Any], key: str) -> str | None:
        value = payload.get(key)
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _recipients_from(
        payload: Mapping[str, Any],
        key: str,
        *,
        required: bool = True,
    ) -> tuple[str, ...]:
        raw = payload.get(key, ())
        if isinstance(raw, str):
            recipients = tuple(item.strip() for item in raw.split(",") if item.strip())
        else:
            recipients = tuple(str(item).strip() for item in raw if str(item).strip())
        if required and not recipients:
            raise ValueError(f"mail {key} recipients must not be empty")
        return recipients

    def _draft_output(self, draft: MailDraft, *, action: str) -> Mapping[str, Any]:
        return {
            "capability": self.ACTION_CAPABILITY,
            "kind": "mail_draft",
            "action": action,
            "draft": draft.to_dict(),
            "requires_consent": True,
            "mutates_external_state": action == "send",
            "natural_summary": (
                f"Preparé un borrador para {', '.join(draft.to)} con asunto "
                f"'{draft.subject}'. No lo envié todavía."
            ),
        }


def build_mail_action_adapter_from_config(config: AppConfig) -> MailActionAdapter:
    """Factory segura: usa credenciales centralizadas para SMTP."""

    address = config.secrets.gmail_address
    password = config.secrets.gmail_app_password
    if address is None or not address.strip():
        raise ValueError("GMAIL_ADDRESS is required for MailActionAdapter")
    if password is None or not password.strip():
        raise ValueError("GMAIL_APP_PASSWORD is required for MailActionAdapter")
    policy = MailActionAdapterPolicy()
    provider = SmtpMailActionClient(
        policy.smtp_host,
        policy.smtp_port,
        address,
        password,
    )
    return MailActionAdapter(provider, policy)
