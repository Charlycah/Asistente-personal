from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.autonomous_action_planning import (
    AutonomousActionPlanningSnapshot,
    AutonomousActionPlanStatus,
)
from core.capability_registry import CapabilityRegistrySnapshot
from core.permission_consent import PermissionConsentSnapshot
from core.tool_gateway import ToolGatewaySnapshot


class GovernedAutonomySignal(str, Enum):
    """Señales de M70 para gobernar autonomía sin ejecución libre."""

    GOVERNANCE_LAYER_READY = "governance_layer_ready"
    POLICY_EVALUATED = "policy_evaluated"
    AUTONOMY_BOUNDED = "autonomy_bounded"
    RESTRICTIVE_PRECEDENCE_APPLIED = "restrictive_precedence_applied"
    AUDIT_RECORD_CREATED = "audit_record_created"
    CONTRACT_PRESERVED = "contract_preserved"


class GovernedAutonomyStatus(str, Enum):
    """Estado normalizado de una decisión de autonomía gobernada."""

    PASSIVE = "passive"
    PROPOSAL_ALLOWED = "proposal_allowed"
    REVIEW_REQUIRED = "review_required"
    AWAITING_CONSENT = "awaiting_consent"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class GovernedAutonomyPolicy:
    """Política final de Fase VI: autonomía útil, limitada y auditable."""

    allow_unattended_execution: bool = False
    allow_low_risk_read_without_confirmation: bool = True
    require_review_for_actions: bool = True
    require_audit_record: bool = True
    require_explainability: bool = True
    most_restrictive_policy_wins: bool = True
    max_audit_records: int = 100
    sensitive_capabilities: tuple[str, ...] = (
        "mail.send",
        "camera.capture",
        "camera.analyze",
    )

    def __post_init__(self) -> None:
        if self.allow_unattended_execution:
            raise ValueError("M70 must not allow unattended autonomous execution")
        if self.max_audit_records <= 0:
            raise ValueError("governed autonomy audit limit must be positive")
        if any(not capability.strip() for capability in self.sensitive_capabilities):
            raise ValueError("sensitive capabilities must not be blank")


