from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.ui_adapter import UIResponse
from core.end_to_end_local_conversation import LocalConversationTurn


class SameTurnAppliedExecution(Protocol):
    def __call__(
        self,
        text: str,
        session_id: str | None = None,
    ) -> object | None: ...


class FallbackTurnExecution(Protocol):
    def __call__(
        self,
        text: str,
        session_id: str | None = None,
    ) -> LocalConversationTurn: ...


@dataclass(frozen=True)
class SameTurnGovernedVisualResult:
    turn: LocalConversationTurn
    applied_result: object | None = None


def expose_same_turn_governed_visual_result(
    *,
    execute_applied: SameTurnAppliedExecution,
    execute_fallback: FallbackTurnExecution,
    text: str,
    session_id: str | None = None,
) -> SameTurnGovernedVisualResult:
    applied_execution = execute_applied(text, session_id=session_id)
    if applied_execution is not None:
        return SameTurnGovernedVisualResult(
            turn=getattr(applied_execution, "turn"),
            applied_result=getattr(applied_execution, "applied_result"),
        )
    return SameTurnGovernedVisualResult(
        turn=execute_fallback(text, session_id=session_id),
    )


class SameTurnVisualRuntimeComposition:
    def __init__(
        self,
        *,
        execute_applied: SameTurnAppliedExecution,
        execute_fallback: FallbackTurnExecution,
    ) -> None:
        self._execute_applied = execute_applied
        self._execute_fallback = execute_fallback

    def process_with_visual_result(
        self,
        text: str,
        session_id: str | None = None,
    ) -> SameTurnGovernedVisualResult:
        return expose_same_turn_governed_visual_result(
            execute_applied=self._execute_applied,
            execute_fallback=self._execute_fallback,
            text=text,
            session_id=session_id,
        )


@dataclass(frozen=True)
class SameTurnVisualUIEvidence:
    response: UIResponse
    turn: LocalConversationTurn | None
    applied_result: object | None = None


class SameTurnVisualUIAdapterComposition:
    def __init__(
        self,
        conversation_adapter: object,
        *,
        gateway: object,
        explicit_context_adapter: object | None = None,
    ) -> None:
        self._conversation_adapter = conversation_adapter
        self._gateway = gateway
        self._explicit_context_adapter = (
            explicit_context_adapter or conversation_adapter
        )

    @property
    def diagnostics(self) -> object | None:
        return getattr(self._conversation_adapter, "diagnostics", None)

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
        **kwargs,
    ) -> UIResponse:
        return self._conversation_adapter.submit_text(
            text,
            session_id=session_id,
            **kwargs,
        )

    def submit_text_with_visual_companion(
        self,
        text: str,
        session_id: str | None = None,
        *,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
    ) -> tuple[UIResponse, object | None]:
        has_explicit_context = bool(
            explicit_document_ids
            or explicit_sources
            or explicit_evidence_references
            or integrated_visual_context is not None
        )
        target = (
            self._explicit_context_adapter
            if has_explicit_context
            else self._conversation_adapter
        )
        kwargs = {}
        if has_explicit_context:
            kwargs = {
                "explicit_document_ids": explicit_document_ids,
                "explicit_sources": explicit_sources,
                "explicit_evidence_references": explicit_evidence_references,
                "integrated_visual_context": integrated_visual_context,
            }
        response = target.submit_text(
            text,
            session_id=session_id,
            **kwargs,
        )
        applied_result = getattr(
            self._gateway,
            "last_applied_owner_turn_result",
            None,
        )
        return response, applied_result

    def submit_text_with_visual_companion_and_turn_evidence(
        self,
        text: str,
        session_id: str | None = None,
        *,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
    ) -> SameTurnVisualUIEvidence:
        has_explicit_context = bool(
            explicit_document_ids
            or explicit_sources
            or explicit_evidence_references
            or integrated_visual_context is not None
        )
        target = (
            self._explicit_context_adapter
            if has_explicit_context
            else self._conversation_adapter
        )
        kwargs = {}
        if has_explicit_context:
            kwargs = {
                "explicit_document_ids": explicit_document_ids,
                "explicit_sources": explicit_sources,
                "explicit_evidence_references": explicit_evidence_references,
                "integrated_visual_context": integrated_visual_context,
            }

        submit_causal = getattr(
            target, "submit_text_with_turn_evidence", None
        )
        if not callable(submit_causal):
            raise NotImplementedError(
                "Selected adapter has no per-call causal evidence interface"
            )

        result = submit_causal(
            text,
            session_id=session_id,
            **kwargs,
        )
        return SameTurnVisualUIEvidence(
            response=result.response,
            turn=result.turn,
            applied_result=getattr(result, "applied_result", None),
        )

    def submit_voice(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        return self._conversation_adapter.submit_voice(
            text,
            session_id=session_id,
        )

    def submit_text_with_turn_evidence(
        self,
        text: str,
        session_id: str | None = None,
        **kwargs,
    ) -> TurnBoundUIResult:
        from app.runtime_ui_adapter import TurnBoundUIResult

        result = self._conversation_adapter.submit_text_with_turn_evidence(
            text,
            session_id=session_id,
            **kwargs,
        )
        return TurnBoundUIResult(
            response=result.response,
            turn=result.turn,
            applied_result=getattr(result, "applied_result", None),
        )

    def submit_voice_with_turn_evidence(
        self,
        text: str,
        session_id: str | None = None,
    ) -> TurnBoundUIResult:
        from app.runtime_ui_adapter import TurnBoundUIResult

        result = self._conversation_adapter.submit_voice_with_turn_evidence(
            text,
            session_id=session_id,
        )
        return TurnBoundUIResult(
            response=result.response,
            turn=result.turn,
            applied_result=getattr(result, "applied_result", None),
        )
