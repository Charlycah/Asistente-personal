from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from core.architectural_principle import ArchitecturalPrincipleManager
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityRegistryManager,
)
from core.permission_consent import (
    ConsentDecisionStatus,
    PermissionConsentManager,
)

ToolHandler = Callable[[Mapping[str, Any]], Mapping[str, Any]]


class ToolGatewaySignal(str, Enum):
    """Señales que describen cómo M61 gobierna herramientas externas."""

    GATEWAY_REQUIRED = "gateway_required"
    CAPABILITY_REQUESTED = "capability_requested"
    CONTRACT_PRESERVED = "contract_preserved"
    EXECUTION_ROUTED = "execution_routed"
    EXECUTION_BLOCKED = "execution_blocked"


class ToolGatewayStatus(str, Enum):
    """Estado operativo del gateway de herramientas."""

    READY = "ready"
    ROUTED = "routed"
    WAITING_FOR_CAPABILITY = "waiting_for_capability"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ToolGatewayPolicy:
    """Política base de M61 para enrutar herramientas sin acoplarlas al core."""

    readiness_threshold: float = 0.55
    routed_threshold: float = 0.75
    allow_unregistered_execution: bool = False
    max_audit_entries: int = 50

    def __post_init__(self) -> None:
        thresholds = (self.readiness_threshold, self.routed_threshold)
        if any(not 0.0 <= threshold <= 1.0 for threshold in thresholds):
            raise ValueError("tool gateway thresholds must be between 0 and 1")
        if self.readiness_threshold > self.routed_threshold:
            raise ValueError("tool gateway thresholds must be ordered")
        if self.max_audit_entries <= 0:
            raise ValueError("tool gateway audit limit must be positive")


@dataclass(frozen=True)
class ToolCapability:
    """Capacidad externa registrada detrás del gateway."""

    name: str
    description: str
    risk_level: str = "low"
    enabled: bool = True
    requires_confirmation: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("tool capability name must not be empty")
        if not self.description.strip():
            raise ValueError("tool capability description must not be empty")
        if not self.risk_level.strip():
            raise ValueError("tool capability risk level must not be empty")
        if any(not key.strip() for key in self.metadata):
            raise ValueError("tool capability metadata keys must not be blank")


@dataclass(frozen=True)
class ToolRequest:
    """Solicitud normalizada para ejecutar una capacidad externa."""

    capability_name: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    reason: str = "user_requested"
    source: str = "cognitive_pipeline"
    request_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.capability_name.strip():
            raise ValueError("tool request capability must not be empty")
        if not self.reason.strip():
            raise ValueError("tool request reason must not be empty")
        if not self.source.strip():
            raise ValueError("tool request source must not be empty")
        if not self.request_id.strip():
            raise ValueError("tool request id must not be empty")


