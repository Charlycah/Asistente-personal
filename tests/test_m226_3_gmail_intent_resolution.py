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
    GmailGovernedIntegration,
    GmailGovernedPolicy,
    GmailIntent,
    GmailIntentResolver,
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
    def _message(message_id: str = "m-226-3") -> MailMessage:
        return MailMessage(
            message_id=message_id,
            sender="ana@example.com",
            subject="Intent layer",
            snippet="Ready",
            received_at=datetime(2026, 7, 14, tzinfo=timezone.utc),
        )


class ActionProvider:
    def create_draft(self, draft: MailDraft) -> MailDraft:
        return draft

    def send(self, draft: MailDraft) -> MailSendReceipt:
        return MailSendReceipt(draft=draft, provider_message_id="gmail-226-3")


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


def test_intent_resolver_maps_canonical_read_intent():
    decision = GmailIntentResolver().resolve("read")
    assert decision.intent is GmailIntent.READ
    assert decision.canonical_action == "read"
    assert decision.semantic_capability is GmailCapability.READ
    assert decision.required_payload_fields == ("message_id",)


def test_intent_resolver_normalizes_whitespace_and_case():
    decision = GmailIntentResolver().resolve("  SeArCh  ")
    assert decision.requested_action == "search"
    assert decision.canonical_action == "search"


def test_intent_resolver_supports_controlled_recent_aliases():
    resolver = GmailIntentResolver()
    assert resolver.resolve("summary").canonical_action == "recent"
    assert resolver.resolve("inbox").canonical_action == "recent"
    assert resolver.resolve("latest").intent is GmailIntent.RECENT


def test_intent_resolver_supports_controlled_action_aliases():
    resolver = GmailIntentResolver()
    assert resolver.resolve("write").canonical_action == "compose"
    assert resolver.resolve("save").canonical_action == "draft"
    assert resolver.resolve("respond").canonical_action == "reply"
    assert resolver.resolve("deliver").canonical_action == "send"


def test_unknown_intent_is_rejected_before_capability_resolution():
    with pytest.raises(ValueError, match="unsupported gmail intent"):
        GmailIntentResolver().resolve("purge")


def test_intent_catalog_is_stable_complete_and_secret_free():
    catalog = GmailIntentResolver().catalog()
    assert tuple(item.intent.value for item in catalog) == (
        "gmail.intent.recent",
        "gmail.intent.search",
        "gmail.intent.read",
        "gmail.intent.compose",
        "gmail.intent.draft",
        "gmail.intent.reply",
        "gmail.intent.send",
    )
    assert "@" not in str(catalog)


def test_integration_exposes_intent_catalog_without_changing_capability_catalog():
    item = make_integration()
    assert item.status()["intent_count"] == 7
    assert len(item.intent_status()) == 7
    assert len(item.capability_status()) == 5


def test_alias_is_canonicalized_before_gateway_routing():
    item = make_integration()
    gateway = make_gateway()
    item.register_with_gateway(gateway)
    result = item.execute(gateway, action="inbox")
    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert result.request.capability_name == "mail.read"
    assert result.request.payload["action"] == "recent"


def test_compose_alias_still_requires_gateway_write_consent():
    item = make_integration()
    gateway = make_gateway(write=False)
    item.register_with_gateway(gateway)
    result = item.execute(
        gateway,
        action="write",
        payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
    )
    assert result.normalized_status is ToolGatewayStatus.BLOCKED
    assert result.error == "consent_required:write"


def test_send_alias_still_requires_local_send_policy():
    item = make_integration()
    gateway = make_gateway(write=True)
    item.register_with_gateway(gateway)
    with pytest.raises(PermissionError, match="deliver"):
        item.execute(
            gateway,
            action="deliver",
            payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
        )


def test_enabled_send_alias_routes_and_audits_canonical_action():
    item = make_integration(policy=GmailGovernedPolicy(allow_send=True))
    gateway = make_gateway(write=True)
    item.register_with_gateway(gateway)
    result = item.execute(
        gateway,
        action="deliver",
        payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
    )
    assert result.succeeded is True
    assert result.request.payload["action"] == "send"
    assert item.audit_log[-1].action == "send"


def test_intent_status_is_immutable_by_copy():
    item = make_integration()
    snapshot = item.intent_status()
    assert isinstance(snapshot, tuple)
    snapshot[0]["canonical_action"] = "send"
    assert item.intent_status()[0]["canonical_action"] == "recent"
