from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from core.tool_gateway import ToolGatewayManager, ToolRequest, ToolResult
from infrastructure.config.config_schema import AppConfig
from infrastructure.mail.mail_client import (
    ImapMailClient,
    MailMessage,
    MailReadProvider,
    MailSearchResult,
)


@dataclass(frozen=True)
class MailReaderAdapterPolicy:
    """Política de M66 para lectura segura y resumible de correo."""

    default_limit: int = 10
    max_limit: int = 25
    default_unread_only: bool = False
    imap_host: str = "imap.gmail.com"
    mailbox: str = "INBOX"

    def __post_init__(self) -> None:
        if self.default_limit <= 0:
            raise ValueError("mail default limit must be positive")
        if self.max_limit <= 0:
            raise ValueError("mail max limit must be positive")
        if self.default_limit > self.max_limit:
            raise ValueError("mail default limit must not exceed max limit")
        if not self.imap_host.strip():
            raise ValueError("mail imap host must not be empty")
        if not self.mailbox.strip():
            raise ValueError("mail mailbox must not be empty")


class MailReaderAdapter:
    """Adapter M66: lectura de correo sin enviar, borrar ni modificar mensajes."""

    READ_CAPABILITY = "mail.read"

    def __init__(
        self,
        provider: MailReadProvider,
        policy: MailReaderAdapterPolicy | None = None,
    ) -> None:
        self.provider = provider
        self.policy = policy or MailReaderAdapterPolicy()

    def register_with_gateway(self, gateway: ToolGatewayManager) -> None:
        """Registra el handler read-only de correo detrás del Tool Gateway."""

        gateway.register_capability(
            gateway.capabilities[self.READ_CAPABILITY],
            handler=self.read_mail,
        )

    def read_mail(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        action = str(payload.get("action") or "summary").casefold()
        if action in {"summary", "list", "recent"}:
            unread_only = bool(
                payload.get("unread_only", self.policy.default_unread_only)
            )
            result = self.provider.list_recent(
                limit=self._limit_from(payload),
                unread_only=unread_only,
            )
            return self._search_output(result, action="recent", unread_only=unread_only)
        if action == "search":
            query = self._query_from(payload)
            result = self.provider.search(query, limit=self._limit_from(payload))
            return self._search_output(result, action="search", query=query)
        if action == "read":
            message = self.provider.read(self._message_id_from(payload))
            return self._message_output(message)
        raise ValueError("unsupported mail reader action")

    def execute_summary(
        self,
        gateway: ToolGatewayManager,
        *,
        limit: int | None = None,
        unread_only: bool | None = None,
        reason: str = "mail_summary_requested",
    ) -> ToolResult:
        payload: dict[str, object] = {"action": "summary"}
        if limit is not None:
            payload["limit"] = limit
        if unread_only is not None:
            payload["unread_only"] = unread_only
        return gateway.execute(
            ToolRequest(self.READ_CAPABILITY, payload=payload, reason=reason)
        )

    def execute_search(
        self,
        gateway: ToolGatewayManager,
        query: str,
        *,
        limit: int | None = None,
        reason: str = "mail_search_requested",
    ) -> ToolResult:
        payload: dict[str, object] = {"action": "search", "query": query}
        if limit is not None:
            payload["limit"] = limit
        return gateway.execute(
            ToolRequest(self.READ_CAPABILITY, payload=payload, reason=reason)
        )

    def execute_read(
        self,
        gateway: ToolGatewayManager,
        message_id: str,
        *,
        reason: str = "mail_read_requested",
    ) -> ToolResult:
        return gateway.execute(
            ToolRequest(
                self.READ_CAPABILITY,
                payload={"action": "read", "message_id": message_id},
                reason=reason,
            )
        )

    def _limit_from(self, payload: Mapping[str, Any]) -> int:
        limit = int(payload.get("limit", self.policy.default_limit))
        if limit <= 0:
            raise ValueError("mail limit must be positive")
        return min(limit, self.policy.max_limit)

    @staticmethod
    def _query_from(payload: Mapping[str, Any]) -> str:
        query = str(payload.get("query") or "")
        if not query.strip():
            raise ValueError("mail search query must not be empty")
        return query

    @staticmethod
    def _message_id_from(payload: Mapping[str, Any]) -> str:
        message_id = str(payload.get("message_id") or "")
        if not message_id.strip():
            raise ValueError("mail message id must not be empty")
        return message_id

    def _search_output(
        self,
        result: MailSearchResult,
        *,
        action: str,
        query: str | None = None,
        unread_only: bool = False,
    ) -> Mapping[str, Any]:
        messages = tuple(message.to_dict() for message in result.messages)
        return {
            "capability": self.READ_CAPABILITY,
            "kind": "mail_read_result",
            "action": action,
            "query": query,
            "unread_only": unread_only,
            "mail": result.to_dict(),
            "messages": messages,
            "natural_summary": self._summary_for(result),
            "read_only": True,
        }

    def _message_output(self, message: MailMessage) -> Mapping[str, Any]:
        return {
            "capability": self.READ_CAPABILITY,
            "kind": "mail_message",
            "message": message.to_dict(),
            "natural_summary": (
                f"Leí el correo '{message.subject}' de {message.sender}. "
                f"Resumen: {message.snippet}"
            ),
            "read_only": True,
        }

    @staticmethod
    def _summary_for(result: MailSearchResult) -> str:
        total = len(result.messages)
        if total == 0:
            return "No encontré correos para ese criterio."
        first = result.messages[0]
        unread = result.unread_count
        unread_text = f"; {unread} sin leer" if unread else ""
        return (
            f"Encontré {total} correo(s){unread_text}. "
            f"El más reciente es '{first.subject}' de {first.sender}."
        )



def build_mail_reader_adapter_from_credentials(
    *,
    address: str | None,
    password: str | None,
) -> MailReaderAdapter:
    """Build the read-only Gmail adapter from canonical ROBY credentials."""

    if address is None or not address.strip():
        raise ValueError("GMAIL_ADDRESS is required for MailReaderAdapter")
    if password is None or not password.strip():
        raise ValueError("GMAIL_APP_PASSWORD is required for MailReaderAdapter")
    policy = MailReaderAdapterPolicy()
    provider = ImapMailClient(
        policy.imap_host,
        address.strip(),
        password,
        mailbox=policy.mailbox,
    )
    return MailReaderAdapter(provider, policy)

def build_mail_reader_adapter_from_config(config: AppConfig) -> MailReaderAdapter:
    """Factory segura: usa credenciales centralizadas para crear IMAP read-only."""

    return build_mail_reader_adapter_from_credentials(
        address=config.secrets.gmail_address,
        password=config.secrets.gmail_app_password,
    )
