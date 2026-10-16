from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.capability_registry import CapabilityDescriptor, PermissionScope


class PermissionConsentSignal(str, Enum):
    """Señales de M63 para permisos y consentimiento explícito."""

    PERMISSION_LAYER_READY = "permission_layer_ready"
    CAPABILITY_PERMISSION_EVALUATED = "capability_permission_evaluated"
    CONSENT_REQUIRED = "consent_required"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_DENIED = "consent_denied"
    CONTRACT_PRESERVED = "contract_preserved"


class ConsentDecisionStatus(str, Enum):
    """Resultado normalizado de una evaluación de permisos."""

    ALLOWED = "allowed"
    REQUIRES_CONSENT = "requires_consent"
    DENIED = "denied"


@dataclass(frozen=True)
class PermissionConsentPolicy:
    """Política base de M63 para gobernar acciones externas."""

    max_grants: int = 100
    allow_none_scope_without_consent: bool = True
    allow_low_risk_read_without_consent: bool = True
    explicit_consent_scopes: tuple[PermissionScope | str, ...] = (
        PermissionScope.WRITE,
        PermissionScope.DEVICE,
    )

    def __post_init__(self) -> None:
        if self.max_grants <= 0:
            raise ValueError("permission grant limit must be positive")
        for scope in self.explicit_consent_scopes:
            PermissionScope(scope)

    @property
    def normalized_explicit_consent_scopes(self) -> tuple[PermissionScope, ...]:
        return tuple(PermissionScope(scope) for scope in self.explicit_consent_scopes)


@dataclass(frozen=True)
class PermissionGrant:
    """Consentimiento explícito concedido para una capacidad concreta."""

    capability_name: str
    scope: PermissionScope | str
    granted_by: str = "user"
    reason: str = "explicit_consent"
    granted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    grant_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.capability_name.strip():
            raise ValueError("permission grant capability must not be empty")
        PermissionScope(self.scope)
        if not self.granted_by.strip():
            raise ValueError("permission grant owner must not be empty")
        if not self.reason.strip():
            raise ValueError("permission grant reason must not be empty")
        if self.granted_at.tzinfo is None:
            raise ValueError("permission grant timestamp must be timezone-aware")
        if not self.grant_id.strip():
            raise ValueError("permission grant id must not be empty")

    @property
    def normalized_scope(self) -> PermissionScope:
        return PermissionScope(self.scope)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.grant_id,
            "capability": self.capability_name,
            "scope": self.normalized_scope.value,
            "granted_by": self.granted_by,
            "reason": self.reason,
            "granted_at": self.granted_at.isoformat(),
        }


