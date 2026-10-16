from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from core.end_to_end_local_conversation import LocalConversationTurn


class AppliedOwnerTurnGateway(Protocol):
    def submit(self, text: str, **kwargs) -> LocalConversationTurn: ...


@dataclass(frozen=True)
class AppliedConversationalOwnerTurnResult:
    turn: LocalConversationTurn
    applied_result: object | None = None


@dataclass(frozen=True)
class AppliedConversationalIntelligenceOwnerTurnComposition:
    gateway: AppliedOwnerTurnGateway

    def submit(
        self,
        text: str,
        *,
        session_id: str | None = None,
        now: datetime | None = None,
        external_evidence: tuple[object, ...] = (),
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
    ) -> AppliedConversationalOwnerTurnResult:
        return compose_applied_conversational_owner_turn(
            gateway=self.gateway,
            text=text,
            session_id=session_id,
            now=now,
            external_evidence=external_evidence,
            explicit_document_ids=explicit_document_ids,
            explicit_sources=explicit_sources,
            explicit_evidence_references=explicit_evidence_references,
            integrated_visual_context=integrated_visual_context,
        )


def compose_applied_conversational_owner_turn(
    *,
    gateway: AppliedOwnerTurnGateway,
    text: str,
    session_id: str | None = None,
    now: datetime | None = None,
    external_evidence: tuple[object, ...] = (),
    explicit_document_ids: tuple[str, ...] = (),
    explicit_sources: tuple[object, ...] = (),
    explicit_evidence_references: tuple[object, ...] = (),
    integrated_visual_context: object | None = None,
) -> AppliedConversationalOwnerTurnResult:
    submit_kwargs = {
        "session_id": session_id,
        "now": now,
        "external_evidence": external_evidence,
        "explicit_document_ids": explicit_document_ids,
        "explicit_sources": explicit_sources,
        "explicit_evidence_references": explicit_evidence_references,
        "integrated_visual_context": integrated_visual_context,
    }
    turn = gateway.submit(text, **submit_kwargs)
    applied_result = getattr(
        gateway,
        "last_applied_owner_turn_result",
        None,
    )
    return AppliedConversationalOwnerTurnResult(
        turn=turn,
        applied_result=applied_result,
    )


