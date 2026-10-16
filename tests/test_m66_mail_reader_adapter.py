from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.capability_registry import (
    CapabilityRegistryManager,
    default_semantic_capabilities,
)
from core.permission_consent import PermissionConsentManager
from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus, ToolRequest
from infrastructure.config.config_schema import (
    AppConfig,
    AssistantConfig,
    LLMConfig,
    MemoryConfig,
    RemindersConfig,
    SecretsConfig,
    VoiceConfig,
    WeatherConfig,
)
from infrastructure.mail.mail_adapter import (
    MailReaderAdapter,
    MailReaderAdapterPolicy,
    build_mail_reader_adapter_from_config,
)
from infrastructure.mail.mail_client import (
    MailMessage,
    MailProviderError,
    MailSearchResult,
)


class FakeMailProvider:
    def __init__(self) -> None:
        self.messages = (
            MailMessage(
                message_id="m-2",
                sender="Ana <ana@example.com>",
                subject="Presupuesto actualizado",
                snippet="Te envío la nueva versión del presupuesto.",
                received_at=datetime(2026, 7, 9, 13, 0, tzinfo=timezone.utc),
                recipients=("carlos@example.com",),
                labels=("INBOX",),
                unread=True,
                body="Te envío la nueva versión del presupuesto.",
            ),
            MailMessage(
                message_id="m-1",
                sender="Soporte <soporte@example.com>",
                subject="Ticket resuelto",
                snippet="El incidente ya fue resuelto.",
                received_at=datetime(2026, 7, 9, 10, 0, tzinfo=timezone.utc),
                recipients=("carlos@example.com",),
                labels=("INBOX",),
                unread=False,
                body="El incidente ya fue resuelto.",
            ),
        )

    def list_recent(
        self,
        *,
        limit: int = 10,
        unread_only: bool = False,
    ) -> MailSearchResult:
        messages = self.messages[:limit]
        if unread_only:
            messages = tuple(message for message in messages if message.unread)
        return MailSearchResult(messages=messages)

    def search(self, query: str, *, limit: int = 10) -> MailSearchResult:
        normalized = query.casefold()
        messages = tuple(
            message
            for message in self.messages
            if normalized in message.subject.casefold()
            or normalized in message.snippet.casefold()
            or normalized in message.sender.casefold()
        )[:limit]
        return MailSearchResult(messages=messages, query=query)

    def read(self, message_id: str) -> MailMessage:
        for message in self.messages:
            if message.message_id == message_id:
                return message
        raise MailProviderError("message not found")


def build_gateway() -> ToolGatewayManager:
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    permissions = PermissionConsentManager()
    return ToolGatewayManager(
        capability_registry=registry,
        permission_consent=permissions,
    )


def base_config(
    *,
    gmail_address: str | None,
    gmail_app_password: str | None,
) -> AppConfig:
    return AppConfig(
        assistant=AssistantConfig("ROBY", "es", "America/Argentina/Buenos_Aires"),
        weather=WeatherConfig("Buenos Aires", "openweather", "openweather"),
        memory=MemoryConfig(True, "roby.db"),
        reminders=RemindersConfig(True, 60),
        llm=LLMConfig("none", "none"),
        voice=VoiceConfig(False, "none", "none"),
        secrets=SecretsConfig(
            openweather_api_key=None,
            weatherapi_key=None,
            google_client_secret_file=None,
            google_token_file=None,
            gmail_address=gmail_address,
            gmail_app_password=gmail_app_password,
            gemini_api_key=None,
            openrouter_api_key=None,
            mistral_api_key=None,
            openai_api_key=None,
            camera_index=0,
        ),
        debug=False,
    )


def test_mail_reader_adapter_registers_read_handler():
    gateway = build_gateway()
    adapter = MailReaderAdapter(FakeMailProvider())

    adapter.register_with_gateway(gateway)
    result = gateway.execute(ToolRequest("mail.read", payload={"action": "summary"}))

    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert result.output["kind"] == "mail_read_result"
    assert result.output["read_only"] is True


def test_mail_reader_summary_lists_recent_messages_without_mutation():
    adapter = MailReaderAdapter(FakeMailProvider())

    output = adapter.read_mail({"action": "summary", "limit": 2})

    assert output["read_only"] is True
    assert len(output["messages"]) == 2
    assert "Presupuesto actualizado" in output["natural_summary"]


def test_mail_reader_can_filter_unread_messages():
    adapter = MailReaderAdapter(FakeMailProvider())

    output = adapter.read_mail({"action": "recent", "unread_only": True})

    assert output["mail"]["unread_count"] == 1
    assert len(output["messages"]) == 1


def test_mail_reader_search_uses_query_payload():
    adapter = MailReaderAdapter(FakeMailProvider())

    output = adapter.read_mail({"action": "search", "query": "presupuesto"})

    assert output["action"] == "search"
    assert output["query"] == "presupuesto"
    assert output["messages"][0]["message_id"] == "m-2"


def test_mail_reader_can_read_single_message():
    adapter = MailReaderAdapter(FakeMailProvider())

    output = adapter.read_mail({"action": "read", "message_id": "m-1"})

    assert output["kind"] == "mail_message"
    assert output["message"]["subject"] == "Ticket resuelto"
    assert output["read_only"] is True


def test_mail_reader_rejects_write_like_or_unknown_actions():
    adapter = MailReaderAdapter(FakeMailProvider())

    with pytest.raises(ValueError, match="unsupported"):
        adapter.read_mail({"action": "send"})


def test_semantic_registry_discovers_mail_read_from_natural_language():
    gateway = build_gateway()
    adapter = MailReaderAdapter(FakeMailProvider())
    adapter.register_with_gateway(gateway)

    snapshot = gateway.observe_turn("ROBY, tengo correos nuevos o algo urgente?")

    assert "mail.read" in snapshot.requested_capabilities


def test_mail_reader_respects_read_permission_layer():
    gateway = build_gateway()
    adapter = MailReaderAdapter(FakeMailProvider())
    adapter.register_with_gateway(gateway)

    result = adapter.execute_summary(gateway, unread_only=True)

    assert result.succeeded is True
    assert gateway.permission_consent is not None
    assert gateway.permission_consent.last_decision is not None
    assert gateway.permission_consent.last_decision.allowed is True


def test_mail_reader_caps_limit_to_policy_maximum():
    adapter = MailReaderAdapter(
        FakeMailProvider(),
        MailReaderAdapterPolicy(default_limit=1, max_limit=1),
    )

    output = adapter.read_mail({"action": "summary", "limit": 50})

    assert len(output["messages"]) == 1


def test_build_mail_reader_adapter_from_config_requires_credentials():
    config = base_config(gmail_address=None, gmail_app_password="secret")

    with pytest.raises(ValueError, match="GMAIL_ADDRESS"):
        build_mail_reader_adapter_from_config(config)


def test_build_mail_reader_adapter_from_config_accepts_credentials():
    config = base_config(
        gmail_address="carlos@example.com",
        gmail_app_password="app-password",
    )

    adapter = build_mail_reader_adapter_from_config(config)

    assert isinstance(adapter, MailReaderAdapter)
