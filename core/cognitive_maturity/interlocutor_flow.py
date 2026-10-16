from __future__ import annotations

from dataclasses import dataclass

from .interlocutor import InterlocutorResolution, InterlocutorResolutionStatus
from .interlocutor_interpreter import (
    ExplicitInterlocutorDeclarationInterpreter,
    InterlocutorDeclarationInterpretation,
    InterlocutorDeclarationKind,
)
from .interlocutor_session import ActiveInterlocutorSessionState


@dataclass(frozen=True)
class ConversationalIdentificationResult:
    handled: bool
    interpretation: InterlocutorDeclarationInterpretation
    resolution: InterlocutorResolution | None
    response_text: str | None
    grants_action_authority: bool = False

    def __post_init__(self) -> None:
        if self.handled:
            if self.resolution is None or not (self.response_text or "").strip():
                raise ValueError("handled identification requires result and response")
        elif self.resolution is not None or self.response_text is not None:
            raise ValueError("unhandled text cannot expose identification state")
        if self.grants_action_authority:
            raise ValueError("identification flow cannot grant action authority")


class ControlledConversationalIdentificationFlow:
    """Combine explicit interpretation and temporary session state."""

    def __init__(
        self,
        *,
        interpreter: ExplicitInterlocutorDeclarationInterpreter | None = None,
        state: ActiveInterlocutorSessionState | None = None,
    ) -> None:
        self._interpreter = (
            interpreter or ExplicitInterlocutorDeclarationInterpreter()
        )
        self._state = state or ActiveInterlocutorSessionState()

    @property
    def state(self) -> ActiveInterlocutorSessionState:
        return self._state

    def process(
        self,
        text: str,
        *,
        session_id: str,
    ) -> ConversationalIdentificationResult:
        interpretation = self._interpreter.interpret(
            text,
            session_id=session_id,
        )
        if not interpretation.matched or interpretation.request is None:
            return ConversationalIdentificationResult(
                handled=False,
                interpretation=interpretation,
                resolution=None,
                response_text=None,
            )
        resolution = self._state.apply(interpretation.request)
        return ConversationalIdentificationResult(
            handled=True,
            interpretation=interpretation,
            resolution=resolution,
            response_text=self._response(interpretation, resolution),
        )

    @staticmethod
    def _response(
        interpretation: InterlocutorDeclarationInterpretation,
        resolution: InterlocutorResolution,
    ) -> str:
        candidate = interpretation.candidate
        candidate_name = candidate.value if candidate is not None else ""
        if resolution.status is InterlocutorResolutionStatus.PENDING_CONFIRMATION:
            return (
                f"Entendí que sos {candidate_name}. Para confirmarlo, escribí "
                f"exactamente: Confirmo que soy {candidate_name}."
            )
        if resolution.status is InterlocutorResolutionStatus.CONFLICT:
            return (
                "La sesión tiene otro interlocutor confirmado. Para cambiar, "
                "escribí exactamente: Confirmo cambiar interlocutor a "
                f"{candidate_name}."
            )
        if resolution.status is InterlocutorResolutionStatus.REVOKED:
            return (
                "La identificación del interlocutor quedó revocada para esta "
                "sesión. El contexto privado permanece cerrado."
            )
        if resolution.status is InterlocutorResolutionStatus.RESOLVED:
            if interpretation.kind is InterlocutorDeclarationKind.REPLACEMENT:
                return (
                    f"Interlocutor cambiado a {candidate_name} para esta sesión. "
                    "La autoridad de Carlos y Cristina sigue siendo idéntica."
                )
            return (
                f"Identidad confirmada para esta sesión: {candidate_name}. "
                "El contexto privado queda limitado a esta sesión."
            )
        return (
            "La identificación no pudo resolverse; el contexto privado sigue "
            "cerrado."
        )
