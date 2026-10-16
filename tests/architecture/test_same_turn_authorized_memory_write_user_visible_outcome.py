from __future__ import annotations

from types import SimpleNamespace

from app.official_conversation_gateway import ConversationOrigin
from app.productive_governed_learning_wiring import (
    ProductiveGovernedLearningOutcome,
    ProductiveGovernedLearningResult,
)
from app.runtime_ui_adapter import LocalConversationUIAdapter


class _Brain:
    def __init__(self) -> None:
        self.calls = []

    @property
    def diagnostics(self):
        return None

    def process(self, text, *, origin, session_id):
        self.calls.append((text, origin, session_id))
        return SimpleNamespace(
            status="completed",
            response_text="normal conversation",
            session_id=session_id,
        )


def _adapter(
    *,
    pending=True,
    authorization=object(),
    result=None,
):
    adapter = LocalConversationUIAdapter.__new__(LocalConversationUIAdapter)
    adapter.runtime = None
    adapter._brain = _Brain()
    adapter._pending_memory_write_reader = lambda session_id: pending
    adapter._pending_memory_write_response_evaluator = (
        lambda **kwargs: authorization
    )
    calls = []

    def execute(**kwargs):
        calls.append(kwargs)
        return result

    adapter._pending_memory_write_executor = execute
    adapter._last_memory_write_execution_authorization = None
    adapter._last_memory_write_execution_result = None
    return adapter, calls


def _result(outcome):
    return ProductiveGovernedLearningResult(
        outcome=outcome,
        rationale_codes=("test",),
        write_request=SimpleNamespace(),
        stored_memory_ids=("memory-1",)
        if outcome
        in {
            ProductiveGovernedLearningOutcome.STORED,
            ProductiveGovernedLearningOutcome.ALREADY_STORED,
        }
        else (),
        writer_call_performed=outcome
        in {
            ProductiveGovernedLearningOutcome.STORED,
            ProductiveGovernedLearningOutcome.ALREADY_STORED,
        },
    )


def test_exact_authorization_executes_once_and_short_circuits_brain() -> None:
    result = _result(ProductiveGovernedLearningOutcome.STORED)
    authorization = object()
    adapter, calls = _adapter(
        authorization=authorization,
        result=result,
    )

    response = adapter._submit(
        "Sí, guardar ahora",
        session_id="session-a",
        origin=ConversationOrigin.DESKTOP_TEXT,
    )

    assert len(calls) == 1
    assert calls[0]["session_id"] == "session-a"
    assert calls[0]["authorization"] is authorization
    assert adapter._brain.calls == []
    assert response.text == "Bien, guardé ese aprendizaje en la memoria oficial."
    assert adapter.last_memory_write_execution_authorization is authorization
    assert adapter.last_memory_write_execution_result is result


def test_generic_response_without_m369_evidence_uses_normal_brain_once() -> None:
    adapter, calls = _adapter(
        authorization=None,
        result=None,
    )

    response = adapter._submit(
        "sí",
        session_id="session-a",
        origin=ConversationOrigin.DESKTOP_TEXT,
    )

    assert calls == []
    assert len(adapter._brain.calls) == 1
    assert response.text == "normal conversation"
    assert adapter.last_memory_write_execution_authorization is None
    assert adapter.last_memory_write_execution_result is None


def test_no_pending_request_uses_normal_brain_once() -> None:
    adapter, calls = _adapter(
        pending=False,
        authorization=object(),
        result=None,
    )

    response = adapter._submit(
        "cualquier mensaje",
        session_id="session-a",
        origin=ConversationOrigin.DESKTOP_TEXT,
    )

    assert calls == []
    assert len(adapter._brain.calls) == 1
    assert response.text == "normal conversation"


def test_write_failed_is_visible_and_short_circuits_normal_brain() -> None:
    result = _result(ProductiveGovernedLearningOutcome.WRITE_FAILED)
    adapter, calls = _adapter(
        authorization=object(),
        result=result,
    )

    response = adapter._submit(
        "Sí, guardar ahora",
        session_id="session-a",
        origin=ConversationOrigin.DESKTOP_TEXT,
    )

    assert len(calls) == 1
    assert adapter._brain.calls == []
    assert (
        response.text
        == "La autorización es válida, pero no pude guardar ese aprendizaje."
    )


def test_memory_unavailable_is_visible_and_short_circuits_normal_brain() -> None:
    result = _result(ProductiveGovernedLearningOutcome.MEMORY_UNAVAILABLE)
    adapter, calls = _adapter(
        authorization=object(),
        result=result,
    )

    response = adapter._submit(
        "Sí, guardar ahora",
        session_id="session-a",
        origin=ConversationOrigin.DESKTOP_TEXT,
    )

    assert len(calls) == 1
    assert adapter._brain.calls == []
    assert (
        response.text
        == "La autorización es válida, pero la memoria oficial no está disponible."
    )


def test_ui_source_has_no_memory_authorization_phrase_parser_or_writer_call() -> None:
    import inspect

    source = inspect.getsource(LocalConversationUIAdapter)

    assert '"guardar ahora"' not in source
    assert "'guardar ahora'" not in source
    assert "_AFFIRMATIVE_RE" not in source
    assert "remember_governed_learning(" not in source
    assert "execute_certified_write_request(" not in source
