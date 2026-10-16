from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from core.capability_registry import (
    CapabilityRegistryManager,
    default_semantic_capabilities,
)
from core.permission_consent import PermissionConsentManager, PermissionGrant
from core.tool_gateway import ToolGatewayManager
from infrastructure.mail.gmail_governed_integration import (
    GmailGovernedIntegration,
    GmailGovernedPolicy,
)
from infrastructure.mail.gmail_oauth_governance import (
    GmailOAuthGovernance,
    GmailOAuthPolicy,
)
from infrastructure.mail.gmail_provider_transport import (
    GmailProviderRateLimitError,
    GmailProviderTransport,
    GmailTransportOperation,
)
from infrastructure.mail.gmail_retry_governance import (
    GmailRetryGovernance,
    GmailRetryPolicy,
)
from infrastructure.mail.gmail_runtime_composition import (
    GmailRuntimeComposition,
    GmailRuntimeConfig,
)
from infrastructure.mail.mail_action_adapter import MailActionAdapter
from infrastructure.mail.mail_action_client import MailDraft, MailSendReceipt
from infrastructure.mail.mail_adapter import MailReaderAdapter
from infrastructure.mail.mail_client import MailMessage, MailSearchResult


@dataclass
class CertificationCredential:
    expires_at: datetime | None
    scopes: tuple[str, ...]
    revoked: bool = False

    def refresh(self) -> None:
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    def revoke(self) -> None:
        self.revoked = True


class CertificationCredentialProvider:
    def __init__(self, credential: CertificationCredential) -> None:
        self.credential = credential

    def load(self, account_fingerprint: str) -> CertificationCredential:
        del account_fingerprint
        return self.credential


class CertificationReadProvider:
    def list_recent(
        self, *, limit: int = 10, unread_only: bool = False
    ) -> MailSearchResult:
        del limit, unread_only
        return MailSearchResult(messages=(self._message(),))

    def search(self, query: str, *, limit: int = 10) -> MailSearchResult:
        del limit
        return MailSearchResult(messages=(self._message(),), query=query)

    def read(self, message_id: str) -> MailMessage:
        return self._message(message_id)

    @staticmethod
    def _message(message_id: str = "cert-message-1") -> MailMessage:
        return MailMessage(
            message_id=message_id,
            sender="certification@example.invalid",
            subject="Certification",
            snippet="Deterministic fixture",
            received_at=datetime(2026, 7, 14, tzinfo=timezone.utc),
        )


class CertificationActionProvider:
    def __init__(self) -> None:
        self.drafts: list[MailDraft] = []
        self.sent: list[MailDraft] = []

    def create_draft(self, draft: MailDraft) -> MailDraft:
        self.drafts.append(draft)
        return draft

    def send(self, draft: MailDraft) -> MailSendReceipt:
        self.sent.append(draft)
        return MailSendReceipt(draft=draft, provider_message_id="cert-provider-1")


class CertificationBackend:
    def __init__(self) -> None:
        self.calls: list[tuple[GmailTransportOperation, Mapping[str, Any], float]] = []
        self.failures_remaining = 0

    def execute(self, operation, payload, *, timeout_seconds):
        self.calls.append((operation, payload, timeout_seconds))
        if self.failures_remaining:
            self.failures_remaining -= 1
            raise GmailProviderRateLimitError("certification retry signal")
        return {"ok": True, "operation": operation.value, "item_count": 1}


@dataclass(frozen=True)
class GmailEndToEndReport:
    action: str
    gateway_status: str
    transport_operation: str
    attempts: int
    runtime_state: str
    audit_entries: int

    def to_dict(self) -> dict[str, object]:
        return {
            "action": self.action,
            "gateway_status": self.gateway_status,
            "transport_operation": self.transport_operation,
            "attempts": self.attempts,
            "runtime_state": self.runtime_state,
            "audit_entries": self.audit_entries,
        }


class GmailEndToEndCertification:
    """M226.9 deterministic certification harness for the complete Gmail stack."""

    _OPERATIONS = {
        "recent": GmailTransportOperation.LIST_RECENT,
        "search": GmailTransportOperation.SEARCH,
        "read": GmailTransportOperation.READ,
        "compose": GmailTransportOperation.CREATE_DRAFT,
        "draft": GmailTransportOperation.CREATE_DRAFT,
        "reply": GmailTransportOperation.CREATE_DRAFT,
        "send": GmailTransportOperation.SEND,
    }

    def __init__(self, *, runtime, integration, gateway, backend) -> None:
        self.runtime = runtime
        self.integration = integration
        self.gateway = gateway
        self.backend = backend

    def certify(
        self,
        action: str,
        payload: Mapping[str, Any] | None = None,
        *,
        now=None,
        idempotency_key=None,
    ) -> GmailEndToEndReport:
        plan = self.integration.plan(action=action, payload=payload)
        gateway_result = self.integration.execute(
            self.gateway,
            action=action,
            payload=payload,
            reason="gmail_e2e_certification",
        )
        operation = self._OPERATIONS[plan.canonical_action]
        before = len(self.backend.calls)
        self.runtime.execute(
            operation,
            payload,
            now=now,
            idempotency_key=idempotency_key,
        )
        return GmailEndToEndReport(
            action=plan.canonical_action,
            gateway_status=gateway_result.normalized_status.value,
            transport_operation=operation.value,
            attempts=len(self.backend.calls) - before,
            runtime_state=self.runtime.status(now=now)["state"],
            audit_entries=len(self.integration.audit_log),
        )

    def status(self, *, now=None) -> dict[str, object]:
        return {
            "milestone": "M226.9",
            "runtime_state": self.runtime.status(now=now)["state"],
            "registered": self.integration.status()["registered"],
            "backend_call_count": len(self.backend.calls),
            "audit_entries": len(self.integration.audit_log),
        }


def build_gmail_e2e_certification(
    *, now: datetime | None = None
) -> GmailEndToEndCertification:
    current = now or datetime.now(timezone.utc)
    credential = CertificationCredential(
        expires_at=current + timedelta(hours=1),
        scopes=("gmail.readonly", "gmail.send"),
    )
    oauth = GmailOAuthGovernance(
        account_fingerprint="certification-account",
        credential_provider=CertificationCredentialProvider(credential),
        policy=GmailOAuthPolicy(required_scopes=("gmail.readonly", "gmail.send")),
    )
    backend = CertificationBackend()
    transport = GmailProviderTransport(backend, oauth)
    retry = GmailRetryGovernance(
        transport,
        GmailRetryPolicy(initial_backoff_seconds=0, max_backoff_seconds=0),
        sleeper=lambda _: None,
    )
    integration = GmailGovernedIntegration(
        account_address="certification@example.invalid",
        reader=MailReaderAdapter(CertificationReadProvider()),
        actions=MailActionAdapter(CertificationActionProvider()),
        policy=GmailGovernedPolicy(allow_send=True),
        oauth_governance=oauth,
        provider_transport=transport,
    )
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    permissions = PermissionConsentManager()
    permissions.grant(PermissionGrant("mail.send", "write"))
    gateway = ToolGatewayManager(
        capability_registry=registry, permission_consent=permissions
    )
    integration.register_with_gateway(gateway)
    runtime = GmailRuntimeComposition(
        config=GmailRuntimeConfig(enabled=True),
        integration=integration,
        oauth=oauth,
        retry=retry,
    )
    return GmailEndToEndCertification(
        runtime=runtime,
        integration=integration,
        gateway=gateway,
        backend=backend,
    )
