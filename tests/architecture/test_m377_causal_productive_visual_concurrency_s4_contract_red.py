"""M377 S4: causal per-call transport and visual concurrent isolation RED."""

from __future__ import annotations

import ast
import inspect
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from types import SimpleNamespace

import pytest

from app.runtime_ui_adapter import LocalConversationUIAdapter
from app.same_turn_governed_visual_result_exposure import (
    SameTurnVisualUIAdapterComposition,
)
from app.ui_adapter import UIResponse


class _Gateway:
    last_applied_owner_turn_result = "stale-other-session"


class _VisualDelegate:
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: list[tuple[str, str | None]] = []

    def submit_text(self, text, session_id=None, **kwargs):
        self.calls.append((text, session_id))
        return UIResponse(text=self.name, status="success", session_id=session_id)

    def submit_text_with_turn_evidence(self, text, session_id=None, **kwargs):
        self.calls.append((text, session_id))
        return SimpleNamespace(
            response=UIResponse(text=text, status="success", session_id=session_id),
            turn=SimpleNamespace(session_id=session_id, marker=text),
            applied_result=(session_id, text),
        )


def _visual():
    protected = _VisualDelegate("protected")
    explicit = _VisualDelegate("explicit")
    return (
        SameTurnVisualUIAdapterComposition(
            protected, gateway=_Gateway(), explicit_context_adapter=explicit
        ),
        protected,
        explicit,
    )


@pytest.mark.parametrize("explicit", (False, True))
def test_existing_visual_target_selection_and_tuple_compatibility(explicit):
    wrapper, protected, explicit_adapter = _visual()
    kwargs = {"integrated_visual_context": object()} if explicit else {}
    result = wrapper.submit_text_with_visual_companion(
        "consulta", session_id="V1", **kwargs
    )
    assert isinstance(result, tuple) and len(result) == 2
    assert result[0].text == ("explicit" if explicit else "protected")
    assert protected.calls == ([] if explicit else [("consulta", "V1")])
    assert explicit_adapter.calls == ([("consulta", "V1")] if explicit else [])


def test_existing_visual_gateway_last_state_is_not_correlated():
    wrapper, _, _ = _visual()
    response, applied = wrapper.submit_text_with_visual_companion(
        "consulta", session_id="V1"
    )
    assert response.session_id == "V1"
    assert applied == "stale-other-session"


@pytest.mark.parametrize("explicit", (False, True))
def test_red_visual_per_call_preserves_target_and_same_operation(explicit):
    wrapper, protected, explicit_adapter = _visual()
    method = getattr(
        wrapper, "submit_text_with_visual_companion_and_turn_evidence", None
    )
    assert callable(method), "M377 S4 RED: visual correlated seam absent"
    kwargs = {"integrated_visual_context": object()} if explicit else {}
    result = method("consulta", session_id="V1", **kwargs)
    assert result.response.session_id == "V1"
    assert result.turn.session_id == "V1"
    assert result.applied_result == ("V1", "consulta")
    assert protected.calls == ([] if explicit else [("consulta", "V1")])
    assert explicit_adapter.calls == ([("consulta", "V1")] if explicit else [])


def test_red_visual_reverse_completion_isolation():
    first_entered = Event()
    second_completed = Event()

    class _ReverseDelegate(_VisualDelegate):
        def submit_text_with_turn_evidence(self, text, session_id=None, **kwargs):
            if session_id == "V1":
                first_entered.set()
                assert second_completed.wait(5), "V2 did not finish"
            result = super().submit_text_with_turn_evidence(
                text, session_id=session_id, **kwargs
            )
            if session_id == "V2":
                second_completed.set()
            return result

    delegate = _ReverseDelegate("explicit")
    wrapper = SameTurnVisualUIAdapterComposition(
        _VisualDelegate("protected"),
        gateway=_Gateway(),
        explicit_context_adapter=delegate,
    )
    method = getattr(
        wrapper, "submit_text_with_visual_companion_and_turn_evidence", None
    )
    assert callable(method), "M377 S4 RED: visual concurrent seam absent"
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(
            method, "uno", session_id="V1", integrated_visual_context=object()
        )
        assert first_entered.wait(5), "V1 did not enter"
        second = pool.submit(
            method, "dos", session_id="V2", integrated_visual_context=object()
        )
        result2 = second.result(timeout=8)
        result1 = first.result(timeout=8)
    for result, session, text in (
        (result1, "V1", "uno"),
        (result2, "V2", "dos"),
    ):
        assert result.response.session_id == session
        assert result.turn.session_id == session
        assert result.turn.marker == text
        assert result.applied_result == (session, text)
    assert sorted(delegate.calls) == [("dos", "V2"), ("uno", "V1")]


@pytest.mark.parametrize("route", ("text", "voice"))
def test_red_local_adapter_exposes_causal_single_call_seam(route):
    method = getattr(
        LocalConversationUIAdapter, f"submit_{route}_with_turn_evidence", None
    )
    assert callable(method), "M377 S4 RED: local causal seam absent"
    assert "session_id" in inspect.signature(method).parameters


def test_red_local_submit_retains_inference_result_in_same_call():
    source = inspect.getsource(LocalConversationUIAdapter._submit)
    tree = ast.parse(
        source.lstrip() if not source.startswith(" ") else inspect.cleandoc(source)
    )
    assert any(
        isinstance(node, ast.Return)
        and isinstance(node.value, ast.Name)
        and node.value.id in ("result", "turn_bound_result")
        for node in ast.walk(tree)
    ), "M377 S4 RED: _submit still discards correlated turn evidence"


def test_protection_visual_historical_signature():
    signature = inspect.signature(
        SameTurnVisualUIAdapterComposition.submit_text_with_visual_companion
    )
    for key in (
        "explicit_document_ids",
        "explicit_sources",
        "explicit_evidence_references",
        "integrated_visual_context",
    ):
        assert key in signature.parameters


def test_protection_no_new_global_visual_cache():
    source = inspect.getsource(SameTurnVisualUIAdapterComposition)
    assert "last_turn_by_session" not in source
    assert "last_visual_by_session" not in source