@dataclass(frozen=True)
class ToolResult:
    """Resultado auditable de una ejecución enrutable por M61."""

    request: ToolRequest
    status: ToolGatewayStatus | str
    output: Mapping[str, Any] = field(default_factory=dict)
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        ToolGatewayStatus(self.status)
        if self.error is not None and not self.error.strip():
            raise ValueError("tool result error must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("tool result timestamp must be timezone-aware")
        if not self.result_id.strip():
            raise ValueError("tool result id must not be empty")

    @property
    def normalized_status(self) -> ToolGatewayStatus:
        return ToolGatewayStatus(self.status)

    @property
    def succeeded(self) -> bool:
        return self.normalized_status is ToolGatewayStatus.ROUTED

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.result_id,
            "request_id": self.request.request_id,
            "capability": self.request.capability_name,
            "status": self.normalized_status.value,
            "output": dict(self.output),
            "error": self.error,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ToolGatewaySnapshot:
    """Snapshot de readiness del gateway para el turno cognitivo."""

    signals: tuple[ToolGatewaySignal | str, ...]
    status: ToolGatewayStatus | str
    readiness_score: float
    available_capabilities: tuple[str, ...]
    requested_capabilities: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    architectural_anchor_present: bool
    last_result_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.signals:
            raise ValueError("tool gateway signals must not be empty")
        for signal in self.signals:
            ToolGatewaySignal(signal)
        ToolGatewayStatus(self.status)
        if not 0.0 <= self.readiness_score <= 1.0:
            raise ValueError("tool gateway readiness must be between 0 and 1")
        if any(not name.strip() for name in self.available_capabilities):
            raise ValueError("tool gateway available capabilities must not be blank")
        if any(not name.strip() for name in self.requested_capabilities):
            raise ValueError("tool gateway requested capabilities must not be blank")
        if any(not reason.strip() for reason in self.blocked_reasons):
            raise ValueError("tool gateway blocked reasons must not be blank")
        if self.last_result_id is not None and not self.last_result_id.strip():
            raise ValueError("tool gateway last result id must not be blank")
        if self.created_at.tzinfo is None:
            raise ValueError("tool gateway timestamp must be timezone-aware")
        if not self.snapshot_id.strip():
            raise ValueError("tool gateway snapshot id must not be empty")

    @property
    def normalized_signals(self) -> tuple[ToolGatewaySignal, ...]:
        return tuple(ToolGatewaySignal(signal) for signal in self.signals)

    @property
    def normalized_status(self) -> ToolGatewayStatus:
        return ToolGatewayStatus(self.status)

    def system_prompt_lines(self) -> tuple[str, ...]:
        signals = ", ".join(signal.value for signal in self.normalized_signals)
        lines = [
            "Tool Gateway M61:",
            f"- Estado: {self.normalized_status.value}",
            f"- Señales: {signals}",
            f"- Preparación: {self.readiness_score:.2f}",
            "- Regla: ROBY solicita capacidades; no invoca APIs directamente.",
            "- Regla: toda herramienta externa debe pasar por el gateway.",
            f"- Ancla arquitectónica M60 presente: "
            f"{str(self.architectural_anchor_present).lower()}",
        ]
        lines.extend(
            f"- Capacidad disponible: {name}" for name in self.available_capabilities
        )
        lines.extend(
            f"- Capacidad solicitada: {name}" for name in self.requested_capabilities
        )
        lines.extend(f"- Bloqueo: {reason}" for reason in self.blocked_reasons)
        if self.last_result_id is not None:
            lines.append(f"- Última ejecución auditada: {self.last_result_id}")
        return tuple(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.snapshot_id,
            "signals": [signal.value for signal in self.normalized_signals],
            "status": self.normalized_status.value,
            "readiness_score": self.readiness_score,
            "available_capabilities": list(self.available_capabilities),
            "requested_capabilities": list(self.requested_capabilities),
            "blocked_reasons": list(self.blocked_reasons),
            "architectural_anchor_present": self.architectural_anchor_present,
            "last_result_id": self.last_result_id,
            "created_at": self.created_at.isoformat(),
        }


class ToolGatewayEngine:
    """Motor puro de M61 — puerta única para herramientas externas."""

    _WEATHER_TERMS = ("clima", "tiempo", "pronóstico", "extendido", "weather")
    _MAIL_TERMS = ("correo", "mail", "gmail", "email", "emails")
    _CAMERA_TERMS = ("cámara", "camara", "camera", "foto", "imagen")

    def __init__(self, policy: ToolGatewayPolicy | None = None) -> None:
        self.policy = policy or ToolGatewayPolicy()

    def evaluate_turn(
        self,
        text: str,
        *,
        capabilities: Mapping[str, ToolCapability],
        last_result: ToolResult | None = None,
        architectural_principle: ArchitecturalPrincipleManager | None = None,
        now: datetime | None = None,
    ) -> ToolGatewaySnapshot:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("tool gateway timestamp must be timezone-aware")
        if not text.strip():
            raise ValueError("tool gateway text must not be empty")

        available = tuple(
            sorted(
                name for name, capability in capabilities.items() if capability.enabled
            )
        )
        requested = self._requested_capabilities_for(text, capabilities)
        anchor_present = (
            architectural_principle is not None
            and architectural_principle.last_snapshot is not None
        )
        blocked_reasons = self._blocked_reasons_for(requested, capabilities)
        signals = self._signals_for(requested, last_result, blocked_reasons)
        readiness_score = self._readiness_for(
            available,
            requested,
            anchor_present,
            blocked_reasons,
        )
        status = self._status_for(
            readiness_score,
            requested,
            blocked_reasons,
            last_result,
        )

        return ToolGatewaySnapshot(
            signals=signals,
            status=status,
            readiness_score=readiness_score,
            available_capabilities=available,
            requested_capabilities=requested,
            blocked_reasons=blocked_reasons,
            architectural_anchor_present=anchor_present,
            last_result_id=last_result.result_id if last_result is not None else None,
            created_at=timestamp,
        )

    def _requested_capabilities_for(
        self,
        text: str,
        capabilities: Mapping[str, ToolCapability],
    ) -> tuple[str, ...]:
        normalized = text.casefold()
        requested: list[str] = []
        for name, capability in capabilities.items():
            terms = self._semantic_terms_for(name, capability)
            if any(term.casefold() in normalized for term in terms):
                requested.append(name)
        if requested:
            return tuple(sorted(requested))
        return self._legacy_requested_capabilities_for(normalized)

    def _semantic_terms_for(
        self,
        name: str,
        capability: ToolCapability,
    ) -> tuple[str, ...]:
        terms = [name, capability.description]
        semantic_keys = (
            "tags",
            "semantic_triggers",
            "supported_intents",
            "example_utterances",
        )
        for key in semantic_keys:
            value = capability.metadata.get(key, "")
            terms.extend(item for item in value.split("|") if item)
        return tuple(dict.fromkeys(term.strip() for term in terms if term.strip()))

    def _legacy_requested_capabilities_for(
        self,
        normalized_text: str,
    ) -> tuple[str, ...]:
        requested: list[str] = []
        if any(term in normalized_text for term in self._WEATHER_TERMS):
            requested.append("weather.current")
        if any(term in normalized_text for term in self._MAIL_TERMS):
            requested.append("mail.read")
        if any(term in normalized_text for term in self._CAMERA_TERMS):
            requested.append("camera.capture")
        return tuple(requested)

    def _blocked_reasons_for(
        self,
        requested: tuple[str, ...],
        capabilities: Mapping[str, ToolCapability],
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        for capability_name in requested:
            capability = capabilities.get(capability_name)
            if capability is None:
                reasons.append(f"capability_not_registered:{capability_name}")
            elif not capability.enabled:
                reasons.append(f"capability_disabled:{capability_name}")
        return tuple(reasons)

    def _signals_for(
        self,
        requested: tuple[str, ...],
        last_result: ToolResult | None,
        blocked_reasons: tuple[str, ...],
    ) -> tuple[ToolGatewaySignal, ...]:
        signals = [
            ToolGatewaySignal.GATEWAY_REQUIRED,
            ToolGatewaySignal.CONTRACT_PRESERVED,
        ]
        if requested:
            signals.append(ToolGatewaySignal.CAPABILITY_REQUESTED)
        if last_result is not None and last_result.succeeded:
            signals.append(ToolGatewaySignal.EXECUTION_ROUTED)
        if blocked_reasons or (last_result is not None and not last_result.succeeded):
            signals.append(ToolGatewaySignal.EXECUTION_BLOCKED)
        return tuple(signals)

    def _readiness_for(
        self,
        available: tuple[str, ...],
        requested: tuple[str, ...],
        anchor_present: bool,
        blocked_reasons: tuple[str, ...],
    ) -> float:
        score = 0.46
        if available:
            score += 0.22
        if requested:
            score += 0.12
        if anchor_present:
            score += 0.14
        if blocked_reasons:
            score -= 0.24
        return max(0.0, min(1.0, score))

    def _status_for(
        self,
        readiness_score: float,
        requested: tuple[str, ...],
        blocked_reasons: tuple[str, ...],
        last_result: ToolResult | None,
    ) -> ToolGatewayStatus:
        if blocked_reasons or (last_result is not None and not last_result.succeeded):
            return ToolGatewayStatus.BLOCKED
        if last_result is not None and last_result.succeeded:
            return ToolGatewayStatus.ROUTED
        if requested and readiness_score >= self.policy.readiness_threshold:
            return ToolGatewayStatus.WAITING_FOR_CAPABILITY
        return ToolGatewayStatus.READY


class ToolGatewayManager:
    """Fachada de M61 para registrar, enrutar y auditar herramientas."""

    def __init__(
        self,
        policy: ToolGatewayPolicy | None = None,
        engine: ToolGatewayEngine | None = None,
        capability_registry: CapabilityRegistryManager | None = None,
        permission_consent: PermissionConsentManager | None = None,
    ) -> None:
        self.policy = policy or ToolGatewayPolicy()
        self.engine = engine or ToolGatewayEngine(self.policy)
        self.capability_registry = capability_registry
        self.permission_consent = permission_consent
        self._capabilities: dict[str, ToolCapability] = {}
        self._handlers: dict[str, ToolHandler] = {}
        self._history: list[ToolGatewaySnapshot] = []
        self._audit_log: list[ToolResult] = []

    @property
    def capabilities(self) -> Mapping[str, ToolCapability]:
        return self._effective_capabilities()

    @property
    def history(self) -> tuple[ToolGatewaySnapshot, ...]:
        return tuple(self._history)

    @property
    def audit_log(self) -> tuple[ToolResult, ...]:
        return tuple(self._audit_log)

    @property
    def last_snapshot(self) -> ToolGatewaySnapshot | None:
        return self._history[-1] if self._history else None

    @property
    def last_result(self) -> ToolResult | None:
        return self._audit_log[-1] if self._audit_log else None

    def register_capability(
        self,
        capability: ToolCapability,
        handler: ToolHandler | None = None,
    ) -> None:
        self._capabilities[capability.name] = capability
        if self.capability_registry is not None:
            self._register_descriptor_for(capability)
        if handler is not None:
            self._handlers[capability.name] = handler

    def execute(self, request: ToolRequest) -> ToolResult:
        capability = self._effective_capabilities().get(request.capability_name)
        if capability is None and not self.policy.allow_unregistered_execution:
            return self._record_result(
                ToolResult(
                    request,
                    ToolGatewayStatus.BLOCKED,
                    error="capability_not_registered",
                )
            )
        if capability is not None and not capability.enabled:
            return self._record_result(
                ToolResult(
                    request,
                    ToolGatewayStatus.BLOCKED,
                    error="capability_disabled",
                )
            )
        if capability is not None and self.permission_consent is not None:
            decision = self.permission_consent.authorize_capability(
                capability.name,
                scope=capability.metadata.get("permission_scope", "none"),
                risk_level=capability.risk_level,
                requires_confirmation=capability.requires_confirmation,
            )
            if decision.normalized_status is ConsentDecisionStatus.REQUIRES_CONSENT:
                return self._record_result(
                    ToolResult(
                        request,
                        ToolGatewayStatus.BLOCKED,
                        error=f"consent_required:{decision.normalized_scope.value}",
                    )
                )
            if decision.normalized_status is ConsentDecisionStatus.DENIED:
                return self._record_result(
                    ToolResult(
                        request,
                        ToolGatewayStatus.BLOCKED,
                        error="consent_denied",
                    )
                )
        handler = self._handlers.get(request.capability_name)
        if handler is None:
            return self._record_result(
                ToolResult(
                    request,
                    ToolGatewayStatus.WAITING_FOR_CAPABILITY,
                    error="handler_not_registered",
                )
            )
        try:
            output = handler(request.payload)
        except Exception as exc:  # pragma: no cover - defensive boundary
            return self._record_result(
                ToolResult(
                    request,
                    ToolGatewayStatus.BLOCKED,
                    error=f"handler_error:{exc.__class__.__name__}",
                )
            )
        return self._record_result(
            ToolResult(request, ToolGatewayStatus.ROUTED, output=dict(output))
        )

    def observe_turn(
        self,
        text: str,
        *,
        architectural_principle: ArchitecturalPrincipleManager | None = None,
    ) -> ToolGatewaySnapshot:
        snapshot = self.engine.evaluate_turn(
            text,
            capabilities=self._effective_capabilities(),
            last_result=self.last_result,
            architectural_principle=architectural_principle,
        )
        self._history.append(snapshot)
        return snapshot

    def system_prompt_lines(self) -> tuple[str, ...]:
        if self.last_snapshot is None:
            return (
                "Tool Gateway M61:",
                "- Estado: ready",
                "- Regla: ROBY solicita capacidades; no invoca APIs directamente.",
                "- Regla: clima, correo y cámara deberán entrar como adapters.",
            )
        return self.last_snapshot.system_prompt_lines()

    def _effective_capabilities(self) -> dict[str, ToolCapability]:
        capabilities = dict(self._capabilities)
        if self.capability_registry is not None:
            for name, descriptor in self.capability_registry.capabilities.items():
                capabilities.setdefault(
                    name,
                    ToolCapability(**descriptor.to_tool_capability_kwargs()),
                )
        return capabilities

    def _register_descriptor_for(self, capability: ToolCapability) -> None:
        assert self.capability_registry is not None
        if self.capability_registry.get(capability.name) is not None:
            return
        descriptor = CapabilityDescriptor(
            name=capability.name,
            description=capability.description,
            risk=capability.risk_level,
            enabled=capability.enabled,
            requires_confirmation=capability.requires_confirmation,
            metadata=dict(capability.metadata),
        )
        self.capability_registry.register(descriptor)

    def _record_result(self, result: ToolResult) -> ToolResult:
        self._audit_log.append(result)
        if len(self._audit_log) > self.policy.max_audit_entries:
            del self._audit_log[0]
        return result