@dataclass(frozen=True)
class GovernedAutonomyDecision:
    """Decisión auditable que delimita lo que ROBY puede hacer."""

    status: GovernedAutonomyStatus | str
    requested_capabilities: tuple[str, ...]
    permitted_capabilities: tuple[str, ...]
    review_required_capabilities: tuple[str, ...]
    consent_required_capabilities: tuple[str, ...]
    blocked_capabilities: tuple[str, ...]
    rationale: str
    can_execute: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        GovernedAutonomyStatus(self.status)
        groups = (
            self.requested_capabilities,
            self.permitted_capabilities,
            self.review_required_capabilities,
            self.consent_required_capabilities,
            self.blocked_capabilities,
        )
        if any(not item.strip() for group in groups for item in group):
            raise ValueError("governed autonomy capability names must not be blank")
        if not self.rationale.strip():
            raise ValueError("governed autonomy rationale must not be empty")
        if self.can_execute:
            raise ValueError("governed autonomy decisions must not execute directly")
        if self.created_at.tzinfo is None:
            raise ValueError("governed autonomy timestamp must be timezone-aware")
        if not self.decision_id.strip():
            raise ValueError("governed autonomy decision id must not be empty")

    @property
    def normalized_status(self) -> GovernedAutonomyStatus:
        return GovernedAutonomyStatus(self.status)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.decision_id,
            "status": self.normalized_status.value,
            "requested_capabilities": list(self.requested_capabilities),
            "permitted_capabilities": list(self.permitted_capabilities),
            "review_required_capabilities": list(self.review_required_capabilities),
            "consent_required_capabilities": list(self.consent_required_capabilities),
            "blocked_capabilities": list(self.blocked_capabilities),
            "rationale": self.rationale,
            "can_execute": self.can_execute,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class GovernedAutonomySnapshot:
    """Snapshot M70 para exponer reglas finales de autonomía a ROBY."""

    signals: tuple[GovernedAutonomySignal | str, ...]
    status: GovernedAutonomyStatus | str
    decision: GovernedAutonomyDecision
    audit_trail: tuple[str, ...]
    governance_contract: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("governed autonomy signals must not be empty")
        for signal in self.signals:
            GovernedAutonomySignal(signal)
        GovernedAutonomyStatus(self.status)
        if any(not item.strip() for item in self.audit_trail):
            raise ValueError("governed autonomy audit items must not be blank")
        if any(not item.strip() for item in self.governance_contract):
            raise ValueError("governance contract lines must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("governed autonomy snapshot timestamp must be aware")
        if not self.snapshot_id.strip():
            raise ValueError("governed autonomy snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[GovernedAutonomySignal, ...]:
        return tuple(GovernedAutonomySignal(signal) for signal in self.signals)

    @property
    def normalized_status(self) -> GovernedAutonomyStatus:
        return GovernedAutonomyStatus(self.status)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Governed Autonomy M70:",
            f"- Estado: {self.normalized_status.value}",
            f"- Señales: {signals}",
            "- Regla: ROBY puede proponer acciones antes de ejecutarlas.",
            "- Regla: ROBY no ejecuta acciones sensibles sin consentimiento.",
            "- Regla: ante conflicto prevalece la política más restrictiva.",
            "- Regla: toda decisión autónoma debe ser auditable y explicable.",
        ]
        for line in self.governance_contract:
            lines.append(f"- Contrato: {line}")
        for capability in self.decision.requested_capabilities:
            lines.append(f"- Capacidad gobernada: {capability}")
        for capability in self.decision.review_required_capabilities:
            lines.append(f"- Revisión requerida: {capability}")
        for capability in self.decision.consent_required_capabilities:
            lines.append(f"- Consentimiento requerido: {capability}")
        for capability in self.decision.blocked_capabilities:
            lines.append(f"- Capacidad bloqueada: {capability}")
        lines.append(f"- Racional: {self.decision.rationale}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "status": self.normalized_status.value,
            "decision": self.decision.to_dict(),
            "audit_trail": list(self.audit_trail),
            "governance_contract": list(self.governance_contract),
            "created_at": self.created_at.isoformat(),
        }


class GovernedAutonomyManager:
    """M70: gobierna autonomía con límites, auditoría y explicación."""

    def __init__(
        self,
        policy: GovernedAutonomyPolicy | None = None,
    ) -> None:
        self.policy = policy or GovernedAutonomyPolicy()
        self._history: list[GovernedAutonomySnapshot] = []

    @property
    def history(self) -> tuple[GovernedAutonomySnapshot, ...]:
        return tuple(self._history)

    @property
    def last_snapshot(self) -> GovernedAutonomySnapshot | None:
        return self._history[-1] if self._history else None

    def observe_turn(
        self,
        text: str,
        *,
        capability_snapshot: CapabilityRegistrySnapshot | None = None,
        permission_snapshot: PermissionConsentSnapshot | None = None,
        planning_snapshot: AutonomousActionPlanningSnapshot | None = None,
        gateway_snapshot: ToolGatewaySnapshot | None = None,
        now: datetime | None = None,
    ) -> GovernedAutonomySnapshot:
        if not text.strip():
            raise ValueError("governed autonomy text must not be empty")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("governed autonomy timestamp must be timezone-aware")

        requested = self._requested_capabilities(
            text,
            capability_snapshot=capability_snapshot,
            planning_snapshot=planning_snapshot,
            gateway_snapshot=gateway_snapshot,
        )
        consent_required = self._consent_required(
            requested,
            permission_snapshot=permission_snapshot,
            planning_snapshot=planning_snapshot,
        )
        blocked = self._blocked_capabilities(
            requested,
            consent_required=consent_required,
            gateway_snapshot=gateway_snapshot,
        )
        review_required = self._review_required(requested, consent_required, blocked)
        permitted = tuple(
            capability
            for capability in requested
            if capability not in blocked and capability not in consent_required
        )
        status = self._status_for(
            requested,
            consent_required=consent_required,
            review_required=review_required,
            blocked=blocked,
            planning_snapshot=planning_snapshot,
        )
        rationale = self._rationale_for(status, requested, consent_required, blocked)
        decision = GovernedAutonomyDecision(
            status=status,
            requested_capabilities=requested,
            permitted_capabilities=permitted,
            review_required_capabilities=review_required,
            consent_required_capabilities=consent_required,
            blocked_capabilities=blocked,
            rationale=rationale,
            can_execute=False,
            created_at=timestamp,
        )
        snapshot = GovernedAutonomySnapshot(
            signals=self._signals_for(decision),
            status=status,
            decision=decision,
            audit_trail=self._audit_trail_for(decision),
            governance_contract=self._contract_lines(),
            created_at=timestamp,
        )
        self._history.append(snapshot)
        if len(self._history) > self.policy.max_audit_records:
            self._history = self._history[-self.policy.max_audit_records :]
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return (
                "Governed Autonomy M70:",
                "- Estado: passive",
                "- Regla: ROBY propone, explica y solicita permiso antes de actuar.",
                "- Regla: no hay ejecución autónoma desatendida.",
            )
        return self.last_snapshot.system_prompt_lines()

    def _requested_capabilities(
        self,
        text: str,
        *,
        capability_snapshot: CapabilityRegistrySnapshot | None,
        planning_snapshot: AutonomousActionPlanningSnapshot | None,
        gateway_snapshot: ToolGatewaySnapshot | None,
    ) -> tuple[str, ...]:
        requested: set[str] = set()
        if capability_snapshot is not None:
            requested.update(capability_snapshot.requested_capabilities)
        if planning_snapshot is not None:
            requested.update(planning_snapshot.requested_capabilities)
        if gateway_snapshot is not None:
            requested.update(gateway_snapshot.requested_capabilities)
        if not requested:
            requested.update(self._heuristic_capabilities(text))
        return tuple(sorted(requested))

    def _heuristic_capabilities(self, text: str) -> tuple[str, ...]:
        normalized = text.casefold()
        requested: set[str] = set()
        if any(term in normalized for term in ("clima", "lluvia", "frío", "frio")):
            requested.add("weather.current")
        if any(term in normalized for term in ("correo", "mail", "email")):
            requested.add("mail.read")
        if any(term in normalized for term in ("respond", "contest", "redact")):
            requested.add("mail.send")
        if any(term in normalized for term in ("cámara", "camara", "mirá", "mira")):
            requested.add("camera.capture")
        return tuple(sorted(requested))

    def _consent_required(
        self,
        requested: tuple[str, ...],
        *,
        permission_snapshot: PermissionConsentSnapshot | None,
        planning_snapshot: AutonomousActionPlanningSnapshot | None,
    ) -> tuple[str, ...]:
        required: set[str] = set()
        if permission_snapshot is not None:
            required.update(permission_snapshot.consent_required_capabilities)
            required.update(permission_snapshot.denied_capabilities)
        if planning_snapshot is not None:
            required.update(planning_snapshot.consent_required_capabilities)
        required.update(
            capability
            for capability in requested
            if capability in self.policy.sensitive_capabilities
        )
        return tuple(sorted(required.intersection(requested)))

    def _blocked_capabilities(
        self,
        requested: tuple[str, ...],
        *,
        consent_required: tuple[str, ...],
        gateway_snapshot: ToolGatewaySnapshot | None,
    ) -> tuple[str, ...]:
        blocked: set[str] = set()
        if gateway_snapshot is not None and gateway_snapshot.blocked_reasons:
            blocked.update(requested)
        if self.policy.most_restrictive_policy_wins:
            blocked.update(
                capability
                for capability in consent_required
                if capability in self.policy.sensitive_capabilities
            )
        return tuple(sorted(blocked))

    def _review_required(
        self,
        requested: tuple[str, ...],
        consent_required: tuple[str, ...],
        blocked: tuple[str, ...],
    ) -> tuple[str, ...]:
        if not self.policy.require_review_for_actions:
            return ()
        review = set(consent_required)
        review.update(
            capability
            for capability in requested
            if capability not in blocked
            and not self._is_low_risk_read_capability(capability)
        )
        return tuple(sorted(review.intersection(requested)))

    def _is_low_risk_read_capability(self, capability: str) -> bool:
        if not self.policy.allow_low_risk_read_without_confirmation:
            return False
        return capability.startswith("weather") or capability == "mail.read"

    def _status_for(
        self,
        requested: tuple[str, ...],
        *,
        consent_required: tuple[str, ...],
        review_required: tuple[str, ...],
        blocked: tuple[str, ...],
        planning_snapshot: AutonomousActionPlanningSnapshot | None,
    ) -> GovernedAutonomyStatus:
        if not requested:
            return GovernedAutonomyStatus.PASSIVE
        if blocked:
            return GovernedAutonomyStatus.BLOCKED
        if consent_required:
            return GovernedAutonomyStatus.AWAITING_CONSENT
        if review_required:
            return GovernedAutonomyStatus.REVIEW_REQUIRED
        if planning_snapshot is not None and planning_snapshot.normalized_status in {
            AutonomousActionPlanStatus.PROPOSED,
            AutonomousActionPlanStatus.READY_FOR_REVIEW,
        }:
            return GovernedAutonomyStatus.PROPOSAL_ALLOWED
        return GovernedAutonomyStatus.PROPOSAL_ALLOWED

    def _rationale_for(
        self,
        status: GovernedAutonomyStatus,
        requested: tuple[str, ...],
        consent_required: tuple[str, ...],
        blocked: tuple[str, ...],
    ) -> str:
        if status is GovernedAutonomyStatus.PASSIVE:
            return "No hay capacidades externas relevantes para gobernar."
        if blocked:
            return "La política más restrictiva bloquea acciones sensibles pendientes."
        if consent_required:
            return "La solicitud requiere consentimiento explícito antes de actuar."
        if requested:
            return (
                "La acción puede proponerse y explicarse, "
                "manteniendo ejecución diferida."
            )
        return "Autonomía gobernada sin acción externa."

    def _signals_for(
        self,
        decision: GovernedAutonomyDecision,
    ) -> tuple[GovernedAutonomySignal, ...]:
        signals = [
            GovernedAutonomySignal.GOVERNANCE_LAYER_READY,
            GovernedAutonomySignal.POLICY_EVALUATED,
            GovernedAutonomySignal.AUTONOMY_BOUNDED,
            GovernedAutonomySignal.CONTRACT_PRESERVED,
        ]
        if self.policy.most_restrictive_policy_wins:
            signals.append(GovernedAutonomySignal.RESTRICTIVE_PRECEDENCE_APPLIED)
        if self.policy.require_audit_record:
            signals.append(GovernedAutonomySignal.AUDIT_RECORD_CREATED)
        return tuple(signals)

    def _audit_trail_for(
        self,
        decision: GovernedAutonomyDecision,
    ) -> tuple[str, ...]:
        return (
            f"decision:{decision.decision_id}",
            f"status:{decision.normalized_status.value}",
            f"requested:{','.join(decision.requested_capabilities) or 'none'}",
            f"can_execute:{str(decision.can_execute).lower()}",
        )

    def _contract_lines(self) -> tuple[str, ...]:
        lines = [
            "ROBY no ejecuta acciones externas sensibles sin permiso explícito.",
            "ROBY puede proponer planes y solicitar autorización contextual.",
            "Las capacidades se gobiernan por riesgo, alcance y consentimiento.",
            "Toda decisión debe poder explicarse y auditarse.",
        ]
        if self.policy.most_restrictive_policy_wins:
            lines.append("Ante conflicto prevalece la regla más restrictiva.")
        if self.policy.require_explainability:
            lines.append(
                "La respuesta debe explicar por qué se propone o bloquea una acción."
            )
        return tuple(lines)
