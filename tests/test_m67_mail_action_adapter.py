from __future__ import annotations

import pytest

from core.capability_registry import (
    CapabilityRegistryManager,
    default_semantic_capabilities,
)
from core.permission_consent import PermissionConsentManager, PermissionGrant
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
from infrastructure.mail.mail_action_adapter import (
    MailActionAdapter,
    MailActionAdapterPolicy,
    build_mail_action_adapter_from_config,
)
from infrastructure.mail.mail_action_client import MailDraft, MailSendReceipt


class FakeMailActionProvider:
    def __init__(self) -> None:
        self.drafts: list[MailDraft] = []
        self.sent: list[MailDraft] = []

    def create_draft(self, draft: MailDraft) -> MailDraft:
        self.drafts.append(draft)
        return draft

    def send(self, draft: MailDraft) -> MailSendReceipt:
        self.sent.append(draft)
        return MailSendReceipt(draft=draft, provider_message_id="fake-message-id")


def build_gateway(*, grant_send: bool = False) -> ToolGatewayManager:
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    permissions = PermissionConsentManager()
    if grant_send:
        permissions.grant(PermissionGrant("mail.send", "write"))
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


def test_mail_action_adapter_registers_write_handler():
    gateway = build_gateway(grant_send=True)
    adapter = MailActionAdapter(FakeMailActionProvider())

    adapter.register_with_gateway(gateway)
    result = gateway.execute(
        ToolRequest(
            "mail.send",
            payload={
                "action": "draft",
                "to": ("ana@example.com",),
                "subject": "Respuesta",
                "body": "Gracias por el aviso.",
            },
        )
    )

    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert result.output["kind"] == "mail_draft"


def test_mail_action_requires_explicit_consent_before_drafting():
    gateway = build_gateway(grant_send=False)
    adapter = MailActionAdapter(FakeMailActionProvider())
    adapter.register_with_gateway(gateway)

    result = adapter.execute_draft(
        gateway,
        to=("ana@example.com",),
        subject="Respuesta",
        body="Lo reviso y te confirmo.",
    )

    assert result.normalized_status is ToolGatewayStatus.BLOCKED
    assert result.error == "consent_required:write"
    assert gateway.permission_consent is not None
    assert gateway.permission_consent.last_decision is not None
    assert gateway.permission_consent.last_decision.required_confirmation is True


def test_mail_action_creates_draft_after_consent_grant():
    provider = FakeMailActionProvider()
    gateway = build_gateway(grant_send=True)
    adapter = MailActionAdapter(provider)
    adapter.register_with_gateway(gateway)

    result = adapter.execute_draft(
        gateway,
        to=("ana@example.com",),
        subject="Respuesta",
        body="Lo reviso y te confirmo.",
    )

    assert result.succeeded is True
    assert len(provider.drafts) == 1
    assert result.output["mutates_external_state"] is False
    assert "No lo envié todavía" in result.output["natural_summary"]


def test_mail_action_reply_prefixes_subject_and_links_original_message():
    gateway = build_gateway(grant_send=True)
    adapter = MailActionAdapter(FakeMailActionProvider())
    adapter.register_with_gateway(gateway)

    result = adapter.execute_reply(
        gateway,
        message_id="m-1",
        to=("soporte@example.com",),
        subject="Ticket resuelto",
        body="Gracias por resolverlo.",
    )

    draft = result.output["draft"]
    assert draft["subject"] == "Re: Ticket resuelto"
    assert draft["reply_to_message_id"] == "m-1"


def test_mail_action_keeps_existing_reply_prefix():
    adapter = MailActionAdapter(FakeMailActionProvider())

    output = adapter.handle_mail_action(
        {
            "action": "reply",
            "message_id": "m-1",
            "to": ("soporte@example.com",),
            "subject": "Re: Ticket resuelto",
            "body": "Gracias.",
        }
    )

    assert output["draft"]["subject"] == "Re: Ticket resuelto"


def test_mail_action_can_send_only_after_gateway_consent():
    provider = FakeMailActionProvider()
    gateway = build_gateway(grant_send=True)
    adapter = MailActionAdapter(provider)
    adapter.register_with_gateway(gateway)

    result = adapter.execute_send(
        gateway,
        to=("ana@example.com",),
        subject="Confirmación",
        body="Confirmado.",
    )

    assert result.succeeded is True
    assert result.output["kind"] == "mail_send_receipt"
    assert result.output["mutates_external_state"] is True
    assert len(provider.sent) == 1


def test_mail_action_can_disable_send_by_policy():
    adapter = MailActionAdapter(
        FakeMailActionProvider(),
        MailActionAdapterPolicy(allow_send_action=False),
    )

    with pytest.raises(ValueError, match="disabled"):
        adapter.handle_mail_action(
            {
                "action": "send",
                "to": ("ana@example.com",),
                "subject": "Confirmación",
                "body": "Confirmado.",
            }
        )


def test_mail_action_rejects_empty_recipients_or_body():
    adapter = MailActionAdapter(FakeMailActionProvider())

    with pytest.raises(ValueError, match="to recipients"):
        adapter.handle_mail_action(
            {"action": "draft", "subject": "Hola", "body": "Texto"}
        )
    with pytest.raises(ValueError, match="body"):
        adapter.handle_mail_action(
            {
                "action": "draft",
                "to": ("ana@example.com",),
                "subject": "Hola",
                "body": "",
            }
        )


def test_semantic_registry_discovers_mail_actions_from_natural_language():
    gateway = build_gateway(grant_send=True)
    adapter = MailActionAdapter(FakeMailActionProvider())
    adapter.register_with_gateway(gateway)

    snapshot = gateway.observe_turn("ROBY, redactá una respuesta para Ana")

    assert "mail.send" in snapshot.requested_capabilities


def test_build_mail_action_adapter_from_config_requires_credentials():
    with pytest.raises(ValueError, match="GMAIL_ADDRESS"):
        build_mail_action_adapter_from_config(
            base_config(gmail_address=None, gmail_app_password="secret")
        )
    with pytest.raises(ValueError, match="GMAIL_APP_PASSWORD"):
        build_mail_action_adapter_from_config(
            base_config(gmail_address="carlos@example.com", gmail_app_password=None)
        )


def test_build_mail_action_adapter_from_config_uses_secure_settings():
    adapter = build_mail_action_adapter_from_config(
        base_config(
            gmail_address="carlos@example.com",
            gmail_app_password="secret",
        )
    )

    assert isinstance(adapter, MailActionAdapter)
