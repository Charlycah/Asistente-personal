from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Any
from uuid import uuid4

from core.tool_gateway import ToolGatewayManager, ToolRequest, ToolResult
from infrastructure.config.config_schema import AppConfig
from infrastructure.mail.gmail_oauth_governance import GmailOAuthGovernance
from infrastructure.mail.gmail_provider_transport import GmailProviderTransport
from infrastructure.mail.mail_action_adapter import (
    MailActionAdapter,
    build_mail_action_adapter_from_config,
)
from infrastructure.mail.mail_adapter import (
    MailReaderAdapter,
    build_mail_reader_adapter_from_config,
)


class GmailCapability(str, Enum):
    """Semantic Gmail capabilities resolved before physical tool routing."""

    READ = "gmail.read"
    COMPOSE = "gmail.compose"
    DRAFT = "gmail.draft"
    REPLY = "gmail.reply"
    SEND = "gmail.send"


class GmailIntent(str, Enum):
    """Canonical Gmail intents resolved before semantic capabilities."""

    RECENT = "gmail.intent.recent"
    SEARCH = "gmail.intent.search"
    READ = "gmail.intent.read"
    COMPOSE = "gmail.intent.compose"
    DRAFT = "gmail.intent.draft"
    REPLY = "gmail.intent.reply"
    SEND = "gmail.intent.send"


@dataclass(frozen=True)
class GmailIntentDecision:
    """Immutable, secret-free interpretation of one Gmail request intent."""

    intent: GmailIntent
    requested_action: str
    canonical_action: str
    semantic_capability: GmailCapability
    required_payload_fields: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "intent": self.intent.value,
            "requested_action": self.requested_action,
            "canonical_action": self.canonical_action,
            "semantic_capability": self.semantic_capability.value,
            "required_payload_fields": self.required_payload_fields,
        }


class GmailIntentResolver:
    """M226.3 deterministic intent normalization before capability resolution."""

    _ALIASES = {
        "summary": "recent",
        "list": "recent",
        "inbox": "recent",
        "latest": "recent",
        "find": "search",
        "open": "read",
        "write": "compose",
        "new": "compose",
        "save": "draft",
        "answer": "reply",
        "respond": "reply",
        "deliver": "send",
    }
    _INTENTS = {
        "recent": (GmailIntent.RECENT, GmailCapability.READ, ()),
        "search": (GmailIntent.SEARCH, GmailCapability.READ, ("query",)),
        "read": (GmailIntent.READ, GmailCapability.READ, ("message_id",)),
        "compose": (
            GmailIntent.COMPOSE,
            GmailCapability.COMPOSE,
            ("to", "subject", "body"),
        ),
        "draft": (
            GmailIntent.DRAFT,
            GmailCapability.DRAFT,
            ("to", "subject", "body"),
        ),
        "reply": (
            GmailIntent.REPLY,
            GmailCapability.REPLY,
            ("message_id", "to", "subject", "body"),
        ),
        "send": (
            GmailIntent.SEND,
            GmailCapability.SEND,
            ("to", "subject", "body"),
        ),
    }

    def resolve(self, action: str) -> GmailIntentDecision:
        requested = action.strip().casefold()
        if not requested:
            raise ValueError("gmail intent must not be empty")
        canonical = self._ALIASES.get(requested, requested)
        definition = self._INTENTS.get(canonical)
        if definition is None:
            raise ValueError("unsupported gmail intent")
        intent, capability, required_fields = definition
        return GmailIntentDecision(
            intent=intent,
            requested_action=requested,
            canonical_action=canonical,
            semantic_capability=capability,
            required_payload_fields=required_fields,
        )

    def catalog(self) -> tuple[GmailIntentDecision, ...]:
        return tuple(self.resolve(action) for action in self._INTENTS)


@dataclass(frozen=True)
class GmailExecutionPlan:
    """Immutable, secret-free plan produced before Tool Gateway execution."""

    intent: GmailIntent
    semantic_capability: GmailCapability
    canonical_action: str
    gateway_capability: str
    permission_scope: str
    required_payload_fields: tuple[str, ...]
    present_payload_fields: tuple[str, ...]
    mutates_external_state: bool
    requires_confirmation: bool

    def __post_init__(self) -> None:
        if not self.canonical_action.strip():
            raise ValueError("gmail execution action must not be empty")
        missing = set(self.required_payload_fields) - set(self.present_payload_fields)
        if missing:
            raise ValueError(
                "gmail execution payload missing required fields: "
                + ", ".join(sorted(missing))
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "intent": self.intent.value,
            "semantic_capability": self.semantic_capability.value,
            "canonical_action": self.canonical_action,
            "gateway_capability": self.gateway_capability,
            "permission_scope": self.permission_scope,
            "required_payload_fields": self.required_payload_fields,
            "present_payload_fields": self.present_payload_fields,
            "mutates_external_state": self.mutates_external_state,
            "requires_confirmation": self.requires_confirmation,
        }


