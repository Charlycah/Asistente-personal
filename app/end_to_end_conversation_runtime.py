from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.cognitive_maturity import IntentReasoningEvidenceAdapter
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
    build_governed_conversation_turn_identity,
)
from core.llm_provider import LLMRequest


@dataclass(frozen=True)
class EndToEndConversationRuntimeSnapshot:
    turns: int
    last_owner: str | None
    last_session_id: str | None
    last_entry_kind: str | None
    last_entry_action: str | None
    context_applied: bool
    intelligence_state: str | None
    intelligence_action: str | None
    reasoning_status: str | None
    cognition_status: str | None
    productive_intake_observed: bool
    productive_intake_status: str | None
    integrated_runtimes: int


@dataclass(frozen=True)
class EndToEndConversationRuntimeResult:
    entry_kind: str
    entry_action: str
    context_applied: bool
    intelligence_state: str
    intelligence_action: str
    reasoning_status: str | None
    cognition_status: str | None
    productive_intake_observed: bool
    productive_intake_status: str | None


class OfficialEndToEndConversationRuntimeGateway:
    """Final observable coordinator over ROBY's certified M257-M263 runtimes."""

    _STATUS_TRIGGERS = (
        "estado del runtime conversacional end to end",
        "estado del runtime conversacional de extremo a extremo",
        "estado end to end conversacional",
    )
    _AUDIT_TRIGGERS = (
        "auditá runtime conversacional end to end",
        "audita runtime conversacional end to end",
        "auditá conversación de extremo a extremo",
        "audita conversacion de extremo a extremo",
    )

    def __init__(
        self,
        *,
        entry_runtime,
        context_runtime,
        device_runtime,
        retrieval_runtime,
        reasoning_runtime,
        cognition_runtime,
        intelligence_runtime,
    ) -> None:
        self.entry_runtime = entry_runtime
        self.context_runtime = context_runtime
        self.device_runtime = device_runtime
        self.retrieval_runtime = retrieval_runtime
        self.reasoning_runtime = reasoning_runtime
        self.cognition_runtime = cognition_runtime
        self.intelligence_runtime = intelligence_runtime
        self._turns = 0
        self._last_result: EndToEndConversationRuntimeResult | None = None
        self._last_owner: str | None = None
        self._last_session_id: str | None = None

    @property
    def snapshot(self) -> EndToEndConversationRuntimeSnapshot:
        result = self._last_result
        return EndToEndConversationRuntimeSnapshot(
            turns=self._turns,
            last_owner=self._last_owner,
            last_session_id=self._last_session_id,
            last_entry_kind=result.entry_kind if result else None,
            last_entry_action=result.entry_action if result else None,
            context_applied=result.context_applied if result else False,
            intelligence_state=result.intelligence_state if result else None,
            intelligence_action=result.intelligence_action if result else None,
            reasoning_status=result.reasoning_status if result else None,
            cognition_status=result.cognition_status if result else None,
            productive_intake_observed=(
                result.productive_intake_observed if result else False
            ),
            productive_intake_status=(
                result.productive_intake_status if result else None
            ),
            integrated_runtimes=7,
        )

    def evaluate_turn(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> EndToEndConversationRuntimeResult:
        entry = self.entry_runtime.evaluate_text(request.text)
        entry_kind = entry.kind
        entry_action = entry.action

        intake_observer = getattr(
            self.reasoning_runtime,
            "observe_productive_temporary_rule_intake",
            None,
        )
        productive_intake_observed = callable(intake_observer)
        productive_intake_status = None
        if productive_intake_observed:
            intake = intake_observer(
                owner=request.owner,
                text=request.text,
                scope_reference=request.session_id,
                now=now,
            )
            productive_intake_status = intake.status.value

        enriched = self.context_runtime.enrich(
            conversation=request,
            inference_request=LLMRequest(prompt=request.text),
        )
        intelligence = self.intelligence_runtime.evaluate_text(
            owner=request.owner,
            session_id=request.session_id,
            text=enriched.prompt,
            now=now,
        )

        reasoning_status = None
        cognition_status = None
        if entry_action == "route_to_reasoning":
            turn_identity = build_governed_conversation_turn_identity(request, now)
            cognition = self.cognition_runtime.evaluate_text(
                owner=request.owner,
                text=enriched.prompt,
                now=now,
                scope_reference=request.session_id,
                observe_productive_intake=False,
                productive_turn_id=turn_identity.turn_id,
            )
            reasoning_status = self.cognition_runtime.snapshot.last_reasoning_status
            cognition_status = (
                "review_required" if cognition.requires_review else "completed"
            )

        result = EndToEndConversationRuntimeResult(
            entry_kind=entry_kind,
            entry_action=entry_action,
            context_applied=enriched.prompt != request.text,
            intelligence_state=intelligence.operational.state.value,
            intelligence_action=intelligence.operational.action.value,
            reasoning_status=reasoning_status,
            cognition_status=cognition_status,
            productive_intake_observed=productive_intake_observed,
            productive_intake_status=productive_intake_status,
        )
        IntentReasoningEvidenceAdapter().observe(
            intent_kind=entry_kind,
            intent_action=entry_action,
            reasoning_status=reasoning_status,
        )
        self._turns += 1
        self._last_result = result
        self._last_owner = request.owner
        self._last_session_id = request.session_id
        return result

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._STATUS_TRIGGERS):
            return GovernedOperationalInterception(
                response_text=self._status_response(),
                rationale="official_end_to_end_conversation_status_completed",
            )
        if any(trigger in normalized for trigger in self._AUDIT_TRIGGERS):
            return GovernedOperationalInterception(
                response_text="\n".join(
                    (
                        "Auditoría del End-to-End Conversation Runtime:",
                        "- Entrada: clasificación determinística.",
                        "- Continuidad: contexto sanitizado y acotado por sesión.",
                        "- Dispositivos y conducción: gobernados, no implícitos.",
                        "- Recuperación externa: solo mediante clientes registrados.",
                        "- Razonamiento: trazable y abstencionista.",
                        "- Cognición: adaptativa, consultiva y no ejecutiva.",
                        (
                            "- Inteligencia conversacional: reparación y "
                            "grounding prioritarios."
                        ),
                        (
                            "- Proveedores, red y mutaciones: no ejecutados "
                            "por la auditoría."
                        ),
                    )
                ),
                rationale="official_end_to_end_conversation_audit_completed",
            )
        return None

    def _status_response(self) -> str:
        snapshot = self.snapshot
        return "\n".join(
            (
                "Estado del End-to-End Conversation Runtime:",
                f"- Turnos evaluados: {snapshot.turns}",
                f"- Runtimes integrados: {snapshot.integrated_runtimes}",
                f"- Última entrada: {snapshot.last_entry_kind or 'ninguna'}",
                f"- Última ruta: {snapshot.last_entry_action or 'ninguna'}",
                f"- Continuidad aplicada: {'sí' if snapshot.context_applied else 'no'}",
                f"- Inteligencia: {snapshot.intelligence_state or 'sin evaluación'}",
                "- Modo: gobernado, observable y no ejecutivo.",
            )
        )
