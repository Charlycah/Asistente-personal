from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.capability_registry import (
    CapabilityRegistryManager,
    default_semantic_capabilities,
)
from core.permission_consent import PermissionConsentManager, PermissionGrant
from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus
from infrastructure.mail.gmail_governed_integration import (
    GmailCapability,
    GmailCapabilityResolver,
    GmailGovernedIntegration,
    GmailGovernedPolicy,
)
from infrastructure.mail.mail_action_adapter import MailActionAdapter
from infrastructure.mail.mail_action_client import MailDraft, MailSendReceipt
from infrastructure.mail.mail_adapter import MailReaderAdapter
from infrastructure.mail.mail_client import MailMessage, MailSearchResult


class ReadProvider:
    def list_recent(
        self, *, limit: int = 10, unread_only: bool = False
    ) -> MailSearchResult:
        return MailSearchResult(messages=(self._message(),))

    def search(self, query: str, *, limit: int = 10) -> MailSearchResult:
        return MailSearchResult(messages=(self._message(),), query=query)

    def read(self, message_id: str) -> MailMessage:
        return self._message(message_id)

    @staticmethod
    def _message(message_id: str = "m-226-2") -> MailMessage:
        return MailMessage(
            message_id=message_id,
            sender="ana@example.com",
            subject="Capability layer",
            snippet="Ready",
            received_at=datetime(2026, 7, 14, tzinfo=timezone.utc),
        )


class ActionProvider:
    def create_draft(self, draft: MailDraft) -> MailDraft:
        return draft

    def send(self, draft: MailDraft) -> MailSendReceipt:
        return MailSendReceipt(draft=draft, provider_message_id="gmail-226-2")


def make_gateway(*, write: bool = False) -> ToolGatewayManager:
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    permissions = PermissionConsentManager()
    if write:
        permissions.grant(PermissionGrant("mail.send", "write"))
    return ToolGatewayManager(
        capability_registry=registry, permission_consent=permissions
    )


def make_integration(
    *, policy: GmailGovernedPolicy | None = None
) -> GmailGovernedIntegration:
    return GmailGovernedIntegration(
        account_address="carlos@example.com",
        reader=MailReaderAdapter(ReadProvider()),
        actions=MailActionAdapter(ActionProvider()),
        policy=policy,
    )


def test_resolver_maps_read_actions_to_semantic_read_and_physical_mail_read():
    decision = GmailCapabilityResolver().resolve("search", GmailGovernedPolicy())
    assert decision.capability is GmailCapability.READ
    assert decision.gateway_capability == "mail.read"
    assert decision.permission_scope == "read"
    assert decision.mutates_external_state is False


def test_resolver_distinguishes_compose_and_draft_semantics():
    resolver = GmailCapabilityResolver()
    compose = resolver.resolve("compose", GmailGovernedPolicy())
    draft = resolver.resolve("draft", GmailGovernedPolicy())
    assert compose.capability is GmailCapability.COMPOSE
    assert draft.capability is GmailCapability.DRAFT
    assert compose.gateway_capability == draft.gateway_capability == "mail.send"


def test_send_is_highest_governed_action_and_requires_confirmation():
    decision = GmailCapabilityResolver().resolve(
        "send", GmailGovernedPolicy(allow_send=True)
    )
    assert decision.capability is GmailCapability.SEND
    assert decision.mutates_external_state is True
    assert decision.requires_confirmation is True


def test_unknown_action_is_rejected_by_resolver():
    with pytest.raises(ValueError, match="unsupported"):
        GmailCapabilityResolver().resolve("purge", GmailGovernedPolicy())


def test_catalog_is_complete_stable_and_secret_free():
    catalog = GmailCapabilityResolver().catalog(GmailGovernedPolicy())
    assert tuple(item.capability.value for item in catalog) == (
        "gmail.read",
        "gmail.compose",
        "gmail.draft",
        "gmail.reply",
        "gmail.send",
    )
    assert "@" not in str(catalog)


def test_policy_is_reflected_in_capability_decision():
    decision = GmailCapabilityResolver().resolve(
        "reply", GmailGovernedPolicy(allow_reply=False)
    )
    assert decision.allowed is False


def test_integration_exposes_semantic_catalog_without_replacing_gateway_capabilities():
    item = make_integration()
    status = item.status()
    assert status["semantic_capability_count"] == 5
    assert item.capability_status()[-1]["capability"] == "gmail.send"
    assert item.capability_status()[0]["gateway_capability"] == "mail.read"


def test_compose_routes_through_existing_mail_send_gateway_handler():
    item = make_integration()
    gateway = make_gateway(write=True)
    item.register_with_gateway(gateway)
    result = item.execute(
        gateway,
        action="compose",
        payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
    )
    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert result.request.capability_name == "mail.send"
    assert result.output["action"] == "draft"


def test_semantic_layer_does_not_bypass_gateway_consent():
    item = make_integration()
    gateway = make_gateway(write=False)
    item.register_with_gateway(gateway)
    result = item.execute(
        gateway,
        action="reply",
        payload={
            "message_id": "m-1",
            "to": ("ana@example.com",),
            "subject": "Hola",
            "body": "Texto",
        },
    )
    assert result.normalized_status is ToolGatewayStatus.BLOCKED
    assert result.error == "consent_required:write"


def test_send_requires_local_policy_even_when_gateway_consent_exists():
    item = make_integration()
    gateway = make_gateway(write=True)
    item.register_with_gateway(gateway)
    with pytest.raises(PermissionError, match="send"):
        item.execute(
            gateway,
            action="send",
            payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
        )


def test_enabled_send_routes_only_after_both_governance_layers_allow_it():
    item = make_integration(policy=GmailGovernedPolicy(allow_send=True))
    gateway = make_gateway(write=True)
    item.register_with_gateway(gateway)
    result = item.execute(
        gateway,
        action="send",
        payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
    )
    assert result.succeeded is True
    assert item.audit_log[-1].capability == "mail.send"
    assert item.audit_log[-1].mutates_external_state is True


def test_capability_status_is_immutable_by_copy():
    item = make_integration()
    snapshot = item.capability_status()
    assert isinstance(snapshot, tuple)
    snapshot[0]["allowed"] = False
    assert item.capability_status()[0]["allowed"] is True
