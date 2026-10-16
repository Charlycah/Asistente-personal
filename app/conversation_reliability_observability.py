from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from threading import RLock
from time import perf_counter

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedConversationPipelineResult,
    GovernedOperationalInterception,
    build_governed_conversation_turn_identity,
)


@dataclass(frozen=True)
class ConversationRuntimeSpan:
    name: str
    status: str
    duration_ms: float
    span_id: str


@dataclass(frozen=True)
class ConversationReliabilityTrace:
    owner: str
    session_id: str
    conversation_id: str
    turn_id: str
    request_id: str
    trace_id: str
    status: str
    spans: tuple[ConversationRuntimeSpan, ...]
    provider_call_performed: bool = False
    retrieval_performed: bool = False
    network_access_performed: bool = False
    platform_mutation_performed: bool = False
    error: str | None = None


@dataclass(frozen=True)
class ConversationRuntimeHealth:
    evaluations: int
    completed: int
    degraded: int
    failed: int
    last_status: str | None
    last_trace_id: str | None
    availability: str


class OfficialConversationReliabilityObservabilityGateway:
    """Correlates, observes and safely contains the official conversation flow."""

    def __init__(self, conversation_runtime) -> None:
        self.conversation_runtime = conversation_runtime
        self._lock = RLock()
        self._traces: dict[tuple[str, str], list[ConversationReliabilityTrace]] = {}
        self._pending: dict[tuple[str, str], ConversationReliabilityTrace] = {}
        self._evaluations = 0
        self._completed = 0
        self._degraded = 0
        self._failed = 0
        self._last_status: str | None = None
        self._last_trace_id: str | None = None

    @property
    def health(self) -> ConversationRuntimeHealth:
        with self._lock:
            return ConversationRuntimeHealth(
                evaluations=self._evaluations,
                completed=self._completed,
                degraded=self._degraded,
                failed=self._failed,
                last_status=self._last_status,
                last_trace_id=self._last_trace_id,
                availability="available" if self._failed == 0 else "degraded",
            )

    def traces_for(
        self, owner: str, session_id: str
    ) -> tuple[ConversationReliabilityTrace, ...]:
        key = (owner.strip().casefold(), session_id.strip())
        with self._lock:
            return tuple(self._traces.get(key, ()))

    def evaluate_turn(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ):
        key = (request.owner.casefold(), request.session_id)
        identity = self._identity(request, now)
        started = perf_counter()
        try:
            result = self.conversation_runtime.evaluate_turn(request, now=now)
            elapsed = (perf_counter() - started) * 1000
            spans = self._conversation_spans(identity["trace_id"], result, elapsed)
            trace = ConversationReliabilityTrace(
                owner=request.owner,
                session_id=request.session_id,
                conversation_id=identity["conversation_id"],
                turn_id=identity["turn_id"],
                request_id=identity["request_id"],
                trace_id=identity["trace_id"],
                status="started",
                spans=spans,
            )
            with self._lock:
                self._evaluations += 1
                self._pending[key] = trace
                self._last_status = trace.status
                self._last_trace_id = trace.trace_id
            return result
        except Exception as exc:
            elapsed = (perf_counter() - started) * 1000
            trace = ConversationReliabilityTrace(
                owner=request.owner,
                session_id=request.session_id,
                conversation_id=identity["conversation_id"],
                turn_id=identity["turn_id"],
                request_id=identity["request_id"],
                trace_id=identity["trace_id"],
                status="degraded",
                spans=(
                    self._span(
                        identity["trace_id"],
                        "conversation_execution",
                        "failed",
                        elapsed,
                    ),
                ),
                error=type(exc).__name__,
            )
            with self._lock:
                self._evaluations += 1
                self._degraded += 1
                self._pending[key] = trace
                self._last_status = trace.status
                self._last_trace_id = trace.trace_id
            return None

    def record_failure(
        self, request: GovernedConversationPipelineRequest, exc: Exception
    ) -> None:
        """Retain only the exception class in the existing pending official trace."""
        from dataclasses import replace

        key = (request.owner.casefold(), request.session_id)
        with self._lock:
            pending = self._pending.get(key)
            if pending is not None:
                self._pending[key] = replace(pending, error=type(exc).__name__)

    def complete_turn(
        self,
        result: GovernedConversationPipelineResult,
        *,
        now: datetime,
    ) -> ConversationReliabilityTrace:
        del now
        key = (result.request.owner.casefold(), result.request.session_id)
        with self._lock:
            pending = self._pending.pop(key, None)
        if pending is None:
            identity = self._identity(result.request, result.created_at)
            pending = ConversationReliabilityTrace(
                owner=result.request.owner,
                session_id=result.request.session_id,
                conversation_id=identity["conversation_id"],
                turn_id=identity["turn_id"],
                request_id=identity["request_id"],
                trace_id=identity["trace_id"],
                status="started",
                spans=(),
            )
        status = (
            "completed" if result.status.value == "completed" else result.status.value
        )
        spans = pending.spans + (
            self._span(
                pending.trace_id,
                "provider",
                "completed" if result.provider_call_performed else "skipped",
                0.0,
            ),
            self._span(
                pending.trace_id,
                "retrieval",
                "completed" if result.retrieval_performed else "skipped",
                0.0,
            ),
            self._span(pending.trace_id, "response_assembly", "completed", 0.0),
        )
        trace = ConversationReliabilityTrace(
            owner=pending.owner,
            session_id=pending.session_id,
            conversation_id=pending.conversation_id,
            turn_id=pending.turn_id,
            request_id=pending.request_id,
            trace_id=pending.trace_id,
            status=status,
            spans=spans,
            provider_call_performed=result.provider_call_performed,
            retrieval_performed=result.retrieval_performed,
            network_access_performed=result.network_access_performed,
            platform_mutation_performed=result.platform_mutation_performed,
            error=pending.error,
        )
        with self._lock:
            self._traces.setdefault(key, []).append(trace)
            if status == "completed":
                self._completed += 1
            elif status == "failed":
                self._failed += 1
            else:
                self._degraded += 1
            self._last_status = status
            self._last_trace_id = trace.trace_id
        return trace

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        normalized = request.text.strip().casefold()
        if normalized in {
            "estado de confiabilidad conversacional",
            "estado de observabilidad conversacional",
        }:
            health = self.health
            return GovernedOperationalInterception(
                response_text="\n".join(
                    (
                        "Estado de confiabilidad y observabilidad:",
                        f"- Evaluaciones: {health.evaluations}",
                        f"- Completadas: {health.completed}",
                        f"- Degradadas: {health.degraded}",
                        f"- Fallidas: {health.failed}",
                        f"- Disponibilidad: {health.availability}",
                    )
                ),
                rationale="conversation_reliability_status_completed",
            )
        if normalized in {
            "audita confiabilidad conversacional",
            "audita observabilidad conversacional",
        }:
            traces = self.traces_for(request.owner, request.session_id)
            return GovernedOperationalInterception(
                response_text="\n".join(
                    (
                        "Auditoría de confiabilidad y observabilidad:",
                        f"- Trazas de sesión: {len(traces)}",
                        "- Correlación: conversación, turno, solicitud, traza y spans.",
                        "- Fallos: contenidos mediante degradación segura.",
                        "- Hardware, red y mutaciones: nunca implícitos.",
                    )
                ),
                rationale="conversation_reliability_audit_completed",
            )
        return None

    @staticmethod
    def _identity(
        request: GovernedConversationPipelineRequest, now: datetime
    ) -> dict[str, str]:
        identity = build_governed_conversation_turn_identity(request, now)
        return {
            "conversation_id": identity.conversation_id,
            "request_id": identity.request_id,
            "turn_id": identity.turn_id,
            "trace_id": identity.trace_id,
        }

    def _conversation_spans(self, trace_id: str, result, duration_ms: float):
        names = ("entry", "context", "intelligence")
        if result.reasoning_status is not None:
            names += ("reasoning", "cognition")
        share = duration_ms / len(names) if names else 0.0
        return tuple(self._span(trace_id, name, "completed", share) for name in names)

    @staticmethod
    def _span(trace_id: str, name: str, status: str, duration_ms: float):
        span_id = sha256(f"{trace_id}|{name}|{status}".encode()).hexdigest()
        return ConversationRuntimeSpan(
            name=name,
            status=status,
            duration_ms=max(0.0, duration_ms),
            span_id=span_id,
        )
