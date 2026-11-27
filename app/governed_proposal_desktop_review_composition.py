from __future__ import annotations

from app.governed_presented_proposal_review_transport import (
    GovernedPresentedProposalReviewTransport,
)
from app.ui_adapter import UIResponse
from app.runtime_ui_adapter import TurnBoundUIResult
from domain.governed_proposal import ProposalState
from domain.response import ResponseStatus


class GovernedProposalDesktopReviewComposition:
    """Compose certified proposal review ahead of the protected desktop adapter.

    This boundary owns no proposal state or review semantics. It delegates exact
    presented-proposal review to S1-B and falls through unchanged when S1-B does
    not produce a terminal disposition.
    """

    def __init__(
        self,
        *,
        proposal_review_transport: GovernedPresentedProposalReviewTransport,
        conversation_adapter: object,
    ) -> None:
        if not isinstance(
            proposal_review_transport,
            GovernedPresentedProposalReviewTransport,
        ):
            raise TypeError(
                "proposal_review_transport must be a "
                "GovernedPresentedProposalReviewTransport instance"
            )
        submit_text = getattr(conversation_adapter, "submit_text", None)
        if not callable(submit_text):
            raise TypeError("conversation_adapter must expose submit_text")
        self._proposal_review_transport = proposal_review_transport
        self._conversation_adapter = conversation_adapter

    @property
    def diagnostics(self) -> object | None:
        return getattr(self._conversation_adapter, "diagnostics", None)

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        reviewed = self._proposal_review_transport.review_presented_proposal(
            response=text,
        )
        if reviewed is None:
            return self._conversation_adapter.submit_text(
                text,
                session_id=session_id,
            )
        if reviewed.state is ProposalState.ACCEPTED:
            response_text = "Propuesta aceptada. No se ejecutó ninguna acción."
        else:
            response_text = "Propuesta descartada."
        return UIResponse(
            text=response_text,
            status=ResponseStatus.SUCCESS.value,
            session_id=session_id,
            needs_input=False,
        )

    def submit_voice(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        return self.submit_text(text, session_id=session_id)

    def submit_text_with_turn_evidence(
        self,
        text: str,
        session_id: str | None = None,
    ) -> TurnBoundUIResult:
        reviewed = self._proposal_review_transport.review_presented_proposal(
            response=text,
        )
        if reviewed is None:
            result = self._conversation_adapter.submit_text_with_turn_evidence(
                text,
                session_id=session_id,
            )
            return TurnBoundUIResult(
                response=result.response,
                turn=result.turn,
                applied_result=getattr(result, "applied_result", None),
            )

        if reviewed.state is ProposalState.ACCEPTED:
            response_text = "Propuesta aceptada. No se ejecut? ninguna acci?n."
        else:
            response_text = "Propuesta descartada."

        return TurnBoundUIResult(
            response=UIResponse(
                text=response_text,
                status=ResponseStatus.SUCCESS.value,
                session_id=session_id,
                needs_input=False,
            ),
            turn=None,
            applied_result=None,
        )

    def submit_voice_with_turn_evidence(
        self,
        text: str,
        session_id: str | None = None,
    ) -> TurnBoundUIResult:
        return self.submit_text_with_turn_evidence(
            text,
            session_id=session_id,
        )