class GmailExecutionPlanner:
    """M226.4 deterministic planning and payload-shape validation boundary."""

    @staticmethod
    def _present_fields(payload: Mapping[str, Any]) -> tuple[str, ...]:
        return tuple(
            sorted(
                key
                for key, value in payload.items()
                if isinstance(key, str)
                and key.strip()
                and value is not None
                and value != ""
                and value != ()
                and value != []
            )
        )

    def plan(
        self,
        intent: GmailIntentDecision,
        capability: "GmailCapabilityDecision",
        payload: Mapping[str, Any] | None = None,
    ) -> GmailExecutionPlan:
        if intent.canonical_action != capability.action:
            raise ValueError("gmail execution decisions are inconsistent")
        present = self._present_fields(payload or {})
        return GmailExecutionPlan(
            intent=intent.intent,
            semantic_capability=capability.capability,
            canonical_action=intent.canonical_action,
            gateway_capability=capability.gateway_capability,
            permission_scope=capability.permission_scope,
            required_payload_fields=intent.required_payload_fields,
            present_payload_fields=present,
            mutates_external_state=capability.mutates_external_state,
            requires_confirmation=capability.requires_confirmation,
        )


@dataclass(frozen=True)
class GmailCapabilityDecision:
    """Immutable policy decision for one semantic Gmail capability."""

    capability: GmailCapability
    action: str
    gateway_capability: str
    permission_scope: str
    allowed: bool
    mutates_external_state: bool
    requires_confirmation: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "capability": self.capability.value,
            "action": self.action,
            "gateway_capability": self.gateway_capability,
            "permission_scope": self.permission_scope,
            "allowed": self.allowed,
            "mutates_external_state": self.mutates_external_state,
            "requires_confirmation": self.requires_confirmation,
        }


class GmailCapabilityResolver:
    """M226.2 semantic capability and policy resolver for Gmail actions."""

    _READ_ACTIONS = frozenset({"summary", "recent", "list", "search", "read"})

    def resolve(
        self, action: str, policy: "GmailGovernedPolicy"
    ) -> GmailCapabilityDecision:
        normalized = action.strip().casefold()
        if not normalized:
            raise ValueError("gmail action must not be empty")
        if normalized in self._READ_ACTIONS:
            capability = GmailCapability.READ
            gateway_capability = MailReaderAdapter.READ_CAPABILITY
            permission_scope = "read"
            mutates = False
            confirmation = False
        elif normalized in {"compose", "draft"}:
            capability = (
                GmailCapability.COMPOSE
                if normalized == "compose"
                else GmailCapability.DRAFT
            )
            gateway_capability = MailActionAdapter.ACTION_CAPABILITY
            permission_scope = "write"
            mutates = False
            confirmation = False
        elif normalized == "reply":
            capability = GmailCapability.REPLY
            gateway_capability = MailActionAdapter.ACTION_CAPABILITY
            permission_scope = "write"
            mutates = False
            confirmation = False
        elif normalized == "send":
            capability = GmailCapability.SEND
            gateway_capability = MailActionAdapter.ACTION_CAPABILITY
            permission_scope = "write"
            mutates = True
            confirmation = True
        else:
            raise ValueError("unsupported gmail action")
        return GmailCapabilityDecision(
            capability=capability,
            action=normalized,
            gateway_capability=gateway_capability,
            permission_scope=permission_scope,
            allowed=policy.allows(normalized),
            mutates_external_state=mutates,
            requires_confirmation=confirmation,
        )

    def catalog(
        self, policy: "GmailGovernedPolicy"
    ) -> tuple[GmailCapabilityDecision, ...]:
        return tuple(
            self.resolve(action, policy)
            for action in ("read", "compose", "draft", "reply", "send")
        )


