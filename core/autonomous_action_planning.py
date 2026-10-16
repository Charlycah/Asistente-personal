from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from core.capability_registry import CapabilityDescriptor, CapabilityRegistrySnapshot
from core.permission_consent import PermissionConsentSnapshot
from core.tool_gateway import ToolGatewaySnapshot


class AutonomousActionPlanningSignal(str, Enum):
    """Señales de M69 para planificar acciones sin ejecutarlas."""

    PLANNING_LAYER_READY = "planning_layer_ready"
    CAPABILITY_PLAN_PROPOSED = "capability_plan_proposed"
    CONSENT_AWARE = "consent_aware"
    EXECUTION_DEFERRED = "execution_deferred"
    CONTRACT_PRESERVED = "contract_preserved"


class AutonomousActionPlanStatus(str, Enum):
    """Estado normalizado de un plan autónomo limitado."""

    IDLE = "idle"
    PROPOSED = "proposed"
    AWAITING_CONSENT = "awaiting_consent"
    READY_FOR_REVIEW = "ready_for_review"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class AutonomousActionPlanningPolicy:
    """Política M69: ROBY puede proponer, pero no ejecutar sin gobierno."""

    max_steps: int = 5
    max_proposals: int = 20
    allow_direct_execution: bool = False
    require_review_before_execution: bool = True

    def __post_init__(self) -> None:
        if self.max_steps <= 0:
            raise ValueError("autonomous action max steps must be positive")
        if self.max_proposals <= 0:
            raise ValueError("autonomous action proposal limit must be positive")
        if self.allow_direct_execution:
            raise ValueError("M69 must not allow direct autonomous execution")


@dataclass(frozen=True)
class AutonomousActionStep:
    """Paso propuesto usando una capacidad registrada, sin invocarla."""

    capability_name: str
    purpose: str
    requires_consent: bool = False
    payload_hint: dict[str, object] = field(default_factory=dict)
    step_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.capability_name.strip():
            raise ValueError("action step capability must not be empty")
        if not self.purpose.strip():
            raise ValueError("action step purpose must not be empty")
        if not self.step_id.strip():
            raise ValueError("action step id must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.step_id,
            "capability": self.capability_name,
            "purpose": self.purpose,
            "requires_consent": self.requires_consent,
            "payload_hint": dict(self.payload_hint),
        }


