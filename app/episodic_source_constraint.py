from __future__ import annotations

from collections.abc import Callable

from app.ui_adapter import UIResponse


class EpisodicSourceConstraintProjection:
    """Project the canonical source assessment for the current user turn."""

    def __init__(
        self,
        *,
        external_source_allowance: Callable[[str], bool],
    ) -> None:
        self._external_source_allowance = external_source_allowance
        self._external_allowed = True

    def observe_user_turn(self, text: str, *, session_id: str | None = None) -> None:
        del session_id
        self._external_allowed = bool(self._external_source_allowance(text))

    def allows_external_sources(self) -> bool:
        return self._external_allowed


class EpisodicSourceConstraintDesktopComposition:
    """Observe each user turn before delegating to the existing desktop adapter."""

    def __init__(
        self,
        *,
        conversation_adapter: object,
        observe_user_turn: Callable[..., None],
    ) -> None:
        submit_text = getattr(conversation_adapter, "submit_text", None)
        if not callable(submit_text):
            raise TypeError("conversation_adapter must expose submit_text")
        self._conversation_adapter = conversation_adapter
        self._observe_user_turn = observe_user_turn

    @property
    def diagnostics(self) -> object | None:
        return getattr(self._conversation_adapter, "diagnostics", None)

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        self._observe_user_turn(text, session_id=session_id)
        return self._conversation_adapter.submit_text(text, session_id=session_id)

    def submit_voice(
        self,
        text: str,
        session_id: str | None = None,
    ) -> UIResponse:
        return self.submit_text(text, session_id=session_id)
