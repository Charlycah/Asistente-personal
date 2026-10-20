"""R-CAP17-CONV-ACCESS-S5: recommendation intent and catalogue bounds.

Contractual RED only. Does not authorize a recommendation engine or a limit change.
"""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.governed_local_library_runtime_wiring import (
    GovernedLocalLibraryConversationInterceptionPort,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)

NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)


class _KnowledgeRuntime:
    def assess(self, text):
        lowered = text.casefold()
        return SimpleNamespace(
            need=SimpleNamespace(
                local_documents_available=(
                    "biblioteca" in lowered or "mis libros" in lowered
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


def _request(text):
    return SimpleNamespace(text=text, owner="Owner", session_id="cap17-s5")


@pytest.mark.parametrize(
    "question",
    [
        "Podrias recomendarme un libro de la biblioteca ?",
        "Roby, ¿podés recomendarme un buen libro de la biblioteca para leer?",
        "¿Me recomendás algún libro de mi biblioteca?",
    ],
)
def test_recommendation_request_does_not_search_for_question_fragments(question):
    conversation = _Conversation()
    port = GovernedLocalLibraryConversationInterceptionPort(conversation)

    result = port.intercept(_request(question), now=NOW)

    assert conversation.calls == [], (
        "Recommendation intent must not be treated as a document-title search"
    )
    if result is not None:
        assert "La búsqueda de" not in result.response_text
        assert "Encontré" not in result.response_text


def test_explicit_book_search_preserves_governed_search_path():
    conversation = _Conversation()
    port = GovernedLocalLibraryConversationInterceptionPort(conversation)

    port.intercept(
        _request("Roby, buscá en la biblioteca el libro robots e imperio."),
        now=NOW,
    )

    assert len(conversation.calls) == 1
    operation, kwargs = conversation.calls[0]
    assert operation == "locate"
    assert "robots e imperio" in kwargs["search_query"].casefold()


def test_catalogue_limit_remains_visible_and_does_not_imply_absence(tmp_path):
    root = tmp_path / "library"
    root.mkdir()
    (root / "a.txt").write_text("A", encoding="utf-8")
    (root / "z.txt").write_text("Z", encoding="utf-8")
    library = GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(
            root=root,
            allowed_suffixes=(".txt",),
            max_catalogue_entries=1,
        )
    )

    catalogue = library.catalogue()
    result = library.search("z", max_results=5)

    assert catalogue.truncated is True
    assert len(catalogue.entries) == 1
    assert result.matches == ()
    assert result.bounded is True
