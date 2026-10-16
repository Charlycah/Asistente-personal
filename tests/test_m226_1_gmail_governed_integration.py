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
    GmailAuditEntry,
    GmailGovernedIntegration,
    GmailGovernedPolicy,
)
from infrastructure.mail.mail_action_adapter import MailActionAdapter
from infrastructure.mail.mail_action_client import MailDraft, MailSendReceipt
from infrastructure.mail.mail_adapter import MailReaderAdapter
from infrastructure.mail.mail_client import MailMessage, MailSearchResult


class FakeReadProvider:
    def list_recent(
        self, *, limit: int = 10, unread_only: bool = False
    ) -> MailSearchResult:
        return MailSearchResult(messages=(self._message(),))

    def search(self, query: str, *, limit: int = 10) -> MailSearchResult:
        return MailSearchResult(messages=(self._message(),), query=query)

    def read(self, message_id: str) -> MailMessage:
        return self._message(message_id)

    @staticmethod
    def _message(message_id: str = "m-1") -> MailMessage:
        return MailMessage(
            message_id=message_id,
            sender="ana@example.com",
            subject="Estado",
            snippet="Todo listo.",
            received_at=datetime(2026, 7, 14, tzinfo=timezone.utc),
        )


class FakeActionProvider:
    def __init__(self) -> None:
        self.drafts: list[MailDraft] = []
        self.sent: list[MailDraft] = []

    def create_draft(self, draft: MailDraft) -> MailDraft:
        self.drafts.append(draft)
        return draft

    def send(self, draft: MailDraft) -> MailSendReceipt:
        self.sent.append(draft)
        return MailSendReceipt(draft=draft, provider_message_id="gmail-1")


def gateway(*, grant_send: bool = False) -> ToolGatewayManager:
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    permissions = PermissionConsentManager()
    if grant_send:
        permissions.grant(PermissionGrant("mail.send", "write"))
    return ToolGatewayManager(
        capability_registry=registry, permission_consent=permissions
    )


def integration(
    *, policy: GmailGovernedPolicy | None = None
) -> GmailGovernedIntegration:
    return GmailGovernedIntegration(
        account_address="Carlos.Example@gmail.com",
        reader=MailReaderAdapter(FakeReadProvider()),
        actions=MailActionAdapter(FakeActionProvider()),
        policy=policy,
    )


def test_account_identity_is_normalized_and_never_exposed_in_status():
    first = integration()
    second = GmailGovernedIntegration(
        account_address=" carlos.example@GMAIL.COM ",
        reader=MailReaderAdapter(FakeReadProvider()),
        actions=MailActionAdapter(FakeActionProvider()),
    )

    assert first.account_fingerprint == second.account_fingerprint
    assert "gmail.com" not in str(first.status())


def test_registration_composes_existing_read_and_action_capabilities():
    item = integration()
    tool_gateway = gateway(grant_send=True)

    item.register_with_gateway(tool_gateway)

    assert item.status()["registered"] is True
    assert "mail.read" in tool_gateway.capabilities
    assert "mail.send" in tool_gateway.capabilities


def test_integration_must_be_registered_before_execution():
    with pytest.raises(ValueError, match="registered"):
        integration().execute(gateway(), action="summary")


def test_read_is_routed_through_gateway_and_audited():
    item = integration()
    tool_gateway = gateway()
    item.register_with_gateway(tool_gateway)

    result = item.execute(tool_gateway, action="summary", reason="inbox_review")

    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert result.output["read_only"] is True
    assert item.audit_log[0].capability == "mail.read"
    assert item.audit_log[0].reason == "inbox_review"
    assert item.audit_log[0].mutates_external_state is False


def test_draft_still_requires_gateway_write_consent():
    item = integration()
    tool_gateway = gateway(grant_send=False)
    item.register_with_gateway(tool_gateway)

    result = item.execute(
        tool_gateway,
        action="draft",
        payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
    )

    assert result.normalized_status is ToolGatewayStatus.BLOCKED
    assert result.error == "consent_required:write"
    assert item.audit_log[-1].status == "blocked"


def test_draft_is_allowed_by_default_after_consent_but_send_is_not():
    item = integration()
    tool_gateway = gateway(grant_send=True)
    item.register_with_gateway(tool_gateway)

    draft = item.execute(
        tool_gateway,
        action="draft",
        payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
    )

    assert draft.succeeded is True
    with pytest.raises(PermissionError, match="send"):
        item.execute(
            tool_gateway,
            action="send",
            payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
        )


def test_send_requires_both_local_policy_and_gateway_consent():
    item = integration(policy=GmailGovernedPolicy(allow_send=True))
    tool_gateway = gateway(grant_send=True)
    item.register_with_gateway(tool_gateway)

    result = item.execute(
        tool_gateway,
        action="send",
        payload={"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"},
    )

    assert result.succeeded is True
    assert item.audit_log[-1].mutates_external_state is True


def test_policy_can_disable_read_independently():
    item = integration(policy=GmailGovernedPolicy(allow_read=False))
    tool_gateway = gateway()
    item.register_with_gateway(tool_gateway)

    with pytest.raises(PermissionError, match="summary"):
        item.execute(tool_gateway, action="summary")


def test_unknown_actions_are_rejected_without_audit_side_effects():
    item = integration()
    tool_gateway = gateway()
    item.register_with_gateway(tool_gateway)

    with pytest.raises(PermissionError, match="purge"):
        item.execute(tool_gateway, action="purge")

    assert item.audit_log == ()


def test_audit_log_is_bounded_by_policy():
    item = integration(policy=GmailGovernedPolicy(max_audit_entries=2))
    tool_gateway = gateway()
    item.register_with_gateway(tool_gateway)

    for _ in range(3):
        item.execute(tool_gateway, action="summary")

    assert len(item.audit_log) == 2
    assert item.status()["audit_entries"] == 2


def test_integration_cannot_be_rebound_to_a_different_gateway():
    item = integration()
    item.register_with_gateway(gateway())

    with pytest.raises(ValueError, match="another gateway"):
        item.register_with_gateway(gateway())


def test_audit_entry_rejects_naive_timestamps():
    with pytest.raises(ValueError, match="timezone-aware"):
        GmailAuditEntry(
            request_id="r",
            result_id="x",
            account_fingerprint="fingerprint",
            capability="mail.read",
            action="read",
            status="routed",
            reason="test",
            mutates_external_state=False,
            created_at=datetime(2026, 7, 14),
        )