@dataclass(frozen=True)
class ConsentDecision:
    """Decisión auditable de M63 para una capacidad solicitada."""

    capability_name: str
    scope: PermissionScope | str
    status: ConsentDecisionStatus | str
    reason: str
    required_confirmation: bool
    grant_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.capability_name.strip():
            raise ValueError("consent decision capability must not be empty")
        PermissionScope(self.scope)
        ConsentDecisionStatus(self.status)
        if not self.reason.strip():
            raise ValueError("consent decision reason must not be empty")
        if self.grant_id is not None and not self.grant_id.strip():
            raise ValueError("consent decision grant id must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("consent decision timestamp must be timezone-aware")
        if not self.decision_id.strip():
            raise ValueError("consent decision id must not be empty")

    @property
    def normalized_scope(self) -> PermissionScope:
        return PermissionScope(self.scope)

    @property
    def normalized_status(self) -> ConsentDecisionStatus:
        return ConsentDecisionStatus(self.status)

    @property
    def allowed(self) -> bool:
        return self.normalized_status is ConsentDecisionStatus.ALLOWED

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.decision_id,
            "capability": self.capability_name,
            "scope": self.normalized_scope.value,
            "status": self.normalized_status.value,
            "reason": self.reason,
            "required_confirmation": self.required_confirmation,
            "grant_id": self.grant_id,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class PermissionConsentSnapshot:
    """Snapshot de permisos para el turno cognitivo actual."""

    signals: tuple[PermissionConsentSignal | str, ...]
    evaluated_capabilities: tuple[str, ...]
    allowed_capabilities: tuple[str, ...]
    consent_required_capabilities: tuple[str, ...]
    denied_capabilities: tuple[str, ...]
    active_grants: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("permission consent signals must not be empty")
        for signal in self.signals:
            PermissionConsentSignal(signal)
        groups = (
            self.evaluated_capabilities,
            self.allowed_capabilities,
            self.consent_required_capabilities,
            self.denied_capabilities,
            self.active_grants,
        )
        if any(not item.strip() for group in groups for item in group):
            raise ValueError("permission consent capability names must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("permission consent timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("permission consent snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[PermissionConsentSignal, ...]:
        return tuple(PermissionConsentSignal(signal) for signal in self.signals)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Permissions & Consent M63:",
            f"- Señales: {signals}",
            "- Regla: ninguna herramienta sensible se ejecuta sin permiso.",
            "- Regla: leer, escribir, red, dispositivo y cámara son ámbitos distintos.",
            "- Regla: el consentimiento se decide antes de ejecutar adapters reales.",
        ]
        lines.extend(
            f"- Capacidad evaluada: {name}" for name in self.evaluated_capabilities
        )
        lines.extend(
            f"- Capacidad permitida: {name}" for name in self.allowed_capabilities
        )
        lines.extend(
            f"- Requiere consentimiento: {name}"
            for name in self.consent_required_capabilities
        )
        lines.extend(
            f"- Capacidad denegada: {name}" for name in self.denied_capabilities
        )
        lines.extend(f"- Permiso activo: {name}" for name in self.active_grants)
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "evaluated_capabilities": list(self.evaluated_capabilities),
            "allowed_capabilities": list(self.allowed_capabilities),
            "consent_required_capabilities": list(self.consent_required_capabilities),
            "denied_capabilities": list(self.denied_capabilities),
            "active_grants": list(self.active_grants),
            "created_at": self.created_at.isoformat(),
        }


class PermissionConsentEngine:
    """Motor puro de M63 para evaluar permisos antes de usar herramientas."""

    def __init__(self, policy: PermissionConsentPolicy | None = None) -> None:
        self.policy = policy or PermissionConsentPolicy()

    def evaluate_capability(
        self,
        capability_name: str,
        *,
        scope: PermissionScope | str,
        risk_level: str,
        requires_confirmation: bool,
        grants: dict[str, PermissionGrant],
        now: datetime | None = None,
    ) -> ConsentDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("permission consent timestamp must be timezone-aware")
        normalized_scope = PermissionScope(scope)
        grant = grants.get(capability_name)
        if grant is not None:
            return ConsentDecision(
                capability_name,
                normalized_scope,
                ConsentDecisionStatus.ALLOWED,
                "active_consent_grant",
                required_confirmation=False,
                grant_id=grant.grant_id,
                created_at=timestamp,
            )
        if requires_confirmation:
            return self._requires_consent_decision(
                capability_name,
                normalized_scope,
                "capability_requires_confirmation",
                timestamp,
            )
        if normalized_scope in self.policy.normalized_explicit_consent_scopes:
            return self._requires_consent_decision(
                capability_name,
                normalized_scope,
                f"scope_requires_explicit_consent:{normalized_scope.value}",
                timestamp,
            )
        if (
            normalized_scope is PermissionScope.NONE
            and self.policy.allow_none_scope_without_consent
        ):
            return self._allowed_decision(
                capability_name,
                normalized_scope,
                "none_scope_allowed",
                timestamp,
            )
        if (
            normalized_scope in {PermissionScope.READ, PermissionScope.NETWORK}
            and risk_level == "low"
            and self.policy.allow_low_risk_read_without_consent
        ):
            return self._allowed_decision(
                capability_name,
                normalized_scope,
                "low_risk_read_allowed",
                timestamp,
            )
        return self._requires_consent_decision(
            capability_name,
            normalized_scope,
            "policy_requires_consent",
            timestamp,
        )

    def build_snapshot(
        self,
        decisions: tuple[ConsentDecision, ...],
        grants: dict[str, PermissionGrant],
        now: datetime | None = None,
    ) -> PermissionConsentSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("permission consent timestamp must be timezone-aware")
        signals = self._signals_for(decisions)
        return PermissionConsentSnapshot(
            signals=signals,
            evaluated_capabilities=tuple(
                sorted(decision.capability_name for decision in decisions)
            ),
            allowed_capabilities=tuple(
                sorted(
                    decision.capability_name
                    for decision in decisions
                    if decision.normalized_status is ConsentDecisionStatus.ALLOWED
                )
            ),
            consent_required_capabilities=tuple(
                sorted(
                    decision.capability_name
                    for decision in decisions
                    if decision.normalized_status
                    is ConsentDecisionStatus.REQUIRES_CONSENT
                )
            ),
            denied_capabilities=tuple(
                sorted(
                    decision.capability_name
                    for decision in decisions
                    if decision.normalized_status is ConsentDecisionStatus.DENIED
                )
            ),
            active_grants=tuple(sorted(grants)),
            created_at=timestamp,
        )

    def _signals_for(
        self,
        decisions: tuple[ConsentDecision, ...],
    ) -> tuple[PermissionConsentSignal, ...]:
        signals = [
            PermissionConsentSignal.PERMISSION_LAYER_READY,
            PermissionConsentSignal.CONTRACT_PRESERVED,
        ]
        if decisions:
            signals.append(PermissionConsentSignal.CAPABILITY_PERMISSION_EVALUATED)
        if any(
            decision.normalized_status is ConsentDecisionStatus.ALLOWED
            for decision in decisions
        ):
            signals.append(PermissionConsentSignal.CONSENT_GRANTED)
        if any(
            decision.normalized_status is ConsentDecisionStatus.REQUIRES_CONSENT
            for decision in decisions
        ):
            signals.append(PermissionConsentSignal.CONSENT_REQUIRED)
        if any(
            decision.normalized_status is ConsentDecisionStatus.DENIED
            for decision in decisions
        ):
            signals.append(PermissionConsentSignal.CONSENT_DENIED)
        return tuple(signals)

    def _allowed_decision(
        self,
        capability_name: str,
        scope: PermissionScope,
        reason: str,
        timestamp: datetime,
    ) -> ConsentDecision:
        return ConsentDecision(
            capability_name,
            scope,
            ConsentDecisionStatus.ALLOWED,
            reason,
            required_confirmation=False,
            created_at=timestamp,
        )

    def _requires_consent_decision(
        self,
        capability_name: str,
        scope: PermissionScope,
        reason: str,
        timestamp: datetime,
    ) -> ConsentDecision:
        return ConsentDecision(
            capability_name,
            scope,
            ConsentDecisionStatus.REQUIRES_CONSENT,
            reason,
            required_confirmation=True,
            created_at=timestamp,
        )


class PermissionConsentManager:
    """Fachada de M63 para conceder, revocar y evaluar permisos."""

    def __init__(
        self,
        policy: PermissionConsentPolicy | None = None,
        engine: PermissionConsentEngine | None = None,
    ) -> None:
        self.policy = policy or PermissionConsentPolicy()
        self.engine = engine or PermissionConsentEngine(self.policy)
        self._grants: dict[str, PermissionGrant] = {}
        self._history: list[PermissionConsentSnapshot] = []
        self._decisions: list[ConsentDecision] = []

    @property
    def grants(self) -> dict[str, PermissionGrant]:
        return dict(self._grants)

    @property
    def history(self) -> tuple[PermissionConsentSnapshot, ...]:
        return tuple(self._history)

    @property
    def decisions(self) -> tuple[ConsentDecision, ...]:
        return tuple(self._decisions)

    @property
    def last_snapshot(self) -> PermissionConsentSnapshot | None:
        return self._history[-1] if self._history else None

    @property
    def last_decision(self) -> ConsentDecision | None:
        return self._decisions[-1] if self._decisions else None

    def grant(self, grant: PermissionGrant) -> None:
        if (
            grant.capability_name not in self._grants
            and len(self._grants) >= self.policy.max_grants
        ):
            raise ValueError("permission grant limit exceeded")
        self._grants[grant.capability_name] = grant

    def revoke(self, capability_name: str) -> None:
        self._grants.pop(capability_name, None)

    def authorize_descriptor(
        self,
        descriptor: CapabilityDescriptor,
    ) -> ConsentDecision:
        return self.authorize_capability(
            descriptor.name,
            scope=descriptor.normalized_permission_scope,
            risk_level=descriptor.normalized_risk.value,
            requires_confirmation=descriptor.requires_confirmation,
        )

    def authorize_capability(
        self,
        capability_name: str,
        *,
        scope: PermissionScope | str,
        risk_level: str = "low",
        requires_confirmation: bool = False,
    ) -> ConsentDecision:
        decision = self.engine.evaluate_capability(
            capability_name,
            scope=scope,
            risk_level=risk_level,
            requires_confirmation=requires_confirmation,
            grants=self._grants,
        )
        self._decisions.append(decision)
        return decision

    def observe_turn(
        self,
        text: str,
        *,
        capabilities: dict[str, CapabilityDescriptor],
        requested_capabilities: tuple[str, ...] = (),
    ) -> PermissionConsentSnapshot:
        if not text.strip():
            raise ValueError("permission consent text must not be empty")
        decisions = tuple(
            self.authorize_descriptor(capabilities[name])
            for name in requested_capabilities
            if name in capabilities
        )
        snapshot = self.engine.build_snapshot(decisions, self._grants)
        self._history.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return (
                "Permissions & Consent M63:",
                "- Estado: permission_layer_ready",
                (
                    "- Regla: las capacidades sensibles requieren "
                    "consentimiento explícito."
                ),
            )
        return self.last_snapshot.system_prompt_lines()
