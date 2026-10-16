from dataclasses import dataclass
from typing import Protocol

from domain.response import ResponseStatus, UserResponse


class ROBYClient(Protocol):
    def process(self, text: str, session_id: str | None = None) -> UserResponse: ...


@dataclass(frozen=True)
class UIResponse:
    text: str
    status: str
    session_id: str | None = None
    needs_input: bool = False


class ROBYUIAdapter:
    def __init__(self, roby: ROBYClient) -> None:
        self.roby = roby

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        normalized_text = text.strip()

        if not normalized_text:
            return UIResponse(
                text="Necesito que escribas un mensaje para continuar.",
                status=ResponseStatus.NEEDS_INFORMATION.value,
                session_id=session_id,
                needs_input=True,
            )

        try:
            response = self.roby.process(normalized_text, session_id=session_id)
        except Exception:
            return UIResponse(
                text="Ocurrió un error al procesar tu mensaje.",
                status=ResponseStatus.FAILURE.value,
                session_id=session_id,
                needs_input=False,
            )

        return UIResponse(
            text=response.text,
            status=response.status.value,
            session_id=session_id,
            needs_input=response.status == ResponseStatus.NEEDS_INFORMATION,
        )
