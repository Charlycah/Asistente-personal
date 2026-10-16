"""M377 S3: preserve governed review and isolate per-call concurrent turns."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Event
from types import MethodType, SimpleNamespace

import pytest

from app.governed_presented_proposal_review_transport import (
    GovernedPresentedProposalReviewTransport,
)
from app.governed_proposal_desktop_review_composition import (
    GovernedProposalDesktopReviewComposition,
)
from app.ui_adapter import UIResponse
from domain.governed_proposal import ProposalState


class _Delegate:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    def submit_text(self, text: str, session_id: str | None = None) -> UIResponse:
        self.calls.append((text, session_id))
        return UIResponse(text=text, status="success", session_id=session_id)

    def submit_voice(self, text: str, session_id: str | None = None) -> UIResponse:
        return self.submit_text(text, session_id=session_id)

    def submit_text_with_turn_evidence(
        self, text: str, session_id: str | None = None
    ) -> SimpleNamespace:
        self.calls.append((text, session_id))
        return SimpleNamespace(
            response=UIResponse(text=text, status="success", session_id=session_id),
            turn=SimpleNamespace(session_id=session_id, marker=text),
        )

    def submit_voice_with_turn_evidence(
        self, text: str, session_id: str | None = None
    ) -> SimpleNamespace:
        return self.submit_text_with_turn_evidence(text, session_id=session_id)


def _wrapper(reviewed: object | None, delegate: _Delegate):
    transport = object.__new__(GovernedPresentedProposalReviewTransport)
    observations: list[str] = []

    def review(self, *, response: str):
        observations.append(response)
        return reviewed

    transport.review_presented_proposal = MethodType(review, transport)
    wrapper = GovernedProposalDesktopReviewComposition(
        proposal_review_transport=transport, conversation_adapter=delegate
    )
    return wrapper, observations


@pytest.mark.parametrize("route", ("text", "voice"))
@pytest.mark.parametrize("state", (ProposalState.ACCEPTED, ProposalState.DISMISSED))
def test_existing_terminal_review_does_not_delegate(route: str, state) -> None:
    delegate = _Delegate()
    wrapper, reviews = _wrapper(SimpleNamespace(state=state), delegate)
    response = getattr(wrapper, f"submit_{route}")("acepto", session_id="P1")
    assert response.status == "success"
    assert response.session_id == "P1"
    assert response.needs_input is False
    assert delegate.calls == []
    assert reviews == ["acepto"]


@pytest.mark.parametrize("route", ("text", "voice"))
def test_existing_unresolved_review_delegates_once(route: str) -> None:
    delegate = _Delegate()
    wrapper, reviews = _wrapper(None, delegate)
    response = getattr(wrapper, f"submit_{route}")("consulta", session_id="P2")
    assert response.text == "consulta"
    assert reviews == ["consulta"]
    assert delegate.calls == [("consulta", "P2")]


@pytest.mark.parametrize("route", ("text", "voice"))
@pytest.mark.parametrize("state", (ProposalState.ACCEPTED, ProposalState.DISMISSED))
def test_red_terminal_review_per_call_has_no_turn(route: str, state) -> None:
    delegate = _Delegate()
    wrapper, reviews = _wrapper(SimpleNamespace(state=state), delegate)
    method = getattr(wrapper, f"submit_{route}_with_turn_evidence", None)
    assert callable(method), "M377 S3 RED: proposal per-call seam absent"
    result = method("acepto", session_id="P1")
    assert result.turn is None
    assert result.response.session_id == "P1"
    assert result.response.needs_input is False
    assert delegate.calls == []
    assert reviews == ["acepto"]


@pytest.mark.parametrize("route", ("text", "voice"))
def test_red_unresolved_review_per_call_delegates_once(route: str) -> None:
    delegate = _Delegate()
    wrapper, reviews = _wrapper(None, delegate)
    method = getattr(wrapper, f"submit_{route}_with_turn_evidence", None)
    assert callable(method), "M377 S3 RED: proposal per-call seam absent"
    result = method("consulta", session_id="P2")
    assert result.turn.session_id == "P2"
    assert result.response.text == "consulta"
    assert reviews == ["consulta"]
    assert delegate.calls == [("consulta", "P2")]


@pytest.mark.parametrize("route", ("text", "voice"))
def test_red_reverse_completion_preserves_each_turn(route: str) -> None:
    started = Event()
    second_finished = Event()

    class _ReverseDelegate(_Delegate):
        def submit_text_with_turn_evidence(
            self, text: str, session_id: str | None = None
        ) -> SimpleNamespace:
            if session_id == "S1":
                started.set()
                assert second_finished.wait(timeout=5), "S2 did not complete"
            result = super().submit_text_with_turn_evidence(text, session_id)
            if session_id == "S2":
                second_finished.set()
            return result

    delegate = _ReverseDelegate()
    wrapper, reviews = _wrapper(None, delegate)
    method = getattr(wrapper, f"submit_{route}_with_turn_evidence", None)
    assert callable(method), "M377 S3 RED: concurrent per-call seam absent"
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(method, "primera", session_id="S1")
        assert started.wait(timeout=5), "S1 did not enter delegate"
        second = pool.submit(method, "segunda", session_id="S2")
        result2 = second.result(timeout=8)
        result1 = first.result(timeout=8)
    assert result1.response.text == "primera"
    assert result1.turn.session_id == "S1"
    assert result1.turn.marker == "primera"
    assert result2.response.text == "segunda"
    assert result2.turn.session_id == "S2"
    assert result2.turn.marker == "segunda"
    assert sorted(reviews) == ["primera", "segunda"]
    assert sorted(delegate.calls) == [("primera", "S1"), ("segunda", "S2")]
