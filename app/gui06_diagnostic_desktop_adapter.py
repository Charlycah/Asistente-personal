"""Temporary, opt-in GUI-06 desktop diagnostic boundary.

Delegates without altering requests or responses.
Does not enable diagnostics, persist data, or call providers independently.
"""

from __future__ import annotations

from typing import Any

from core.gui06_diagnostic_probe import (
    capture_diagnostic_stage,
    diagnostic_recorder,
    diagnostic_turn_context,
)


def _observe_gui06_response(stage: str, response: Any) -> Any:
    """Observe opportunistically without changing the returned response."""
    try:
        capture_diagnostic_stage(
            stage,
            text=getattr(response, "text", ""),
        )
    except Exception:
        pass
    return response


class GUI06DiagnosticDesktopAdapter:
    """Preserve desktop entry points while correlating diagnostic stages."""

    def __init__(self, adapter: object) -> None:
        self._adapter = adapter

    @property
    def diagnostics(self) -> object | None:
        return getattr(self._adapter, "diagnostics", None)

    @property
    def supports_same_turn_visual_evidence(self) -> bool:
        return callable(
            getattr(
                self._adapter,
                "submit_text_with_visual_companion_and_turn_evidence",
                None,
            )
        )

    def _invoke(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        method = getattr(self._adapter, method_name)
        recorder = diagnostic_recorder()

        if not recorder.enabled:
            return method(*args, **kwargs)

        try:
            turn_id = recorder.begin_turn()
        except Exception:
            return method(*args, **kwargs)

        with diagnostic_turn_context(turn_id):
            result = method(*args, **kwargs)
            if (
                method_name == "submit_text_with_visual_companion"
                and isinstance(result, tuple)
                and result
            ):
                response = result[0]
            elif method_name == (
                "submit_text_with_visual_companion_and_turn_evidence"
            ):
                response = result.response
            else:
                response = result
            _observe_gui06_response("P5b", response)
            return result

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return self._invoke(
            "submit_text",
            text,
            session_id=session_id,
            **kwargs,
        )

    def submit_text_with_visual_companion(
        self,
        text: str,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return self._invoke(
            "submit_text_with_visual_companion",
            text,
            session_id=session_id,
            **kwargs,
        )

    def submit_text_with_visual_companion_and_turn_evidence(
        self,
        text: str,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return self._invoke(
            "submit_text_with_visual_companion_and_turn_evidence",
            text,
            session_id=session_id,
            **kwargs,
        )

    def submit_voice(
        self,
        text: str,
        session_id: str | None = None,
    ) -> Any:
        return self._invoke(
            "submit_voice",
            text,
            session_id=session_id,
        )


class GUI06DiagnosticLocalAdapter:
    """Observe local UI responses without modifying the protected adapter."""

    def __init__(self, adapter: object) -> None:
        self._adapter = adapter

    @property
    def runtime(self) -> object:
        return self._adapter.runtime

    @property
    def diagnostics(self) -> object | None:
        return getattr(self._adapter, "diagnostics", None)

    @staticmethod
    def _observe(response: Any) -> Any:
        return _observe_gui06_response("P5a", response)

    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        response = self._adapter.submit_text(
            text,
            session_id=session_id,
            **kwargs,
        )
        return self._observe(response)

    def submit_text_with_turn_evidence(
        self,
        text: str,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        result = self._adapter.submit_text_with_turn_evidence(
            text,
            session_id=session_id,
            **kwargs,
        )
        self._observe(result.response)
        return result


    def submit_voice(
        self,
        text: str,
        session_id: str | None = None,
    ) -> Any:
        response = self._adapter.submit_voice(
            text,
            session_id=session_id,
        )
        return self._observe(response)