@dataclass(frozen=True)
class AutonomousActionPlan:
    """Plan autónomo limitado: propuesta auditable, no ejecución."""

    title: str
    rationale: str
    steps: tuple[AutonomousActionStep, ...]
    status: AutonomousActionPlanStatus | str
    user_confirmation_required: bool
    blocked_reasons: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    plan_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("action plan title must not be empty")
        if not self.rationale.strip():
            raise ValueError("action plan rationale must not be empty")
        if not self.steps:
            raise ValueError("action plan must contain at least one step")
        AutonomousActionPlanStatus(self.status)
        if any(not reason.strip() for reason in self.blocked_reasons):
            raise ValueError("action plan blocked reasons must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("action plan timestamp must be timezone-aware")
        if not self.plan_id.strip():
            raise ValueError("action plan id must not be empty")

    @property
    def normalized_status(self) -> AutonomousActionPlanStatus:
        return AutonomousActionPlanStatus(self.status)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.plan_id,
            "title": self.title,
            "rationale": self.rationale,
            "status": self.normalized_status.value,
            "user_confirmation_required": self.user_confirmation_required,
            "blocked_reasons": list(self.blocked_reasons),
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class AutonomousActionPlanningSnapshot:
    """Snapshot M69 para exponer propuestas al ciclo cognitivo."""

    signals: tuple[AutonomousActionPlanningSignal | str, ...]
    status: AutonomousActionPlanStatus | str
    proposed_plans: tuple[AutonomousActionPlan, ...]
    requested_capabilities: tuple[str, ...]
    consent_required_capabilities: tuple[str, ...]
    execution_deferred: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("action planning signals must not be empty")
        for signal in self.signals:
            AutonomousActionPlanningSignal(signal)
        AutonomousActionPlanStatus(self.status)
        if any(not item.strip() for item in self.requested_capabilities):
            raise ValueError("requested action capabilities must not be blank")
        if any(not item.strip() for item in self.consent_required_capabilities):
            raise ValueError("consent action capabilities must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("action planning timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("action planning snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[AutonomousActionPlanningSignal, ...]:
        return tuple(AutonomousActionPlanningSignal(signal) for signal in self.signals)

    @property
    def normalized_status(self) -> AutonomousActionPlanStatus:
        return AutonomousActionPlanStatus(self.status)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Autonomous Action Planning M69:",
            f"- Estado: {self.normalized_status.value}",
            f"- Señales: {signals}",
            "- Regla: ROBY puede proponer planes, no ejecutarlos solo.",
            "- Regla: toda acción sensible requiere revisión o consentimiento.",
            f"- Ejecución diferida: {str(self.execution_deferred).lower()}",
        ]
        lines.extend(
            f"- Capacidad considerada: {name}" for name in self.requested_capabilities
        )
        lines.extend(
            f"- Consentimiento pendiente: {name}"
            for name in self.consent_required_capabilities
        )
        for plan in self.proposed_plans:
            lines.append(f"- Plan propuesto: {plan.title}")
            for step in plan.steps:
                lines.append(f"  - Paso: {step.capability_name} — {step.purpose}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "status": self.normalized_status.value,
            "proposed_plans": [plan.to_dict() for plan in self.proposed_plans],
            "requested_capabilities": list(self.requested_capabilities),
            "consent_required_capabilities": list(self.consent_required_capabilities),
            "execution_deferred": self.execution_deferred,
            "created_at": self.created_at.isoformat(),
        }


class AutonomousActionPlanningManager:
    """M69: propone acciones coordinadas sin ejecutar herramientas."""

    def __init__(
        self,
        policy: AutonomousActionPlanningPolicy | None = None,
    ) -> None:
        self.policy = policy or AutonomousActionPlanningPolicy()
        self._history: list[AutonomousActionPlanningSnapshot] = []

    @property
    def history(self) -> tuple[AutonomousActionPlanningSnapshot, ...]:
        return tuple(self._history)

    @property
    def last_snapshot(self) -> AutonomousActionPlanningSnapshot | None:
        return self._history[-1] if self._history else None

    def observe_turn(
        self,
        text: str,
        *,
        capabilities: dict[str, CapabilityDescriptor] | None = None,
        capability_snapshot: CapabilityRegistrySnapshot | None = None,
        permission_snapshot: PermissionConsentSnapshot | None = None,
        gateway_snapshot: ToolGatewaySnapshot | None = None,
        now: datetime | None = None,
    ) -> AutonomousActionPlanningSnapshot:
        if not text.strip():
            raise ValueError("action planning text must not be empty")
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("action planning timestamp must be timezone-aware")

        requested = self._requested_capabilities(
            text,
            capability_snapshot,
            gateway_snapshot,
        )
        consent_required = self._consent_required(permission_snapshot, requested)
        plans = self._plans_for(
            text,
            requested=requested,
            consent_required=consent_required,
            capabilities=capabilities or {},
        )
        status = self._status_for(plans, consent_required, gateway_snapshot)
        signals = self._signals_for(plans, consent_required)
        snapshot = AutonomousActionPlanningSnapshot(
            signals=signals,
            status=status,
            proposed_plans=plans,
            requested_capabilities=requested,
            consent_required_capabilities=consent_required,
            execution_deferred=bool(plans),
            created_at=timestamp,
        )
        self._history.append(snapshot)
        if len(self._history) > self.policy.max_proposals:
            self._history = self._history[-self.policy.max_proposals :]
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return (
                "Autonomous Action Planning M69:",
                "- Estado: idle",
                "- Regla: ROBY propone acciones; no ejecuta sin revisión.",
            )
        return self.last_snapshot.system_prompt_lines()

    def _requested_capabilities(
        self,
        text: str,
        capability_snapshot: CapabilityRegistrySnapshot | None,
        gateway_snapshot: ToolGatewaySnapshot | None,
    ) -> tuple[str, ...]:
        requested: set[str] = set()
        if capability_snapshot is not None:
            requested.update(capability_snapshot.requested_capabilities)
        if gateway_snapshot is not None:
            requested.update(gateway_snapshot.requested_capabilities)
        if requested:
            return tuple(sorted(requested))
        return self._heuristic_capabilities(text)

    def _heuristic_capabilities(self, text: str) -> tuple[str, ...]:
        normalized = text.casefold()
        requested: set[str] = set()
        weather_terms = ("clima", "lluvia", "frío", "frio", "paraguas", "abrigo")
        if any(term in normalized for term in weather_terms):
            requested.add("weather.current")
        if any(term in normalized for term in ("correo", "mail", "email")):
            requested.add("mail.read")
        if any(term in normalized for term in ("respond", "contest", "redact")):
            requested.add("mail.send")
        if any(term in normalized for term in ("mirá", "mira", "cámara", "camara")):
            requested.add("camera.capture")
        return tuple(sorted(requested))

    def _consent_required(
        self,
        permission_snapshot: PermissionConsentSnapshot | None,
        requested: tuple[str, ...],
    ) -> tuple[str, ...]:
        if permission_snapshot is None:
            return ()
        required = set(permission_snapshot.consent_required_capabilities)
        return tuple(sorted(required.intersection(requested)))

    def _plans_for(
        self,
        text: str,
        *,
        requested: tuple[str, ...],
        consent_required: tuple[str, ...],
        capabilities: dict[str, CapabilityDescriptor],
    ) -> tuple[AutonomousActionPlan, ...]:
        if not requested:
            return ()
        steps = tuple(
            AutonomousActionStep(
                capability_name=name,
                purpose=self._purpose_for(name, text),
                requires_consent=name in consent_required
                or capabilities.get(name, None) is not None
                and capabilities[name].requires_confirmation,
                payload_hint=self._payload_hint_for(name, text),
            )
            for name in requested[: self.policy.max_steps]
        )
        blocked_reasons = tuple(f"consent_required:{name}" for name in consent_required)
        status = (
            AutonomousActionPlanStatus.AWAITING_CONSENT
            if consent_required
            else AutonomousActionPlanStatus.READY_FOR_REVIEW
        )
        return (
            AutonomousActionPlan(
                title=self._title_for(requested),
                rationale="El turno del usuario coincide con capacidades registradas; "
                "ROBY debe proponer un plan revisable antes de actuar.",
                steps=steps,
                status=status,
                user_confirmation_required=True,
                blocked_reasons=blocked_reasons,
            ),
        )

    def _purpose_for(self, capability_name: str, text: str) -> str:
        if capability_name.startswith("weather"):
            return "consultar clima o pronóstico para responder con contexto útil"
        if capability_name == "mail.read":
            return "leer o resumir correos sin modificar la casilla"
        if capability_name == "mail.send":
            return "preparar una respuesta o borrador sujeto a confirmación"
        if capability_name == "camera.capture":
            return "capturar imagen local solo si el usuario concede permiso"
        return f"usar la capacidad para atender: {text[:60]}"

    def _payload_hint_for(self, capability_name: str, text: str) -> dict[str, object]:
        if capability_name.startswith("weather"):
            return {"location": "default", "source_text": text}
        if capability_name == "mail.read":
            return {"query": "natural_language", "source_text": text}
        if capability_name == "mail.send":
            return {"mode": "draft_or_reply", "source_text": text}
        if capability_name == "camera.capture":
            return {"camera_index": "default", "source_text": text}
        return {"source_text": text}

    def _title_for(self, requested: tuple[str, ...]) -> str:
        if requested == ("weather.current",):
            return "Consultar clima antes de responder"
        if requested == ("mail.read",):
            return "Revisar correos solicitados"
        if requested == ("mail.send",):
            return "Preparar acción de correo"
        if requested == ("camera.capture",):
            return "Solicitar captura de cámara"
        return "Coordinar capacidades externas"

    def _status_for(
        self,
        plans: tuple[AutonomousActionPlan, ...],
        consent_required: tuple[str, ...],
        gateway_snapshot: ToolGatewaySnapshot | None,
    ) -> AutonomousActionPlanStatus:
        if not plans:
            return AutonomousActionPlanStatus.IDLE
        if gateway_snapshot is not None and gateway_snapshot.blocked_reasons:
            return AutonomousActionPlanStatus.BLOCKED
        if consent_required:
            return AutonomousActionPlanStatus.AWAITING_CONSENT
        return AutonomousActionPlanStatus.PROPOSED

    def _signals_for(
        self,
        plans: tuple[AutonomousActionPlan, ...],
        consent_required: tuple[str, ...],
    ) -> tuple[AutonomousActionPlanningSignal, ...]:
        signals = [
            AutonomousActionPlanningSignal.PLANNING_LAYER_READY,
            AutonomousActionPlanningSignal.CONTRACT_PRESERVED,
            AutonomousActionPlanningSignal.EXECUTION_DEFERRED,
        ]
        if plans:
            signals.append(AutonomousActionPlanningSignal.CAPABILITY_PLAN_PROPOSED)
        if consent_required:
            signals.append(AutonomousActionPlanningSignal.CONSENT_AWARE)
        return tuple(signals)