@dataclass(frozen=True)
class GmailGovernedPolicy:
    """Local policy for the M226.1 Gmail integration boundary."""

    allow_read: bool = True
    allow_draft: bool = True
    allow_reply: bool = True
    allow_send: bool = False
    max_audit_entries: int = 100

    def __post_init__(self) -> None:
        if self.max_audit_entries <= 0:
            raise ValueError("gmail audit limit must be positive")

    def allows(self, action: str) -> bool:
        normalized = action.casefold()
        return {
            "summary": self.allow_read,
            "recent": self.allow_read,
            "list": self.allow_read,
            "search": self.allow_read,
            "read": self.allow_read,
            "compose": self.allow_draft,
            "draft": self.allow_draft,
            "reply": self.allow_reply,
            "send": self.allow_send,
        }.get(normalized, False)


@dataclass(frozen=True)
class GmailAuditEntry:
    """Secret-free audit record for one governed Gmail request."""

    request_id: str
    result_id: str
    account_fingerprint: str
    capability: str
    action: str
    status: str
    reason: str
    mutates_external_state: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    audit_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        values = (
            self.request_id,
            self.result_id,
            self.account_fingerprint,
            self.capability,
            self.action,
            self.status,
            self.reason,
            self.audit_id,
        )
        if any(not value.strip() for value in values):
            raise ValueError("gmail audit fields must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("gmail audit timestamp must be timezone-aware")

    def to_dict(self) -> dict[str, object]:
        return {
            "audit_id": self.audit_id,
            "request_id": self.request_id,
            "result_id": self.result_id,
            "account_fingerprint": self.account_fingerprint,
            "capability": self.capability,
            "action": self.action,
            "status": self.status,
            "reason": self.reason,
            "mutates_external_state": self.mutates_external_state,
            "created_at": self.created_at.isoformat(),
        }


class GmailGovernedIntegration:
    """M226.1 composition boundary for governed Gmail capabilities."""

    READ_CAPABILITY = MailReaderAdapter.READ_CAPABILITY
    ACTION_CAPABILITY = MailActionAdapter.ACTION_CAPABILITY
    PROVIDER = "gmail"
    TRANSPORT = "imap_smtp"

    def __init__(
        self,
        *,
        account_address: str,
        reader: MailReaderAdapter,
        actions: MailActionAdapter,
        policy: GmailGovernedPolicy | None = None,
        resolver: GmailCapabilityResolver | None = None,
        intent_resolver: GmailIntentResolver | None = None,
        execution_planner: GmailExecutionPlanner | None = None,
        oauth_governance: GmailOAuthGovernance | None = None,
        provider_transport: GmailProviderTransport | None = None,
    ) -> None:
        if not account_address.strip():
            raise ValueError("gmail account address must not be empty")
        self._account_fingerprint = self.fingerprint_account(account_address)
        self.reader = reader
        self.actions = actions
        self.policy = policy or GmailGovernedPolicy()
        self.resolver = resolver or GmailCapabilityResolver()
        self.intent_resolver = intent_resolver or GmailIntentResolver()
        self.execution_planner = execution_planner or GmailExecutionPlanner()
        self.oauth_governance = oauth_governance
        self.provider_transport = provider_transport
        self._audit_log: list[GmailAuditEntry] = []
        self._registered_gateway: ToolGatewayManager | None = None

    @staticmethod
    def fingerprint_account(account_address: str) -> str:
        normalized = account_address.strip().casefold()
        if not normalized:
            raise ValueError("gmail account address must not be empty")
        return sha256(normalized.encode("utf-8")).hexdigest()[:16]

    @property
    def account_fingerprint(self) -> str:
        return self._account_fingerprint

    @property
    def audit_log(self) -> tuple[GmailAuditEntry, ...]:
        return tuple(self._audit_log)

    def register_with_gateway(self, gateway: ToolGatewayManager) -> None:
        if (
            self._registered_gateway is not None
            and self._registered_gateway is not gateway
        ):
            raise ValueError("gmail integration is already bound to another gateway")
        self.reader.register_with_gateway(gateway)
        self.actions.register_with_gateway(gateway)
        self._registered_gateway = gateway

    def execute(
        self,
        gateway: ToolGatewayManager,
        *,
        action: str,
        payload: Mapping[str, Any] | None = None,
        reason: str = "gmail_user_requested",
    ) -> ToolResult:
        requested_action = action.strip().casefold()
        if not requested_action:
            raise ValueError("gmail action must not be empty")
        if not reason.strip():
            raise ValueError("gmail reason must not be empty")
        if self._registered_gateway is not gateway:
            raise ValueError("gmail integration must be registered with this gateway")
        try:
            intent = self.intent_resolver.resolve(requested_action)
            decision = self.resolver.resolve(intent.canonical_action, self.policy)
            plan = self.execution_planner.plan(intent, decision, payload)
        except ValueError as exc:
            raise PermissionError(
                f"gmail action disabled by policy: {requested_action}"
            ) from exc
        if not decision.allowed:
            raise PermissionError(
                f"gmail action disabled by policy: {requested_action}"
            )

        capability = plan.gateway_capability
        request_payload = dict(payload or {})
        request_payload["action"] = plan.canonical_action
        request = ToolRequest(
            capability,
            payload=request_payload,
            reason=reason,
            source="gmail_governed_integration",
        )
        result = gateway.execute(request)
        self._record(result, plan.canonical_action, reason)
        return result

    def status(self) -> Mapping[str, object]:
        return {
            "provider": self.PROVIDER,
            "transport": self.TRANSPORT,
            "account_fingerprint": self.account_fingerprint,
            "registered": self._registered_gateway is not None,
            "read_enabled": self.policy.allow_read,
            "draft_enabled": self.policy.allow_draft,
            "reply_enabled": self.policy.allow_reply,
            "send_enabled": self.policy.allow_send,
            "audit_entries": len(self._audit_log),
            "semantic_capability_count": len(self.resolver.catalog(self.policy)),
            "intent_count": len(self.intent_resolver.catalog()),
            "execution_planning_enabled": True,
            "oauth_governance_enabled": self.oauth_governance is not None,
            "oauth_state": (
                self.oauth_governance.inspect().state.value
                if self.oauth_governance is not None
                else "unconfigured"
            ),
            "provider_transport_enabled": self.provider_transport is not None,
            "provider_transport": (
                self.provider_transport.status()["transport"]
                if self.provider_transport is not None
                else "unconfigured"
            ),
        }

    def capability_status(self) -> tuple[Mapping[str, object], ...]:
        """Returns the governed semantic Gmail catalog without secrets."""

        return tuple(
            decision.to_dict() for decision in self.resolver.catalog(self.policy)
        )

    def intent_status(self) -> tuple[Mapping[str, object], ...]:
        """Returns the immutable, secret-free Gmail intent catalog."""

        return tuple(decision.to_dict() for decision in self.intent_resolver.catalog())

    def plan(
        self,
        *,
        action: str,
        payload: Mapping[str, Any] | None = None,
    ) -> GmailExecutionPlan:
        """Builds and validates a governed plan without invoking the gateway."""

        intent = self.intent_resolver.resolve(action)
        decision = self.resolver.resolve(intent.canonical_action, self.policy)
        if not decision.allowed:
            raise PermissionError(f"gmail action disabled by policy: {action}")
        return self.execution_planner.plan(intent, decision, payload)

    @classmethod
    def _capability_for(cls, action: str) -> str:
        if action in {"summary", "recent", "list", "search", "read"}:
            return cls.READ_CAPABILITY
        if action in {"draft", "reply", "send"}:
            return cls.ACTION_CAPABILITY
        raise ValueError("unsupported gmail action")

    def _record(self, result: ToolResult, action: str, reason: str) -> None:
        mutates = bool(result.output.get("mutates_external_state", False))
        entry = GmailAuditEntry(
            request_id=result.request.request_id,
            result_id=result.result_id,
            account_fingerprint=self.account_fingerprint,
            capability=result.request.capability_name,
            action=action,
            status=result.normalized_status.value,
            reason=reason,
            mutates_external_state=mutates,
        )
        self._audit_log.append(entry)
        excess = len(self._audit_log) - self.policy.max_audit_entries
        if excess > 0:
            del self._audit_log[:excess]


def build_gmail_governed_integration_from_config(
    config: AppConfig,
    *,
    policy: GmailGovernedPolicy | None = None,
) -> GmailGovernedIntegration:
    """Builds M226.1 without exposing credentials outside existing factories."""

    address = config.secrets.gmail_address
    if address is None or not address.strip():
        raise ValueError("GMAIL_ADDRESS is required for GmailGovernedIntegration")
    return GmailGovernedIntegration(
        account_address=address,
        reader=build_mail_reader_adapter_from_config(config),
        actions=build_mail_action_adapter_from_config(config),
        policy=policy,
    )
