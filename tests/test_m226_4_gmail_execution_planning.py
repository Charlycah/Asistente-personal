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
    GmailCapabilityDecision,
    GmailExecutionPlan,
    GmailExecutionPlanner,
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
    def _message(message_id: str = "m-226-4") -> MailMessage:
        return MailMessage(
            message_id=message_id,
            sender="ana@example.com",
            subject="Planning layer",
            snippet="Ready",
            received_at=datetime(2026, 7, 14, tzinfo=timezone.utc),
        )


class ActionProvider:
    def create_draft(self, draft: MailDraft) -> MailDraft:
        return draft

    def send(self, draft: MailDraft) -> MailSendReceipt:
        return MailSendReceipt(draft=draft, provider_message_id="gmail-226-4")


def make_integration(*, allow_send: bool = False) -> GmailGovernedIntegration:
    return GmailGovernedIntegration(
        account_address="carlos@example.com",
        reader=MailReaderAdapter(ReadProvider()),
        actions=MailActionAdapter(ActionProvider()),
        policy=GmailGovernedPolicy(allow_send=allow_send),
    )


def make_gateway(*, write: bool = False) -> ToolGatewayManager:
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    permissions = PermissionConsentManager()
    if write:
        permissions.grant(PermissionGrant("mail.send", "write"))
    return ToolGatewayManager(
        capability_registry=registry, permission_consent=permissions
    )


def test_planner_builds_immutable_read_plan():
    item = make_integration().plan(action="open", payload={"message_id": "m-1"})
    assert isinstance(item, GmailExecutionPlan)
    assert item.intent is GmailIntent.READ
    assert item.semantic_capability is GmailCapability.READ
    assert item.canonical_action == "read"
    assert item.present_payload_fields == ("message_id",)


def test_plan_is_secret_free_and_contains_only_payload_field_names():
    item = make_integration().plan(
        action="draft",
        payload={"to": ("secret@example.com",), "subject": "Secret", "body": "Body"},
    )
    rendered = str(item.to_dict())
    assert "secret@example.com" not in rendered
    assert "Secret" not in rendered
    assert item.present_payload_fields == ("body", "subject", "to")


def test_missing_required_payload_is_rejected_before_gateway():
    with pytest.raises(ValueError, match="message_id"):
        make_integration().plan(action="read", payload={})


def test_blank_required_payload_is_treated_as_missing():
    with pytest.raises(ValueError, match="query"):
        make_integration().plan(action="search", payload={"query": ""})


def test_recent_plan_requires_no_payload():
    item = make_integration().plan(action="latest")
    assert item.required_payload_fields == ()
    assert item.present_payload_fields == ()


def test_send_plan_classifies_external_mutation_and_confirmation():
    item = make_integration(allow_send=True).plan(
        action="send", payload={"to": ("a@example.com",), "subject": "S", "body": "B"}
    )
    assert item.mutates_external_state is True
    assert item.requires_confirmation is True
    assert item.permission_scope == "write"


def test_disabled_send_is_rejected_during_planning():
    with pytest.raises(PermissionError, match="disabled by policy"):
        make_integration().plan(
            action="send",
            payload={"to": ("a@example.com",), "subject": "S", "body": "B"},
        )


def test_inconsistent_intent_and_capability_decisions_are_rejected():
    intent = GmailIntentResolver().resolve("read")
    capability = GmailCapabilityDecision(
        capability=GmailCapability.SEND,
        action="send",
        gateway_capability="mail.send",
        permission_scope="write",
        allowed=True,
        mutates_external_state=True,
        requires_confirmation=True,
    )
    with pytest.raises(ValueError, match="inconsistent"):
        GmailExecutionPlanner().plan(intent, capability, {"message_id": "m-1"})


def test_execute_validates_plan_before_gateway_invocation():
    item = make_integration()
    gateway = make_gateway()
    item.register_with_gateway(gateway)
    with pytest.raises(PermissionError, match="disabled by policy"):
        item.execute(gateway, action="read", payload={})
    assert item.audit_log == ()


def test_valid_plan_routes_with_canonical_action():
    item = make_integration()
    gateway = make_gateway()
    item.register_with_gateway(gateway)
    result = item.execute(gateway, action="open", payload={"message_id": "m-1"})
    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert result.request.payload["action"] == "read"


def test_status_reports_execution_planning_enabled():
    assert make_integration().status()["execution_planning_enabled"] is True


def test_execution_plan_to_dict_is_independent_copy():
    plan = make_integration().plan(action="read", payload={"message_id": "m-1"})
    snapshot = plan.to_dict()
    snapshot["canonical_action"] = "send"
    assert plan.canonical_action == "read"
