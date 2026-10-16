"""M377: preserve existing wrapper behavior while requiring per-call evidence."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.episodic_source_constraint import EpisodicSourceConstraintDesktopComposition
from app.same_turn_governed_visual_result_exposure import (
    SameTurnVisualUIAdapterComposition,
)
from app.ui_adapter import UIResponse


class _Delegate:
    def __init__(self, events: list[tuple]) -> None:
        self.events = events

    def submit_text(self, text: str, session_id=None, **kwargs) -> UIResponse:
        self.events.append(("text", text, session_id, kwargs))
        return UIResponse(text=text, status="success", session_id=session_id)

    def submit_voice(self, text: str, session_id=None) -> UIResponse:
        self.events.append(("voice", text, session_id))
        return UIResponse(text=text, status="success", session_id=session_id)


@pytest.mark.parametrize("route", ("text", "voice"))
def test_existing_episodic_observes_once_before_delegate(route: str) -> None:
    events: list[tuple] = []
    wrapper = EpisodicSourceConstraintDesktopComposition(
        conversation_adapter=_Delegate(events),
        observe_user_turn=lambda text, *, session_id=None: events.append(
            ("observe", text, session_id)
        ),
    )
    response = getattr(wrapper, f"submit_{route}")("mensaje", session_id="S1")
    assert response.text == "mensaje"
    assert events == [
        ("observe", "mensaje", "S1"),
        ("text", "mensaje", "S1", {}),
    ]


@pytest.mark.parametrize("explicit", (False, True))
def test_existing_visual_selects_exactly_one_adapter(explicit: bool) -> None:
    events: list[tuple] = []

    class _TaggedDelegate(_Delegate):
        def __init__(self, tag: str) -> None:
            self.tag = tag
            super().__init__(events)

        def submit_text(self, text, session_id=None, **kwargs):
            events.append((self.tag, text, session_id, kwargs))
            return UIResponse(text=self.tag, status="success", session_id=session_id)

    wrapper = SameTurnVisualUIAdapterComposition(
        _TaggedDelegate("protected"),
        gateway=SimpleNamespace(last_applied_owner_turn_result="visual"),
        explicit_context_adapter=_TaggedDelegate("explicit"),
    )
    kwargs = {"integrated_visual_context": object()} if explicit else {}
    response, applied = wrapper.submit_text_with_visual_companion(
        "mensaje", session_id="S1", **kwargs
    )
    assert response.text == ("explicit" if explicit else "protected")
    assert applied == "visual"
    assert len(events) == 1
    assert events[0][0] == ("explicit" if explicit else "protected")
    assert bool(events[0][3]) is explicit


def test_existing_visual_voice_does_not_take_explicit_context_route() -> None:
    events: list[tuple] = []
    wrapper = SameTurnVisualUIAdapterComposition(
        _Delegate(events),
        gateway=object(),
        explicit_context_adapter=_Delegate(events),
    )
    response = wrapper.submit_voice("audio", session_id="S2")
    assert response.text == "audio"
    assert events == [("voice", "audio", "S2")]


def test_red_episodic_per_call_keeps_observation_before_delegate() -> None:
    events: list[tuple] = []

    class _TurnDelegate(_Delegate):
        def submit_text_with_turn_evidence(self, text, session_id=None, **kwargs):
            events.append(("turn", text, session_id))
            return SimpleNamespace(response=UIResponse(
                text=text, status="success", session_id=session_id
            ), turn=object())

    wrapper = EpisodicSourceConstraintDesktopComposition(
        conversation_adapter=_TurnDelegate(events),
        observe_user_turn=lambda text, *, session_id=None: events.append(
            ("observe", text, session_id)
        ),
    )
    method = getattr(wrapper, "submit_text_with_turn_evidence", None)
    assert callable(method), "M377 RED: episodic per-call seam absent"
    result = method("mensaje", session_id="S1")
    assert result.turn is not None
    assert events == [("observe", "mensaje", "S1"), ("turn", "mensaje", "S1")]


def test_red_visual_per_call_preserves_explicit_target_selection() -> None:
    events: list[tuple] = []

    class _TurnDelegate(_Delegate):
        def __init__(self, tag: str) -> None:
            super().__init__(events)
            self.tag = tag

        def submit_text_with_turn_evidence(self, text, session_id=None, **kwargs):
            events.append((self.tag, text, session_id, kwargs))
            return SimpleNamespace(
                response=UIResponse(text=self.tag, status="success"),
                turn=object(),
            )

    wrapper = SameTurnVisualUIAdapterComposition(
        _TurnDelegate("protected"),
        gateway=object(),
        explicit_context_adapter=_TurnDelegate("explicit"),
    )
    method = getattr(
        wrapper, "submit_text_with_visual_companion_and_turn_evidence", None
    )
    assert callable(method), "M377 RED: correlated visual seam absent"
    result = method("mensaje", session_id="S1", integrated_visual_context=object())
    assert result is not None
    assert len(events) == 1
    assert events[0][0] == "explicit"
