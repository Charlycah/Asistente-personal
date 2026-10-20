"""R-CAP17-CONV-ACCESS-S2: conversational capability query contract (RED)."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.governed_local_library_runtime_wiring import (
    GovernedLocalLibraryConversationInterceptionPort,
)

NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)


class _KnowledgeRuntime:
    def assess(self, text):
        return SimpleNamespace(
            need=SimpleNamespace(
                local_documents_available=(
                    "biblioteca" in text.casefold() or "mis libros" in text.casefold()
                )
            )
        )


class _Conversation:
    def __init__(self):
        self.knowledge_runtime = _KnowledgeRuntime()
        self.calls = []

    def handle_user_request(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            status=SimpleNamespace(value="no_match"),
            bounded=True,
            query=kwargs["search_query"],
        )

    def locate_admitted_request(self, **kwargs):
        self.calls.append(("locate", kwargs))
        return SimpleNamespace(
            status=SimpleNamespace(value="no_match"),
            bounded=True,
            query=kwargs["search_query"],
        )

    def handle_admitted_request(self, **kwargs):
        self.calls.append(kwargs)
        raise AssertionError("Unexpected follow-up search")


def _request(text, session_id="cap17-s2"):
    return SimpleNamespace(text=text, owner="Owner", session_id=session_id)


@pytest.mark.parametrize(
    "question",
    [
        "Roby, ¿podés tener acceso a la biblioteca?",
        "¿Podés acceder a la biblioteca?",
        "¿Tenés acceso a mis libros?",
    ],
)
def test_capability_question_does_not_start_document_search(question):
    conversation = _Conversation()
    port = GovernedLocalLibraryConversationInterceptionPort(conversation)
    result = port.intercept(_request(question), now=NOW)
    assert conversation.calls == [], "A capability question must not run a search"
    assert result is None or "búsqueda de" not in result.response_text.casefold()


def test_empty_explicit_library_search_requests_query_without_search():
    conversation = _Conversation()
    port = GovernedLocalLibraryConversationInterceptionPort(conversation)
    result = port.intercept(_request("Buscá en la biblioteca"), now=NOW)
    assert conversation.calls == []
    assert result is not None
    assert result.rationale == "local_library_query_required"


def test_explicit_search_still_enters_existing_governed_path():
    conversation = _Conversation()
    port = GovernedLocalLibraryConversationInterceptionPort(conversation)
    port.intercept(_request("Buscá en la biblioteca Fundación"), now=NOW)
    assert len(conversation.calls) == 1
    operation, kwargs = conversation.calls[0]
    assert operation == "locate"
    assert kwargs["search_query"] == "Fundación"
